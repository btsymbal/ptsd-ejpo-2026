# %% [markdown]
# # Compute Temporal Threat Bias (Trial-Level)
#
# Extract **trial-level** threat_delta_dwell (one value per threat–neutral slide
# per session) to enable temporal-dynamics analyses.  Zvielli et al. (2015) and
# Schäfer et al. (2016) argue that within-session variability of attentional bias
# carries diagnostic information beyond aggregate scores.
#
# Outputs:
# - `temporal_threat_bias_by_session.csv` — 1,276 rows (29 sessions × 44 threat slides)
# - `temporal_threat_bias_aggregated.csv` — 88 rows (44 slides × 2 groups)
# - `temporal_threat_bias_variability.csv` — 29 rows (TL-BS variability indices per session)

# %%
import os
from pathlib import Path

os.chdir(Path(__file__).resolve().parent.parent)

import json
import numpy as np
import pandas as pd
from collections import defaultdict
from scipy import stats

# %%  Load materials
# -------------------------------------------------------------------
slide_dur_df = pd.read_csv('materials/slide_durations.csv')
slide_duration = dict(zip(slide_dur_df['slide_number'], slide_dur_df['expected_duration_ms']))

with open('materials/id_to_category_mapping.json') as f:
    id_to_category = json.load(f)

with open('materials/image_pair_ids.json') as f:
    slide_to_image_ids = {int(k): v for k, v in json.load(f).items()}

# %%  Build threat slide map
# -------------------------------------------------------------------
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

# Flatten to single dict: {slide_num: (threat_img, neutral_img, category)}
threat_slides = {}
for threat_cat, slide_list in threat_slide_map.items():
    for (sn, t_img, n_img) in slide_list:
        assert sn not in threat_slides, f"Slide {sn} maps to multiple threat categories"
        threat_slides[sn] = (t_img, n_img, threat_cat)

# Build trial_order: sort threat slides by presentation order (slide_num)
sorted_threat_slide_nums = sorted(threat_slides.keys())
trial_order = {sn: idx + 1 for idx, sn in enumerate(sorted_threat_slide_nums)}

N_THREAT_SLIDES = len(threat_slides)
print(f"Threat–neutral slides: {N_THREAT_SLIDES}")
for t, slides in threat_slide_map.items():
    print(f"  {t}: {len(slides)} slides")
assert N_THREAT_SLIDES == 44, f"Expected 44 threat slides, got {N_THREAT_SLIDES}"

# %%  compute_slide_dwell_pct (copied from compute_eyetracking_metrics.py)
# -------------------------------------------------------------------
def compute_slide_dwell_pct(slide_df, slide_num, expected_ms=None):
    """Return {img_id: dwell_pct} for both images on this slide."""
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

# %%  Main processing loop
# -------------------------------------------------------------------
EXCLUDED_SESSION = 'UgMWkyrkRYVZ9cr9thRw'

raw_dir = Path('data/raw_sessions')
session_files = sorted(raw_dir.glob('*.csv'))
assert len(session_files) == 30, f"Expected 30 session files, got {len(session_files)}"

rows = []

for fpath in session_files:
    session_id = fpath.stem
    if session_id == EXCLUDED_SESSION:
        print(f"Skipping excluded session: {session_id}")
        continue

    print(f"Processing {session_id} ...")
    df = pd.read_csv(fpath, usecols=['TIMESTAMP', 'SCENE_INDEX', 'IMAGE'])
    df = df.sort_values('TIMESTAMP').reset_index(drop=True)

    for slide_num in sorted_threat_slide_nums:
        scene_idx = slide_num * 2 - 1
        slide_df = df[df['SCENE_INDEX'] == float(scene_idx)]

        t_img, n_img, threat_cat = threat_slides[slide_num]
        dwell = compute_slide_dwell_pct(slide_df, slide_num)
        t_pct = dwell.get(t_img, 0.0)
        n_pct = dwell.get(n_img, 0.0)

        rows.append({
            'session_id': session_id,
            'slide_num': slide_num,
            'trial_index': trial_order[slide_num],
            'threat_category': threat_cat,
            'threat_dwell_pct': t_pct,
            'neutral_dwell_pct': n_pct,
            'threat_delta_dwell': t_pct - n_pct,
        })

