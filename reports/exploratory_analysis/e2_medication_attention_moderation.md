# E2: Medication-Attention Moderation

## 1. Motivation

Antipsychotic medication is common in PTSD treatment but may affect visual attention independently of PTSD status. This exploratory analysis examines whether antipsychotic medication status moderates attention metrics across threat-related stimulus categories. Understanding medication effects is important for interpreting group differences in eye-tracking data.

## 2. Method

### Participants

- **Total sample**: N = 29
- **2x2 cell sizes** (PTSD x Antipsychotic):

| | No-Anti | Anti |
|---|---|---|
| **No-PTSD** | 6 | 6 |
| **PTSD** | 9 | 8 |

### Variables

**Grouping variables**: `if_antipsychotic` (Part A), `if_PTSD x if_antipsychotic` (Part B)

**Dependent variables** (12 DVs, 3 families of 4 threat categories):

- **F1: Mean Dwell %** — mean_dwell_pct_{angry_face, anxiety_inducing, warfare, soldiers}
- **F2: Attention Bias Variability (Std Dwell %)** — std_dwell_pct_{angry_face, anxiety_inducing, warfare, soldiers}
- **F3: Mean Visits** — mean_visits_{angry_face, anxiety_inducing, warfare, soldiers}

### Statistical Approach

- **Part A**: Two-group comparison (Antipsychotic vs No-Antipsychotic) using assumption-driven test selection (Student's t / Welch's t / Mann-Whitney U). BH-FDR correction within each of 3 families.
- **Part B**: 2x2 permutation ANOVA (if_PTSD x if_antipsychotic) with Type II SS. 10,000 permutations per DV. BH-FDR correction applied separately per effect x family (9 correction rounds: 3 effects x 3 families, 4 p-values each). Post-hoc simple effects computed only if interaction survives BH correction.

## 3. Part A: Group Comparisons (Antipsychotic vs No-Antipsychotic)

### Descriptive Patterns

Across all three metric families, the antipsychotic group showed numerically higher means than the no-antipsychotic group:

- **Mean Dwell %**: Anti group showed 5–10 percentage points higher dwell time across all threat categories (e.g., soldiers: 32.6% vs 22.8%)
- **Std Dwell %**: Nearly identical between groups (differences < 2 percentage points)
- **Mean Visits**: Anti group slightly higher across all categories (differences 0.1–0.3 visits)

### Assumption Checks

- **Normality**: 11 of 12 DVs met normality in both groups (Shapiro-Wilk p > .05). Exception: mean_dwell_pct_anxiety_inducing (No-Anti group non-normal).
- **Homogeneity of variance**: All 12 DVs passed Levene's test.
- **Tests used**: Student's t-test for 11 DVs; Mann-Whitney U for 1 DV (anxiety_inducing dwell).

### Results

**No significant results across any family after BH-FDR correction.**

| Family | DV | Test | Stat | p_raw | p_BH | Effect Size [95% CI] |
|---|---|---|---|---|---|---|
| **F1: Mean Dwell %** | | | | | | |
| | angry_face | Student's t | 1.399 | .173 | .173 | d = 0.52 [-0.50, 1.54] |
| | anxiety_inducing | Mann-Whitney U | 137.0 | .169 | .173 | r = -0.30 [-0.60, 0.07] |
| | warfare | Student's t | 1.605 | .120 | .173 | d = 0.60 [-0.51, 1.70] |
| | soldiers | Student's t | 1.902 | .068 | .173 | d = 0.71 [-0.51, 1.93] |
| **F2: Std Dwell %** | | | | | | |
| | angry_face | Student's t | -0.189 | .851 | .851 | d = -0.07 [-0.81, 0.66] |
| | anxiety_inducing | Student's t | 1.042 | .307 | .851 | d = 0.39 [-0.52, 1.29] |
| | warfare | Student's t | 0.210 | .835 | .851 | d = 0.08 [-0.66, 0.81] |
| | soldiers | Student's t | 0.460 | .649 | .851 | d = 0.17 [-0.60, 0.94] |
| **F3: Mean Visits** | | | | | | |
| | angry_face | Student's t | 0.810 | .425 | .541 | d = 0.30 [-0.54, 1.14] |
| | anxiety_inducing | Student's t | 0.619 | .541 | .541 | d = 0.23 [-0.57, 1.03] |
| | warfare | Student's t | 1.105 | .279 | .541 | d = 0.41 [-0.51, 1.34] |
| | soldiers | Student's t | 1.328 | .196 | .541 | d = 0.49 [-0.51, 1.49] |

