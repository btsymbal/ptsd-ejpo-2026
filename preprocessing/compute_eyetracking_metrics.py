# %% [markdown]
# # Compute Eye-Tracking Metrics from Raw Gaze Sessions
#
# Extract dwell time, visit counts, and blink behavior from 30 raw gaze
# session CSVs.  Aggregate per category, merge with clinical metadata,
# and export a single-row-per-session dataset for downstream analysis.

# %%
import os
from pathlib import Path

os.chdir(Path(__file__).resolve().parent.parent)

import json
import numpy as np
import pandas as pd
from collections import Counter, defaultdict

# %%  Load materials
# -------------------------------------------------------------------
slide_dur_df = pd.read_csv('materials/slide_durations.csv')
slide_duration = dict(zip(slide_dur_df['slide_number'], slide_dur_df['expected_duration_ms']))

with open('materials/id_to_category_mapping.json') as f:
    id_to_category = json.load(f)

with open('materials/image_pair_ids.json') as f:
    slide_to_image_ids = {int(k): v for k, v in json.load(f).items()}

# Derive slide → [cat1, cat2]
slide_to_categories = {}
for sn, (img1, img2) in slide_to_image_ids.items():
    slide_to_categories[sn] = (
        id_to_category.get(img1, 'unknown'),
        id_to_category.get(img2, 'unknown'),
    )

CATEGORIES = sorted({c for pair in slide_to_categories.values() for c in pair})
assert len(CATEGORIES) == 11, f"Expected 11 categories, got {len(CATEGORIES)}: {CATEGORIES}"

cat_slide_counts = Counter()
for sn, (c1, c2) in slide_to_categories.items():
    cat_slide_counts[c1] += 1
    cat_slide_counts[c2] += 1

VISIT_MIN_DURATION_MS = 100

# Threat categories → eligible neutral counterparts
THREAT_NEUTRALS = {
    'angry_face':       ['neutral_face'],
    'anxiety_inducing': ['neutral'],
    'warfare':          ['happy_event', 'neutral'],
    'soldiers':         ['happy_face', 'neutral', 'neutral_face'],
}

# Precompute which slides match each threat–neutral pair
# For each threat category, store list of (slide_num, threat_img_id, neutral_img_id)
threat_slide_map = {t: [] for t in THREAT_NEUTRALS}
for sn, (img1, img2) in slide_to_image_ids.items():
    c1 = id_to_category.get(img1, 'unknown')
    c2 = id_to_category.get(img2, 'unknown')
    for threat, neutrals in THREAT_NEUTRALS.items():
        if c1 == threat and c2 in neutrals:
            threat_slide_map[threat].append((sn, img1, img2))
        elif c2 == threat and c1 in neutrals:
            threat_slide_map[threat].append((sn, img2, img1))

print("Categories:", CATEGORIES)
for t, slides in threat_slide_map.items():
    print(f"  {t}: {len(slides)} threat–neutral slides")

# %%  compute_slide_dwell_pct
# -------------------------------------------------------------------
def compute_slide_dwell_pct(slide_df, slide_num, expected_ms=None):
    """Return {img_id: dwell_pct} for both images on this slide.

    dwell_pct = (time spent gazing at image / expected_ms) * 100
    Time at each row = TIMESTAMP[i+1] - TIMESTAMP[i]; last row gets 0.
    If expected_ms is None, uses full slide duration.
    """
    img1, img2 = slide_to_image_ids[slide_num]
    if expected_ms is None:
        expected_ms = slide_duration[slide_num]

    if len(slide_df) == 0 or expected_ms <= 0:
        return {img1: 0.0, img2: 0.0}

    timestamps = slide_df['TIMESTAMP'].values
    images = slide_df['IMAGE'].values

    # Duration at each sample = gap to next sample; last = 0
    durations = np.empty(len(timestamps))
    durations[:-1] = np.diff(timestamps)
    durations[-1] = 0.0

    time_per_img = defaultdict(float)
    for dur, img in zip(durations, images):
        if img != 'no_image':
            time_per_img[img] += dur

    return {
        img1: (time_per_img.get(img1, 0.0) / expected_ms) * 100,
        img2: (time_per_img.get(img2, 0.0) / expected_ms) * 100,
    }


