# LMM-Based Image Quality Evaluation

## Methodology

This analysis integrates multiple per-image metrics to identify poorly performing
images in the stimulus set. The approach combines:

1. **Coefficient of Variation (CV)**: within-group variability of dwell time percentage
   per image, computed separately for PTSD and No-PTSD groups. High CV indicates
   inconsistent attentional responses across participants.
2. **Distributional properties**: skewness and kurtosis of dwell time distributions
   across all participants, identifying images with atypical response patterns.
3. **Group comparisons**: per-image effect sizes (Cohen's d for parametric tests,
   rank-biserial r for non-parametric tests) comparing PTSD vs No-PTSD dwell time,
   with Benjamini-Hochberg FDR correction.
4. **Linear Mixed Models (LMM)**: fitted as an informational diagnostic only.
   Model: `dwell_pct ~ if_PTSD + (1 | image) + VC(participant)` per category
   using REML estimation. Image-level BLUPs (Best Linear Unbiased Predictors)
   capture each image's deviation from the category mean after controlling
   for group and participant variability — i.e. overall engagement, not a
   PTSD-specific response. BLUPs are reported in dotplots for interpretive
   context but are **not** used for flagging (see discussion below).

Images are flagged by the combined rule:

    flagged = C1 OR C2 OR (C3 AND C4)

Strong criteria (each fires alone):

- **C1 — CV (within PTSD group)**: `CV_PTSD >= 1.0` (within-group SD exceeds
  the mean — a scale-free indicator of substantively noisy measurement).
- **C2 — Wrong-direction effect size with confidence**: Cohen's d / rank-
  biserial r has the unexpected sign **and** uncorrected p ≤ 0.5. The p-value
  gate prevents wrong-direction effects from extremely uncertain tests
  (e.g. p ≈ 0.99) from triggering a flag — those are noise, not a real
  failure of the theoretical prediction. Categories with no directional
  expectation (`neutral`, `neutral_face`, `sad_face`) are skipped by C2.

Weak criteria (must co-occur to fire):

- **C3 — Pooled skewness**: `|skewness| > 1.0` across all participants.
  Highly skewed dwell-time distributions mean nearly everyone reacts the
  same way to the image, so the image cannot discriminate between the groups.
- **C4 — Bottom-quintile BLUP**: image's intercept BLUP is in the bottom
  20% of its category (low absolute engagement). The intercept BLUP captures
  overall engagement, not PTSD-specific response, so we only count it when
  it co-occurs with C3.

### Expected Directions

| Category | Expected sign | Rationale |
|----------|---------------|-----------|
| angry_face | positive | hypervigilance to threat |
| anxiety_inducing | positive | hypervigilance to potential (hidden) threat |
| combat_vehicles | positive | emotionally driven memories |
| happy_event | negative | anhedonistic subtype |
| happy_face | negative | anhedonistic subtype |
| neutral | — | no consistent pattern (paired with diverse images) |
| neutral_face | — | no direct expectation (former direction was inferred from opposite threat image) |
| sad_face | — | no direct expectation (former direction was inferred from opposite happy image) |
| sleep_related | positive | PTSD group expected to dwell longer due to sleep-related symptoms |
| soldiers | positive | hypervigilance to threat |
| warfare | positive | hypervigilance to threat |

## LMM Results Per Category (diagnostic)

| Category | n_images | n_participants | Intercept | Group coef | Group p | Image var | Participant var | Residual var | Converged | Hessian warning |
|----------|----------|----------------|-----------|------------|---------|-----------|-----------------|--------------|-----------|-----------------|
| angry_face | 10 | 29 | 22.9825 | 2.5905 | 0.2558 | 7.6725 | 238.9759 | 126.5315 | Yes | No |
| anxiety_inducing | 14 | 29 | 26.8700 | 4.4369 | 0.0499 | 7.7225 | 332.3800 | 171.8003 | Yes | No |
| combat_vehicles | 8 | 29 | 27.3854 | 1.0863 | 0.7372 | 151.7129 | 479.7845 | 110.1855 | No | Yes |
| happy_event | 9 | 29 | 26.6038 | -3.6886 | 0.1242 | 11.2007 | 235.3946 | 128.9624 | Yes | No |
| happy_face | 11 | 29 | 24.4186 | -3.1034 | 0.1346 | 18.5688 | 248.9201 | 83.9794 | No | Yes |
| neutral | 50 | 29 | 20.0396 | 0.5380 | 0.5755 | 4.8139 | 214.2976 | 110.3975 | Yes | No |
| neutral_face | 13 | 29 | 24.4253 | -0.8392 | 0.6816 | 134.7852 | 318.1839 | 64.3510 | No | Yes |
| sad_face | 8 | 29 | 20.9761 | 3.0407 | 0.2140 | 6.6439 | 220.6869 | 116.3111 | Yes | No |
| sleep_related | 7 | 29 | 25.2017 | -0.4904 | 0.8692 | 122.9788 | 357.1790 | 79.2621 | No | Yes |
| soldiers | 8 | 29 | 28.4119 | -1.5207 | 0.6102 | 154.0058 | 412.3058 | 88.3645 | No | Yes |
| warfare | 12 | 29 | 23.5564 | 2.3202 | 0.3224 | 149.9026 | 383.5059 | 80.5395 | No | Yes |

