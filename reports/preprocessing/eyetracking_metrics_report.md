# Eye-Tracking Metrics Report

**Generated:** 2026-02-19 14:54
**Sessions processed:** 30
**Output columns:** 134

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

### Late-Window Dwell Time (≥ 800 ms)

- **`mean_dwell_pct_late_{category}`**: Same as `mean_dwell_pct` but computed only
  on gaze samples from 800 ms after slide onset. Denominator is `expected_duration_ms - 800`.
  Captures sustained attention after initial orienting.

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

### Late-Window Visit Counts (≥ 800 ms)

- **`mean_visits_late_{category}`**: Same as `mean_visits` but computed only on
  gaze samples from 800 ms after slide onset.

### Off-Screen Gaze

- **`mean_offscreen_pct_{category}`**: Mean percentage of expected slide duration
  where gaze was off-screen (RX ∉ [0,1] or RY ∉ [0,1]), averaged across slides
  of this category. Attributed to both categories of the slide.

### Late-Window Off-Screen Gaze (≥ 800 ms)

- **`mean_offscreen_pct_late_{category}`**: Same as `mean_offscreen_pct` but
  computed only on gaze samples from 800 ms after slide onset. Denominator is
  `expected_duration_ms - 800`.

### Blink Metrics

A blink is a run of consecutive `BLINK=True` samples. Runs are split at
`SCENE_INDEX` boundaries. Each blink is attributed to both categories of its slide.

- **`total_blink_count`**: Total blinks across the entire session.
- **`mean_blink_rate_{category}`**: Mean blinks per slide for this category.
  Computed as `total_blinks_on_category_slides / number_of_slides_in_category`.
  Normalized for unequal slide counts across categories.
- **`mean_blink_interval_norm`**: Mean inter-blink interval normalized by the
  slide duration of the first blink in each pair. Dimensionless ratio.
- **`std_blink_interval_norm`**: Std of normalized inter-blink intervals (ddof=1).
- **`mean_blink_latency_norm_{category}`**: Mean time from slide onset to first blink,
  normalized by slide duration. Dimensionless ratio. Slides with no blinks excluded.
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
| mean_dwell_pct_late | 11 |
| mean_visits_late | 11 |
| mean_offscreen_pct | 11 |
| mean_offscreen_pct_late | 11 |
| total_blink_count | 1 |
| mean_blink_rate | 11 |
| mean_blink_interval_norm | 1 |
| std_blink_interval_norm | 1 |
| mean_blink_latency_norm | 11 |
| mean_blink_duration_ms | 1 |
| mean_blink_duration | 11 |
| std_blink_duration | 11 |
| metadata | 4 |
| **Total** | **134** |

## Edge Cases

- Slides where both images show `no_image`: 0% dwell and 0 visits (included in aggregation).
- Blink latency: slides with no blinks are excluded from the per-category mean.
- Blink runs spanning SCENE_INDEX boundaries are split into separate blinks.
- Late window: for slides with expected_duration_ms = 1500, the late window is only 700 ms.
  If no samples exist in the late window, dwell = 0% and visits = 0.
- Off-screen gaze: uses raw RX/RY coordinates. Values outside [0,1] indicate gaze
  is off the screen area. NaN RX/RY rows are treated as on-screen (conservative).