# %%  compute_slide_offscreen_pct
# -------------------------------------------------------------------
def compute_slide_offscreen_pct(slide_df, slide_num, expected_ms=None):
    """Return percentage of time with gaze off-screen (RX not in [0,1] or RY not in [0,1]).

    Uses timestamp-based durations / expected_duration_ms * 100.
    """
    if expected_ms is None:
        expected_ms = slide_duration[slide_num]

    if len(slide_df) == 0 or expected_ms <= 0:
        return 0.0

    timestamps = slide_df['TIMESTAMP'].values
    rx = slide_df['RX'].values
    ry = slide_df['RY'].values

    durations = np.empty(len(timestamps))
    durations[:-1] = np.diff(timestamps)
    durations[-1] = 0.0

    offscreen_mask = (rx < 0) | (rx > 1) | (ry < 0) | (ry > 1)
    offscreen_time = durations[offscreen_mask].sum()

    return (offscreen_time / expected_ms) * 100


# %%  filter_late
# -------------------------------------------------------------------
def filter_late(slide_df, late_onset_ms=800):
    """Filter to rows where TIMESTAMP >= first_timestamp + late_onset_ms."""
    if len(slide_df) == 0:
        return slide_df
    first_ts = slide_df['TIMESTAMP'].iloc[0]
    return slide_df[slide_df['TIMESTAMP'] >= first_ts + late_onset_ms]


# %%  compute_slide_visits
# -------------------------------------------------------------------
def compute_slide_visits(slide_df, slide_num):
    """Return {img_id: visit_count} for both images on this slide.

    A "visit" = a continuous run of gaze samples on the same image
    whose total duration >= VISIT_MIN_DURATION_MS.
    """
    img1, img2 = slide_to_image_ids[slide_num]

    if len(slide_df) == 0:
        return {img1: 0, img2: 0}

    timestamps = slide_df['TIMESTAMP'].values
    images = slide_df['IMAGE'].values

    visits = {img1: 0, img2: 0}
    current_img = None
    run_start = 0.0

    for i, (ts, img) in enumerate(zip(timestamps, images)):
        if img != current_img:
            # End previous run — check if it qualifies
            if current_img is not None and current_img != 'no_image':
                run_dur = ts - run_start
                if run_dur >= VISIT_MIN_DURATION_MS:
                    visits[current_img] = visits.get(current_img, 0) + 1
            current_img = img
            run_start = ts

    # Close final run using last timestamp (duration = 0 for last sample,
    # so effectively run_dur = last_ts - run_start which may be 0)
    if current_img is not None and current_img != 'no_image' and len(timestamps) > 1:
        run_dur = timestamps[-1] - run_start
        if run_dur >= VISIT_MIN_DURATION_MS:
            visits[current_img] = visits.get(current_img, 0) + 1

    return visits


