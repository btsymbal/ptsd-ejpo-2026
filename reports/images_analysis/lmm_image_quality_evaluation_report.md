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

Images are flagged if they meet **either** of two direction-aware criteria
(applied to all categories except `neutral`, which is excluded from flagging
as a baseline/filler category with no interpretable attentional bias expectation).
Each criterion independently indicates a real failure mode — unreliability or
failure of the theoretical prediction — so either alone is sufficient to flag.

- **CV criterion**: within-PTSD-group CV >= 1.0 (within-group SD exceeds
  the mean — a scale-free indicator of substantively noisy measurement).
- **Effect size criterion**: Cohen's d / rank-biserial r from the raw
  group comparison has the unexpected sign (opposite to the category's
  theoretical direction). Magnitude is not thresholded — any wrong-direction
  effect counts, since it indicates the image drives the group difference
  opposite to its intended purpose.

**Note on BLUPs and flagging**: Earlier iterations used a direction-aware
BLUP criterion (bottom/top 20% within category, per `EXPECTED_SIGN`). On
reflection this conflated the image's overall engagement level with its
PTSD-specific response — the intercept BLUP measures only the former. A
random-slope extension `(1 + if_PTSD | image)` would give per-image PTSD
effects directly, but statsmodels' MixedLM could not reliably converge such
models here given the competing participant variance component. The effect
size criterion (Cohen's d / rank-biserial r) is already a direct, model-free
test of the theoretical direction prediction, so dropping the BLUP criterion
does not lose group-sensitive signal.

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

**Total flagged (either criterion)**: 49/150

| Image ID | Category | BLUP | CV (PTSD) | ES Type | Effect Size | p (uncorr) | Skewness |
|----------|----------|------|-----------|---------|-------------|------------|----------|
| MamyfpQXRqCkhsxuPo2UxQ | sleep_related | -1.9477 | 1.2048 | rank-biserial r | -0.1520 | 0.5035 | 1.3640 |
| fefWMtd9R8KSv7H2BTpIrw | anxiety_inducing | -2.2514 | 1.1635 | rank-biserial r | -0.2255 | 0.3178 | 0.9105 |
| 68123391 | sad_face | -1.9638 | 1.1623 | rank-biserial r | -0.1471 | 0.5165 | 1.2632 |
| QFVNirMFT5uK66NfTCL2cw | neutral_face | -3.1131 | 1.1595 | rank-biserial r | -0.2892 | 0.1959 | 0.6244 |
| WMKKOlK4QrGOs3Cn2b_lZg | soldiers | -4.8399 | 1.1310 | rank-biserial r | -0.3186 | 0.1554 | 0.3388 |
| axcFiBXmT_69RLbTxgEX_g | angry_face | -1.9732 | 1.1235 | rank-biserial r | -0.1373 | 0.5472 | 1.0020 |
| D50IOgoBSkCOAosH87negA | combat_vehicles | 0.6446 | 1.1158 | rank-biserial r | -0.0392 | 0.8768 | 1.1392 |
| CLZddDIORpCOa5MK6Rsc7w | warfare | -0.6577 | 1.1016 | rank-biserial r | -0.1373 | 0.5494 | 0.8891 |
| Jk-2DYfARdOZFHZl54GTYw | neutral_face | 0.3161 | 1.0999 | rank-biserial r | -0.4412 | 0.0485 | 1.1003 |
| E37Nm1hER9WMwQvsa2Hflw | neutral_face | -1.3823 | 1.0983 | rank-biserial r | -0.3333 | 0.1352 | 0.5664 |
| VBsOU00iTcmFmqu6o4q07A | combat_vehicles | -9.1758 | 1.0877 | rank-biserial r | 0.0245 | 0.9284 | 1.9443 |
| 68123521 | happy_face | 1.2606 | 1.0574 | rank-biserial r | 0.0882 | 0.7059 | 0.9952 |
| CCkWAVY9SZyZENRWRaCbQQ | anxiety_inducing | -0.9981 | 1.0573 | rank-biserial r | 0.1814 | 0.4248 | 1.3683 |
| KzR2IFB3TZOI8LzfUmb0Gw | warfare | -4.3504 | 1.0535 | rank-biserial r | -0.0833 | 0.7225 | 0.8580 |
| XtWPclE2Rs6IrWpB1mbQ_g | happy_event | -2.8140 | 1.0414 | rank-biserial r | -0.0980 | 0.6732 | 0.8717 |
| E0GzwqkNRt2EbWvJjA60Hw | anxiety_inducing | -1.5411 | 1.0213 | rank-biserial r | 0.0294 | 0.9118 | 1.3241 |
| Dtg8yTd7QBCVthQf7oIqdg | happy_event | 0.0111 | 1.0124 | rank-biserial r | -0.3088 | 0.1680 | 0.5715 |
| Onhyu_ssRze6tmryDPDhcw | warfare | -2.1437 | 1.0111 | rank-biserial r | 0.1422 | 0.5324 | 0.7429 |
| 68123473 | happy_face | -1.8813 | 1.0085 | rank-biserial r | -0.0294 | 0.9118 | 1.3709 |
| cdYWSf1LR1mOH4iXiIMfNQ | combat_vehicles | 1.0014 | 1.0026 | rank-biserial r | 0.1667 | 0.4639 | 1.1869 |
| C2BYNvtJTjOgDpgLvVllVQ | soldiers | 0.5979 | 0.9799 | rank-biserial r | -0.0686 | 0.7729 | 0.5186 |
| K2MSJLWFQ9SzRgId1rIUHA | neutral_face | -1.8557 | 0.9525 | rank-biserial r | 0.1765 | 0.4373 | 1.3737 |
| YaLqQjVwQz6vQerO40WDBg | sleep_related | -3.9639 | 0.9501 | rank-biserial r | -0.2059 | 0.3619 | 0.7449 |
| 68123537 | sad_face | -0.9135 | 0.8977 | Cohen's d | -0.2116 | 0.5792 | 0.4480 |
| Byi3ZPboRuWBVDB9i8iTHA | angry_face | -0.8867 | 0.8967 | Cohen's d | -0.4251 | 0.2694 | 0.8869 |
| R0NAzO_VSdqYLe6zb_H3-Q | warfare | 0.1569 | 0.8928 | Cohen's d | -0.3272 | 0.3931 | 0.4542 |
| EOpW2Zg0Sc-2GKMkPQ2J2Q | neutral_face | -0.4977 | 0.8904 | rank-biserial r | 0.0686 | 0.7734 | 0.6348 |
| OHKQX4gnTWeT_PiEr1dDeg | warfare | 1.6802 | 0.8633 | Cohen's d | -0.0862 | 0.8208 | 0.7891 |
| dhTttH-yT_6WdPoz5dAEvg | happy_event | -1.8778 | 0.8365 | rank-biserial r | 0.0931 | 0.6895 | 0.6245 |
| UpJ_d0LSQYuIKfuHLEy0PQ | anxiety_inducing | -1.3311 | 0.8299 | Cohen's d | -0.0481 | 0.8994 | 0.6655 |
| M1gYVgk3Qf2m1xK8NsXYmw | anxiety_inducing | -0.8636 | 0.8212 | rank-biserial r | -0.0588 | 0.8074 | 0.2313 |
| DnxOjrfTQhy9XTxVLuLkQA | soldiers | 2.0920 | 0.8201 | Cohen's d | -0.1079 | 0.7769 | 0.4894 |
| A_-1OArYQ_adCPIKemPHdg | soldiers | 0.3955 | 0.8064 | rank-biserial r | -0.1225 | 0.5951 | 0.7257 |
| aVGF810aT3S69s0ZSZgX2Q | neutral_face | -3.9039 | 0.7980 | rank-biserial r | 0.0343 | 0.8943 | 0.9765 |
| 68123426 | sad_face | -0.0937 | 0.7769 | Cohen's d | -0.0785 | 0.8366 | 0.8274 |
| DJw0-xR_TCaB-_LfnL6lig | sleep_related | -0.0238 | 0.7719 | Cohen's d | -0.1889 | 0.6204 | 0.7359 |
| fSG5fxkDTPeS1y7Cz44blw | neutral_face | -0.4379 | 0.6952 | rank-biserial r | 0.2745 | 0.2231 | 0.7398 |
| AV47lONxTSegnnp_qwxxYw | happy_event | -0.4340 | 0.6873 | Cohen's d | 0.2151 | 0.5730 | 0.6148 |
| Ym_NeAeOS8GjRc7sHx7leQ | neutral_face | 1.5378 | 0.6870 | Cohen's d | 0.3633 | 0.3438 | 0.3464 |
| S5f18yxeTJ227K9DSyWbjw | neutral_face | -0.4859 | 0.6689 | Cohen's d | 0.0229 | 0.9521 | -0.0173 |
| b1Q664ESSTG5H25GTXaraQ | sleep_related | -0.7035 | 0.6682 | Cohen's d | -0.2545 | 0.5054 | 0.3491 |
| cpneNStTRAyJlnfbtOB0Zg | combat_vehicles | -2.0567 | 0.6472 | Cohen's d | -0.0896 | 0.8139 | 0.1393 |
| 68123428 | happy_face | 1.1768 | 0.6397 | Cohen's d | 0.2625 | 0.4923 | 0.3206 |
| LT6YQ4czS9Wle5QjrZ76dQ | happy_face | -0.7932 | 0.6218 | rank-biserial r | 0.1569 | 0.4914 | 0.5421 |
| CHk-QJZ1ThGlvByAi3I_RQ | neutral_face | 3.6397 | 0.6185 | rank-biserial r | 0.4118 | 0.0654 | 0.8475 |
| F-zQ4ls4SyqcPxvljy9n0Q | combat_vehicles | 1.7011 | 0.6111 | Cohen's d | -0.3117 | 0.4156 | 0.5141 |
| O_0Teij0SoWKQvRhaFqWXA | anxiety_inducing | 1.2013 | 0.5653 | Cohen's d | -0.0226 | 0.9527 | 0.2076 |
| FogYThQ8Sn-ECl0o8aOcVg | happy_event | 1.1287 | 0.5298 | Cohen's d | 0.0387 | 0.9191 | -0.1206 |
| avk_faNVR-etdQf4CvXR0A | neutral_face | 4.3589 | 0.4972 | Cohen's d | 0.0941 | 0.8049 | -0.0459 |

### Flags Per Category

| Category | n_images | Flagged | CV flags | ES flags |
|----------|----------|---------|----------|----------|
| angry_face | 10 | 2 | 1 | 2 |
| anxiety_inducing | 14 | 6 | 3 | 4 |
| combat_vehicles | 8 | 5 | 3 | 3 |
| happy_event | 9 | 5 | 2 | 3 |
| happy_face | 11 | 4 | 2 | 3 |
| neutral | 50 | 0 | 0 | 0 |
| neutral_face | 13 | 11 | 3 | 8 |
| sad_face | 8 | 3 | 1 | 3 |
| sleep_related | 7 | 4 | 1 | 4 |
| soldiers | 8 | 4 | 1 | 4 |
| warfare | 12 | 5 | 3 | 4 |

## Summary & Recommendation

49/150 images (32.7%) flagged across all categories.

A substantial proportion of images (32.7%) are flagged. This may
indicate broader issues with the paradigm design or population variability
rather than individual image quality. Trimming alone may not suffice.

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