session_df = pd.DataFrame(rows)
print(f"\nSession-level data: {session_df.shape[0]} rows")

# %%  Merge PTSD metadata
# -------------------------------------------------------------------
meta_df = pd.read_csv('data/simplified/dataset_merged_1_and_2.csv',
                       usecols=['sessions', 'if_PTSD'])
meta_df = meta_df.rename(columns={'sessions': 'session_id'})

session_df = session_df.merge(meta_df, on='session_id', how='left')
session_df['group'] = session_df['if_PTSD'].map({1: 'PTSD', 0: 'No-PTSD'})
assert session_df['group'].notna().all(), "Missing group labels after merge"

print(f"Group sizes: {session_df.groupby('group')['session_id'].nunique().to_dict()}")

# %%  Distribution check — decide mean vs median for aggregation
# -------------------------------------------------------------------
print("\n=== Distribution Check (Shapiro-Wilk per slide across sessions) ===")
n_normal = 0
n_nonnormal = 0

for sn in sorted_threat_slide_nums:
    vals = session_df.loc[session_df['slide_num'] == sn, 'threat_delta_dwell'].values
    if len(vals) >= 3:
        w, p = stats.shapiro(vals)
        if p > 0.05:
            n_normal += 1
        else:
            n_nonnormal += 1

pct_normal = n_normal / (n_normal + n_nonnormal) * 100
print(f"Normal: {n_normal}/{n_normal + n_nonnormal} slides ({pct_normal:.1f}%)")
print(f"Non-normal: {n_nonnormal}/{n_normal + n_nonnormal} slides ({100 - pct_normal:.1f}%)")

# Decision rule: if majority of slides are non-normal, use median
USE_MEDIAN = n_nonnormal > n_normal
central_measure = 'median' if USE_MEDIAN else 'mean'
print(f"→ Using {central_measure} for aggregation")

# %%  Aggregate by (slide_num, trial_index, threat_category, group)
# -------------------------------------------------------------------
def aggregate_group(grp):
    vals = grp['threat_delta_dwell']
    center = vals.median() if USE_MEDIAN else vals.mean()
    sd = vals.std(ddof=1)
    n = len(vals)
    se = sd / np.sqrt(n) if n > 0 else np.nan
    ci95_lo = center - 1.96 * se
    ci95_hi = center + 1.96 * se
    return pd.Series({
        'central_threat_delta_dwell': center,
        'sd': sd,
        'n': n,
        'se': se,
        'ci95_lo': ci95_lo,
        'ci95_hi': ci95_hi,
    })

agg_df = (session_df
          .groupby(['slide_num', 'trial_index', 'threat_category', 'group'])
          .apply(aggregate_group, include_groups=False)
          .reset_index())

print(f"\nAggregated data: {agg_df.shape[0]} rows")

# %%  Compute TL-BS variability indices per session
# -------------------------------------------------------------------
var_rows = []
for sid, grp in session_df.groupby('session_id'):
    deltas = grp['threat_delta_dwell'].values
    if_ptsd = grp['if_PTSD'].iloc[0]
    group = grp['group'].iloc[0]

    var_rows.append({
        'session_id': sid,
        'if_PTSD': if_ptsd,
        'group': group,
        'tl_bs_mean': np.mean(deltas),
        'tl_bs_sd': np.std(deltas, ddof=1),
        'tl_bs_peak_toward': np.max(deltas),
        'tl_bs_peak_away': np.min(deltas),
        'tl_bs_range': np.max(deltas) - np.min(deltas),
    })

var_df = pd.DataFrame(var_rows)
print(f"\nVariability indices: {var_df.shape[0]} rows")
print(var_df.groupby('group')[['tl_bs_mean', 'tl_bs_sd', 'tl_bs_range']].describe().round(2))

# %%  Validation
# -------------------------------------------------------------------
print("\n=== Validation ===")

