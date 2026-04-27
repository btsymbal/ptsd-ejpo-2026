# Step 8 — Baseline PTSD Predictive Model

## Spec

- **Dataset**: `data/simplified/dataset_eyetracking_metrics_clean.csv` (29 sessions; PTSD=17, no-PTSD=12)
- **Features (n=8)**:
  - `mean_dwell_pct_angry_face`
  - `mean_dwell_pct_warfare`
  - `mean_dwell_pct_anxiety_inducing`
  - `mean_dwell_pct_soldiers`
  - `std_dwell_pct_angry_face`
  - `std_dwell_pct_warfare`
  - `mean_visits_late_angry_face`
  - `mean_offscreen_pct_angry_face`
- **Pipeline**: `StandardScaler` → `LogisticRegression(penalty='l2', C=1.0, solver='liblinear')`
- **CV**: leave-one-out (LOOCV)
- **Metrics**: AUC (primary), balanced accuracy, accuracy. 95 % CIs via percentile bootstrap (2 000 resamples).

## Feature rationale

Features were chosen from the existing analysis as the most theoretically
and empirically promising discriminators of PTSD status:

- The four `mean_dwell_pct_*` columns map directly onto the H1 family.
- `std_dwell_pct_angry_face` / `std_dwell_pct_warfare` map onto H2 — angry-
  face dwell variability was the strongest pre-cleanup signal (d = 0.76).
- `mean_visits_late_angry_face` and `mean_offscreen_pct_angry_face`
  capture late-window monitoring and off-screen avoidance respectively
  (H5/H6 signals).

We deliberately kept the feature set small (8 features for n = 29) — more
predictors than ~n/3 are unstable under LOOCV even with L2 regularisation.

## Performance

| Metric | Value | 95 % CI (bootstrap) |
|---|---|---|
| AUC | 0.574 | [0.343, 0.788] |
| Balanced accuracy | 0.591 | [0.413, 0.766] |
| Accuracy | 0.621 | [0.448, 0.793] |

## Confusion matrix (LOOCV predictions)

|  | predicted no-PTSD | predicted PTSD |
|---|---|---|
| true no-PTSD | 5 | 7 |
| true PTSD | 4 | 13 |

## Coefficients (mean ± SD across LOOCV folds, standardised features)

| Feature | Mean coef | SD coef |
|---|---|---|
| `mean_dwell_pct_angry_face` | -0.087 | 0.136 |
| `mean_dwell_pct_warfare` | +0.710 | 0.082 |
| `mean_dwell_pct_anxiety_inducing` | +0.514 | 0.072 |
| `mean_dwell_pct_soldiers` | -0.825 | 0.088 |
| `std_dwell_pct_angry_face` | +0.899 | 0.068 |
| `std_dwell_pct_warfare` | -0.250 | 0.087 |
| `mean_visits_late_angry_face` | +0.397 | 0.097 |
| `mean_offscreen_pct_angry_face` | +0.763 | 0.094 |

## Caveats

- n = 29 is very small for a classifier; the bootstrap CI for
  AUC will be wide, and any single-point estimate should not be over-interpreted.
- LOOCV is the only honest CV given the sample size, but the resulting AUC
  is sensitive to a single mis-prediction (one swap moves AUC by ~0.005).
- Without external validation we cannot tell if these features generalise.
