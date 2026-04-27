# %% [markdown]
# # Recompute Eye-Tracking Metrics with Flagged Images Removed
#
# Re-aggregates per-category eye-tracking metrics after dropping the images
# flagged as low-quality by `images_analysis/lmm_image_quality_evaluation.py`
# (see `data/simplified/image_quality_flags.csv` and
# `reports/images_analysis/05_final_flagging_rule.md`).
#
# The helper functions and slide-mapping setup mirror
# `preprocessing/compute_eyetracking_metrics.py` (lines 19–305) — duplicated
# here so the cleaned-image variant lives as a single self-contained script.
#
# Filtering policy:
#
# - Per-image metrics (dwell, visits, late-window dwell/visits): skip the
#   image entirely if its `image_id` is in the flagged set.
# - Off-screen percentage is a slide-level metric; we attribute it to a
#   category only via the *unflagged* image of that slide.
# - Threat–neutral delta dwell (used by H3): skip the slide-pair if either
#   the threat or the neutral image is flagged.
# - Blink metrics: NOT filtered (session/slide-level events).

# %%
import os
from pathlib import Path

os.chdir(Path(__file__).resolve().parent.parent)

import json
import numpy as np
import pandas as pd
from collections import Counter, defaultdict

# %%  Load materials
slide_dur_df = pd.read_csv('materials/slide_durations.csv')
slide_duration = dict(zip(slide_dur_df['slide_number'], slide_dur_df['expected_duration_ms']))

with open('materials/id_to_category_mapping.json') as f:
    id_to_category = json.load(f)

with open('materials/image_pair_ids.json') as f:
    slide_to_image_ids = {int(k): v for k, v in json.load(f).items()}

slide_to_categories = {}
for sn, (img1, img2) in slide_to_image_ids.items():
    slide_to_categories[sn] = (
        id_to_category.get(img1, 'unknown'),
        id_to_category.get(img2, 'unknown'),
    )

CATEGORIES = sorted({c for pair in slide_to_categories.values() for c in pair})
assert len(CATEGORIES) == 11, f"Expected 11 categories, got {len(CATEGORIES)}"

cat_slide_counts = Counter()
for sn, (c1, c2) in slide_to_categories.items():
    cat_slide_counts[c1] += 1
    cat_slide_counts[c2] += 1

VISIT_MIN_DURATION_MS = 100

THREAT_NEUTRALS = {
    'angry_face':       ['neutral_face'],
    'anxiety_inducing': ['neutral'],
    'warfare':          ['happy_event', 'neutral'],
    'soldiers':         ['happy_face', 'neutral', 'neutral_face'],
}

threat_slide_map = {t: [] for t in THREAT_NEUTRALS}
for sn, (img1, img2) in slide_to_image_ids.items():
    c1 = id_to_category.get(img1, 'unknown')
    c2 = id_to_category.get(img2, 'unknown')
    for threat, neutrals in THREAT_NEUTRALS.items():
        if c1 == threat and c2 in neutrals:
            threat_slide_map[threat].append((sn, img1, img2))
        elif c2 == threat and c1 in neutrals:
            threat_slide_map[threat].append((sn, img2, img1))

# %%  Helper: compute_slide_dwell_pct
def compute_slide_dwell_pct(slide_df, slide_num, expected_ms=None):
    img1, img2 = slide_to_image_ids[slide_num]
    if expected_ms is None:
        expected_ms = slide_duration[slide_num]
    if len(slide_df) == 0 or expected_ms <= 0:
        return {img1: 0.0, img2: 0.0}
    timestamps = slide_df['TIMESTAMP'].values
    images = slide_df['IMAGE'].values
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

# %%  Helper: compute_slide_offscreen_pct
def compute_slide_offscreen_pct(slide_df, slide_num, expected_ms=None):
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

# %%  Helper: filter_late
def filter_late(slide_df, late_onset_ms=800):
    if len(slide_df) == 0:
        return slide_df
    first_ts = slide_df['TIMESTAMP'].iloc[0]
    return slide_df[slide_df['TIMESTAMP'] >= first_ts + late_onset_ms]

