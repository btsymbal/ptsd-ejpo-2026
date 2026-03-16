# Per-Image Dwell Times Report

**Generated:** 2026-03-16
**Sessions processed:** 30
**Output rows:** 4,500 (30 sessions × 150 images)
**Output columns:** 10

## Purpose

Compute dwell time at the **individual image** level — one value per image per
session — to enable fine-grained image-level analysis. This complements the
category-aggregated metrics in `dataset_eyetracking_metrics.csv`.

## Data Sources

- `data/raw_sessions/*.csv` — 30 raw gaze session files (columns: TIMESTAMP, SCENE_INDEX, IMAGE)
- `materials/slide_durations.csv` — expected duration per slide (ms)
- `materials/id_to_category_mapping.json` — image ID → category (11 categories)
- `materials/image_pair_ids.json` — slide number → pair of image IDs
- `data/simplified/dataset_merged_1_and_2.csv` — clinical metadata

## Algorithm

For each session and each slide (1–75):

1. Filter raw gaze data to `SCENE_INDEX == slide_num * 2 - 1`
2. Sort by TIMESTAMP
3. Compute duration at each sample as the gap to the next timestamp; last sample gets 0
4. Sum time per image ID (excluding `no_image` samples)
5. `dwell_pct = (time_on_image / expected_slide_duration_ms) * 100`

This is identical to `compute_slide_dwell_pct()` in `compute_eyetracking_metrics.py`.

## Output Format

Long format — one row per session × image.

| Column | Description |
|---|---|
| `session_id` | Session identifier (from filename) |
| `slide_num` | Slide number (1–75, original presentation order) |
| `image_position` | Position within slide: 1 or 2 (per `image_pair_ids.json` order) |
| `image_id` | Image identifier string |
| `category` | Image category from `id_to_category_mapping.json` |
| `dwell_pct` | Dwell time as % of expected slide duration |
| `if_PTSD` | Binary PTSD status |
| `ITI_PTSD` | ITI PTSD score |
| `ITI_cPTSD` | ITI complex PTSD score |
| `if_antipsychotic` | Binary antipsychotic status |

## Value Ranges

- `dwell_pct`: [0.00, 100.93] — values slightly above 100% are possible due to
  timestamp jitter (consistent with the existing metrics pipeline, which uses a
  tolerance of 101%)
- `slide_num`: 1–75
- `image_position`: 1 or 2
- 11 categories, 150 unique images per session

## Edge Cases

- Slides with no gaze data: both images get `dwell_pct = 0`
- `no_image` gaze samples are excluded from dwell computation
- Sum of `dwell_pct` for both images on a slide plus off-screen/no_image time ≈ 100%
