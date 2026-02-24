# Eye-Tracking Metrics Overview Report

## 1. Dataset Overview

The eye-tracking metrics dataset contains **30 sessions x 134 columns**. Column types: 131 float64, 2 int64, and 1 object (session_id).

### Column Groups

| Metric Family | Columns | Description |
|---|---|---|
| mean_dwell_pct | 11 | Mean dwell percentage on AOI per image category |
| std_dwell_pct | 11 | Within-session variability of dwell percentage |
| std_delta_dwell_pct | 4 | Variability of threat-minus-neutral dwell bias (threat categories only) |
| mean_visits | 11 | Mean number of AOI visits per image category |
| mean_dwell_pct_late | 11 | Mean dwell percentage in the late window (>= 800 ms post-onset) |
| mean_visits_late | 11 | Mean visit count in the late window (>= 800 ms post-onset) |
| mean_offscreen_pct | 11 | Mean percentage of slide duration with gaze off-screen |
| mean_offscreen_pct_late | 11 | Mean off-screen percentage in the late window (>= 800 ms) |
| mean_blink_rate | 11 | Mean blinks per slide for each category (normalized for slide count) |
| mean_blink_duration | 11 | Mean blink duration per category (ms) |
| std_blink_duration | 11 | Within-session variability of blink duration |
| mean_blink_latency_norm | 11 | Mean latency to first blink per category (normalized by slide duration, dimensionless) |
| global_blink | 4 | Session-level blink metrics (total count, mean duration, normalized mean/std interval) |
| metadata | 4 | if_PTSD, ITI_PTSD, ITI_cPTSD, if_antipsychotic |

### Missingness

Blink duration, blink latency (normalized), and std blink duration columns have substantial missingness because some sessions produce zero blinks in certain categories, making duration and latency undefined. NaN counts range from 1 (happy_face) to 14 (combat_vehicles, sleep_related). These are structurally missing values, not data collection failures. All other metric families (dwell, visits, blink rate, off-screen, global blink, late-window metrics) are complete.

### Metadata Variables

The dataset includes four metadata columns alongside session_id:

**Group counts:**
- **if_PTSD**: n = 17 PTSD, n = 13 non-PTSD
- **if_antipsychotic**: n = 14 antipsychotic-use, n = 16 non-use

**ITI scores (PTSD group only, n = 17):**

| Metric | Mean | Median | SD | Min | Max | Zero count |
|---|---|---|---|---|---|---|
| ITI_PTSD | 12.65 | 12.00 | 3.18 | 8.0 | 19.0 | 0 |
| ITI_cPTSD | 7.35 | 9.00 | 4.60 | 0.0 | 14.0 | 4 |

ITI descriptives are computed only for PTSD participants (if_PTSD == 1), since non-PTSD participants have 0 by definition. All PTSD participants have non-zero ITI_PTSD scores (range 8-19). ITI_cPTSD shows more spread, with 4 of 17 PTSD participants scoring 0 on the complex PTSD subscale.

![Metadata Overview](../../figures/eyetracking_metrics_overview/metadata_overview.png)

## 2. Descriptive Statistics

### Mean Dwell Percentage

Dwell percentages are roughly symmetric across all 11 categories, with means ranging from 19.7% (neutral) to 28.7% (anxiety_inducing). Standard deviations range from 7.8% to 15.2%, indicating moderate between-subject variability. The neutral category has the narrowest spread, while anxiety_inducing and warfare are the most variable.

Shapiro-Wilk tests show no category significantly deviates from normality at p < 0.05 (lowest p = 0.059 for anxiety_inducing). This is the most well-behaved metric family.

![Mean Dwell % Histograms](../../figures/eyetracking_metrics_overview/hist_mean_dwell_pct.png)

### Std Dwell Percentage

Within-session dwell variability (std) averages 15-20% across categories. Two categories show marginal normality violations: std_dwell_pct_anxiety_inducing (Shapiro p = 0.031) and std_dwell_pct_neutral (Shapiro p = 0.016), both driven by mild skewness.