# %%  compute_blinks
# -------------------------------------------------------------------
def compute_blinks(session_df):
    """Detect blink events and compute per-session and per-category metrics.

    Returns a dict with:
      - total_blink_count
      - mean_blink_rate_{cat}  (blinks per slide for that category)
      - mean/std_blink_interval_norm  (interval / slide_duration, dimensionless)
      - mean_blink_latency_norm_{cat}  (latency / slide_duration, dimensionless)
      - mean_blink_duration_ms
      - mean/std_blink_duration_{cat}
    """
    blink_col = session_df['BLINK'].values
    ts_col = session_df['TIMESTAMP'].values
    scene_col = session_df['SCENE_INDEX'].values

    # Detect blink runs — split at SCENE_INDEX changes too
    blinks = []  # list of (start_ts, end_ts, duration, slide_num)
    in_blink = False
    blink_start_ts = 0.0
    blink_scene = 0.0

    for i in range(len(blink_col)):
        if blink_col[i]:
            if not in_blink:
                # Start new blink
                in_blink = True
                blink_start_ts = ts_col[i]
                blink_scene = scene_col[i]
            elif scene_col[i] != blink_scene:
                # SCENE_INDEX changed mid-blink → close previous, start new
                end_ts = ts_col[i - 1] if i > 0 else blink_start_ts
                duration = end_ts - blink_start_ts
                sn = int((blink_scene + 1) / 2)
                if 1 <= sn <= 75:
                    blinks.append((blink_start_ts, end_ts, duration, sn))
                blink_start_ts = ts_col[i]
                blink_scene = scene_col[i]
        else:
            if in_blink:
                # End blink
                end_ts = ts_col[i - 1] if i > 0 else blink_start_ts
                duration = end_ts - blink_start_ts
                sn = int((blink_scene + 1) / 2)
                if 1 <= sn <= 75:
                    blinks.append((blink_start_ts, end_ts, duration, sn))
                in_blink = False

    # Close trailing blink
    if in_blink:
        end_ts = ts_col[-1]
        duration = end_ts - blink_start_ts
        sn = int((blink_scene + 1) / 2)
        if 1 <= sn <= 75:
            blinks.append((blink_start_ts, end_ts, duration, sn))

    result = {}
    result['total_blink_count'] = len(blinks)

    # Per-category blink count and duration
    cat_blink_durations = defaultdict(list)
    for _, _, dur, sn in blinks:
        for cat in slide_to_categories.get(sn, ()):
            cat_blink_durations[cat].append(dur)

    for cat in CATEGORIES:
        durs = cat_blink_durations.get(cat, [])
        result[f'mean_blink_rate_{cat}'] = len(durs) / cat_slide_counts[cat]
        result[f'mean_blink_duration_{cat}'] = np.mean(durs) if durs else np.nan
        result[f'std_blink_duration_{cat}'] = np.std(durs, ddof=1) if len(durs) > 1 else np.nan

    # Overall blink duration
    all_durs = [b[2] for b in blinks]
    result['mean_blink_duration_ms'] = np.mean(all_durs) if all_durs else np.nan

    # Blink intervals normalized by slide duration of the first blink in each pair
    if len(blinks) > 1:
        onsets = [b[0] for b in blinks]
        slide_nums = [b[3] for b in blinks]
        intervals_norm = []
        for i in range(len(onsets) - 1):
            interval_ms = onsets[i + 1] - onsets[i]
            sn = slide_nums[i]
            sd = slide_duration.get(sn, 2500)
            intervals_norm.append(interval_ms / sd)
        intervals_norm = np.array(intervals_norm)
        result['mean_blink_interval_norm'] = np.mean(intervals_norm)
        result['std_blink_interval_norm'] = np.std(intervals_norm, ddof=1) if len(intervals_norm) > 1 else np.nan
    else:
        result['mean_blink_interval_norm'] = np.nan
        result['std_blink_interval_norm'] = np.nan

    # Per-category blink latency: time from slide onset to first blink on that slide
    # Slide onset = first TIMESTAMP where SCENE_INDEX maps to that slide
    slide_onsets = {}
    for i in range(len(scene_col)):
        sn = int((scene_col[i] + 1) / 2)
        if 1 <= sn <= 75 and sn not in slide_onsets:
            slide_onsets[sn] = ts_col[i]

    cat_latencies = defaultdict(list)
    # Group blinks by slide, take earliest per slide
    slide_first_blink = {}
    for start_ts, _, _, sn in blinks:
        if sn not in slide_first_blink or start_ts < slide_first_blink[sn]:
            slide_first_blink[sn] = start_ts

    for sn, first_blink_ts in slide_first_blink.items():
        onset = slide_onsets.get(sn)
        if onset is not None:
            latency = first_blink_ts - onset
            sd = slide_duration.get(sn, 2500)
            latency_norm = latency / sd
            for cat in slide_to_categories.get(sn, ()):
                cat_latencies[cat].append(latency_norm)

    for cat in CATEGORIES:
        lats = cat_latencies.get(cat, [])
        result[f'mean_blink_latency_norm_{cat}'] = np.mean(lats) if lats else np.nan

    return result


