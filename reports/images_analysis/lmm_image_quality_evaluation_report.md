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
4. **Linear Mixed Models (LMM)**: the central analysis, fitting
   `dwell_pct ~ if_PTSD + (1|participant) + (1|image)` separately per category
   using REML estimation. Image-level BLUPs (Best Linear Unbiased Predictors)
   capture each image's deviation from the category mean after controlling for
   group and participant variability.

Images are flagged if they meet two or more of three direction-aware criteria:

- **BLUP criterion**: bottom 20% for positive-expected categories (weak stimuli)
  or top 20% for negative-expected categories (counteracting expected avoidance)
- **CV criterion**: top 20% within-PTSD-group CV (noisy measurement)
- **Effect size criterion**: near-zero (|ES| < 0.1) or unexpected-direction effect

### Expected Directions

| Category | Expected sign | Rationale |
|----------|---------------|-----------|
| angry_face | positive | hypervigilance to threat |
| anxiety_inducing | positive | hypervigilance to potential (hidden) threat |
| combat_vehicles | positive | emotionally driven memories |
| happy_event | negative | anhedonistic subtype |
| happy_face | negative | anhedonistic subtype |
| neutral | — | no consistent pattern (paired with diverse images) |
| neutral_face | negative | hypervigilance to threat (opposite image) |
| sad_face | positive | anhedonistic subtype (opposite image) |
| sleep_related | — | no strong theoretical expectation |
| soldiers | positive | hypervigilance to threat |
| warfare | positive | hypervigilance to threat |

## LMM Results Per Category

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

**Total flagged (2+ criteria)**: 26/150