n_sessions = session_df['session_id'].nunique()
assert n_sessions == 29, f"Expected 29 sessions, got {n_sessions}"
assert len(session_df) == 29 * 44, f"Expected {29 * 44} rows, got {len(session_df)}"
print(f"✓ Session-level: {len(session_df)} rows (29 × 44)")

assert len(agg_df) == 44 * 2, f"Expected 88 aggregated rows, got {len(agg_df)}"
print(f"✓ Aggregated: {len(agg_df)} rows (44 × 2)")

assert len(var_df) == 29, f"Expected 29 variability rows, got {len(var_df)}"
print(f"✓ Variability: {len(var_df)} rows")

# Delta dwell should be in [-100, 100]
delta_min = session_df['threat_delta_dwell'].min()
delta_max = session_df['threat_delta_dwell'].max()
assert delta_min >= -102, f"Delta below -102: {delta_min}"
assert delta_max <= 102, f"Delta above 102: {delta_max}"
print(f"✓ Delta range: [{delta_min:.2f}, {delta_max:.2f}]")

# Group sizes
group_sizes = session_df.groupby('group')['session_id'].nunique().to_dict()
assert group_sizes['PTSD'] == 17, f"Expected 17 PTSD, got {group_sizes['PTSD']}"
assert group_sizes['No-PTSD'] == 12, f"Expected 12 No-PTSD, got {group_sizes['No-PTSD']}"
print(f"✓ Group sizes: PTSD={group_sizes['PTSD']}, No-PTSD={group_sizes['No-PTSD']}")

# Trial indices span 1–44
assert session_df['trial_index'].min() == 1
assert session_df['trial_index'].max() == 44
print(f"✓ Trial indices: 1–44")

print("\nAll validations passed!")

# %%  Export
# -------------------------------------------------------------------
os.makedirs('data/simplified', exist_ok=True)

session_df.to_csv('data/simplified/temporal_threat_bias_by_session.csv', index=False)
print(f"Exported: data/simplified/temporal_threat_bias_by_session.csv ({len(session_df)} rows)")

agg_df.to_csv('data/simplified/temporal_threat_bias_aggregated.csv', index=False)
print(f"Exported: data/simplified/temporal_threat_bias_aggregated.csv ({len(agg_df)} rows)")

var_df.to_csv('data/simplified/temporal_threat_bias_variability.csv', index=False)
print(f"Exported: data/simplified/temporal_threat_bias_variability.csv ({len(var_df)} rows)")

# %%  Generate report
# -------------------------------------------------------------------
os.makedirs('reports/preprocessing', exist_ok=True)

# Build threat-neutral table for report
threat_table_lines = []
for threat, neutrals in THREAT_NEUTRALS.items():
    n_slides = len(threat_slide_map[threat])
    threat_table_lines.append(f"| `{threat}` | {', '.join(f'`{n}`' for n in neutrals)} | {n_slides} |")