# %%  Helper: compute_slide_visits
def compute_slide_visits(slide_df, slide_num):
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
            if current_img is not None and current_img != 'no_image':
                run_dur = ts - run_start
                if run_dur >= VISIT_MIN_DURATION_MS:
                    visits[current_img] = visits.get(current_img, 0) + 1
            current_img = img
            run_start = ts
    if current_img is not None and current_img != 'no_image' and len(timestamps) > 1:
        run_dur = timestamps[-1] - run_start
        if run_dur >= VISIT_MIN_DURATION_MS:
            visits[current_img] = visits.get(current_img, 0) + 1
    return visits

# %%  Helper: compute_blinks  (verbatim from compute_eyetracking_metrics.py:184-305)
def compute_blinks(session_df):
    blink_col = session_df['BLINK'].values
    ts_col = session_df['TIMESTAMP'].values
    scene_col = session_df['SCENE_INDEX'].values

    blinks = []
    in_blink = False
    blink_start_ts = 0.0
    blink_scene = 0.0

    for i in range(len(blink_col)):
        if blink_col[i]:
            if not in_blink:
                in_blink = True
                blink_start_ts = ts_col[i]
                blink_scene = scene_col[i]
            elif scene_col[i] != blink_scene:
                end_ts = ts_col[i - 1] if i > 0 else blink_start_ts
                duration = end_ts - blink_start_ts
                sn = int((blink_scene + 1) / 2)
                if 1 <= sn <= 75:
                    blinks.append((blink_start_ts, end_ts, duration, sn))
                blink_start_ts = ts_col[i]
                blink_scene = scene_col[i]
        else:
            if in_blink:
                end_ts = ts_col[i - 1] if i > 0 else blink_start_ts
                duration = end_ts - blink_start_ts
                sn = int((blink_scene + 1) / 2)
                if 1 <= sn <= 75:
                    blinks.append((blink_start_ts, end_ts, duration, sn))
                in_blink = False

    if in_blink:
        end_ts = ts_col[-1]
        duration = end_ts - blink_start_ts
        sn = int((blink_scene + 1) / 2)
        if 1 <= sn <= 75:
            blinks.append((blink_start_ts, end_ts, duration, sn))

    result = {'total_blink_count': len(blinks)}

    cat_blink_durations = defaultdict(list)
    for _, _, dur, sn in blinks:
        for cat in slide_to_categories.get(sn, ()):
            cat_blink_durations[cat].append(dur)

    for cat in CATEGORIES:
        durs = cat_blink_durations.get(cat, [])
        result[f'mean_blink_rate_{cat}'] = len(durs) / cat_slide_counts[cat]
        result[f'mean_blink_duration_{cat}'] = np.mean(durs) if durs else np.nan
        result[f'std_blink_duration_{cat}'] = np.std(durs, ddof=1) if len(durs) > 1 else np.nan

    all_durs = [b[2] for b in blinks]
    result['mean_blink_duration_ms'] = np.mean(all_durs) if all_durs else np.nan

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

    slide_onsets = {}
    for i in range(len(scene_col)):
        sn = int((scene_col[i] + 1) / 2)
        if 1 <= sn <= 75 and sn not in slide_onsets:
            slide_onsets[sn] = ts_col[i]

    cat_latencies = defaultdict(list)
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

# %% [markdown]
# ## Load image quality flags

# %%
flags = pd.read_csv('data/simplified/image_quality_flags.csv')
FLAGGED = set(flags.loc[flags['flagged'], 'image_id'].astype(str))
print(f"Flagged images: {len(FLAGGED)}/{len(flags)}")

# %% [markdown]
# ## Filtered main loop
#
# Mirrors `compute_eyetracking_metrics.py` (lines 308–416) but skips per-image
# contributions whose `image_id` is in FLAGGED.

# %%
raw_dir = Path('data/raw_sessions')
session_files = sorted(raw_dir.glob('*.csv'))
assert len(session_files) == 30, f"Expected 30 session files, got {len(session_files)}"

results = []

