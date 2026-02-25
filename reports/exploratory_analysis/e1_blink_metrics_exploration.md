# E1: Exploratory Analysis of Blink Metrics in PTSD vs No-PTSD Groups

## 1. Motivation

The preanalysis overview ([blink_metrics_overview_report](../preanalysis_overview/blink_metrics_overview_report.md)) identified two key challenges for blink-based hypothesis testing:

1. **Structural missingness**: Blink duration, std blink duration, and blink latency columns have category-level missingness (n = 14–26 depending on category), because sessions with zero blinks in a category produce undefined duration/latency values.

2. **High intercorrelations**: Per-category blink rates are near-redundant (r = 0.43–0.97, median ~0.85), and per-category blink durations are similarly correlated (r = 0.51–1.00). This limits the information gained from testing each category separately.

Based on these findings, we selected 8 metrics for exploratory analysis: 4 global blink summaries (complete data, no missingness) and 4 per-category blink rates for the threat stimulus categories. This is an **exploratory analysis (E1)**, not a confirmatory hypothesis test.

## 2. Method

### Participants

- **Total**: N = 26 (from the blink-clean dataset, after removing 4 sessions for poor quality or extreme blink counts)
- **PTSD group**: n = 15
- **No-PTSD group**: n = 11

### Variables

**Dependent variables (8 metrics):**

| Family | Metrics | N tests |
|--------|---------|---------|
| F1: Blink Count & Interval | total_blink_count, mean_blink_interval_norm | 2 |
| F2: Blink Duration | mean_blink_duration_ms | 1 |
| F3: Interval Variability | std_blink_interval_norm | 1 |
| F4: Blink Rate (Threat) | mean_blink_rate × {angry_face, anxiety_inducing, warfare, soldiers} | 4 |

**Independent variable (Part B):** ITI_PTSD (continuous PTSD severity score, within PTSD group only)

### Analysis Approach

- **Part A**: Group comparisons (PTSD vs No-PTSD) — test selection based on Shapiro-Wilk normality + Levene's variance equality
- **Part B**: Within-PTSD correlational analysis (ITI_PTSD as IV) — Pearson or Kendall based on normality + outlier checks
- **Multiple comparisons**: BH-FDR correction applied separately within each family, separately for Parts A and B

## 3. Part A: Group Comparisons (PTSD vs No-PTSD)

### Descriptive Statistics

| Metric | Group | n | Mean | SD | Median |
|--------|-------|---|------|----|--------|
| total_blink_count | PTSD | 15 | 28.67 | 18.04 | 24.00 |
| total_blink_count | No-PTSD | 11 | 16.09 | 8.80 | 16.00 |
| mean_blink_interval_norm | PTSD | 15 | 4.97 | 2.80 | 4.60 |
| mean_blink_interval_norm | No-PTSD | 11 | 6.54 | 3.48 | 5.58 |
| mean_blink_duration_ms | PTSD | 15 | 81.34 | 36.03 | 65.41 |
| mean_blink_duration_ms | No-PTSD | 11 | 96.19 | 32.64 | 96.09 |
| std_blink_interval_norm | PTSD | 15 | 4.61 | 2.11 | 4.28 |
| std_blink_interval_norm | No-PTSD | 11 | 5.62 | 2.80 | 4.56 |
| mean_blink_rate_angry_face | PTSD | 15 | 0.37 | 0.34 | 0.30 |
| mean_blink_rate_angry_face | No-PTSD | 11 | 0.21 | 0.18 | 0.30 |
| mean_blink_rate_anxiety_inducing | PTSD | 15 | 0.34 | 0.24 | 0.36 |
| mean_blink_rate_anxiety_inducing | No-PTSD | 11 | 0.18 | 0.18 | 0.14 |
| mean_blink_rate_warfare | PTSD | 15 | 0.47 | 0.36 | 0.42 |
| mean_blink_rate_warfare | No-PTSD | 11 | 0.27 | 0.14 | 0.25 |
| mean_blink_rate_soldiers | PTSD | 15 | 0.34 | 0.24 | 0.25 |
| mean_blink_rate_soldiers | No-PTSD | 11 | 0.18 | 0.20 | 0.13 |

### Assumption Checks