# %%  Main processing loop
# -------------------------------------------------------------------
raw_dir = Path('data/raw_sessions')
session_files = sorted(raw_dir.glob('*.csv'))
assert len(session_files) == 30, f"Expected 30 session files, got {len(session_files)}"

results = []

for fpath in session_files:
    session_id = fpath.stem
    print(f"Processing {session_id} ...")

    df = pd.read_csv(fpath, usecols=['TIMESTAMP', 'BLINK', 'SCENE_INDEX', 'IMAGE', 'RX', 'RY'])
    df = df.sort_values('TIMESTAMP').reset_index(drop=True)

    # Per-category accumulators
    cat_dwell_pcts = defaultdict(list)       # cat → [pct, pct, ...]
    cat_visits = defaultdict(list)           # cat → [visit_count, ...]
    threat_delta_dwell = defaultdict(list)   # threat_cat → [delta, ...]
    cat_dwell_pcts_late = defaultdict(list)
    cat_visits_late = defaultdict(list)
    cat_offscreen_pcts = defaultdict(list)
    cat_offscreen_pcts_late = defaultdict(list)

    for slide_num in range(1, 76):
        scene_idx = slide_num * 2 - 1  # 1→1, 2→3, ..., 75→149
        slide_df = df[df['SCENE_INDEX'] == float(scene_idx)]

        # Dwell percentages
        dwell = compute_slide_dwell_pct(slide_df, slide_num)
        for img_id, pct in dwell.items():
            cat = id_to_category.get(img_id, 'unknown')
            cat_dwell_pcts[cat].append(pct)

        # Visits
        vis = compute_slide_visits(slide_df, slide_num)
        for img_id, cnt in vis.items():
            cat = id_to_category.get(img_id, 'unknown')
            cat_visits[cat].append(cnt)

        # Late-window dwell and visits (>= 800 ms)
        slide_df_late = filter_late(slide_df)
        late_expected_ms = slide_duration[slide_num] - 800
        dwell_late = compute_slide_dwell_pct(slide_df_late, slide_num, expected_ms=late_expected_ms)
        for img_id, pct in dwell_late.items():
            cat = id_to_category.get(img_id, 'unknown')
            cat_dwell_pcts_late[cat].append(pct)

        vis_late = compute_slide_visits(slide_df_late, slide_num)
        for img_id, cnt in vis_late.items():
            cat = id_to_category.get(img_id, 'unknown')
            cat_visits_late[cat].append(cnt)

        # Off-screen percentage (full slide)
        offscreen_pct = compute_slide_offscreen_pct(slide_df, slide_num)
        for cat in slide_to_categories.get(slide_num, ()):
            cat_offscreen_pcts[cat].append(offscreen_pct)

        # Off-screen percentage (late window)
        offscreen_pct_late = compute_slide_offscreen_pct(slide_df_late, slide_num, expected_ms=late_expected_ms)
        for cat in slide_to_categories.get(slide_num, ()):
            cat_offscreen_pcts_late[cat].append(offscreen_pct_late)

        # Threat–neutral delta dwell
        for threat, slide_list in threat_slide_map.items():
            for (sn, t_img, n_img) in slide_list:
                if sn == slide_num:
                    t_pct = dwell.get(t_img, 0.0)
                    n_pct = dwell.get(n_img, 0.0)
                    threat_delta_dwell[threat].append(t_pct - n_pct)

    # Blink metrics
    blink_metrics = compute_blinks(df)

    # Build row
    row = {'session_id': session_id}

    for cat in CATEGORIES:
        vals = cat_dwell_pcts.get(cat, [])
        row[f'mean_dwell_pct_{cat}'] = np.mean(vals) if vals else np.nan
        row[f'std_dwell_pct_{cat}'] = np.std(vals, ddof=1) if len(vals) > 1 else np.nan

    for threat in THREAT_NEUTRALS:
        vals = threat_delta_dwell.get(threat, [])
        row[f'std_delta_dwell_pct_{threat}'] = np.std(vals, ddof=1) if len(vals) > 1 else np.nan

    for cat in CATEGORIES:
        vals = cat_visits.get(cat, [])
        row[f'mean_visits_{cat}'] = np.mean(vals) if vals else np.nan

    for cat in CATEGORIES:
        vals = cat_dwell_pcts_late.get(cat, [])
        row[f'mean_dwell_pct_late_{cat}'] = np.mean(vals) if vals else np.nan

    for cat in CATEGORIES:
        vals = cat_visits_late.get(cat, [])
        row[f'mean_visits_late_{cat}'] = np.mean(vals) if vals else np.nan

    for cat in CATEGORIES:
        vals = cat_offscreen_pcts.get(cat, [])
        row[f'mean_offscreen_pct_{cat}'] = np.mean(vals) if vals else np.nan

    for cat in CATEGORIES:
        vals = cat_offscreen_pcts_late.get(cat, [])
        row[f'mean_offscreen_pct_late_{cat}'] = np.mean(vals) if vals else np.nan

    row.update(blink_metrics)

    results.append(row)