for fpath in session_files:
    session_id = fpath.stem
    print(f"Processing {session_id} ...")

    df = pd.read_csv(fpath, usecols=['TIMESTAMP', 'BLINK', 'SCENE_INDEX', 'IMAGE', 'RX', 'RY'])
    df = df.sort_values('TIMESTAMP').reset_index(drop=True)

    cat_dwell_pcts = defaultdict(list)
    cat_visits = defaultdict(list)
    threat_delta_dwell = defaultdict(list)
    cat_dwell_pcts_late = defaultdict(list)
    cat_visits_late = defaultdict(list)
    cat_offscreen_pcts = defaultdict(list)
    cat_offscreen_pcts_late = defaultdict(list)

    for slide_num in range(1, 76):
        scene_idx = slide_num * 2 - 1
        slide_df = df[df['SCENE_INDEX'] == float(scene_idx)]
        img1, img2 = slide_to_image_ids[slide_num]

        # Dwell
        dwell = compute_slide_dwell_pct(slide_df, slide_num)
        for img_id, pct in dwell.items():
            if img_id in FLAGGED:
                continue
            cat = id_to_category.get(img_id, 'unknown')
            cat_dwell_pcts[cat].append(pct)

        # Visits
        vis = compute_slide_visits(slide_df, slide_num)
        for img_id, cnt in vis.items():
            if img_id in FLAGGED:
                continue
            cat = id_to_category.get(img_id, 'unknown')
            cat_visits[cat].append(cnt)

        # Late dwell + visits
        slide_df_late = filter_late(slide_df)
        late_expected_ms = slide_duration[slide_num] - 800
        dwell_late = compute_slide_dwell_pct(slide_df_late, slide_num, expected_ms=late_expected_ms)
        for img_id, pct in dwell_late.items():
            if img_id in FLAGGED:
                continue
            cat = id_to_category.get(img_id, 'unknown')
            cat_dwell_pcts_late[cat].append(pct)

        vis_late = compute_slide_visits(slide_df_late, slide_num)
        for img_id, cnt in vis_late.items():
            if img_id in FLAGGED:
                continue
            cat = id_to_category.get(img_id, 'unknown')
            cat_visits_late[cat].append(cnt)

        # Off-screen — slide-level metric, attributed only to unflagged-image categories
        offscreen_pct = compute_slide_offscreen_pct(slide_df, slide_num)
        offscreen_pct_late = compute_slide_offscreen_pct(slide_df_late, slide_num, expected_ms=late_expected_ms)
        for img_id in (img1, img2):
            if img_id in FLAGGED:
                continue
            cat = id_to_category.get(img_id, 'unknown')
            cat_offscreen_pcts[cat].append(offscreen_pct)
            cat_offscreen_pcts_late[cat].append(offscreen_pct_late)

        # Threat–neutral delta dwell — need both images unflagged
        for threat, slide_list in threat_slide_map.items():
            for (sn, t_img, n_img) in slide_list:
                if sn != slide_num:
                    continue
                if t_img in FLAGGED or n_img in FLAGGED:
                    continue
                t_pct = dwell.get(t_img, 0.0)
                n_pct = dwell.get(n_img, 0.0)
                threat_delta_dwell[threat].append(t_pct - n_pct)

    blink_metrics = compute_blinks(df)

    row = {'session_id': session_id}
    for cat in CATEGORIES:
        vals = cat_dwell_pcts.get(cat, [])
        row[f'mean_dwell_pct_{cat}'] = np.mean(vals) if vals else np.nan
        row[f'std_dwell_pct_{cat}'] = np.std(vals, ddof=1) if len(vals) > 1 else np.nan
    for threat in THREAT_NEUTRALS:
        vals = threat_delta_dwell.get(threat, [])
        row[f'std_delta_dwell_pct_{threat}'] = np.std(vals, ddof=1) if len(vals) > 1 else np.nan
    for cat in CATEGORIES:
        row[f'mean_visits_{cat}'] = np.mean(cat_visits.get(cat, [])) if cat_visits.get(cat) else np.nan
    for cat in CATEGORIES:
        row[f'mean_dwell_pct_late_{cat}'] = np.mean(cat_dwell_pcts_late.get(cat, [])) if cat_dwell_pcts_late.get(cat) else np.nan
    for cat in CATEGORIES:
        row[f'mean_visits_late_{cat}'] = np.mean(cat_visits_late.get(cat, [])) if cat_visits_late.get(cat) else np.nan
    for cat in CATEGORIES:
        row[f'mean_offscreen_pct_{cat}'] = np.mean(cat_offscreen_pcts.get(cat, [])) if cat_offscreen_pcts.get(cat) else np.nan
    for cat in CATEGORIES:
        row[f'mean_offscreen_pct_late_{cat}'] = np.mean(cat_offscreen_pcts_late.get(cat, [])) if cat_offscreen_pcts_late.get(cat) else np.nan
    row.update(blink_metrics)
    results.append(row)

