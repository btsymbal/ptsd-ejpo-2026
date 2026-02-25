# Temporal Threat Bias — Preprocessing Report

**Generated:** 2026-02-25 17:26
**Sessions processed:** 29
**Excluded session:** `UgMWkyrkRYVZ9cr9thRw` (poor gaze quality — 8% usable slides)

## Purpose

Extract trial-level threat attentional bias (one delta per threat–neutral slide per
session) for temporal-dynamics analyses inspired by Zvielli et al. (2015) and Schäfer
et al. (2016). Unlike aggregate metrics that collapse across slides, trial-level data
preserves within-session temporal trajectories and variability.

## Data Sources

- `data/raw_sessions/*.csv` — 30 raw gaze session files
- `materials/slide_durations.csv` — expected duration per slide
- `materials/id_to_category_mapping.json` — image ID → category
- `materials/image_pair_ids.json` — slide number → image pair IDs
- `data/simplified/dataset_merged_1_and_2.csv` — clinical metadata (if_PTSD)

## Method

### Threat–Neutral Slide Identification

| Threat Category | Neutral Counterparts | Slide Count |
|-----------------|---------------------|-------------|
| `angry_face` | `neutral_face` | 10 |
| `anxiety_inducing` | `neutral` | 14 |
| `warfare` | `happy_event`, `neutral` | 12 |
| `soldiers` | `happy_face`, `neutral`, `neutral_face` | 8 |

**Total:** 44 threat–neutral slides across 4 threat categories.

### Metric Formula

```
threat_delta_dwell = threat_dwell_pct − neutral_dwell_pct
```

where `dwell_pct = (gaze_time_ms / expected_duration_ms) × 100` for each image.
Positive values indicate bias toward threat; negative values indicate avoidance.

### Trial Indexing

The 44 threat–neutral slides are re-indexed as `trial_index` 1–44 in presentation
order (ascending slide number). This enables temporal trajectory plots.

### Distribution Check

Shapiro-Wilk normality tests on per-slide delta distributions across sessions:
- Normal: 41/44 slides (93.2%)
- Non-normal: 3/44 slides (6.8%)
- **Decision:** Use **mean** as central tendency for aggregated file.

### TL-BS Variability Indices (Zvielli-Inspired)

Per-session indices computed from the 44 trial-level deltas:

| Index | Definition |
|-------|-----------|
| `tl_bs_mean` | Mean of 44 trial-level deltas |
| `tl_bs_sd` | SD of 44 trial-level deltas (within-session variability) |
| `tl_bs_peak_toward` | Max positive delta (strongest threat bias) |
| `tl_bs_peak_away` | Min delta (strongest avoidance) |
| `tl_bs_range` | peak_toward − peak_away |

## Output Files

### `temporal_threat_bias_by_session.csv`

- **Rows:** 1276 (29 sessions × 44 slides)
- **Columns:** session_id, slide_num, trial_index, threat_category,
  threat_dwell_pct, neutral_dwell_pct, threat_delta_dwell, if_PTSD, group

### `temporal_threat_bias_aggregated.csv`

- **Rows:** 88 (44 slides × 2 groups)
- **Columns:** slide_num, trial_index, threat_category, group,
  central_threat_delta_dwell (mean), sd, n, se, ci95_lo, ci95_hi

### `temporal_threat_bias_variability.csv`

- **Rows:** 29 (1 per session)
- **Columns:** session_id, if_PTSD, group, tl_bs_mean, tl_bs_sd,
  tl_bs_peak_toward, tl_bs_peak_away, tl_bs_range

## Validation

- Row counts: 1276 session-level, 88 aggregated, 29 variability
- Delta range: [-100.93, 100.27] (within [-100, 100])
- Group sizes: PTSD = 17, No-PTSD = 12
- Trial indices: 1–44

## Session Exclusion

- `UgMWkyrkRYVZ9cr9thRw`: Excluded due to poor gaze quality (only 8% usable slides).
  This is the only exclusion; blink-outlier sessions are not excluded here as they
  are a separate concern relevant to blink-specific analyses.