| Image ID | Category | BLUP | CV (PTSD) | ES Type | Effect Size | p (uncorr) | Skewness | Criteria Met |
|----------|----------|------|-----------|---------|-------------|------------|----------|--------------|
| [fefWMtd9R8KSv7H2BTpIrw](../../materials/stimuli/fefWMtd9R8KSv7H2BTpIrw.png) | anxiety_inducing | -2.2514 | 1.1635 | rank-biserial r | -0.2255 | 0.3178 | 0.9105 | BLUP, CV, ES |
| [68123391](../../materials/stimuli/68123391.png) | sad_face | -1.9638 | 1.1623 | rank-biserial r | -0.1471 | 0.5165 | 1.2632 | BLUP, CV, ES |
| [WMKKOlK4QrGOs3Cn2b_lZg](../../materials/stimuli/WMKKOlK4QrGOs3Cn2b_lZg.png) | soldiers | -4.8399 | 1.1310 | rank-biserial r | -0.3186 | 0.1554 | 0.3388 | BLUP, CV, ES |
| [axcFiBXmT_69RLbTxgEX_g](../../materials/stimuli/axcFiBXmT_69RLbTxgEX_g.png) | angry_face | -1.9732 | 1.1235 | rank-biserial r | -0.1373 | 0.5472 | 1.0020 | BLUP, CV, ES |
| [68123521](../../materials/stimuli/68123521.png) | happy_face | 1.2606 | 1.0574 | rank-biserial r | 0.0882 | 0.7059 | 0.9952 | BLUP, CV, ES |
| [KzR2IFB3TZOI8LzfUmb0Gw](../../materials/stimuli/KzR2IFB3TZOI8LzfUmb0Gw.png) | warfare | -4.3504 | 1.0535 | rank-biserial r | -0.0833 | 0.7225 | 0.8580 | BLUP, CV, ES |
| [dIsJdajoT4msRkkJ_zfW3w](../../materials/stimuli/dIsJdajoT4msRkkJ_zfW3w.png) | sleep_related | -0.5619 | 0.9525 | rank-biserial r | 0.0882 | 0.7059 | 0.9102 | BLUP, CV, ES |
| [ScZovXGJRdO257M1YbYzOw](../../materials/stimuli/ScZovXGJRdO257M1YbYzOw.png) | neutral | -1.1700 | 1.2360 | rank-biserial r | -0.0686 | 0.7673 | 1.2848 | CV, ES |
| [YMjbkdnMSqilocbDaFK_lQ](../../materials/stimuli/YMjbkdnMSqilocbDaFK_lQ.png) | neutral | -0.8795 | 1.1993 | rank-biserial r | -0.0196 | 0.9467 | 1.2554 | CV, ES |
| [aX7_5eB-SruGeFTptfKWlw](../../materials/stimuli/aX7_5eB-SruGeFTptfKWlw.png) | neutral | -0.1690 | 1.1499 | rank-biserial r | -0.1471 | 0.5198 | 1.1261 | BLUP, CV |
| [RriA_iA-T8CtzcT6pDhKcA](../../materials/stimuli/RriA_iA-T8CtzcT6pDhKcA.png) | neutral | -0.7807 | 1.1279 | rank-biserial r | 0.0343 | 0.8938 | 0.8764 | CV, ES |
| [D50IOgoBSkCOAosH87negA](../../materials/stimuli/D50IOgoBSkCOAosH87negA.png) | combat_vehicles | 0.6446 | 1.1158 | rank-biserial r | -0.0392 | 0.8768 | 1.1392 | CV, ES |
| [a5wTdTZzRBWI8S5rtGpSnw](../../materials/stimuli/a5wTdTZzRBWI8S5rtGpSnw.png) | neutral | -1.5757 | 1.1037 | rank-biserial r | 0.0490 | 0.8414 | 1.5358 | CV, ES |
| [CLZddDIORpCOa5MK6Rsc7w](../../materials/stimuli/CLZddDIORpCOa5MK6Rsc7w.png) | warfare | -0.6577 | 1.1016 | rank-biserial r | -0.1373 | 0.5494 | 0.8891 | CV, ES |
| [VBsOU00iTcmFmqu6o4q07A](../../materials/stimuli/VBsOU00iTcmFmqu6o4q07A.png) | combat_vehicles | -9.1758 | 1.0877 | rank-biserial r | 0.0245 | 0.9284 | 1.9443 | BLUP, CV |
| [E0GzwqkNRt2EbWvJjA60Hw](../../materials/stimuli/E0GzwqkNRt2EbWvJjA60Hw.png) | anxiety_inducing | -1.5411 | 1.0213 | rank-biserial r | 0.0294 | 0.9118 | 1.3241 | BLUP, CV |
| [Onhyu_ssRze6tmryDPDhcw](../../materials/stimuli/Onhyu_ssRze6tmryDPDhcw.png) | warfare | -2.1437 | 1.0111 | rank-biserial r | 0.1422 | 0.5324 | 0.7429 | BLUP, CV |
| [aFt8UlJUS7WAxa3lTutG-g](../../materials/stimuli/aFt8UlJUS7WAxa3lTutG-g.png) | neutral | 0.1284 | 0.9847 | rank-biserial r | 0.0931 | 0.6899 | 0.9749 | BLUP, ES |
| [68123524](../../materials/stimuli/68123524.png) | sad_face | -1.2294 | 0.9662 | rank-biserial r | 0.0833 | 0.7228 | 1.0181 | BLUP, CV |
| [Byi3ZPboRuWBVDB9i8iTHA](../../materials/stimuli/Byi3ZPboRuWBVDB9i8iTHA.png) | angry_face | -0.8867 | 0.8967 | Cohen's d | -0.4251 | 0.2694 | 0.8869 | CV, ES |
| [UhDwyHuQSByzKUI5ODt3BA](../../materials/stimuli/UhDwyHuQSByzKUI5ODt3BA.png) | neutral | 0.0890 | 0.8391 | rank-biserial r | 0.0882 | 0.7062 | 1.8016 | BLUP, ES |
| [Ym_NeAeOS8GjRc7sHx7leQ](../../materials/stimuli/Ym_NeAeOS8GjRc7sHx7leQ.png) | neutral_face | 1.5378 | 0.6870 | Cohen's d | 0.3633 | 0.3438 | 0.3464 | BLUP, ES |
| [cpneNStTRAyJlnfbtOB0Zg](../../materials/stimuli/cpneNStTRAyJlnfbtOB0Zg.png) | combat_vehicles | -2.0567 | 0.6472 | Cohen's d | -0.0896 | 0.8139 | 0.1393 | BLUP, ES |
| [68123428](../../materials/stimuli/68123428.png) | happy_face | 1.1768 | 0.6397 | Cohen's d | 0.2625 | 0.4923 | 0.3206 | BLUP, ES |
| [CHk-QJZ1ThGlvByAi3I_RQ](../../materials/stimuli/CHk-QJZ1ThGlvByAi3I_RQ.png) | neutral_face | 3.6397 | 0.6185 | rank-biserial r | 0.4118 | 0.0654 | 0.8475 | BLUP, ES |
| [avk_faNVR-etdQf4CvXR0A](../../materials/stimuli/avk_faNVR-etdQf4CvXR0A.png) | neutral_face | 4.3589 | 0.4972 | Cohen's d | 0.0941 | 0.8049 | -0.0459 | BLUP, ES |

### Flags Per Category

| Category | n_images | Flagged | BLUP flags | CV flags | ES flags |
|----------|----------|---------|------------|----------|----------|
| angry_face | 10 | 2 | 2 | 2 | 2 |
| anxiety_inducing | 14 | 2 | 3 | 3 | 4 |
| combat_vehicles | 8 | 3 | 2 | 2 | 3 |
| happy_event | 9 | 0 | 2 | 2 | 3 |
| happy_face | 11 | 2 | 3 | 3 | 3 |
| neutral | 50 | 7 | 10 | 10 | 16 |
| neutral_face | 13 | 3 | 3 | 3 | 8 |
| sad_face | 8 | 2 | 2 | 2 | 3 |
| sleep_related | 7 | 1 | 2 | 2 | 1 |
| soldiers | 8 | 1 | 2 | 2 | 4 |
| warfare | 12 | 3 | 3 | 3 | 4 |

