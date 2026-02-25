# Blink Metrics Overview Report (Blink-Clean Dataset)

## 1. Dataset Overview

The blink-clean eye-tracking dataset contains **26 sessions × 134 columns**. Column types: 131 float64, 2 int64, and 1 object (session_id).

### Removed Sessions

Four sessions were removed from the original 30-session dataset:

| Session | Reason | Detail |
|---|---|---|
| UgMWkyrkRYVZ9cr9thRw | Poor gaze quality | 8.0% usable slides |
| DTGxc0RwsWrTMRKpenb8 | Extreme high blink count | 217 blinks (72.5/min), 12 IQR flags |
| RBRGZzWIzDitollqkpzW | Very low blink count | 7 total blinks |
| xn3yMJ8STzchnQPg94lH | Very low blink count | 4 total blinks |

### Blink Column Groups

| Group | Count | Description |
|---|---|---|
| global_blink | 4 | total_blink_count, mean_blink_duration_ms, mean/std_blink_interval_norm |
| mean_blink_rate | 11 | Mean blinks per slide for each image category |
| mean_blink_duration | 11 | Mean blink duration per category (ms) |
| std_blink_duration | 11 | Within-session variability of blink duration |
| mean_blink_latency_norm | 11 | Normalized latency to first blink per category |
| metadata | 5 | session_id, if_PTSD, ITI_PTSD, ITI_cPTSD, if_antipsychotic |

**Total blink columns: 48** (plus 5 metadata)

### Missingness

Blink duration, std blink duration, and blink latency columns have structural missingness — some sessions produce zero blinks in certain categories, making duration and latency undefined. NaN counts range from 2 (anxiety_inducing, sad_face) to 12 (combat_vehicles, sleep_related for std_blink_duration). Blink rate and global blink columns are complete across all 26 sessions.

## 2. Metadata

### Group Counts

| Variable | Group | n |
|---|---|---|
| if_PTSD | Non-PTSD | 11 |
| if_PTSD | PTSD | 15 |
| if_antipsychotic | No | 15 |
| if_antipsychotic | Yes | 11 |

### ITI Scores (PTSD group only, n = 15)

| Metric | Mean | Median | SD | Min | Max | Zero count |
|---|---|---|---|---|---|---|
| ITI_PTSD | 12.87 | 12.00 | 3.14 | 10.0 | 19.0 | 0 |
| ITI_cPTSD | 7.73 | 9.00 | 4.46 | 0.0 | 14.0 | 3 |

After removing 2 PTSD participants (DTGxc0RwsWrTMRKpenb8, xn3yMJ8STzchnQPg94lH) and 2 non-PTSD participants (UgMWkyrkRYVZ9cr9thRw, RBRGZzWIzDitollqkpzW), the PTSD group retains 15 of 17 original participants. ITI scores are slightly higher than the original sample means (ITI_PTSD: 12.87 vs. 12.65; ITI_cPTSD: 7.73 vs. 7.35), consistent with removal of lower-scoring participants. Zero-count for ITI_cPTSD decreased from 4 to 3.

![Metadata Overview](../../figures/blink_metrics_overview/metadata_overview.png)

## 3. Descriptive Statistics

### Global Blink Metrics

| Metric | n | Mean | Median | SD | Skewness | Kurtosis | Shapiro p |
|---|---|---|---|---|---|---|---|
| total_blink_count | 26 | 23.3 | 18.0 | 15.9 | 1.43 | 1.90 | 0.002 |
| mean_blink_duration_ms | 26 | 87.6 | 78.9 | 34.8 | -0.10 | -1.13 | 0.012 |
| mean_blink_interval_norm | 26 | 5.64 | 4.78 | 3.14 | 0.77 | -0.57 | 0.016 |
| std_blink_interval_norm | 26 | 5.04 | 4.32 | 2.43 | 0.89 | -0.36 | 0.007 |

All four global blink metrics fail the Shapiro-Wilk test at p < 0.05. Total blink count remains right-skewed (skewness 1.43) despite removal of the extreme 217-blink session. The blink interval metrics are moderately right-skewed. Mean blink duration is platykurtic but approximately symmetric.

