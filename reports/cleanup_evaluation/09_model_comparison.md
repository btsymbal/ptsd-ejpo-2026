# Step 9 — Image-Cleanup Effect on PTSD Prediction

**Datasets**: `data/simplified/dataset_eyetracking_metrics_clean.csv` (orig) and `data/simplified/dataset_eyetracking_metrics_clean_imageclean.csv` (cleaned). Same n=29 sessions, identical CV splits, identical features and pipeline.

## Headline performance

| Metric | Original | Cleaned | Δ (clean − orig) |
|---|---|---|---|
| AUC | 0.574 [0.343, 0.788] | 0.480 [0.258, 0.706] | -0.093 |
| Balanced accuracy | 0.591 [0.413, 0.766] | 0.502 [0.317, 0.688] | -0.088 |
| Accuracy | 0.621 [0.448, 0.793] | 0.517 [0.345, 0.690] | -0.103 |

## ΔAUC significance test

Paired permutation test (5 000 perms) on per-fold predicted probabilities:
**ΔAUC = -0.093, two-sided p = 0.2506**.

The test swaps each held-out subject's proba between the two models and
recomputes ΔAUC; the null distribution under random swaps is centred at zero.

## Confusion matrices

### Original

|  | predicted no-PTSD | predicted PTSD |
|---|---|---|
| true no-PTSD | 5 | 7 |
| true PTSD | 4 | 13 |

### Cleaned

|  | predicted no-PTSD | predicted PTSD |
|---|---|---|
| true no-PTSD | 5 | 7 |
| true PTSD | 7 | 10 |

## Per-feature coefficient changes (mean across LOOCV folds, standardised X)

| Feature | mean_coef orig | mean_coef clean | Δ |
|---|---|---|---|
| `mean_dwell_pct_angry_face` | -0.087 | +0.254 | +0.341 |
| `mean_dwell_pct_warfare` | +0.710 | +0.741 | +0.031 |
| `mean_dwell_pct_anxiety_inducing` | +0.514 | +0.191 | -0.323 |
| `mean_dwell_pct_soldiers` | -0.825 | -0.781 | +0.044 |
| `std_dwell_pct_angry_face` | +0.899 | +0.640 | -0.260 |
| `std_dwell_pct_warfare` | -0.250 | -0.149 | +0.101 |
| `mean_visits_late_angry_face` | +0.397 | +0.411 | +0.014 |
| `mean_offscreen_pct_angry_face` | +0.763 | +0.685 | -0.078 |

## Honest interpretation

- With n = 29, the bootstrap CIs for AUC are wide: the original
  CI is roughly [0.34, 0.79] and the cleaned
  CI is roughly [0.26, 0.71], i.e. they
  overlap heavily.
- The paired permutation test does not detect a significant ΔAUC; the headline ΔAUC is plausibly noise at this sample size.
- Headline AUC moves *against* the expected direction (cleaned < original). One reading is that with such a small set of features and small n, removing trial-level noise also removes some idiosyncratic discriminative information; another is simple sampling noise.

- Coefficient changes are interpretable individually, but with LOOCV at n=29
  the per-fold coefficient SD is comparable in magnitude to the mean,
  so individual coefficient comparisons should not drive conclusions.
- A more conclusive test of cleanup utility would require external
  validation data — out of scope here.