## Summary & Recommendation

26/150 images (17.3%) flagged across all categories.

A moderate proportion of images are flagged. Trimming these 26 images
is recommended if the categories have enough remaining stimuli for reliable
measurement. Review category-level counts to assess impact.

## Figures

- Assumption diagnostics: `figures/images_analysis/lmm_image_quality/assumption_diagnostics.png`
- BLUP dotplot (angry_face): `figures/images_analysis/lmm_image_quality/blup_dotplot_angry_face.png`
- BLUP vs CV (angry_face): `figures/images_analysis/lmm_image_quality/blup_vs_cv_angry_face.png`
- Effect size dotplot (angry_face): `figures/images_analysis/lmm_image_quality/effect_size_dotplot_angry_face.png`
- BLUP dotplot (anxiety_inducing): `figures/images_analysis/lmm_image_quality/blup_dotplot_anxiety_inducing.png`
- BLUP vs CV (anxiety_inducing): `figures/images_analysis/lmm_image_quality/blup_vs_cv_anxiety_inducing.png`
- Effect size dotplot (anxiety_inducing): `figures/images_analysis/lmm_image_quality/effect_size_dotplot_anxiety_inducing.png`
- BLUP dotplot (combat_vehicles): `figures/images_analysis/lmm_image_quality/blup_dotplot_combat_vehicles.png`
- BLUP vs CV (combat_vehicles): `figures/images_analysis/lmm_image_quality/blup_vs_cv_combat_vehicles.png`
- Effect size dotplot (combat_vehicles): `figures/images_analysis/lmm_image_quality/effect_size_dotplot_combat_vehicles.png`
- BLUP dotplot (happy_event): `figures/images_analysis/lmm_image_quality/blup_dotplot_happy_event.png`
- BLUP vs CV (happy_event): `figures/images_analysis/lmm_image_quality/blup_vs_cv_happy_event.png`
- Effect size dotplot (happy_event): `figures/images_analysis/lmm_image_quality/effect_size_dotplot_happy_event.png`
- BLUP dotplot (happy_face): `figures/images_analysis/lmm_image_quality/blup_dotplot_happy_face.png`
- BLUP vs CV (happy_face): `figures/images_analysis/lmm_image_quality/blup_vs_cv_happy_face.png`
- Effect size dotplot (happy_face): `figures/images_analysis/lmm_image_quality/effect_size_dotplot_happy_face.png`
- BLUP dotplot (neutral): `figures/images_analysis/lmm_image_quality/blup_dotplot_neutral.png`
- BLUP vs CV (neutral): `figures/images_analysis/lmm_image_quality/blup_vs_cv_neutral.png`
- Effect size dotplot (neutral): `figures/images_analysis/lmm_image_quality/effect_size_dotplot_neutral.png`
- BLUP dotplot (neutral_face): `figures/images_analysis/lmm_image_quality/blup_dotplot_neutral_face.png`
- BLUP vs CV (neutral_face): `figures/images_analysis/lmm_image_quality/blup_vs_cv_neutral_face.png`
- Effect size dotplot (neutral_face): `figures/images_analysis/lmm_image_quality/effect_size_dotplot_neutral_face.png`
- BLUP dotplot (sad_face): `figures/images_analysis/lmm_image_quality/blup_dotplot_sad_face.png`
- BLUP vs CV (sad_face): `figures/images_analysis/lmm_image_quality/blup_vs_cv_sad_face.png`
- Effect size dotplot (sad_face): `figures/images_analysis/lmm_image_quality/effect_size_dotplot_sad_face.png`
- BLUP dotplot (sleep_related): `figures/images_analysis/lmm_image_quality/blup_dotplot_sleep_related.png`
- BLUP vs CV (sleep_related): `figures/images_analysis/lmm_image_quality/blup_vs_cv_sleep_related.png`
- Effect size dotplot (sleep_related): `figures/images_analysis/lmm_image_quality/effect_size_dotplot_sleep_related.png`
- BLUP dotplot (soldiers): `figures/images_analysis/lmm_image_quality/blup_dotplot_soldiers.png`
- BLUP vs CV (soldiers): `figures/images_analysis/lmm_image_quality/blup_vs_cv_soldiers.png`
- Effect size dotplot (soldiers): `figures/images_analysis/lmm_image_quality/effect_size_dotplot_soldiers.png`
- BLUP dotplot (warfare): `figures/images_analysis/lmm_image_quality/blup_dotplot_warfare.png`
- BLUP vs CV (warfare): `figures/images_analysis/lmm_image_quality/blup_vs_cv_warfare.png`
- Effect size dotplot (warfare): `figures/images_analysis/lmm_image_quality/effect_size_dotplot_warfare.png`