![Std Dwell % Histograms](../../figures/eyetracking_metrics_overview/hist_std_dwell_pct.png)

### Std Delta Dwell (Threat Bias Variability)

The four threat-bias variability metrics (angry_face, anxiety_inducing, warfare, soldiers) have means near 25-26% and show approximately symmetric distributions. All pass the Shapiro-Wilk normality test (p > 0.40).

![Std Delta Dwell Histograms](../../figures/eyetracking_metrics_overview/hist_std_delta_dwell.png)

### Mean Visits

Mean visits per category range from 1.19 (combat_vehicles) to 1.75 (anxiety_inducing), with standard deviations of 0.49-0.84. Distributions are roughly symmetric with mild negative skewness in some categories. All pass the Shapiro-Wilk test (lowest p = 0.185 for soldiers).

![Mean Visits Histograms](../../figures/eyetracking_metrics_overview/hist_mean_visits.png)

### Global Blink Metrics

Global blink metrics are severely non-normal:

| Metric | Mean | Median | Skewness | Kurtosis | Shapiro p |
|---|---|---|---|---|---|
| total_blink_count | 28.2 | 17.0 | 4.02 | 16.87 | < 0.0001 |
| mean_blink_duration_ms | 87.8 | 78.9 | -0.08 | -1.10 | 0.006 |
| mean_blink_interval_norm | 7.03 | 4.88 | 2.17 | 4.79 | < 0.0001 |
| std_blink_interval_norm | 6.56 | 4.45 | 2.50 | 5.98 | < 0.0001 |

Total blink count and normalized blink interval metrics are strongly right-skewed with heavy tails, driven by one extreme session (DTGxc0RwsWrTMRKpenb8, 217 blinks). Mean blink duration is platykurtic but not severely skewed. The interval metrics are now normalized by slide duration (dimensionless ratios), so values represent multiples of the slide duration between blinks.

![Global Blink Histograms](../../figures/eyetracking_metrics_overview/hist_global_blink.png)

### Mean Blink Rate by Category

Per-category blink rates (mean blinks per slide) are heavily right-skewed across all 11 categories (skewness 2.9-4.2, kurtosis 10.8-17.9). All fail the Shapiro-Wilk test (p < 0.0001). Means range from 0.28 (combat_vehicles) to 0.52 (sad_face) blinks per slide. The distributions are zero-inflated: many sessions have very low blink rates per slide.

![Blink Rate Histograms](../../figures/eyetracking_metrics_overview/hist_mean_blink_rate.png)

### Mean Blink Latency (Normalized)

Blink latency is the most affected by missingness (n = 21-29 per category vs. 30 for complete metrics). Values are now dimensionless ratios (latency divided by slide duration), with means clustering around 0.42-0.51. Distributions are approximately normal; all pass the Shapiro-Wilk test (p > 0.12).

![Blink Latency Histograms](../../figures/eyetracking_metrics_overview/hist_mean_blink_latency_norm.png)

### Mean Dwell % Late Window

Late-window dwell percentages (gaze >= 800 ms post-onset) show means ranging from 18.7% (neutral) to 30.1% (anxiety_inducing). Standard deviations (8.2%-18.6%) are generally larger than for full-window dwell, reflecting more variability in sustained attention. Most categories are approximately normal, with two marginal exceptions: anxiety_inducing (Shapiro p = 0.011) and warfare (Shapiro p = 0.021), both showing mild right-skew.

![Late Dwell % Histograms](../../figures/eyetracking_metrics_overview/hist_mean_dwell_pct_late.png)

### Mean Visits Late Window

Late-window visit counts range from 0.66 (combat_vehicles) to 1.25 (anxiety_inducing). All categories pass the Shapiro-Wilk normality test (lowest p = 0.055 for sleep_related), making this a parametric-friendly family. Distributions are roughly symmetric with moderate between-subject variability (SD 0.35-0.70).