![Global Blink Histograms](../../figures/blink_metrics_overview/hist_global_blink.png)

### Mean Blink Rate by Category

Per-category blink rates are right-skewed across all 11 categories (skewness 0.41–2.09). All fail the Shapiro-Wilk test (p < 0.035), with warfare showing the most extreme skewness (2.09, Shapiro p < 0.001). Means range from 0.24 (combat_vehicles) to 0.46 (sad_face) blinks per slide. The distributions remain zero-inflated even after cleaning: many sessions have very low blink rates per slide.

Compared to the original 30-session dataset, the removal of the 3 extreme blink sessions reduced the maximum blink rate substantially (e.g., warfare max dropped from ~3.42 to 1.50) but did not normalize the distributions.

![Blink Rate Histograms](../../figures/blink_metrics_overview/hist_mean_blink_rate.png)

### Mean Blink Duration by Category

Blink durations show substantial missingness (n = 19–26 depending on category). Means cluster around 78–91 ms, consistent with a typical adult blink duration range. Distributions are roughly symmetric (skewness near 0) but platykurtic (kurtosis -0.8 to -1.5), reflecting a flattened distribution across the range. Most categories fail the Shapiro-Wilk test (p < 0.05), with only sad_face approaching normality (p = 0.051).

![Blink Duration Histograms](../../figures/blink_metrics_overview/hist_mean_blink_duration.png)

### Std Blink Duration by Category

Within-session blink duration variability is heavily right-skewed across all categories (skewness 0.68–1.96). All fail the Shapiro-Wilk test (p < 0.01). Means range from 6.1 (angry_face) to 23.5 (sad_face) ms. Many sessions have zero or near-zero variability (only 1 blink in that category), driving the right skew.

![Std Blink Duration Histograms](../../figures/blink_metrics_overview/hist_std_blink_duration.png)

### Mean Blink Latency (Normalized) by Category

Blink latency is the most well-behaved blink family. All 11 categories pass the Shapiro-Wilk test (p > 0.12). Means cluster around 0.44–0.54 (dimensionless ratios of latency to slide duration). Distributions are approximately symmetric with moderate variability (SD 0.14–0.29). Missingness ranges from 0 (warfare, happy_face, neutral) to 7 (angry_face).

![Blink Latency Histograms](../../figures/blink_metrics_overview/hist_mean_blink_latency_norm.png)

## 4. Distributional Observations

The blink metrics fall into three distributional regimes:

1. **Approximately normal**: Mean blink latency (normalized) — all 11 categories pass Shapiro-Wilk. Suitable for parametric tests, though reduced n due to missingness.

2. **Severely right-skewed**: Total blink count, per-category blink rate, blink interval (normalized), and std blink duration. All fail normality tests. Require non-parametric tests (Mann-Whitney U) or log-transformation.

3. **Platykurtic / mildly non-normal**: Mean blink duration by category — approximately symmetric but with flattened distributions. Parametric tests may be acceptable with caution.

## 5. Outlier Detection

### Univariate IQR Flags

Across all 48 blink columns, 14 of 26 sessions had at least one IQR flag. Top flagged sessions:

**9Pd2lTJaNZ7CGrLBPjuU (10 flags)**: The top outlier in the cleaned dataset, with high total blink count (73) and high blink rates across 7 categories (angry_face = 1.30, warfare = 1.50 blinks/slide). Also flagged on 2 std_blink_duration columns. This is a high-blink participant, not a data quality issue.

**Y20f3G9ulPHmbLwFS3JL (5 flags)**: High blink rates in 4 categories (anxiety_inducing, happy_event, neutral, sleep_related) and high std_blink_duration_sleep_related.

**DAccofkFpBK00oVonRAi (4 flags)**: High std_blink_duration in 3 face categories and low blink latency on neutral (0.11).

**R1h2U5EvesqWzc3ADps6 (3 flags)**: High blink rate (happy_event) and high std_blink_duration in 2 face categories.

12 of 26 sessions had zero flags.