## Assumption Checks

LMM assumptions were assessed for each category.

**Note on residual computation**: Residuals and fitted values for diagnostics are
computed as fixed effects + image BLUPs only, excluding participant variance-component
predictions. This is necessary because statsmodels' `fittedvalues` includes participant
VC pseudo-predictions that are poorly estimated (the VC approach does not produce true
conditional modes for the second random effect), creating spurious residual-fitted
correlations. The image BLUPs — the primary output of interest — are properly estimated
via the `groups` factor.

- **Normality of residuals**: Shapiro-Wilk test + Q-Q plots
- **Homoscedasticity**: Residuals vs. fitted values scatter plots
- **Normality of random effects**: Q-Q plots for image BLUPs
- **Independence**: Satisfied by design (each participant sees each image once)
- **Linearity**: Trivially met with a single binary predictor

| Category | n_obs | Shapiro W | Shapiro p | Resid skewness | Resid kurtosis | n_BLUPs |
|----------|-------|-----------|-----------|----------------|----------------|---------|
| angry_face | 290 | 0.9518 | 0.0000 | 0.6860 | 0.1665 | 10 |
| anxiety_inducing | 406 | 0.9551 | 0.0000 | 0.5745 | -0.3355 | 14 |
| combat_vehicles | 232 | 0.9344 | 0.0000 | 0.9124 | 0.5095 | 8 |
| happy_event | 261 | 0.9574 | 0.0000 | 0.5425 | -0.4625 | 9 |
| happy_face | 319 | 0.9481 | 0.0000 | 0.8118 | 0.5817 | 11 |
| neutral | 1450 | 0.9231 | 0.0000 | 0.8888 | 0.4763 | 50 |
| neutral_face | 377 | 0.9452 | 0.0000 | 0.7142 | 0.0435 | 13 |
| sad_face | 232 | 0.9423 | 0.0000 | 0.6782 | -0.1832 | 8 |
| sleep_related | 203 | 0.9372 | 0.0000 | 0.8785 | 0.5840 | 7 |
| soldiers | 232 | 0.9396 | 0.0000 | 0.4502 | -0.8971 | 8 |
| warfare | 348 | 0.9357 | 0.0000 | 0.6690 | -0.3900 | 12 |

Residual normality satisfied (p > 0.05): 0/11 categories.

LMMs are generally robust to moderate departures from normality, especially with
repeated measures and the sample sizes in this study. Categories with strongly
non-normal residuals should be interpreted with caution.

### Convergence Warnings

6/11 categories produced Hessian/convergence warnings:
combat_vehicles, happy_face, neutral_face, sleep_related, soldiers, warfare.

These warnings typically arise in categories with few images (7-13), where the
image variance component is estimated at a boundary or the optimization landscape
is flat. The models still converge to parameter estimates, but BLUPs from these
categories should be interpreted with extra caution. Flagging decisions for these
categories are less reliable than for categories without warnings.

Diagnostic plots: `figures/images_analysis/lmm_image_quality/assumption_diagnostics.png`

## Flagged Images

**Total flagged (combined rule)**: 22/150

Flag CSV: `data/simplified/image_quality_flags.csv`