![Late Visits Histograms](../../figures/eyetracking_metrics_overview/hist_mean_visits_late.png)

### Mean Off-Screen %

Off-screen percentages are severely right-skewed across all 11 categories (Shapiro p < 0.005 for all). Means range from 20.2% (anxiety_inducing) to 24.5% (warfare). The right skew is driven by poor-quality sessions with very high off-screen proportions (UgMWkyrkRYVZ9cr9thRw: 83-93% across categories). Medians (14.5%-21.5%) are consistently lower than means, confirming the positive skew.

![Off-Screen % Histograms](../../figures/eyetracking_metrics_overview/hist_mean_offscreen_pct.png)

### Mean Off-Screen % Late Window

Late-window off-screen percentages follow the same pattern as full-window: all severely right-skewed (Shapiro p < 0.011 for all categories). Means range from 21.1% (soldiers) to 25.7% (warfare), slightly higher than full-window means, consistent with gaze drift increasing over time. The same poor-quality sessions drive the right tail.

![Late Off-Screen % Histograms](../../figures/eyetracking_metrics_overview/hist_mean_offscreen_pct_late.png)

## 3. Distributional Observations

The metrics fall into three distributional regimes:

1. **Approximately normal**: Mean dwell %, std dwell %, std delta dwell %, mean visits, mean blink latency (normalized), mean dwell % late, and mean visits late. These are suitable for parametric tests (t-tests, ANOVA) with n = 30.

2. **Severely right-skewed**: Total blink count, per-category blink rate, mean/std blink interval (normalized), mean off-screen %, and mean off-screen % late. These require non-parametric tests (Mann-Whitney U, Kruskal-Wallis) or log-transformation before parametric analysis. Off-screen % joins this group due to poor-quality sessions inflating the right tail.

3. **Intermediate**: Mean blink duration fails the Shapiro-Wilk test (p = 0.006) primarily due to platykurtosis rather than skewness.

The late-window dwell and visit metrics are mostly normal, joining the parametric-friendly group. Late-window off-screen metrics remain right-skewed, similar to their full-window counterparts.

## 4. Outlier Detection

### Univariate IQR Outliers

Sessions were flagged across all numeric columns using the 1.5x IQR rule. 15 of 30 sessions had zero flags. Detailed breakdown of the top flagged sessions:

**UgMWkyrkRYVZ9cr9thRw (28 flags) [POOR QUALITY]**: The top outlier is driven overwhelmingly by off-screen metrics — 22 of 28 flags are off-screen percentage flags (HIGH), with values of 77-93% across all categories in both full and late windows. The remaining 6 flags include low dwell (neutral = 0.86%), low visits (happy_event, neutral, neutral_face), and low late-window metrics. Consistent with near-zero gaze engagement from only 8% usable slides.

**DTGxc0RwsWrTMRKpenb8 (12 flags) [POOR QUALITY]**: All 12 flags are blink-related — total_blink_count (217, HIGH) and all 11 per-category mean_blink_rate values (HIGH, e.g., angry_face = 3.00, warfare = 3.42 blinks/slide). This session's poor gaze quality likely inflates blink detection.

**9Pd2lTJaNZ7CGrLBPjuU (12 flags)**: 6 blink rate flags (HIGH: angry_face = 1.30, warfare = 1.50, etc.), total_blink_count = 73 (HIGH), 1 visit flag (mean_visits_happy_event = 3.0, HIGH), and 4 late-window visit flags (happy_event = 2.33, happy_face = 2.55, neutral = 1.86, neutral_face = 2.15, all HIGH). This is a high-engagement participant, not a data quality issue.

**VvTiIIg9tjuA8dCwFABk (4 flags)**: Dwell outliers — 2 full-window (happy_face = 46.24%, neutral_face = 52.40%, HIGH) and 2 late-window (happy_event = 46.64%, happy_face = 46.92%, HIGH).

