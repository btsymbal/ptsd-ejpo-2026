# Eye-Tracking Metrics Report

**Generated:** 2026-02-17 18:42
**Sessions processed:** 30
**Output columns:** 90

## Data Sources

- `data/raw_sessions/*.csv` — 30 raw gaze session files
- `materials/slide_durations.csv` — expected duration per slide
- `materials/id_to_category_mapping.json` — image ID to category (11 categories)
- `materials/image_pair_ids.json` — slide number to image pair IDs
- `data/simplified/dataset_merged_1_and_2.csv` — clinical metadata

## Categories

- `angry_face`
- `anxiety_inducing`
- `combat_vehicles`
- `happy_event`
- `happy_face`
- `neutral`
- `neutral_face`
- `sad_face`
- `sleep_related`
- `soldiers`
- `warfare`

## Metric Descriptions

### Dwell Time

- **`mean_dwell_pct_{category}`**: Mean percentage of expected slide duration spent
  gazing at images of this category, across all slides containing the category.
  Computed as `(gaze_time_ms / expected_duration_ms) * 100` per image per slide,
  then averaged across all images of the category.
- **`std_dwell_pct_{category}`**: Standard deviation of dwell percentages (ddof=1).

### Delta Dwell (Threat Bias)

For each threat category, slides are identified where one image is threat and
the other is an eligible neutral counterpart:

| Threat | Neutral counterparts | Slide count |
|--------|---------------------|-------------|
| `angry_face` | `neutral_face` | 10 |
| `anxiety_inducing` | `neutral` | 14 |
| `warfare` | `happy_event`, `neutral` | 12 |
| `soldiers` | `happy_face`, `neutral`, `neutral_face` | 8 |

- **`std_delta_dwell_pct_{threat}`**: Standard deviation (ddof=1) of
  `threat_dwell_pct - neutral_dwell_pct` across all threat–neutral slides.
  Higher values indicate more variable attentional bias toward the threat image.

### Visit Counts

- **`mean_visits_{category}`**: Mean number of qualifying visits (continuous gaze
  runs >= 100 ms) to images of this category, across all relevant slides.

### Blink Metrics

A blink is a run of consecutive `BLINK=True` samples. Runs are split at
`SCENE_INDEX` boundaries. Each blink is attributed to both categories of its slide.

- **`total_blink_count`**: Total blinks across the entire session.
- **`blink_count_{category}`**: Number of blinks on slides containing this category.
- **`mean_blink_interval_ms`**: Mean time between consecutive blink onsets (ms).
- **`std_blink_interval_ms`**: Std of inter-blink intervals (ddof=1).
- **`mean_blink_latency_{category}`**: Mean time from slide onset to first blink,
  averaged across slides of this category. Slides with no blinks are excluded.
- **`mean_blink_duration_ms`**: Mean blink duration across all blinks.
- **`mean_blink_duration_{category}`**: Mean blink duration on slides of this category.
- **`std_blink_duration_{category}`**: Std of blink durations on slides of this
  category (ddof=1).

### Metadata

Merged from `dataset_merged_1_and_2.csv`:

- **`if_PTSD`**: Binary PTSD status
- **`ITI_PTSD`**: ITI PTSD score
- **`ITI_cPTSD`**: ITI complex PTSD score
- **`if_antipsychotic`**: Binary antipsychotic medication status

## Column Summary

| Group | Count |
|-------|-------|
| session_id | 1 |
| mean_dwell_pct | 11 |
| std_dwell_pct | 11 |
| std_delta_dwell_pct | 4 |
| mean_visits | 11 |
| total_blink_count | 1 |
| blink_count | 11 |
| mean_blink_interval_ms | 1 |
| std_blink_interval_ms | 1 |
| mean_blink_latency | 11 |
| mean_blink_duration_ms | 1 |
| mean_blink_duration | 11 |
| std_blink_duration | 11 |
| metadata | 4 |
| **Total** | **90** |

## Edge Cases

- Slides where both images show `no_image`: 0% dwell and 0 visits (included in aggregation).
- Blink latency: slides with no blinks are excluded from the per-category mean.
- Blink runs spanning SCENE_INDEX boundaries are split into separate blinks.