| Image ID | Category | Fired | CV (PTSD) | ES | p (uncorr) | Skewness | BLUP |
|----------|----------|-------|-----------|----|------------|----------|------|
| MamyfpQXRqCkhsxuPo2UxQ | sleep_related | C1, C3∧C4 | 1.205 | -0.152 | 0.504 | 1.364 | -1.948 |
| fefWMtd9R8KSv7H2BTpIrw | anxiety_inducing | C1, C2 | 1.164 | -0.225 | 0.318 | 0.911 | -2.251 |
| WMKKOlK4QrGOs3Cn2b_lZg | soldiers | C1, C2 | 1.131 | -0.319 | 0.155 | 0.339 | -4.840 |
| axcFiBXmT_69RLbTxgEX_g | angry_face | C1, C3∧C4 | 1.123 | -0.137 | 0.547 | 1.002 | -1.973 |
| VBsOU00iTcmFmqu6o4q07A | combat_vehicles | C1, C3∧C4 | 1.088 | 0.025 | 0.928 | 1.944 | -9.176 |
| E0GzwqkNRt2EbWvJjA60Hw | anxiety_inducing | C1, C3∧C4 | 1.021 | 0.029 | 0.912 | 1.324 | -1.541 |
| 68123473 | happy_face | C1, C3∧C4 | 1.008 | -0.029 | 0.912 | 1.371 | -1.881 |
| D50IOgoBSkCOAosH87negA | combat_vehicles | C1 | 1.116 | -0.039 | 0.877 | 1.139 | 0.645 |
| CCkWAVY9SZyZENRWRaCbQQ | anxiety_inducing | C1 | 1.057 | 0.181 | 0.425 | 1.368 | -0.998 |
| KzR2IFB3TZOI8LzfUmb0Gw | warfare | C1 | 1.054 | -0.083 | 0.722 | 0.858 | -4.350 |
| XtWPclE2Rs6IrWpB1mbQ_g | happy_event | C1 | 1.041 | -0.098 | 0.673 | 0.872 | -2.814 |
| Onhyu_ssRze6tmryDPDhcw | warfare | C1 | 1.011 | 0.142 | 0.532 | 0.743 | -2.144 |
| cdYWSf1LR1mOH4iXiIMfNQ | combat_vehicles | C1 | 1.003 | 0.167 | 0.464 | 1.187 | 1.001 |
| YaLqQjVwQz6vQerO40WDBg | sleep_related | C2 | 0.950 | -0.206 | 0.362 | 0.745 | -3.964 |
| CLZddDIORpCOa5MK6Rsc7w | warfare | C1 | 1.102 | -0.137 | 0.549 | 0.889 | -0.658 |
| 68123521 | happy_face | C1 | 1.057 | 0.088 | 0.706 | 0.995 | 1.261 |
| Dtg8yTd7QBCVthQf7oIqdg | happy_event | C1 | 1.012 | -0.309 | 0.168 | 0.571 | 0.011 |
| Byi3ZPboRuWBVDB9i8iTHA | angry_face | C2 | 0.897 | -0.425 | 0.269 | 0.887 | -0.887 |
| R0NAzO_VSdqYLe6zb_H3-Q | warfare | C2 | 0.893 | -0.327 | 0.393 | 0.454 | 0.157 |
| 68123428 | happy_face | C2 | 0.640 | 0.262 | 0.492 | 0.321 | 1.177 |
| LT6YQ4czS9Wle5QjrZ76dQ | happy_face | C2 | 0.622 | 0.157 | 0.491 | 0.542 | -0.793 |
| F-zQ4ls4SyqcPxvljy9n0Q | combat_vehicles | C2 | 0.611 | -0.312 | 0.416 | 0.514 | 1.701 |

### Flags Per Category

| Category | n_images | Flagged | C1 (CV) | C2 (ES) | C3 (skew) | C4 (BLUP) |
|----------|----------|---------|---------|---------|-----------|-----------|
| angry_face | 10 | 2 | 1 | 1 | 2 | 2 |
| anxiety_inducing | 14 | 3 | 3 | 1 | 3 | 3 |
| combat_vehicles | 8 | 4 | 3 | 1 | 3 | 2 |
| happy_event | 9 | 2 | 2 | 0 | 0 | 2 |
| happy_face | 11 | 4 | 2 | 2 | 2 | 3 |
| neutral | 50 | 0 | 0 | 0 | 0 | 0 |
| neutral_face | 13 | 0 | 0 | 0 | 0 | 0 |
| sad_face | 8 | 0 | 0 | 0 | 0 | 0 |
| sleep_related | 7 | 2 | 1 | 1 | 1 | 2 |
| soldiers | 8 | 1 | 1 | 1 | 0 | 2 |
| warfare | 12 | 4 | 3 | 1 | 1 | 3 |

## Summary & Recommendation

22/150 images (14.7%) flagged across all categories.

A moderate proportion of images are flagged. Trimming these 22 images
is recommended if the categories have enough remaining stimuli for reliable
measurement. Review category-level counts to assess impact.

## Figures