metrics_df = pd.DataFrame(results)
print(f"\nComputed metrics for {len(metrics_df)} sessions, {len(metrics_df.columns)} columns.")

# %%  Merge metadata + validate
meta_df = pd.read_csv('data/simplified/dataset_merged_1_and_2.csv',
                     usecols=['sessions', 'if_PTSD', 'ITI_PTSD', 'ITI_cPTSD', 'if_antipsychotic'])
meta_df = meta_df.rename(columns={'sessions': 'session_id'})
metrics_df = metrics_df.merge(meta_df, on='session_id', how='left')

assert len(metrics_df) == 30
for col in ['if_PTSD', 'ITI_PTSD', 'ITI_cPTSD', 'if_antipsychotic']:
    assert metrics_df[col].notna().all(), f"Missing metadata in {col}"

dwell_cols = [c for c in metrics_df.columns if c.startswith('mean_dwell_pct_') and '_late_' not in c]
for col in dwell_cols:
    vals = metrics_df[col].dropna()
    assert vals.min() >= -0.01, f"{col} has negative values: {vals.min()}"
    assert vals.max() <= 101, f"{col} has values > 100: {vals.max()}"

# %%  Write the three filtered datasets
out_full = 'data/simplified/dataset_eyetracking_metrics_imageclean.csv'
metrics_df.to_csv(out_full, index=False)
print(f"Wrote: {out_full}  ({metrics_df.shape})")

clean = metrics_df[metrics_df['session_id'] != 'UgMWkyrkRYVZ9cr9thRw'].reset_index(drop=True)
assert len(clean) == 29, f"Expected 29 rows in clean variant, got {len(clean)}"
out_clean = 'data/simplified/dataset_eyetracking_metrics_clean_imageclean.csv'
clean.to_csv(out_clean, index=False)
print(f"Wrote: {out_clean}  ({clean.shape})")

blink_clean_orig = pd.read_csv('data/simplified/dataset_eyetracking_metrics_blink_clean.csv',
                                usecols=['session_id'])
blink_clean = clean[clean['session_id'].isin(blink_clean_orig['session_id'])].reset_index(drop=True)
assert len(blink_clean) == 26, f"Expected 26 rows in blink_clean variant, got {len(blink_clean)}"
out_blink_clean = 'data/simplified/dataset_eyetracking_metrics_blink_clean_imageclean.csv'
blink_clean.to_csv(out_blink_clean, index=False)
print(f"Wrote: {out_blink_clean}  ({blink_clean.shape})")

# %% [markdown]
# ## Diagnostics: per-category effective slide counts and shifts

# %%
n_slides_before = {cat: cat_slide_counts[cat] for cat in CATEGORIES}
n_slides_after = Counter()
for sn, (img1, img2) in slide_to_image_ids.items():
    for img_id in (img1, img2):
        if img_id not in FLAGGED:
            cat = id_to_category.get(img_id, 'unknown')
            n_slides_after[cat] += 1

print("\n=== Per-category contributing-slide counts ===")
print(f"{'category':20s} {'before':>8s} {'after':>8s} {'pct_kept':>10s}")
for cat in CATEGORIES:
    b = n_slides_before[cat]
    a = n_slides_after[cat]
    print(f"{cat:20s} {b:>8d} {a:>8d} {100.0*a/b:>9.1f}%")

orig_full = pd.read_csv('data/simplified/dataset_eyetracking_metrics.csv')
print("\n=== Mean of per-session mean_dwell_pct_{cat}: original vs. image-cleaned ===")
print(f"{'category':20s} {'orig':>10s} {'cleaned':>10s} {'delta':>10s}")
for cat in CATEGORIES:
    col = f'mean_dwell_pct_{cat}'
    o = orig_full[col].mean()
    c = metrics_df[col].mean()
    print(f"{cat:20s} {o:>10.3f} {c:>10.3f} {c - o:>+10.3f}")

# Threat-neutral delta SD shift
print("\n=== std_delta_dwell_pct_{threat}: original vs. image-cleaned (mean across sessions) ===")
for threat in THREAT_NEUTRALS:
    col = f'std_delta_dwell_pct_{threat}'
    o = orig_full[col].mean()
    c = metrics_df[col].mean()
    print(f"{threat:20s} {o:>10.3f} {c:>10.3f} {c - o:>+10.3f}")

print("\nDone.")