metrics_df = pd.DataFrame(results)
print(f"\nComputed metrics for {len(metrics_df)} sessions.")
print(f"Columns: {len(metrics_df.columns)}")

# %%  Merge with metadata
# -------------------------------------------------------------------
meta_df = pd.read_csv('data/simplified/dataset_merged_1_and_2.csv',
                       usecols=['sessions', 'if_PTSD', 'ITI_PTSD', 'ITI_cPTSD', 'if_antipsychotic'])
meta_df = meta_df.rename(columns={'sessions': 'session_id'})

metrics_df = metrics_df.merge(meta_df, on='session_id', how='left')
print(f"After merge: {metrics_df.shape}")

# %%  Validation
# -------------------------------------------------------------------
assert len(metrics_df) == 30, f"Expected 30 rows, got {len(metrics_df)}"
assert metrics_df['session_id'].nunique() == 30, "Duplicate session_ids detected"

# Dwell pct should be in [0, 100] range (with small tolerance for floating point)
dwell_cols = [c for c in metrics_df.columns if 'dwell_pct' in c and c.startswith('mean_') and '_late_' not in c]
for col in dwell_cols:
    vals = metrics_df[col].dropna()
    assert vals.min() >= -0.01, f"{col} has negative values: {vals.min()}"
    assert vals.max() <= 101, f"{col} has values > 100: {vals.max()}"

# Late dwell pct should be in [0, 100]
late_dwell_cols = [c for c in metrics_df.columns if 'dwell_pct_late_' in c and c.startswith('mean_')]
for col in late_dwell_cols:
    vals = metrics_df[col].dropna()
    assert vals.min() >= -0.01, f"{col} has negative values: {vals.min()}"
    assert vals.max() <= 101, f"{col} has values > 100: {vals.max()}"

# Visit counts should be non-negative
visit_cols = [c for c in metrics_df.columns if 'visits' in c]
for col in visit_cols:
    assert (metrics_df[col].dropna() >= 0).all(), f"{col} has negative values"

# Offscreen pct should be in [0, 100]
offscreen_cols = [c for c in metrics_df.columns if 'offscreen_pct' in c]
for col in offscreen_cols:
    vals = metrics_df[col].dropna()
    assert vals.min() >= -0.01, f"{col} has negative values: {vals.min()}"
    assert vals.max() <= 101, f"{col} has values > 100: {vals.max()}"

# Blink counts should be non-negative integers
assert (metrics_df['total_blink_count'] >= 0).all()

# Metadata should be present for all sessions
for col in ['if_PTSD', 'ITI_PTSD', 'ITI_cPTSD', 'if_antipsychotic']:
    assert metrics_df[col].notna().all(), f"Missing metadata in {col}"

print("All validations passed!")
print(f"\nFinal shape: {metrics_df.shape}")
print(f"\nSummary statistics for dwell_pct columns:")
print(metrics_df[dwell_cols].describe().round(2))