- Assumption diagnostics: `figures/images_analysis/lmm_image_quality/assumption_diagnostics.png`
- BLUP dotplot (diagnostic, angry_face): `figures/images_analysis/lmm_image_quality/blup_dotplot_angry_face.png`
- BLUP vs CV (diagnostic, angry_face): `figures/images_analysis/lmm_image_quality/blup_vs_cv_angry_face.png`
- Effect size dotplot (angry_face): `figures/images_analysis/lmm_image_quality/effect_size_dotplot_angry_face.png`
- BLUP dotplot (diagnostic, anxiety_inducing): `figures/images_analysis/lmm_image_quality/blup_dotplot_anxiety_inducing.png`
- BLUP vs CV (diagnostic, anxiety_inducing): `figures/images_analysis/lmm_image_quality/blup_vs_cv_anxiety_inducing.png`
- Effect size dotplot (anxiety_inducing): `figures/images_analysis/lmm_image_quality/effect_size_dotplot_anxiety_inducing.png`
- BLUP dotplot (diagnostic, combat_vehicles): `figures/images_analysis/lmm_image_quality/blup_dotplot_combat_vehicles.png`
- BLUP vs CV (diagnostic, combat_vehicles): `figures/images_analysis/lmm_image_quality/blup_vs_cv_combat_vehicles.png`
- Effect size dotplot (combat_vehicles): `figures/images_analysis/lmm_image_quality/effect_size_dotplot_combat_vehicles.png`
- BLUP dotplot (diagnostic, happy_event): `figures/images_analysis/lmm_image_quality/blup_dotplot_happy_event.png`
- BLUP vs CV (diagnostic, happy_event): `figures/images_analysis/lmm_image_quality/blup_vs_cv_happy_event.png`
- Effect size dotplot (happy_event): `figures/images_analysis/lmm_image_quality/effect_size_dotplot_happy_event.png`
- BLUP dotplot (diagnostic, happy_face): `figures/images_analysis/lmm_image_quality/blup_dotplot_happy_face.png`
- BLUP vs CV (diagnostic, happy_face): `figures/images_analysis/lmm_image_quality/blup_vs_cv_happy_face.png`
- Effect size dotplot (happy_face): `figures/images_analysis/lmm_image_quality/effect_size_dotplot_happy_face.png`
- BLUP dotplot (diagnostic, neutral): `figures/images_analysis/lmm_image_quality/blup_dotplot_neutral.png`
- BLUP vs CV (diagnostic, neutral): `figures/images_analysis/lmm_image_quality/blup_vs_cv_neutral.png`
- Effect size dotplot (neutral): `figures/images_analysis/lmm_image_quality/effect_size_dotplot_neutral.png`
- BLUP dotplot (diagnostic, neutral_face): `figures/images_analysis/lmm_image_quality/blup_dotplot_neutral_face.png`
- BLUP vs CV (diagnostic, neutral_face): `figures/images_analysis/lmm_image_quality/blup_vs_cv_neutral_face.png`
- Effect size dotplot (neutral_face): `figures/images_analysis/lmm_image_quality/effect_size_dotplot_neutral_face.png`
- BLUP dotplot (diagnostic, sad_face): `figures/images_analysis/lmm_image_quality/blup_dotplot_sad_face.png`
- BLUP vs CV (diagnostic, sad_face): `figures/images_analysis/lmm_image_quality/blup_vs_cv_sad_face.png`
- Effect size dotplot (sad_face): `figures/images_analysis/lmm_image_quality/effect_size_dotplot_sad_face.png`
- BLUP dotplot (diagnostic, sleep_related): `figures/images_analysis/lmm_image_quality/blup_dotplot_sleep_related.png`
- BLUP vs CV (diagnostic, sleep_related): `figures/images_analysis/lmm_image_quality/blup_vs_cv_sleep_related.png`
- Effect size dotplot (sleep_related): `figures/images_analysis/lmm_image_quality/effect_size_dotplot_sleep_related.png`
- BLUP dotplot (diagnostic, soldiers): `figures/images_analysis/lmm_image_quality/blup_dotplot_soldiers.png`
- BLUP vs CV (diagnostic, soldiers): `figures/images_analysis/lmm_image_quality/blup_vs_cv_soldiers.png`
- Effect size dotplot (soldiers): `figures/images_analysis/lmm_image_quality/effect_size_dotplot_soldiers.png`
- BLUP dotplot (diagnostic, warfare): `figures/images_analysis/lmm_image_quality/blup_dotplot_warfare.png`
- BLUP vs CV (diagnostic, warfare): `figures/images_analysis/lmm_image_quality/blup_vs_cv_warfare.png`
- Effect size dotplot (warfare): `figures/images_analysis/lmm_image_quality/effect_size_dotplot_warfare.png`

