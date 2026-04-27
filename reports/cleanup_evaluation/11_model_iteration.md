# Step 11 — PTSD Predictor: Feature-Set Iteration

## Why we iterated

The Step 8/9 PTSD predictor was a quick feasibility model picked to keep the
image-cleanup comparison fair, not optimised for performance (AUC 0.574 / 0.480
on original / cleaned with 8 mostly mean-dwell features). A reference model from
a prior analysis (`/Users/bohdantsymbal/Downloads/model_summary.txt`) reached
AUC = 0.820 on a slightly different sample with 6 features, leaning heavily on
**dwell-time SDs across multiple categories**.

This step tests several principled feature sets on the image-cleaned dataset
(n = 29) and re-runs the winner on the un-image-cleaned dataset as a backward
check.

## Excluded features and why

- **`blink_count`** — flagged as low-quality (eye-tracker sample rate too low to
  detect blinks reliably; outlier sessions already removed for this reason). The
  reference model used it but was inflated by one extreme participant; we drop it.
- **`nose_dist_norm`** (head-trajectory length) — initial iteration found it the
  strongest non-gaze feature, but a follow-up exploration showed the same outlier
  pathology as `blink_count`: PTSD vs no-PTSD medians are almost equal (471 vs
  425), the discriminative signal sits in the upper tail (4 of 5 Tukey outliers
  are PTSD, including a 2218 maximum), and dropping the top 3 PTSD participants
  collapses the univariate AUC from 0.637 to 0.560. Most likely a tracker
  quality issue rather than a real PTSD-related head-movement effect. Dropped.

## Decisions (locked)

- **Pipeline**: `StandardScaler → LogisticRegression(penalty='l2', C=1.0,
  solver='liblinear', class_weight='balanced')`. `class_weight='balanced'`
  handles the mild 17 / 12 imbalance without SMOTE (synthetic samples
  inside LOOCV inflate AUC misleadingly at n = 29).
- **CV**: leave-one-out. **Primary metric**: AUC. **Secondary**: balanced
  accuracy, accuracy. **CIs**: percentile bootstrap, 2 000 resamples.
- **≤ 6 features per candidate** (n = 29 — more invites unstable LOOCV).

## Candidates (4)

### A2_reference_minus_nose

Features:
- `std_dwell_pct_happy_event`
- `std_dwell_pct_combat_vehicles`
- `std_dwell_pct_angry_face`
- `std_dwell_pct_neutral`

### B_h1_h6_driven

Features:
- `std_dwell_pct_angry_face`
- `std_dwell_pct_warfare`
- `mean_dwell_pct_angry_face`
- `mean_dwell_pct_warfare`
- `mean_offscreen_pct_angry_face`
- `mean_visits_late_angry_face`

### D_threat_stds_only

Features:
- `std_dwell_pct_angry_face`
- `std_dwell_pct_warfare`
- `std_dwell_pct_soldiers`
- `std_dwell_pct_anxiety_inducing`

### F_broad_stds

Features:
- `std_dwell_pct_angry_face`
- `std_dwell_pct_warfare`
- `std_dwell_pct_soldiers`
- `std_dwell_pct_anxiety_inducing`
- `std_dwell_pct_combat_vehicles`
- `std_dwell_pct_happy_event`

## Results — cleaned dataset (n = 29)

| Candidate | AUC | Balanced acc | Accuracy |
|---|---|---|---|
| A2_reference_minus_nose | 0.578 [0.348, 0.805] | 0.645 [0.457, 0.826] | 0.655 [0.483, 0.828] |
| B_h1_h6_driven | 0.525 [0.280, 0.750] | 0.586 [0.389, 0.766] | 0.586 [0.414, 0.759] |
| D_threat_stds_only | 0.505 [0.263, 0.740] | 0.456 [0.267, 0.640] | 0.448 [0.276, 0.621] |
| F_broad_stds | 0.480 [0.247, 0.725] | 0.502 [0.315, 0.686] | 0.517 [0.345, 0.690] |

### A2_reference_minus_nose — coefficients & univariate AUCs

| Feature | mean coef | SD coef | univariate AUC | aligned AUC |
|---|---|---|---|---|
| `std_dwell_pct_happy_event` | -0.337 | 0.073 | 0.578 | 0.578 |
| `std_dwell_pct_combat_vehicles` | +0.557 | 0.096 | 0.706 | 0.706 |
| `std_dwell_pct_angry_face` | +0.395 | 0.097 | 0.696 | 0.696 |
| `std_dwell_pct_neutral` | +0.310 | 0.072 | 0.652 | 0.652 |

Confusion matrix (LOOCV):

|  | predicted no-PTSD | predicted PTSD |
|---|---|---|
| true no-PTSD | 7 | 5 |
| true PTSD | 5 | 12 |