**RBRGZzWIzDitollqkpzW and xn3yMJ8STzchnQPg94lH (2 flags each)**: Both flagged on normalized blink interval metrics (mean_blink_interval_norm and std_blink_interval_norm, HIGH), reflecting very low blink rates (7 and 4 total blinks respectively).

### Outlier Box Plots

Box plots with IQR whiskers and individual session points (red = poor gaze quality) for each metric group that produced outlier flags.

**Blink rate** — DTGxc0RwsWrTMRKpenb8 is a clear extreme outlier across all categories; 9Pd2lTJaNZ7CGrLBPjuU is a secondary high-blink session.

![Outlier Box Plots: Blink Rate](../../figures/eyetracking_metrics_overview/outlier_boxplot_blink_rate.png)

**Mean visits** — A few sessions fall outside the whiskers (UgMWkyrkRYVZ9cr9thRw at the low end, 9Pd2lTJaNZ7CGrLBPjuU at the high end).

![Outlier Box Plots: Mean Visits](../../figures/eyetracking_metrics_overview/outlier_boxplot_mean_visits.png)

**Mean dwell %** — UgMWkyrkRYVZ9cr9thRw is visible as a low outlier on several categories.

![Outlier Box Plots: Mean Dwell %](../../figures/eyetracking_metrics_overview/outlier_boxplot_mean_dwell_pct.png)

**Blink interval (normalized)** — Two sessions with very few blinks produce extreme high interval values.

![Outlier Box Plots: Blink Interval](../../figures/eyetracking_metrics_overview/outlier_boxplot_blink_interval.png)

**Blink latency (normalized)** — Mild outliers only; distributions are relatively well-behaved.

![Outlier Box Plots: Blink Latency](../../figures/eyetracking_metrics_overview/outlier_boxplot_blink_latency.png)

**Late dwell %** — Similar pattern to full-window dwell. VvTiIIg9tjuA8dCwFABk and 8LQQmNuNOOg5wGfdKZf3 visible at the high end.

![Outlier Box Plots: Late Dwell %](../../figures/eyetracking_metrics_overview/outlier_boxplot_mean_dwell_pct_late.png)

**Late visits** — 9Pd2lTJaNZ7CGrLBPjuU at the high end; UgMWkyrkRYVZ9cr9thRw at the low end.

![Outlier Box Plots: Late Visits](../../figures/eyetracking_metrics_overview/outlier_boxplot_mean_visits_late.png)

**Off-screen %** — UgMWkyrkRYVZ9cr9thRw is a dramatic outlier (80-93%) across all categories. 9gSnpeygVxyRw0VLNI6F shows a secondary high outlier on soldiers.

![Outlier Box Plots: Off-Screen %](../../figures/eyetracking_metrics_overview/outlier_boxplot_mean_offscreen_pct.png)

**Late off-screen %** — Same pattern as full-window off-screen. UgMWkyrkRYVZ9cr9thRw dominates the upper tail, xx19J8Xeoc4thStIAtUe visible on warfare.

![Outlier Box Plots: Late Off-Screen %](../../figures/eyetracking_metrics_overview/outlier_boxplot_mean_offscreen_pct_late.png)

### Multivariate Mahalanobis Distance

Mahalanobis distances were computed within seven metric subspaces using a chi-squared threshold at p < 0.01:

**Mean Dwell %**: No sessions exceeded the critical value (chi2 crit = 4.97). Range 1.70-4.57.

**Mean Visits**: No multivariate outliers detected (range 1.73-4.43, crit = 4.97).

**Blink Metrics** (rate + interval + duration): No sessions exceeded the threshold (range 1.71-4.78, crit = 5.40).

**Mean Dwell % Late Window**: No multivariate outliers (range 2.20-4.54, crit = 4.97).

**Mean Visits Late Window**: No multivariate outliers (range 1.89-4.02, crit = 4.97).

**Mean Off-Screen %**: No multivariate outliers (range 1.53-4.68, crit = 4.97).

**Mean Off-Screen % Late Window**: No multivariate outliers (range 1.75-4.73, crit = 4.97).

