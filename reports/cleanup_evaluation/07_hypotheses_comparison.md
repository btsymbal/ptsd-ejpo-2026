# Step 7 — Hypothesis Re-Evaluation Comparison

Re-runs H1–H6 on both the original analysis dataset (n = 29) and the
image-cleaned variant from Step 6, with identical test selection logic.
Each family receives Benjamini-Hochberg FDR correction (4 tests per family).

Within each row, `effect_orig` / `effect_clean` is Cohen's d, rank-biserial r,
Pearson r, or Kendall τ_b depending on which test was selected (column `test_*`).
The `change` column tags whether the cleaned dataset moved in the pre-registered
direction *and* lowered the uncorrected p-value:

- **improved** — moved as predicted, p decreased
- **regressed** — moved opposite to prediction, p increased
- **effect↑ p↑** — moved as predicted but p increased (effect strengthened, less precise)
- **p↓ effect↓** — opposite direction but p decreased (different finding, more precise)
- **—** — no directional expectation (none of H1–H6 currently)

**Aggregate**: 22 of 52 rows improved; 18 regressed.  BH-significant rows: orig = 0, clean = 0.

## H1 — Threat Stimulus Dwell Time × PTSD Group

| Family | Category | Test (orig) | effect_orig | p_unc orig | p_BH orig | effect_clean | p_unc clean | p_BH clean | Δeffect | Δp_unc | change |
|---|---|---|---|---|---|---|---|---|---|---|---|
| mean_dwell_pct | angry_face | Student's t | +0.213 | 0.576 | 0.786 | +0.377 | 0.326 | 0.674 | +0.164 | -0.250 | improved |
| mean_dwell_pct | anxiety_inducing | MW-U | -0.147 | 0.521 | 0.786 | +0.302 | 0.430 | 0.674 | +0.449 | -0.091 | improved |
| mean_dwell_pct | soldiers | Student's t | -0.103 | 0.786 | 0.786 | -0.039 | 0.918 | 0.918 | +0.064 | +0.132 | effect↑ p↑ |
| mean_dwell_pct | warfare | Student's t | +0.154 | 0.686 | 0.786 | +0.254 | 0.505 | 0.674 | +0.100 | -0.181 | improved |

**H1 summary**: 3/4 rows improved, 0/4 regressed; BH-sig orig=0, clean=0.

## H2 — Threat Dwell-Time Variability × PTSD Group

| Family | Category | Test (orig) | effect_orig | p_unc orig | p_BH orig | effect_clean | p_unc clean | p_BH clean | Δeffect | Δp_unc | change |
|---|---|---|---|---|---|---|---|---|---|---|---|
| std_dwell_pct | angry_face | Student's t | +0.756 | 0.055 | 0.221 | +0.647 | 0.098 | 0.390 | -0.108 | +0.042 | regressed |
| std_dwell_pct | anxiety_inducing | Student's t | +0.621 | 0.111 | 0.223 | +0.319 | 0.405 | 0.757 | -0.301 | +0.293 | regressed |
| std_dwell_pct | soldiers | Student's t | -0.008 | 0.984 | 0.984 | +0.118 | 0.757 | 0.757 | +0.126 | -0.227 | improved |
| std_dwell_pct | warfare | Student's t | +0.041 | 0.914 | 0.984 | +0.120 | 0.752 | 0.757 | +0.079 | -0.162 | improved |

**H2 summary**: 2/4 rows improved, 2/4 regressed; BH-sig orig=0, clean=0.

## H3 — Threat-minus-Neutral Bias Variability × PTSD Group

| Family | Category | Test (orig) | effect_orig | p_unc orig | p_BH orig | effect_clean | p_unc clean | p_BH clean | Δeffect | Δp_unc | change |
|---|---|---|---|---|---|---|---|---|---|---|---|
| std_delta_dwell_pct | angry_face | Student's t | +0.224 | 0.558 | 0.960 | +0.166 | 0.663 | 0.927 | -0.057 | +0.105 | regressed |
| std_delta_dwell_pct | anxiety_inducing | Student's t | +0.361 | 0.347 | 0.960 | +0.235 | 0.539 | 0.927 | -0.127 | +0.192 | regressed |
| std_delta_dwell_pct | soldiers | Student's t | -0.019 | 0.960 | 0.960 | +0.035 | 0.927 | 0.927 | +0.054 | -0.033 | improved |
| std_delta_dwell_pct | warfare | Student's t | +0.054 | 0.888 | 0.960 | -0.133 | 0.727 | 0.927 | -0.187 | -0.162 | p↓ effect↓ |

**H3 summary**: 1/4 rows improved, 2/4 regressed; BH-sig orig=0, clean=0.