### B_h1_h6_driven — coefficients & univariate AUCs

| Feature | mean coef | SD coef | univariate AUC | aligned AUC |
|---|---|---|---|---|
| `std_dwell_pct_angry_face` | +0.663 | 0.079 | 0.696 | 0.696 |
| `std_dwell_pct_warfare` | -0.210 | 0.113 | 0.564 | 0.564 |
| `mean_dwell_pct_angry_face` | +0.176 | 0.182 | 0.672 | 0.672 |
| `mean_dwell_pct_warfare` | +0.398 | 0.115 | 0.578 | 0.578 |
| `mean_offscreen_pct_angry_face` | +0.708 | 0.092 | 0.544 | 0.544 |
| `mean_visits_late_angry_face` | +0.304 | 0.114 | 0.574 | 0.574 |

Confusion matrix (LOOCV):

|  | predicted no-PTSD | predicted PTSD |
|---|---|---|
| true no-PTSD | 7 | 5 |
| true PTSD | 7 | 10 |

### D_threat_stds_only — coefficients & univariate AUCs

| Feature | mean coef | SD coef | univariate AUC | aligned AUC |
|---|---|---|---|---|
| `std_dwell_pct_angry_face` | +0.639 | 0.084 | 0.696 | 0.696 |
| `std_dwell_pct_warfare` | -0.110 | 0.094 | 0.564 | 0.564 |
| `std_dwell_pct_soldiers` | -0.136 | 0.100 | 0.490 | 0.510 |
| `std_dwell_pct_anxiety_inducing` | +0.241 | 0.077 | 0.583 | 0.583 |

Confusion matrix (LOOCV):

|  | predicted no-PTSD | predicted PTSD |
|---|---|---|
| true no-PTSD | 6 | 6 |
| true PTSD | 10 | 7 |

### F_broad_stds — coefficients & univariate AUCs

| Feature | mean coef | SD coef | univariate AUC | aligned AUC |
|---|---|---|---|---|
| `std_dwell_pct_angry_face` | +0.486 | 0.103 | 0.696 | 0.696 |
| `std_dwell_pct_warfare` | +0.181 | 0.092 | 0.564 | 0.564 |
| `std_dwell_pct_soldiers` | -0.256 | 0.101 | 0.490 | 0.510 |
| `std_dwell_pct_anxiety_inducing` | +0.324 | 0.089 | 0.583 | 0.583 |
| `std_dwell_pct_combat_vehicles` | +0.606 | 0.103 | 0.706 | 0.706 |
| `std_dwell_pct_happy_event` | -0.396 | 0.091 | 0.578 | 0.578 |

Confusion matrix (LOOCV):

|  | predicted no-PTSD | predicted PTSD |
|---|---|---|
| true no-PTSD | 5 | 7 |
| true PTSD | 7 | 10 |

## Winner

**A2_reference_minus_nose** with AUC = 0.578 [0.348, 0.805].

Ranking (by AUC, ties broken by balanced accuracy):

1. **A2_reference_minus_nose** — AUC 0.578, balanced acc 0.645
2. **B_h1_h6_driven** — AUC 0.525, balanced acc 0.586
3. **D_threat_stds_only** — AUC 0.505, balanced acc 0.456
4. **F_broad_stds** — AUC 0.480, balanced acc 0.502

## Backward check — winning feature set on the *un-image-cleaned* dataset

| Metric | Cleaned | Original (un-cleaned) | Δ (clean − orig) |
|---|---|---|---|
| AUC | 0.578 [0.348, 0.805] | 0.510 [0.276, 0.742] | +0.069 |
| Balanced accuracy | 0.645 [0.457, 0.826] | 0.544 [0.358, 0.726] | +0.100 |
| Accuracy | 0.655 [0.483, 0.828] | 0.552 [0.379, 0.724] | +0.103 |

Paired permutation test on per-fold predicted probabilities for ΔAUC (cleaned − original): **ΔAUC = +0.069, two-sided p = 0.5472**.

## Honest caveats

- **n = 29** is very small for a classifier. Bootstrap CIs are wide;
  most span 0.5 (chance) for AUC.
- **A swap of one or two LOOCV predictions** moves AUC by ~0.05. Headline
  ranking differences smaller than that should not drive conclusions.
- **The reference model's AUC = 0.820 was on a different sample** with
  different exclusions (and used `blink_count`, which we deliberately drop).
  We should not expect to match that headline.
- **Backward check direction**: positive Δ (cleaned > original) is the
  predicted direction. If the winner shows negative Δ on this small sample,
  read it as "image cleanup did not move the predictor at this resolution",
  not "image cleanup hurt the predictor." See the paired-perm p-value.