| Metric | Shapiro PTSD p | Shapiro No-PTSD p | Both Normal | Levene p | Equal Var |
|--------|---------------|-------------------|-------------|----------|-----------|
| total_blink_count | 0.103 | 0.278 | Yes | 0.095 | Yes |
| mean_blink_interval_norm | 0.073 | 0.220 | Yes | 0.328 | Yes |
| mean_blink_duration_ms | 0.051 | 0.139 | Yes | 0.985 | Yes |
| std_blink_interval_norm | 0.076 | 0.115 | Yes | 0.435 | Yes |
| mean_blink_rate_angry_face | 0.026 | 0.049 | No | 0.256 | Yes |
| mean_blink_rate_anxiety_inducing | 0.046 | 0.036 | No | 0.414 | Yes |
| mean_blink_rate_warfare | 0.012 | 0.182 | No | 0.113 | Yes |
| mean_blink_rate_soldiers | 0.178 | 0.015 | No | 0.943 | Yes |

Global metrics (F1–F3) met normality assumptions (parametric t-tests). All four blink rate metrics (F4) violated normality in at least one group (non-parametric Mann-Whitney U).

### Results

| Family | Metric | Test | Statistic | p (uncorr.) | p (BH) | Effect Size | 95% CI | Sig. |
|--------|--------|------|-----------|-------------|---------|-------------|--------|------|
| F1 | total_blink_count | Student's t | 2.125 | 0.044 | 0.088 | d = 0.84 | [-0.56, 2.25] | No |
| F1 | mean_blink_interval_norm | Student's t | -1.278 | 0.214 | 0.214 | d = -0.51 | [-1.56, 0.54] | No |
| F2 | mean_blink_duration_ms | Student's t | -1.079 | 0.291 | 0.291 | d = -0.43 | [-1.41, 0.55] | No |
| F3 | std_blink_interval_norm | Student's t | -1.059 | 0.300 | 0.300 | d = -0.42 | [-1.39, 0.55] | No |
| F4 | mean_blink_rate_angry_face | Mann-Whitney U | 103.5 | 0.278 | 0.278 | r = -0.25 | [-0.58, 0.15] | No |
| F4 | mean_blink_rate_anxiety_inducing | Mann-Whitney U | 119.5 | 0.056 | 0.128 | r = -0.45 | [-0.71, -0.07] | No |
| F4 | mean_blink_rate_warfare | Mann-Whitney U | 116.0 | 0.084 | 0.128 | r = -0.41 | [-0.69, -0.02] | No |
| F4 | mean_blink_rate_soldiers | Mann-Whitney U | 114.5 | 0.096 | 0.128 | r = -0.39 | [-0.67, -0.00] | No |

**No significant group differences** after BH-FDR correction at alpha = 0.05.

### Figures

![Violin + Strip: Global Metrics](../../figures/e1_blink_metrics_exploration/violin_strip_global.png)

![Violin + Strip: Blink Rate](../../figures/e1_blink_metrics_exploration/violin_strip_blink_rate.png)

![Forest Plot: Effect Sizes](../../figures/e1_blink_metrics_exploration/forest_plot_part_a.png)

![Bar Chart: Group Means](../../figures/e1_blink_metrics_exploration/bar_chart_part_a.png)

## 4. Part B: Correlational Analysis (within PTSD group)

### Sample

- PTSD group only: n = 15
- IV: ITI_PTSD (Shapiro-Wilk W = 0.830, p = 0.009 — non-normal)

Because ITI_PTSD is non-normal (p = 0.009), all correlations default to Kendall's tau_b regardless of DV normality.

### Assumption Checks

| Metric | Shapiro DV p | DV Normal | Both Normal | N Outliers | Use Pearson |
|--------|-------------|-----------|-------------|------------|-------------|
| total_blink_count | 0.103 | Yes | No | 0 | No |
| mean_blink_interval_norm | 0.073 | Yes | No | 0 | No |
| mean_blink_duration_ms | 0.051 | Yes | No | 0 | No |
| std_blink_interval_norm | 0.076 | Yes | No | 0 | No |
| mean_blink_rate_angry_face | 0.026 | No | No | 0 | No |
| mean_blink_rate_anxiety_inducing | 0.046 | No | No | 0 | No |
| mean_blink_rate_warfare | 0.012 | No | No | 0 | No |
| mean_blink_rate_soldiers | 0.178 | Yes | No | 0 | No |

