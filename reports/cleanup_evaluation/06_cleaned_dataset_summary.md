# Step 6 — Cleaned Per-Category Datasets

## Pipeline

`preprocessing/recompute_eyetracking_metrics_clean_images.py` re-runs the
per-session × per-category aggregation from `compute_eyetracking_metrics.py`,
but skips per-image contributions for the **22 images** flagged in
`data/simplified/image_quality_flags.csv` (flagged set is restricted to
directional categories — see Step 5).

Filtering policy (encoded in the script header):

| Metric family | How filtering applies |
|---|---|
| `mean_dwell_pct_*`, `std_dwell_pct_*` | Skip per-image dwell pct if `image_id` is flagged. Per-session per-category mean/SD computed only over kept images. |
| `mean_visits_*`, `mean_visits_late_*` | Skip per-image visit counts if flagged. |
| `mean_dwell_pct_late_*` | Same as dwell, on the post-800 ms window. |
| `mean_offscreen_pct_*`, `mean_offscreen_pct_late_*` | Off-screen is a slide-level metric; we attribute it to the category of an image only if that image is unflagged. |
| `std_delta_dwell_pct_{threat}` (H3) | Per-pair contrast; skip the slide-pair if either threat or neutral image is flagged. (No neutrals are flagged now, so only the threat-image side ever drops a pair.) |
| Blink metrics | Not filtered — these are session/slide-level events independent of per-image quality. |

## Outputs

| Path | Rows | Cols | Use |
|---|---|---|---|
| `data/simplified/dataset_eyetracking_metrics_imageclean.csv` | 30 | 134 | Pre-removal-of-bad-session dataset |
| `data/simplified/dataset_eyetracking_metrics_clean_imageclean.csv` | 29 | 134 | Step 7 H1–H6 + Step 8/9 model — drops `UgMWkyrkRYVZ9cr9thRw` |
| `data/simplified/dataset_eyetracking_metrics_blink_clean_imageclean.csv` | 26 | 134 | E1 + blink overview — also drops 3 blink outliers |

Same column set, same row counts, same session ids as the originals.

## Per-category contributing-slide counts (before vs. after filter)

| Category | Slides before | Slides after | % retained |
|---|---|---|---|
| angry_face | 10 | 8 | 80 % |
| anxiety_inducing | 14 | 11 | 79 % |
| combat_vehicles | 8 | 4 | 50 % |
| happy_event | 9 | 7 | 78 % |
| happy_face | 11 | 7 | 64 % |
| neutral | 50 | 50 | 100 % |
| neutral_face | 13 | 13 | 100 % |
| sad_face | 8 | 8 | 100 % |
| sleep_related | 7 | 5 | 71 % |
| soldiers | 8 | 7 | 88 % |
| warfare | 12 | 8 | 67 % |

`combat_vehicles` is the most aggressively trimmed (50 %); the four
pre-registered threat categories all retain ≥ 67 %. None / neutral_face /
sad_face are unchanged. **No new NaNs** in the cleaned datasets.

## Sanity-check shifts (n = 29; orig vs. cleaned)

### Mean of per-session `mean_dwell_pct_{cat}`

| Category | Original | Cleaned | Δ |
|---|---|---|---|
| angry_face | 23.74 | 24.67 | +0.93 |
| anxiety_inducing | 28.71 | 30.12 | +1.41 |
| combat_vehicles | 27.09 | 28.69 | +1.60 |
| happy_event | 23.63 | 24.45 | +0.82 |
| happy_face | 21.97 | 22.08 | +0.11 |
| neutral | 19.71 | 19.71 | **0.00** |
| neutral_face | 23.17 | 23.17 | **0.00** |
| sad_face | 22.07 | 22.07 | **0.00** |
| sleep_related | 24.09 | 25.38 | +1.29 |
| soldiers | 26.60 | 27.35 | +0.74 |
| warfare | 24.10 | 25.04 | +0.94 |

Directional categories shift up modestly (the filter preferentially removes
low-engagement images). None / neutral_face / sad_face are byte-identical to
the originals as expected.

### Mean of per-session `std_delta_dwell_pct_{threat}` (used by H3)

| Threat | Original | Cleaned | Δ |
|---|---|---|---|
| angry_face | 26.14 | 26.83 | +0.69 |
| anxiety_inducing | 25.60 | 25.62 | +0.02 |
| warfare | 25.06 | 23.79 | -1.27 |
| soldiers | 26.11 | 25.59 | -0.52 |

Mixed shifts. With neutrals fully retained, the only changes come from
slide-pairs whose *threat* image was flagged and dropped.

### Mean of per-session `std_dwell_pct_{threat}` (used by H2 / H4)

| Threat | Original | Cleaned | Δ |
|---|---|---|---|
| angry_face | 15.28 | 15.38 | +0.10 |
| anxiety_inducing | 17.33 | 16.87 | -0.46 |
| warfare | 15.82 | 15.82 | -0.00 |
| soldiers | 17.59 | 17.56 | -0.03 |

Within-session dispersion is essentially stable — small shifts that should
not materially change H2 or H4 conclusions.

### Mean of per-session `mean_visits_{threat}` (used by H5)

| Threat | Original | Cleaned | Δ |
|---|---|---|---|
| angry_face | 1.74 | 1.81 | +0.07 |
| anxiety_inducing | 1.79 | 1.85 | +0.06 |
| warfare | 1.59 | 1.69 | +0.10 |
| soldiers | 1.70 | 1.74 | +0.05 |

All four threat categories show small positive nudges in mean visits — the
removed images had slightly fewer visits on average.

## Validation

The script asserts:
- Exactly 30 rows after the loop, 29 after dropping `UgMWkyrkRYVZ9cr9thRw`, 26 after dropping blink outliers.
- All metadata columns (`if_PTSD`, `ITI_PTSD`, `ITI_cPTSD`, `if_antipsychotic`) are non-null.
- All `mean_dwell_pct_*` values lie in `[-0.01, 101]`.

All assertions passed.

## Caveats for downstream interpretation

- **combat_vehicles (50 % retained)** is well below the others; not used by
  H1–H6 but worth noting if exploratory analyses touch it.
- The kept-image set is enriched for high-engagement, low-CV, expected-
  direction images within the directional categories. The None-direction
  categories (neutral / neutral_face / sad_face) are unchanged, so threat-
  vs-neutral contrasts retain their full comparator base.
- Image-level filtering does not propagate into the temporal-bias datasets
  (`temporal_threat_bias_*.csv`); E3 should be re-run separately if needed.
  Out of scope for the current cleanup pass.