### Outlier Box Plots

![Global Blink Box Plots](../../figures/blink_metrics_overview/outlier_boxplot_global_blink.png)

![Blink Rate Box Plots](../../figures/blink_metrics_overview/outlier_boxplot_blink_rate.png)

![Blink Duration Box Plots](../../figures/blink_metrics_overview/outlier_boxplot_blink_duration.png)

![Std Blink Duration Box Plots](../../figures/blink_metrics_overview/outlier_boxplot_std_blink_duration.png)

![Blink Latency Box Plots](../../figures/blink_metrics_overview/outlier_boxplot_blink_latency.png)

### Multivariate Mahalanobis Distance

Mahalanobis distances were computed for the blink metrics subspace (rate + interval + duration, 14 variables). No sessions exceeded the chi-squared critical threshold (crit = 5.40, p < 0.01). The range was 2.38–4.39, with 9Pd2lTJaNZ7CGrLBPjuU at the top.

Blink duration and blink latency subspaces could not be tested (only 11 complete cases for 11 variables — insufficient for Mahalanobis).

## 6. Correlation Structure

With n = 26, the critical values for Pearson r are |r| >= 0.388 (p < 0.05) and |r| >= 0.496 (p < 0.01).

### Blink Rate

Per-category blink rates show very high intercorrelations (range 0.43–0.97), all significant at p < 0.05. 51 of 55 pairs reach p < 0.01; the four at p < 0.05 only involve combat_vehicles-sleep_related (r = 0.43), anxiety_inducing-happy_face (r = 0.49), happy_event-sad_face (r = 0.44), and happy_face-soldiers (r = 0.49). The near-unity correlations confirm that blink rate is dominated by an individual-differences trait rather than category-specific effects.

![Blink Rate Correlation Heatmap](../../figures/blink_metrics_overview/corr_blink_rate.png)

### Blink Duration

Per-category blink durations show very high intercorrelations (range 0.51–1.00), all significant at p < 0.01. This indicates blink duration is also strongly trait-driven, though with slightly more category-specific variation than blink rate.

![Blink Duration Correlation Heatmap](../../figures/blink_metrics_overview/corr_blink_duration.png)

### Blink Latency (Normalized)

Blink latency correlations are notably weaker (range 0.05–0.99). Only 43 of 55 pairs are significant at p < 0.05, and 33 at p < 0.01. This suggests blink latency carries more category-specific information than blink rate or duration — the timing of the first blink may be influenced by stimulus content.

![Blink Latency Correlation Heatmap](../../figures/blink_metrics_overview/corr_blink_latency.png)

## 7. Blink Rate Plausibility

Estimated session duration: 179,500 ms (2.99 min). Typical adult blink rate: 15–20 blinks/min.

- **Sample**: Mean 7.8 blinks/min, median 6.0, range 2.0–24.4
- **8 of 26 sessions** (31%) fall below the 5 blinks/min plausibility floor
- **18 of 26 sessions** (69%) are in the plausible 5–40 range
- No sessions exceed 40 blinks/min (the extreme outlier DTGxc0RwsWrTMRKpenb8 was removed)

The low median (6.0) suggests the eye tracker's blink detection may under-count blinks, or that the sustained visual attention task suppresses blink rate below typical resting levels. This is consistent with the pre-cleaning analysis.

## 8. PTSD-Group Visual Preview

### Global Blink Metrics

With the extreme outlier removed, total blink count distributions overlap between groups. The PTSD group (n = 15) shows slightly higher median blink count. Blink duration and interval metrics show no clear group separation.

![PTSD Global Blink](../../figures/blink_metrics_overview/ptsd_global_blink.png)

### Blink Rate by Category

Per-category blink rates show largely overlapping distributions between PTSD and non-PTSD groups. The high-blink session (9Pd2lTJaNZ7CGrLBPjuU) is visible as an upper outlier in the PTSD group across multiple categories.

![PTSD Blink Rate](../../figures/blink_metrics_overview/ptsd_blink_rate.png)

### Blink Duration by Category