No multivariate outliers were detected in any metric subspace. While UgMWkyrkRYVZ9cr9thRw and DTGxc0RwsWrTMRKpenb8 rank among the top sessions by Mahalanobis distance in several subspaces, neither exceeds the chi-squared critical threshold.

### Cross-Reference with Poor Gaze Quality Sessions

The three sessions previously flagged for poor gaze quality (see [Gaze Quality Check Report](../routine_exploration/gaze_quality_check_report.md)):

| Session | IQR Flags (Rank) | Mahalanobis Outlier? |
|---|---|---|
| UgMWkyrkRYVZ9cr9thRw | 28 (1st/30) | No |
| DTGxc0RwsWrTMRKpenb8 | 12 (3rd/30) | No |
| xx19J8Xeoc4thStIAtUe | 2 (10th/30) | No |

UgMWkyrkRYVZ9cr9thRw is the clear univariate outlier driven almost entirely by off-screen metrics (22 of 28 flags). DTGxc0RwsWrTMRKpenb8 is an extreme blink-rate outlier. xx19J8Xeoc4thStIAtUe falls within normal ranges on most metrics, consistent with its borderline gaze quality (45.3% usable slides, just below the 50% threshold but not dramatically so).

## 5. Correlation Structure

With n = 30, the critical values for Pearson r are |r| >= 0.361 (p < 0.05) and |r| >= 0.463 (p < 0.01).

### Mean Dwell %

All pairwise correlations are positive (range 0.38-0.93) and significant at p < 0.05. 51 of 55 pairs reach p < 0.01; the four that reach only p < 0.05 are angry_face-happy_face (r = 0.45), angry_face-neutral_face (r = 0.38), anxiety_inducing-happy_event (r = 0.43), and happy_event-warfare (r = 0.45). This indicates a strong individual-differences component: participants who dwell more on one category tend to dwell more on all categories.

![Mean Dwell % Correlation Heatmap](../../figures/eyetracking_metrics_overview/corr_mean_dwell_pct.png)

### Mean Visits

Correlations are uniformly positive (range 0.38-0.87) and all significant at p < 0.05. 51 of 55 pairs reach p < 0.01; the four that reach only p < 0.05 involve warfare (happy_event-warfare r = 0.38, neutral-warfare r = 0.44, happy_face-warfare r = 0.41) and one face pair (happy_face-neutral_face r = 0.39).

![Mean Visits Correlation Heatmap](../../figures/eyetracking_metrics_overview/corr_mean_visits.png)

### Blink Rate

Per-category blink rates show very high intercorrelations (range 0.87-0.99), all significant at p < 0.01, indicating that blink rates are dominated by an individual blink-rate trait rather than category-specific effects. This is expected: blink rate is largely physiological and should not vary substantially by stimulus content over short viewing windows.

![Blink Rate Correlation Heatmap](../../figures/eyetracking_metrics_overview/corr_blink_rate.png)

### Mean Dwell % Late Window

Late-window dwell correlations are notably weaker than full-window dwell (range 0.13-0.91 vs. 0.38-0.93). Only 38 of 55 pairs are significant at p < 0.05, and 28 of 55 at p < 0.01. The weaker correlations suggest that sustained attention (late window) is more category-specific than initial orienting (full window), which is dominated by individual-differences in overall engagement.

![Late Dwell % Correlation Heatmap](../../figures/eyetracking_metrics_overview/corr_mean_dwell_pct_late.png)

### Mean Visits Late Window

Late-window visit correlations follow a similar pattern (range 0.21-0.84). 44 of 55 pairs significant at p < 0.05, 35 of 55 at p < 0.01. Stronger than late dwell but weaker than full-window visits, again suggesting more category-specific variation in the sustained attention window.

![Late Visits Correlation Heatmap](../../figures/eyetracking_metrics_overview/corr_mean_visits_late.png)

### Mean Off-Screen %