The largest effect sizes were in the Mean Dwell % family (Cohen's d = 0.52–0.71, medium effects), particularly for soldiers (d = 0.71) and warfare (d = 0.60), but none survived multiple comparison correction.

### Figures

![Violin + strip plots](../../figures/e2_medication_attention_moderation/violin_strip_part_a.png)
*Figure 1: Distribution of attention metrics by antipsychotic status across threat categories.*

![Forest plot](../../figures/e2_medication_attention_moderation/forest_plot_part_a.png)
*Figure 2: Effect sizes with 95% CIs for all 12 group comparisons.*

![Bar chart](../../figures/e2_medication_attention_moderation/bar_chart_part_a.png)
*Figure 3: Group means ± 95% CI by antipsychotic status.*

## 4. Part B: Permutation ANOVA (PTSD x Antipsychotic)

### 2x2 Cell Descriptive Patterns

The interaction pattern of interest: whether the antipsychotic effect differs by PTSD status. Numerically, the Anti-vs-No-Anti difference appeared larger within the PTSD group for some DVs (e.g., mean_dwell_pct_warfare: PTSD+Anti = 32.9% vs PTSD+NoAnti = 19.6%, a 13.3 pp difference, compared to NoPTSD+Anti = 24.7% vs NoPTSD+NoAnti = 22.5%, a 2.2 pp difference).

### Assumption Checks

- **Normality**: 10 of 12 DVs had all 4 cells normal; 2 DVs had one non-normal cell (mean_dwell_pct_anxiety_inducing, mean_visits_angry_face).
- **Homogeneity**: All 12 DVs passed Levene's test across 4 cells.
- **Note**: Permutation ANOVA was used regardless, given cell sizes of 6–9.

### Permutation ANOVA Results

**No significant results for any effect after BH-FDR correction.**

#### Main Effect: PTSD

| Family | DV | F | p_perm | p_BH |
|---|---|---|---|---|
| F1: Mean Dwell % | angry_face | 0.37 | .558 | .820 |
| | anxiety_inducing | 0.71 | .404 | .820 |
| | warfare | 0.22 | .650 | .820 |
| | soldiers | 0.05 | .820 | .820 |
| F2: Std Dwell % | angry_face | 3.71 | .063 | .211 |
| | anxiety_inducing | 2.78 | .106 | .211 |
| | warfare | 0.01 | .910 | .994 |
| | soldiers | 0.00 | .994 | .994 |
| F3: Mean Visits | angry_face | 0.67 | .424 | .758 |
| | anxiety_inducing | 0.33 | .569 | .758 |
| | warfare | 0.51 | .488 | .758 |
| | soldiers | 0.00 | .982 | .982 |

#### Main Effect: Antipsychotic

| Family | DV | F | p_perm | p_BH |
|---|---|---|---|---|
| F1: Mean Dwell % | angry_face | 1.89 | .189 | .189 |
| | anxiety_inducing | 2.03 | .169 | .189 |
| | warfare | 2.54 | .125 | .189 |
| | soldiers | 3.35 | .084 | .189 |
| F2: Std Dwell % | angry_face | 0.02 | .887 | .887 |
| | anxiety_inducing | 1.24 | .276 | .887 |
| | warfare | 0.04 | .837 | .887 |
| | soldiers | 0.20 | .655 | .887 |
| F3: Mean Visits | angry_face | 0.67 | .426 | .555 |
| | anxiety_inducing | 0.38 | .555 | .555 |
| | warfare | 1.27 | .275 | .549 |
| | soldiers | 1.67 | .212 | .549 |

#### Interaction: PTSD x Antipsychotic

| Family | DV | F | p_perm | p_BH |
|---|---|---|---|---|
| F1: Mean Dwell % | angry_face | 0.04 | .852 | .852 |
| | anxiety_inducing | 0.61 | .444 | .852 |
| | warfare | 1.00 | .323 | .852 |
| | soldiers | 0.16 | .691 | .852 |
| F2: Std Dwell % | angry_face | 0.03 | .858 | .929 |
| | anxiety_inducing | 0.44 | .511 | .929 |
| | warfare | 0.11 | .744 | .929 |
| | soldiers | 0.01 | .929 | .929 |
| F3: Mean Visits | angry_face | 0.19 | .660 | .860 |
| | anxiety_inducing | 0.03 | .860 | .860 |
| | warfare | 1.60 | .217 | .840 |
| | soldiers | 0.68 | .420 | .840 |

**Post-hoc**: Not performed (no significant interactions).

### Figures

![Interaction plots](../../figures/e2_medication_attention_moderation/interaction_plots_part_b.png)
*Figure 4: Interaction plots showing cell means ± SE for PTSD x Antipsychotic across all DVs.*

![Heatmap](../../figures/e2_medication_attention_moderation/heatmap_pvalues_part_b.png)
*Figure 5: Heatmap of BH-corrected permutation p-values for all DVs x effects.*

## 5. Summary & Interpretation

### Key Findings

1. **No significant group differences** in Part A (Antipsychotic vs No-Antipsychotic) after BH-FDR correction for any of the 12 DVs across 3 families.

2. **No significant main effects or interactions** in Part B (2x2 permutation ANOVA) for any effect or DV after BH-FDR correction.

3. **Descriptive trends**: The antipsychotic group showed numerically higher mean dwell time across all threat categories (medium effect sizes, d = 0.52–0.71), with the largest difference for soldiers. However, these trends did not reach statistical significance.

4. **No evidence of moderation**: The PTSD x Antipsychotic interaction was non-significant for all 12 DVs, suggesting that antipsychotic medication does not differentially affect attention metrics across PTSD status. The numerically larger antipsychotic effect within the PTSD group (e.g., warfare dwell: 13.3 pp vs 2.2 pp difference) did not reach statistical significance.

5. **Attention variability (Std Dwell %)**: Essentially no group differences (d < 0.40), suggesting antipsychotic status does not affect trial-to-trial variability in attention allocation.

### Interpretation of Descriptive Trends

**Why antipsychotics may increase dwell time globally.** The consistent pattern of longer dwell times in the antipsychotic group across all threat categories is plausibly explained by the pharmacological profile of antipsychotic medications. Antipsychotics — particularly second-generation agents common in PTSD treatment — antagonize dopamine D2 receptors and often have anticholinergic and antihistaminergic properties, all of which slow cognitive processing speed. This would manifest in eye-tracking as prolonged fixations: participants on antipsychotics take longer to recognize and process image content before redirecting gaze, resulting in higher dwell percentages on whatever stimulus is currently being viewed. Notably, this effect appears in mean dwell time but not in dwell variability or visit count, consistent with a general slowing of perceptual processing rather than a change in attentional strategy or engagement pattern.

**Why the antipsychotic effect may be amplified in the PTSD group.** The numerically larger antipsychotic-related dwell increase within the PTSD subgroup (e.g., warfare: 13.3 pp difference in PTSD vs 2.2 pp in non-PTSD) may reflect an interaction between medication-induced processing slowdown and PTSD-related attentional capture by threat. In individuals with PTSD, threat-relevant stimuli already command heightened attentional engagement due to hypervigilance and difficulty disengaging from threat cues. When antipsychotic-induced cognitive slowing is layered on top of this attentional capture, the combined effect could be additive or even synergistic: PTSD participants on antipsychotics may both lock onto threat stimuli more readily (due to PTSD) and disengage from them more slowly (due to medication). In contrast, non-PTSD participants lack the threat-capture component, so the medication effect on its own produces only a modest increase in dwell time. This interpretation remains speculative given the non-significant interaction terms and small cell sizes.

### Caveats

- **Very small cell sizes** (n = 6–9) severely limit statistical power; medium effects (d ~ 0.5–0.7) would require n ~ 60–100 per group for 80% power
- **Exploratory analysis** — results are hypothesis-generating, not confirmatory
- **Multiple comparisons** corrected via BH-FDR within families
- **Unbalanced design** (Type II SS used; appropriate for unbalanced factorial designs)
- **Confounding**: Antipsychotic use may be correlated with symptom severity, medication side effects, or other clinical factors not controlled for

## 6. Metadata

| Field | Value |
|---|---|
| Analysis ID | E2 |
| Script | `exploratory_analysis/e2_medication_attention_moderation.py` |
| Dataset | `data/simplified/dataset_eyetracking_metrics_clean.csv` |
| N | 29 (cells: 6/6/9/8) |
| DVs | 12 (3 families x 4 threat categories) |
| Alpha | 0.05 |
| FDR method | BH (Benjamini-Hochberg) |
| Permutations | 10,000 (Part B) |
| Seed | 42 |
| Date | 2026-02-25 |