No outliers detected (|z_resid| > 3) for any metric pair.

### Results

| Family | Metric | Test | Coefficient | p (uncorr.) | p (BH) | 95% CI | Sig. |
|--------|--------|------|-------------|-------------|---------|--------|------|
| F1 | total_blink_count | Kendall's tau_b | 0.051 | 0.800 | 0.960 | [-0.48, 0.57] | No |
| F1 | mean_blink_interval_norm | Kendall's tau_b | -0.010 | 0.960 | 0.960 | [-0.52, 0.51] | No |
| F2 | mean_blink_duration_ms | Kendall's tau_b | -0.374 | 0.062 | 0.062 | [-0.71, 0.00] | No |
| F3 | std_blink_interval_norm | Kendall's tau_b | 0.172 | 0.391 | 0.391 | [-0.20, 0.53] | No |
| F4 | mean_blink_rate_angry_face | Kendall's tau_b | 0.043 | 0.837 | 0.837 | [-0.46, 0.53] | No |
| F4 | mean_blink_rate_anxiety_inducing | Kendall's tau_b | 0.245 | 0.238 | 0.809 | [-0.30, 0.75] | No |
| F4 | mean_blink_rate_warfare | Kendall's tau_b | 0.159 | 0.443 | 0.809 | [-0.33, 0.65] | No |
| F4 | mean_blink_rate_soldiers | Kendall's tau_b | 0.108 | 0.607 | 0.809 | [-0.41, 0.59] | No |

**No significant correlations** after BH-FDR correction at alpha = 0.05.

### Figures

![Scatter Plots](../../figures/e1_blink_metrics_exploration/scatterplots_part_b.png)

![Forest Plot: Correlations](../../figures/e1_blink_metrics_exploration/forest_plot_part_b.png)

## 5. Summary & Interpretation

### Key Findings

1. **No significant group differences** were found between PTSD and No-PTSD groups for any of the 8 blink metrics after BH-FDR correction.

2. **No significant correlations** between ITI_PTSD severity and blink metrics were found within the PTSD group.

3. **Trend-level observations** (exploratory, not confirmatory):
   - Total blink count showed the largest group effect (d = 0.84, p_uncorr = 0.044), with the PTSD group blinking more frequently (M = 28.7 vs 16.1). This did not survive FDR correction within the F1 family.
   - Per-category blink rates for threat stimuli showed consistent small-to-medium effects (r = -0.25 to -0.45) suggesting higher blink rates in the PTSD group across all 4 threat categories, though none reached significance after correction.
   - Mean blink duration showed a trend-level negative correlation with ITI_PTSD (tau = -0.37, p_uncorr = 0.062), suggesting higher-severity PTSD may be associated with shorter blinks.

### Caveats

- **Small sample size**: With n = 26 total (15 PTSD, 11 No-PTSD) and n = 15 for correlational analyses, statistical power is severely limited. Many of the observed effect sizes are medium-to-large but confidence intervals are wide and cross zero.
- **Multiple comparisons**: 8 tests per analysis type across 4 families. Even with BH-FDR correction within families, the exploratory nature of this analysis means results should be treated as hypothesis-generating.
- **Non-normal distributions**: All blink rate metrics and the IV (ITI_PTSD) violated normality, requiring non-parametric tests which have lower power with small samples.
- **High intercorrelation of blink rates**: As documented in the preanalysis overview (r = 0.43–0.97), per-category blink rates are largely redundant. The consistent direction of effects across threat categories likely reflects individual-differences in overall blink rate rather than category-specific stimulus responses.
- **Blink detection limitations**: The sample median blink rate (6.0 blinks/min) is well below typical adult rates (15–20/min), suggesting possible under-detection by the eye tracker or task-induced blink suppression.

---

**Report Generated**: 2026-02-25
**Analysis Code**: `exploratory_analysis/e1_blink_metrics_exploration.py`
**Figures**: `figures/e1_blink_metrics_exploration/` (6 PNGs)