## H4 — Within-PTSD Correlation: Variability vs. ITI_PTSD

| Family | Category | Test (orig) | effect_orig | p_unc orig | p_BH orig | effect_clean | p_unc clean | p_BH clean | Δeffect | Δp_unc | change |
|---|---|---|---|---|---|---|---|---|---|---|---|
| std_delta_dwell_pct | angry_face | Pearson r | -0.179 | 0.491 | 0.491 | -0.089 | 0.735 | 0.735 | +0.091 | +0.244 | effect↑ p↑ |
| std_delta_dwell_pct | anxiety_inducing | Pearson r | -0.293 | 0.253 | 0.338 | -0.301 | 0.240 | 0.369 | -0.008 | -0.013 | p↓ effect↓ |
| std_delta_dwell_pct | soldiers | Pearson r | -0.331 | 0.194 | 0.338 | -0.280 | 0.277 | 0.369 | +0.051 | +0.082 | effect↑ p↑ |
| std_delta_dwell_pct | warfare | Pearson r | -0.359 | 0.157 | 0.338 | -0.324 | 0.204 | 0.369 | +0.034 | +0.047 | effect↑ p↑ |
| std_dwell_pct | angry_face | Pearson r | +0.135 | 0.606 | 0.606 | +0.216 | 0.406 | 0.406 | +0.081 | -0.200 | improved |
| std_dwell_pct | anxiety_inducing | Pearson r | -0.396 | 0.116 | 0.201 | -0.427 | 0.087 | 0.163 | -0.031 | -0.028 | p↓ effect↓ |
| std_dwell_pct | soldiers | Pearson r | -0.424 | 0.090 | 0.201 | -0.457 | 0.065 | 0.163 | -0.033 | -0.025 | p↓ effect↓ |
| std_dwell_pct | warfare | Pearson r | -0.364 | 0.151 | 0.201 | -0.390 | 0.122 | 0.163 | -0.026 | -0.029 | p↓ effect↓ |

**H4 summary**: 1/8 rows improved, 0/8 regressed; BH-sig orig=0, clean=0.

## H5 — Visits to Threat Stimuli × PTSD Group

| Family | Category | Test (orig) | effect_orig | p_unc orig | p_BH orig | effect_clean | p_unc clean | p_BH clean | Δeffect | Δp_unc | change |
|---|---|---|---|---|---|---|---|---|---|---|---|
| mean_visits | angry_face | Student's t | +0.305 | 0.425 | 0.571 | +0.360 | 0.348 | 0.464 | +0.055 | -0.077 | improved |
| mean_visits | anxiety_inducing | Student's t | +0.216 | 0.571 | 0.571 | +0.365 | 0.342 | 0.464 | +0.149 | -0.229 | improved |
| mean_visits | soldiers | MW-U | +0.181 | 0.423 | 0.571 | +0.118 | 0.609 | 0.609 | -0.064 | +0.186 | regressed |
| mean_visits | warfare | Student's t | +0.252 | 0.510 | 0.571 | +0.398 | 0.300 | 0.464 | +0.147 | -0.210 | improved |
| mean_visits_late | angry_face | Student's t | +0.192 | 0.616 | 0.616 | +0.262 | 0.493 | 0.657 | +0.071 | -0.123 | improved |
| mean_visits_late | anxiety_inducing | Student's t | +0.272 | 0.476 | 0.616 | +0.438 | 0.256 | 0.657 | +0.165 | -0.220 | improved |
| mean_visits_late | soldiers | Student's t | -0.214 | 0.575 | 0.616 | +0.022 | 0.954 | 0.954 | +0.236 | +0.378 | effect↑ p↑ |
| mean_visits_late | warfare | Student's t | +0.198 | 0.603 | 0.616 | +0.284 | 0.458 | 0.657 | +0.086 | -0.145 | improved |

**H5 summary**: 6/8 rows improved, 1/8 regressed; BH-sig orig=0, clean=0.

## H6 — Within-PTSD Correlation: Avoidance-Like Gaze vs. ITI_PTSD

