# E3: Temporal Dynamics of Threat Attentional Bias

## 1. Motivation

Zvielli et al. (2015) and Schäfer et al. (2016) demonstrate that within-session
temporal dynamics of attentional bias carry diagnostic information beyond aggregate
scores. This exploratory analysis examines trial-level temporal trajectories and
TL-BS (Trial-Level Bias Score) variability indices for threat attentional bias,
comparing PTSD and No-PTSD groups.

## 2. Method

### Participants

- Total: N = 29
- PTSD: n = 17
- No-PTSD: n = 12
- Excluded: `UgMWkyrkRYVZ9cr9thRw` (poor gaze quality)

### Variables

| Variable | Description |
|----------|------------|
| `threat_delta_dwell` | Threat dwell % − neutral dwell % per slide |
| `trial_index` | Presentation order (1–44) of threat–neutral slides |
| `tl_bs_mean` | Session mean of 44 trial-level deltas |
| `tl_bs_sd` | Session SD of 44 trial-level deltas |
| `tl_bs_peak_toward` | Max positive delta (strongest threat bias) |
| `tl_bs_peak_away` | Min delta (strongest avoidance) |
| `tl_bs_range` | peak_toward − peak_away |

### Analysis Approach

- **Part A**: Group-level temporal trajectories with 95% CI bands
- **Part B**: Group comparisons on 5 TL-BS variability indices; assumption-driven
  test selection (Student's t / Welch's t / Mann-Whitney U); BH-FDR correction
  as a single family
- **Part C**: Individual spaghetti plots to visualize within-session variability

## 3. Part A — Group-Level Temporal Trajectories

Central tendency: **mean** (selected based on Shapiro-Wilk distribution
checks on per-slide delta distributions in preprocessing).

- PTSD group mean range: [-9.82, 23.64]
- No-PTSD group mean range: [-11.99, 19.52]

Both groups show generally positive threat bias (above zero) across most trials,
indicating a slight tendency to dwell more on threat images than neutral counterparts.

![Temporal Trajectory](../../figures/e3_temporal_dynamics_threat_bias/temporal_trajectory_mean_median.png)

## 4. Part B — TL-BS Variability Indices

### Descriptive Statistics

| Metric | Group | n | Mean | SD | Median | Min | Max |
|--------|-------|---|------|----|--------|-----|-----|
| `tl_bs_mean` | PTSD | 17 | 7.06 | 13.90 | 3.68 | -17.56 | 34.42 |
| `tl_bs_mean` | No-PTSD | 12 | 4.17 | 10.40 | 1.03 | -10.51 | 24.74 |
| `tl_bs_sd` | PTSD | 17 | 27.92 | 7.77 | 27.66 | 17.07 | 41.98 |
| `tl_bs_sd` | No-PTSD | 12 | 26.74 | 9.04 | 28.78 | 6.77 | 38.44 |
| `tl_bs_peak_toward` | PTSD | 17 | 64.71 | 25.37 | 66.84 | 29.34 | 100.27 |
| `tl_bs_peak_toward` | No-PTSD | 12 | 55.66 | 20.22 | 57.15 | 15.34 | 89.57 |
| `tl_bs_peak_away` | PTSD | 17 | -54.05 | 20.49 | -54.14 | -100.93 | -14.04 |
| `tl_bs_peak_away` | No-PTSD | 12 | -55.50 | 23.93 | -53.06 | -98.93 | -18.70 |
| `tl_bs_range` | PTSD | 17 | 118.76 | 29.98 | 114.21 | 70.05 | 159.09 |
| `tl_bs_range` | No-PTSD | 12 | 111.16 | 36.67 | 109.57 | 34.04 | 161.76 |

### Assumption Checks

| Metric | Shapiro PTSD (W, p) | Shapiro No-PTSD (W, p) | Levene (F, p) | Both Normal | Equal Var |
|--------|---------------------|------------------------|---------------|------------|-----------|
| `tl_bs_mean` | 0.935, 0.2614 | 0.833, 0.0231 | 1.114, 0.3005 | No | Yes |
| `tl_bs_sd` | 0.951, 0.4720 | 0.936, 0.4460 | 0.093, 0.7628 | Yes | Yes |
| `tl_bs_peak_toward` | 0.898, 0.0617 | 0.974, 0.9478 | 1.804, 0.1905 | Yes | Yes |
| `tl_bs_peak_away` | 0.978, 0.9375 | 0.959, 0.7676 | 0.571, 0.4564 | Yes | Yes |
| `tl_bs_range` | 0.922, 0.1627 | 0.958, 0.7517 | 0.030, 0.8648 | Yes | Yes |