Off-screen percentages show near-unity intercorrelations (range 0.87-0.99), all significant at p < 0.01. This indicates that off-screen gaze is almost entirely an individual-differences trait: participants with high off-screen rates show them uniformly across all categories. This is consistent with off-screen gaze reflecting overall data quality or disengagement rather than stimulus-specific avoidance.

![Off-Screen % Correlation Heatmap](../../figures/eyetracking_metrics_overview/corr_mean_offscreen_pct.png)

### Mean Off-Screen % Late Window

Late off-screen correlations remain near-unity (range 0.83-0.99), all significant at p < 0.01. The same individual-differences interpretation applies.

![Late Off-Screen % Correlation Heatmap](../../figures/eyetracking_metrics_overview/corr_mean_offscreen_pct_late.png)

### Dwell % vs. Visits Scatter

Dwell percentage and visit count are positively associated within categories. The poor-quality sessions (red points in the scatter plots) tend to cluster at the low end of both metrics, consistent with reduced gaze engagement.

![Dwell vs. Visits Scatter](../../figures/eyetracking_metrics_overview/scatter_dwell_vs_visits.png)

### Late Dwell % vs. Late Visits Scatter

The same positive association holds in the late window. Scatter is wider than for full-window metrics, consistent with the weaker correlation structure observed in the late-window heatmaps.

![Late Dwell vs. Late Visits Scatter](../../figures/eyetracking_metrics_overview/scatter_late_dwell_vs_visits.png)

## 6. Domain Sanity Checks

### Blink Rate

Estimated session duration: 179.5 seconds (3.0 minutes). Typical adult blink rate is 15-20 blinks/min.

- **Sample**: Mean 9.4 blinks/min, median 5.7 blinks/min, range 1.3-72.5.
- **12 of 30 sessions** (40%) fall outside the 5-40 blinks/min plausibility range.
- The low median (5.7) and the large number of sub-5 sessions suggest the eye tracker's blink detection may under-count blinks, or that the task (sustained visual attention to slides) suppresses blink rate.
- One extreme outlier: DTGxc0RwsWrTMRKpenb8 at 72.5 blinks/min (217 total). This is a poor-quality session where noise in the gaze signal likely inflates the blink count.

### Dwell Percentage Range

Only one session produces implausibly low dwell values (< 1%): **UgMWkyrkRYVZ9cr9thRw**, with 0.0% dwell on combat_vehicles, happy_event, and soldiers, and near-zero on neutral (0.86%), sleep_related (0.19%), and warfare (0.45%). This is a known poor-quality session with only 8% usable slides. No sessions show implausibly high values (> 90%).

### Delta Dwell Uniformity

Three std_delta_dwell_pct values are suspiciously close to zero (< 5), all from session **UgMWkyrkRYVZ9cr9thRw**: angry_face (1.38), warfare (2.28), soldiers (0.95). Near-zero variability in the threat-bias metric implies the participant showed no slide-to-slide fluctuation in attentional bias, which is consistent with near-zero gaze engagement overall rather than a meaningful pattern.

### Late Dwell Range

All late-window dwell values fall within [0, 100] across all categories. No negative or over-100% values were detected.

### Off-Screen Percentage

Mean off-screen percentage across categories ranges from ~20% to ~25%, with medians consistently lower (14-21%), confirming right-skew. Two sessions have mean off-screen > 50% across categories:
- **UgMWkyrkRYVZ9cr9thRw**: 86.82% mean off-screen [POOR QUALITY]
- **xx19J8Xeoc4thStIAtUe**: 51.02% mean off-screen [POOR QUALITY]

Both are known poor-quality sessions. The remaining sessions have mean off-screen rates of 2.5-48%, which is plausible given that off-screen includes gaze outside the monitor area.

## 7. PTSD-Group Visual Preview

### Mean Dwell %

Violin plots split by PTSD status show largely overlapping distributions across all categories. No category shows a dramatic separation between groups. The PTSD group may show slightly wider spread in some threat categories (combat_vehicles, soldiers, warfare), but with only 17 PTSD and 13 non-PTSD participants, visual impressions are unreliable.