report_lines = [
    "# Temporal Threat Bias — Preprocessing Report",
    "",
    f"**Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",
    f"**Sessions processed:** {n_sessions}",
    f"**Excluded session:** `{EXCLUDED_SESSION}` (poor gaze quality — 8% usable slides)",
    "",
    "## Purpose",
    "",
    "Extract trial-level threat attentional bias (one delta per threat–neutral slide per",
    "session) for temporal-dynamics analyses inspired by Zvielli et al. (2015) and Schäfer",
    "et al. (2016). Unlike aggregate metrics that collapse across slides, trial-level data",
    "preserves within-session temporal trajectories and variability.",
    "",
    "## Data Sources",
    "",
    "- `data/raw_sessions/*.csv` — 30 raw gaze session files",
    "- `materials/slide_durations.csv` — expected duration per slide",
    "- `materials/id_to_category_mapping.json` — image ID → category",
    "- `materials/image_pair_ids.json` — slide number → image pair IDs",
    "- `data/simplified/dataset_merged_1_and_2.csv` — clinical metadata (if_PTSD)",
    "",
    "## Method",
    "",
    "### Threat–Neutral Slide Identification",
    "",
    "| Threat Category | Neutral Counterparts | Slide Count |",
    "|-----------------|---------------------|-------------|",
] + threat_table_lines + [
    "",
    f"**Total:** {N_THREAT_SLIDES} threat–neutral slides across 4 threat categories.",
    "",
    "### Metric Formula",
    "",
    "```",
    "threat_delta_dwell = threat_dwell_pct − neutral_dwell_pct",
    "```",
    "",
    "where `dwell_pct = (gaze_time_ms / expected_duration_ms) × 100` for each image.",
    "Positive values indicate bias toward threat; negative values indicate avoidance.",
    "",
    "### Trial Indexing",
    "",
    "The 44 threat–neutral slides are re-indexed as `trial_index` 1–44 in presentation",
    "order (ascending slide number). This enables temporal trajectory plots.",
    "",
    f"### Distribution Check",
    "",
    f"Shapiro-Wilk normality tests on per-slide delta distributions across sessions:",
    f"- Normal: {n_normal}/{n_normal + n_nonnormal} slides ({pct_normal:.1f}%)",
    f"- Non-normal: {n_nonnormal}/{n_normal + n_nonnormal} slides ({100 - pct_normal:.1f}%)",
    f"- **Decision:** Use **{central_measure}** as central tendency for aggregated file.",
    "",
    "### TL-BS Variability Indices (Zvielli-Inspired)",
    "",
    "Per-session indices computed from the 44 trial-level deltas:",
    "",
    "| Index | Definition |",
    "|-------|-----------|",
    "| `tl_bs_mean` | Mean of 44 trial-level deltas |",
    "| `tl_bs_sd` | SD of 44 trial-level deltas (within-session variability) |",
    "| `tl_bs_peak_toward` | Max positive delta (strongest threat bias) |",
    "| `tl_bs_peak_away` | Min delta (strongest avoidance) |",
    "| `tl_bs_range` | peak_toward − peak_away |",
    "",
    "## Output Files",
    "",
    "### `temporal_threat_bias_by_session.csv`",
    "",
    f"- **Rows:** {len(session_df)} (29 sessions × 44 slides)",
    "- **Columns:** session_id, slide_num, trial_index, threat_category,",
    "  threat_dwell_pct, neutral_dwell_pct, threat_delta_dwell, if_PTSD, group",
    "",
    "### `temporal_threat_bias_aggregated.csv`",
    "",
    f"- **Rows:** {len(agg_df)} (44 slides × 2 groups)",
    f"- **Columns:** slide_num, trial_index, threat_category, group,",
    f"  central_threat_delta_dwell ({central_measure}), sd, n, se, ci95_lo, ci95_hi",
    "",
    "### `temporal_threat_bias_variability.csv`",
    "",
    f"- **Rows:** {len(var_df)} (1 per session)",
    "- **Columns:** session_id, if_PTSD, group, tl_bs_mean, tl_bs_sd,",
    "  tl_bs_peak_toward, tl_bs_peak_away, tl_bs_range",
    "",
    "## Validation",
    "",
    f"- Row counts: {len(session_df)} session-level, {len(agg_df)} aggregated, {len(var_df)} variability",
    f"- Delta range: [{delta_min:.2f}, {delta_max:.2f}] (within [-100, 100])",
    f"- Group sizes: PTSD = {group_sizes['PTSD']}, No-PTSD = {group_sizes['No-PTSD']}",
    "- Trial indices: 1–44",
    "",
    "## Session Exclusion",
    "",
    f"- `{EXCLUDED_SESSION}`: Excluded due to poor gaze quality (only 8% usable slides).",
    "  This is the only exclusion; blink-outlier sessions are not excluded here as they",
    "  are a separate concern relevant to blink-specific analyses.",
    "",
]

with open('reports/preprocessing/temporal_threat_bias_report.md', 'w') as f:
    f.write('\n'.join(report_lines))

print("\nReport saved to reports/preprocessing/temporal_threat_bias_report.md")