### Results

| Metric | Test | Statistic | p (uncorr.) | p (BH) | Effect Size | 95% CI | Sig. |
|--------|------|-----------|-------------|--------|-------------|--------|------|
| `tl_bs_mean` | Mann-Whitney U | 110.000 | 0.7398 | 0.8624 | rank-biserial r = -0.078 | [-0.433, 0.297] | No |
| `tl_bs_sd` | Student's t-test | 0.375 | 0.7107 | 0.8624 | Cohen's d = 0.141 | [-0.623, 0.906] | No |
| `tl_bs_peak_toward` | Student's t-test | 1.025 | 0.3145 | 0.8624 | Cohen's d = 0.386 | [-0.526, 1.299] | No |
| `tl_bs_peak_away` | Student's t-test | 0.175 | 0.8624 | 0.8624 | Cohen's d = 0.066 | [-0.679, 0.811] | No |
| `tl_bs_range` | Student's t-test | 0.613 | 0.5449 | 0.8624 | Cohen's d = 0.231 | [-0.574, 1.037] | No |

**Overall:** No significant results at α = 0.05 (BH-corrected).

![Violin Plots](../../figures/e3_temporal_dynamics_threat_bias/violin_variability_indices.png)

![Forest Plot](../../figures/e3_temporal_dynamics_threat_bias/forest_plot_variability.png)

## 5. Part C — Individual Trajectories

Spaghetti plots show substantial within-session variability for both groups.
Individual trajectories oscillate widely around zero, consistent with trial-level
attentional bias being highly variable.

![Side-by-Side Spaghetti](../../figures/e3_temporal_dynamics_threat_bias/spaghetti_individual_trajectories.png)

![Combined Spaghetti](../../figures/e3_temporal_dynamics_threat_bias/spaghetti_combined.png)

## 6. Summary & Interpretation

### Key Findings

1. Both groups show generally positive threat bias across the 44 trial presentations, with largely overlapping trajectories and 95% CI bands.
2. None of the 5 TL-BS variability indices showed significant group differences after BH-FDR correction.
3. Individual trajectories show substantial within-session variability in both groups.
4. The null results likely reflect methodological limitations (non-contiguous trial selection) and the trauma-exposed nature of the comparison group (see below).

### Caveats

- Small sample size (N=29) limits statistical power
- Exploratory analysis — results are hypothesis-generating, not confirmatory
- Trial order confounded with threat category (slides presented in fixed order)
- No correction for multiple comparisons across Parts A–C (only within Part B)

### Why This Approach May Not Differentiate Groups

Two design features likely contribute to the null results:

1. **Non-contiguous threat trial selection.** The 44 threat–neutral slides are interspersed
   among 75 total slides (31 non-threat slides omitted). The temporal trajectory treats these
   44 trials as contiguous (trial_index 1–44), but participants actually experienced interleaved
   non-threat content between them. This breaks the assumption of continuous temporal evolution
   that Zvielli et al. (2015) relied on, where consecutive trials were all bias-relevant. The
   gaps between threat trials likely reset or disrupt any accumulating attentional pattern.

2. **Trauma-exposed comparison group.** The No-PTSD group consists of soldiers potentially
   exposed to trauma but without a PTSD diagnosis. Unlike civilian controls, these individuals
   may exhibit similar threat-related attentional dynamics (hypervigilance, variable engagement
   with threat stimuli) as the PTSD group, making temporal variability indices indistinguishable
   between groups. A civilian control group might show different temporal patterns.

## 7. Metadata

| Field | Value |
|-------|-------|
| Analysis ID | E3 |
| Script | `exploratory_analysis/e3_temporal_dynamics_threat_bias.py` |
| Datasets | `temporal_threat_bias_by_session.csv`, `temporal_threat_bias_aggregated.csv`, `temporal_threat_bias_variability.csv` |
| N | 29 (PTSD: 17, No-PTSD: 12) |
| DVs | 5 TL-BS variability indices |
| Alpha | 0.05 |
| FDR | BH (single family of 5 tests) |
| Central Tendency | mean |
| LOWESS frac | 0.3 |
| Date | 2026-02-25 |