![PTSD Mean Dwell %](../../figures/eyetracking_metrics_overview/ptsd_mean_dwell_pct.png)

### Std Delta Dwell (Threat Bias Variability)

The PTSD and non-PTSD groups show broadly similar distributions of threat-bias variability. No striking group differences are visible.

![PTSD Std Delta Dwell](../../figures/eyetracking_metrics_overview/ptsd_std_delta_dwell.png)

### Global Blink Metrics

The extreme total_blink_count outlier (217 blinks) is in the PTSD group, pulling the PTSD violin upward. After mentally discounting this outlier, the two groups appear similar. Blink duration distributions overlap substantially. Blink interval shows no clear group separation.

![PTSD Global Blink](../../figures/eyetracking_metrics_overview/ptsd_global_blink.png)

### Mean Visits

Visit counts are broadly similar across groups for most categories. The PTSD group shows slightly narrower distributions in some categories, though this may reflect the smaller group size.

![PTSD Mean Visits](../../figures/eyetracking_metrics_overview/ptsd_mean_visits.png)

### Std Dwell %

Within-session dwell variability distributions are broadly similar across PTSD groups. No category shows a clear separation.

![PTSD Std Dwell %](../../figures/eyetracking_metrics_overview/ptsd_std_dwell_pct.png)

### Mean Dwell % Late Window

Late-window dwell shows broadly overlapping distributions between PTSD groups. As with full-window dwell, no dramatic category-level differences are apparent.

![PTSD Late Dwell %](../../figures/eyetracking_metrics_overview/ptsd_mean_dwell_pct_late.png)

### Mean Visits Late Window

Late-window visits overlap substantially between groups across all categories.

![PTSD Late Visits](../../figures/eyetracking_metrics_overview/ptsd_mean_visits_late.png)

### Mean Off-Screen %

Off-screen distributions are right-skewed in both groups, driven by the poor-quality sessions (red points). No clear group-level separation is visible.

![PTSD Off-Screen %](../../figures/eyetracking_metrics_overview/ptsd_mean_offscreen_pct.png)

### Mean Off-Screen % Late Window

Same pattern as full-window off-screen: overlapping and right-skewed in both groups.

![PTSD Late Off-Screen %](../../figures/eyetracking_metrics_overview/ptsd_mean_offscreen_pct_late.png)

## 8. Antipsychotic-Group Visual Preview

### Mean Dwell %

The antipsychotic-use group (n = 14) shows similar dwell distributions to the non-use group (n = 16). No consistent pattern of higher or lower dwell across categories is apparent.

![Antipsychotic Mean Dwell %](../../figures/eyetracking_metrics_overview/antipsychotic_mean_dwell_pct.png)

### Global Blink Metrics

The extreme blink-count outlier (DTGxc0RwsWrTMRKpenb8) falls in the antipsychotic-use group. Excluding this point, blink counts appear comparable. Blink duration may be slightly lower in the antipsychotic group, but the small sample precludes conclusions. Blink intervals show no clear pattern.

![Antipsychotic Global Blink](../../figures/eyetracking_metrics_overview/antipsychotic_global_blink.png)

### Std Dwell %

Within-session dwell variability shows no consistent differences between antipsychotic-use and non-use groups across categories.

![Antipsychotic Std Dwell %](../../figures/eyetracking_metrics_overview/antipsychotic_std_dwell_pct.png)

### Mean Visits

Visit count distributions overlap substantially between antipsychotic groups.

![Antipsychotic Mean Visits](../../figures/eyetracking_metrics_overview/antipsychotic_mean_visits.png)

### Std Delta Dwell

Threat-bias variability distributions are similar between antipsychotic groups.

![Antipsychotic Std Delta Dwell](../../figures/eyetracking_metrics_overview/antipsychotic_std_delta_dwell.png)

### Mean Dwell % Late Window