# %%  Export
# -------------------------------------------------------------------
os.makedirs('data/simplified', exist_ok=True)
metrics_df.to_csv('data/simplified/dataset_eyetracking_metrics.csv', index=False)
print(f"Exported to data/simplified/dataset_eyetracking_metrics.csv")
print(f"Shape: {metrics_df.shape[0]} rows x {metrics_df.shape[1]} columns")

# %%  Generate report
# -------------------------------------------------------------------
os.makedirs('reports', exist_ok=True)

report_lines = [
    "# Eye-Tracking Metrics Report",
    "",
    f"**Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",
    f"**Sessions processed:** {len(metrics_df)}",
    f"**Output columns:** {len(metrics_df.columns)}",
    "",
    "## Data Sources",
    "",
    "- `data/raw_sessions/*.csv` — 30 raw gaze session files",
    "- `materials/slide_durations.csv` — expected duration per slide",
    "- `materials/id_to_category_mapping.json` — image ID to category (11 categories)",
    "- `materials/image_pair_ids.json` — slide number to image pair IDs",
    "- `data/simplified/dataset_merged_1_and_2.csv` — clinical metadata",
    "",
    "## Categories",
    "",
]
for cat in CATEGORIES:
    report_lines.append(f"- `{cat}`")

report_lines += [
    "",
    "## Metric Descriptions",
    "",
    "### Dwell Time",
    "",
    "- **`mean_dwell_pct_{category}`**: Mean percentage of expected slide duration spent",
    "  gazing at images of this category, across all slides containing the category.",
    "  Computed as `(gaze_time_ms / expected_duration_ms) * 100` per image per slide,",
    "  then averaged across all images of the category.",
    "- **`std_dwell_pct_{category}`**: Standard deviation of dwell percentages (ddof=1).",
    "",
    "### Late-Window Dwell Time (≥ 800 ms)",
    "",
    "- **`mean_dwell_pct_late_{category}`**: Same as `mean_dwell_pct` but computed only",
    "  on gaze samples from 800 ms after slide onset. Denominator is `expected_duration_ms - 800`.",
    "  Captures sustained attention after initial orienting.",
    "",
    "### Delta Dwell (Threat Bias)",
    "",
    "For each threat category, slides are identified where one image is threat and",
    "the other is an eligible neutral counterpart:",
    "",
    "| Threat | Neutral counterparts | Slide count |",
    "|--------|---------------------|-------------|",
]
for threat, neutrals in THREAT_NEUTRALS.items():
    n_slides = len(threat_slide_map[threat])
    report_lines.append(f"| `{threat}` | {', '.join(f'`{n}`' for n in neutrals)} | {n_slides} |")