| Family | Category | Test (orig) | effect_orig | p_unc orig | p_BH orig | effect_clean | p_unc clean | p_BH clean | Δeffect | Δp_unc | change |
|---|---|---|---|---|---|---|---|---|---|---|---|
| mean_dwell_pct | angry_face | Pearson r | -0.302 | 0.238 | 0.476 | -0.261 | 0.313 | 0.569 | +0.042 | +0.074 | regressed |
| mean_dwell_pct | anxiety_inducing | Kendall τ_b | -0.302 | 0.103 | 0.412 | -0.249 | 0.336 | 0.569 | +0.053 | +0.233 | regressed |
| mean_dwell_pct | soldiers | Pearson r | -0.147 | 0.575 | 0.575 | -0.149 | 0.569 | 0.569 | -0.002 | -0.005 | improved |
| mean_dwell_pct | warfare | Pearson r | -0.195 | 0.453 | 0.575 | -0.203 | 0.436 | 0.569 | -0.007 | -0.017 | improved |
| mean_dwell_pct_late | angry_face | Pearson r | -0.305 | 0.233 | 0.466 | -0.257 | 0.318 | 0.425 | +0.048 | +0.085 | regressed |
| mean_dwell_pct_late | anxiety_inducing | Kendall τ_b | -0.317 | 0.087 | 0.346 | -0.311 | 0.225 | 0.425 | +0.006 | +0.138 | regressed |
| mean_dwell_pct_late | soldiers | Pearson r | -0.179 | 0.492 | 0.492 | -0.174 | 0.503 | 0.503 | +0.004 | +0.011 | regressed |
| mean_dwell_pct_late | warfare | Pearson r | -0.201 | 0.439 | 0.492 | -0.284 | 0.269 | 0.425 | -0.083 | -0.170 | improved |
| mean_offscreen_pct | angry_face | Pearson r | +0.225 | 0.385 | 0.532 | +0.201 | 0.438 | 0.636 | -0.024 | +0.053 | regressed |
| mean_offscreen_pct | anxiety_inducing | Pearson r | +0.045 | 0.863 | 0.863 | -0.011 | 0.967 | 0.967 | -0.056 | +0.104 | regressed |
| mean_offscreen_pct | soldiers | Pearson r | +0.219 | 0.399 | 0.532 | +0.131 | 0.477 | 0.636 | -0.087 | +0.078 | regressed |
| mean_offscreen_pct | warfare | Kendall τ_b | +0.162 | 0.380 | 0.532 | +0.178 | 0.336 | 0.636 | +0.015 | -0.044 | improved |
| mean_offscreen_pct_late | angry_face | Pearson r | +0.186 | 0.475 | 0.633 | +0.171 | 0.511 | 0.682 | -0.015 | +0.037 | regressed |
| mean_offscreen_pct_late | anxiety_inducing | Pearson r | -0.006 | 0.981 | 0.981 | -0.070 | 0.790 | 0.790 | -0.064 | -0.191 | p↓ effect↓ |
| mean_offscreen_pct_late | soldiers | Pearson r | +0.203 | 0.435 | 0.633 | +0.162 | 0.380 | 0.682 | -0.040 | -0.055 | p↓ effect↓ |
| mean_offscreen_pct_late | warfare | Kendall τ_b | +0.147 | 0.427 | 0.633 | +0.162 | 0.380 | 0.682 | +0.015 | -0.047 | improved |
| mean_visits | angry_face | Pearson r | -0.220 | 0.397 | 0.934 | -0.113 | 0.665 | 0.894 | +0.106 | +0.268 | regressed |
| mean_visits | anxiety_inducing | Pearson r | -0.040 | 0.878 | 0.934 | -0.035 | 0.894 | 0.894 | +0.005 | +0.016 | regressed |
| mean_visits | soldiers | Pearson r | -0.022 | 0.934 | 0.934 | -0.088 | 0.736 | 0.894 | -0.066 | -0.197 | improved |
| mean_visits | warfare | Pearson r | -0.140 | 0.592 | 0.934 | -0.086 | 0.744 | 0.894 | +0.054 | +0.152 | regressed |
| mean_visits_late | angry_face | Pearson r | -0.267 | 0.300 | 0.488 | -0.145 | 0.578 | 0.578 | +0.122 | +0.278 | regressed |
| mean_visits_late | anxiety_inducing | Pearson r | -0.196 | 0.451 | 0.488 | -0.231 | 0.373 | 0.498 | -0.035 | -0.078 | improved |
| mean_visits_late | soldiers | Pearson r | -0.221 | 0.393 | 0.488 | -0.260 | 0.314 | 0.498 | -0.038 | -0.079 | improved |
| mean_visits_late | warfare | Pearson r | -0.180 | 0.488 | 0.488 | -0.232 | 0.370 | 0.498 | -0.052 | -0.118 | improved |

**H6 summary**: 9/24 rows improved, 13/24 regressed; BH-sig orig=0, clean=0.

## Overall verdict

- **22/52** directional rows improved across all 6 hypotheses.
- **18/52** regressed.
- BH-significant findings: **orig = 0**, **clean = 0**.

Image cleanup moved more results in the predicted direction than against it.
BH-significance count is unchanged.

See `data/simplified/image_quality_flags.csv` for the flag table and `reports/cleanup_evaluation/06_cleaned_dataset_summary.md` for the per-category retention rates.