Late-window dwell shows no clear antipsychotic-group differences.

![Antipsychotic Late Dwell %](../../figures/eyetracking_metrics_overview/antipsychotic_mean_dwell_pct_late.png)

### Mean Visits Late Window

Late-window visits overlap between groups.

![Antipsychotic Late Visits](../../figures/eyetracking_metrics_overview/antipsychotic_mean_visits_late.png)

### Mean Off-Screen %

Off-screen distributions are right-skewed in both groups, with no clear separation.

![Antipsychotic Off-Screen %](../../figures/eyetracking_metrics_overview/antipsychotic_mean_offscreen_pct.png)

### Mean Off-Screen % Late Window

Same pattern as full-window off-screen for antipsychotic groups.

![Antipsychotic Late Off-Screen %](../../figures/eyetracking_metrics_overview/antipsychotic_mean_offscreen_pct_late.png)

## 9. Implications for Statistical Analysis

### Test Selection

| Metric Family | Distribution | Recommended Approach |
|---|---|---|
| Mean dwell % | Normal | Parametric (t-test, ANOVA) |
| Std dwell % | Mostly normal | Parametric; check anxiety_inducing and neutral |
| Std delta dwell % | Normal | Parametric |
| Mean visits | Normal | Parametric |
| Mean dwell % late | Mostly normal | Parametric; check anxiety_inducing and warfare |
| Mean visits late | Normal | Parametric |
| Mean blink latency (norm) | Normal | Parametric (note reduced n due to missingness) |
| Mean blink duration | Mildly non-normal | Parametric acceptable with n = 30; verify with non-parametric |
| Total blink count | Severely skewed | Non-parametric (Mann-Whitney U) or log-transform |
| Mean blink rate | Severely skewed | Non-parametric or log-transform |
| Blink interval (norm) | Severely skewed | Non-parametric or log-transform |
| Mean off-screen % | Severely skewed | Non-parametric or log-transform |
| Mean off-screen % late | Severely skewed | Non-parametric or log-transform |

### Key Considerations

1. **Blink rate correlations are near-unity across categories** (r = 0.87-0.99). Category-level blink rates carry almost no category-specific information. The global total_blink_count (or blink rate) is likely sufficient; per-category blink rates may be redundant.

2. **Off-screen metrics are dominated by individual differences** (r = 0.87-0.99 across categories in both full and late windows). Off-screen gaze reflects overall data quality or disengagement rather than stimulus-specific avoidance. A single session-level off-screen summary may suffice; category-level off-screen metrics are largely redundant.

3. **Late-window metrics show more category-specific variation than full-window metrics.** Late dwell correlations (r = 0.13-0.91, only 38/55 pairs significant) are substantially weaker than full-window dwell correlations (r = 0.38-0.93, all 55 pairs significant). This suggests that sustained attention after initial orienting carries more category-specific information, making late-window metrics potentially more sensitive to stimulus-driven effects.

4. **Dwell and visit correlations are high but not redundant.** The correlation structure shows meaningful within-cluster variation (threat vs. positive categories), so category-level analyses are warranted.

5. **The poor-quality sessions drive most outlier flags.** UgMWkyrkRYVZ9cr9thRw (28 flags, overwhelmingly off-screen) and DTGxc0RwsWrTMRKpenb8 (12 flags, all blink rate) are the dominant univariate outliers. Sensitivity analyses with and without these sessions are recommended.

6. **Missingness in blink duration/latency is structural.** Analyses using these metrics will have reduced sample sizes (n = 21-29 depending on category). This should be accounted for in power considerations.

7. **Small sample (n = 30) limits subgroup analyses.** PTSD and antipsychotic group comparisons will have low power. Effect size estimation may be more informative than null-hypothesis testing.

---

**Report Generated**: 2026-02-19
**Analysis Code**: `preanalysis_overview/eyetracking_metrics_overview.py`
**Figures**: `figures/eyetracking_metrics_overview/` (52 PNGs)