report_lines += [
    "",
    "- **`std_delta_dwell_pct_{threat}`**: Standard deviation (ddof=1) of",
    "  `threat_dwell_pct - neutral_dwell_pct` across all threat–neutral slides.",
    "  Higher values indicate more variable attentional bias toward the threat image.",
    "",
    "### Visit Counts",
    "",
    "- **`mean_visits_{category}`**: Mean number of qualifying visits (continuous gaze",
    f"  runs >= {VISIT_MIN_DURATION_MS} ms) to images of this category, across all relevant slides.",
    "",
    "### Late-Window Visit Counts (≥ 800 ms)",
    "",
    "- **`mean_visits_late_{category}`**: Same as `mean_visits` but computed only on",
    "  gaze samples from 800 ms after slide onset.",
    "",
    "### Off-Screen Gaze",
    "",
    "- **`mean_offscreen_pct_{category}`**: Mean percentage of expected slide duration",
    "  where gaze was off-screen (RX ∉ [0,1] or RY ∉ [0,1]), averaged across slides",
    "  of this category. Attributed to both categories of the slide.",
    "",
    "### Late-Window Off-Screen Gaze (≥ 800 ms)",
    "",
    "- **`mean_offscreen_pct_late_{category}`**: Same as `mean_offscreen_pct` but",
    "  computed only on gaze samples from 800 ms after slide onset. Denominator is",
    "  `expected_duration_ms - 800`.",
    "",
    "### Blink Metrics",
    "",
    "A blink is a run of consecutive `BLINK=True` samples. Runs are split at",
    "`SCENE_INDEX` boundaries. Each blink is attributed to both categories of its slide.",
    "",
    "- **`total_blink_count`**: Total blinks across the entire session.",
    "- **`mean_blink_rate_{category}`**: Mean blinks per slide for this category.",
    "  Computed as `total_blinks_on_category_slides / number_of_slides_in_category`.",
    "  Normalized for unequal slide counts across categories.",
    "- **`mean_blink_interval_norm`**: Mean inter-blink interval normalized by the",
    "  slide duration of the first blink in each pair. Dimensionless ratio.",
    "- **`std_blink_interval_norm`**: Std of normalized inter-blink intervals (ddof=1).",
    "- **`mean_blink_latency_norm_{category}`**: Mean time from slide onset to first blink,",
    "  normalized by slide duration. Dimensionless ratio. Slides with no blinks excluded.",
    "- **`mean_blink_duration_ms`**: Mean blink duration across all blinks.",
    "- **`mean_blink_duration_{category}`**: Mean blink duration on slides of this category.",
    "- **`std_blink_duration_{category}`**: Std of blink durations on slides of this",
    "  category (ddof=1).",
    "",
    "### Metadata",
    "",
    "Merged from `dataset_merged_1_and_2.csv`:",
    "",
    "- **`if_PTSD`**: Binary PTSD status",
    "- **`ITI_PTSD`**: ITI PTSD score",
    "- **`ITI_cPTSD`**: ITI complex PTSD score",
    "- **`if_antipsychotic`**: Binary antipsychotic medication status",
    "",
    "## Column Summary",
    "",
    f"| Group | Count |",
    f"|-------|-------|",
    f"| session_id | 1 |",
    f"| mean_dwell_pct | {len(CATEGORIES)} |",
    f"| std_dwell_pct | {len(CATEGORIES)} |",
    f"| std_delta_dwell_pct | {len(THREAT_NEUTRALS)} |",
    f"| mean_visits | {len(CATEGORIES)} |",
    f"| mean_dwell_pct_late | {len(CATEGORIES)} |",
    f"| mean_visits_late | {len(CATEGORIES)} |",
    f"| mean_offscreen_pct | {len(CATEGORIES)} |",
    f"| mean_offscreen_pct_late | {len(CATEGORIES)} |",
    f"| total_blink_count | 1 |",
    f"| mean_blink_rate | {len(CATEGORIES)} |",
    f"| mean_blink_interval_norm | 1 |",
    f"| std_blink_interval_norm | 1 |",
    f"| mean_blink_latency_norm | {len(CATEGORIES)} |",
    f"| mean_blink_duration_ms | 1 |",
    f"| mean_blink_duration | {len(CATEGORIES)} |",
    f"| std_blink_duration | {len(CATEGORIES)} |",
    f"| metadata | 4 |",
    f"| **Total** | **{len(metrics_df.columns)}** |",
    "",
    "## Edge Cases",
    "",
    "- Slides where both images show `no_image`: 0% dwell and 0 visits (included in aggregation).",
    "- Blink latency: slides with no blinks are excluded from the per-category mean.",
    "- Blink runs spanning SCENE_INDEX boundaries are split into separate blinks.",
    "- Late window: for slides with expected_duration_ms = 1500, the late window is only 700 ms.",
    "  If no samples exist in the late window, dwell = 0% and visits = 0.",
    "- Off-screen gaze: uses raw RX/RY coordinates. Values outside [0,1] indicate gaze",
    "  is off the screen area. NaN RX/RY rows are treated as on-screen (conservative).",
    "",
]

with open('reports/eyetracking_metrics_report.md', 'w') as f:
    f.write('\n'.join(report_lines))

print("Report saved to reports/eyetracking_metrics_report.md")