Blink duration distributions overlap substantially between groups. No category shows a clear PTSD-group separation.

![PTSD Blink Duration](../../figures/blink_metrics_overview/ptsd_blink_duration.png)

### Std Blink Duration by Category

Within-session blink duration variability shows no consistent group differences.

![PTSD Std Blink Duration](../../figures/blink_metrics_overview/ptsd_std_blink_duration.png)

### Blink Latency by Category

Blink latency distributions overlap between groups. This is the blink family with the most category-specific variation, but visual inspection suggests no clear PTSD-group pattern.

![PTSD Blink Latency](../../figures/blink_metrics_overview/ptsd_blink_latency.png)

## 9. Antipsychotic-Group Visual Preview

### Global Blink Metrics

Global blink metrics show no clear separation between antipsychotic-use (n = 11) and non-use (n = 15) groups.

![Antipsychotic Global Blink](../../figures/blink_metrics_overview/antipsychotic_global_blink.png)

### Blink Rate by Category

Per-category blink rates show overlapping distributions between antipsychotic groups.

![Antipsychotic Blink Rate](../../figures/blink_metrics_overview/antipsychotic_blink_rate.png)

### Blink Duration by Category

Blink duration distributions are similar between groups.

![Antipsychotic Blink Duration](../../figures/blink_metrics_overview/antipsychotic_blink_duration.png)

### Std Blink Duration by Category

No consistent antipsychotic-group differences in blink duration variability.

![Antipsychotic Std Blink Duration](../../figures/blink_metrics_overview/antipsychotic_std_blink_duration.png)

### Blink Latency by Category

Blink latency distributions overlap between antipsychotic groups.

![Antipsychotic Blink Latency](../../figures/blink_metrics_overview/antipsychotic_blink_latency.png)

## 10. Implications for Blink Hypothesis Testing

### Test Selection

| Metric Family | Distribution | Recommended Approach |
|---|---|---|
| Total blink count | Right-skewed (p = 0.002) | Non-parametric (Mann-Whitney U) or log-transform |
| Mean blink rate | Right-skewed (all p < 0.035) | Non-parametric or log-transform |
| Mean blink duration | Platykurtic (most p < 0.05) | Parametric acceptable with caution; verify with non-parametric |
| Std blink duration | Severely right-skewed | Non-parametric |
| Mean blink interval | Right-skewed (p < 0.02) | Non-parametric or log-transform |
| Mean blink latency (norm) | Normal (all p > 0.12) | Parametric (t-test, correlation) |

### Key Considerations

1. **Blink rate correlations remain near-unity** (r = 0.43–0.97, median ~0.85). Per-category blink rates carry minimal category-specific information. Session-level total blink count may be sufficient for most hypotheses.

2. **Blink latency is the most category-sensitive blink metric.** With weaker intercorrelations (33/55 pairs at p < 0.01 vs. 51/55 for blink rate), latency may capture stimulus-driven blink suppression or facilitation effects that rate and duration cannot.

3. **Missingness reduces effective sample size.** Blink duration and latency analyses will have n = 14–26 depending on category. Combat_vehicles and sleep_related are most affected (n = 14–21). Power considerations should account for these reductions.

4. **Outlier profile is benign after cleaning.** The top univariate outlier (9Pd2lTJaNZ7CGrLBPjuU, 10 flags) is a legitimate high-blink participant, not a data quality issue. No multivariate outliers were detected. The cleaning successfully removed the extreme cases.

5. **Blink rate is low overall.** The sample median of 6.0 blinks/min is well below the typical 15–20 range. This may reflect task-induced blink suppression, under-detection by the eye tracker, or both. Hypotheses about blink rate should be interpreted in this context.

6. **Small sample (n = 26) limits power.** With 15 PTSD and 11 non-PTSD participants, group comparisons will have limited statistical power. Effect size estimation should complement null-hypothesis testing.

---

**Report Generated**: 2026-02-24
**Analysis Code**: `preanalysis_overview/blink_metrics_overview.py`
**Figures**: `figures/blink_metrics_overview/` (24 PNGs)
