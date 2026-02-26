# Summary of Exploratory Analyses (E1–E3)

## 1. Overview

Three exploratory analyses extended beyond the pre-registered hypotheses (H1–H6) to investigate blink metrics (E1), medication effects on attention (E2), and temporal dynamics of attentional bias (E3). All produced null results after Benjamini-Hochberg FDR correction. Each was motivated by specific theoretical or methodological questions that emerged during preanalysis, and each surfaced design insights valuable for future work.

---

## 2. E1: Blink Metrics

**Sample**: N = 26 (PTSD n = 15, No-PTSD n = 11; blink-clean dataset after quality exclusions)

### Rationale

The preanalysis overview revealed two challenges: (1) structural missingness in blink duration/latency columns (n = 14–26 undefined values per category, from zero-blink sessions), and (2) high intercorrelation among per-category blink rates (r = 0.43–0.97, median ~0.85). To address this, 8 metrics were selected: 4 global summaries (complete data, no missingness) and 4 per-category threat blink rates.

### Key Results

- **Total blink count** showed the largest group effect (d = 0.84, p_uncorr = .044, p_BH = .088): PTSD M = 28.7 vs No-PTSD M = 16.1. Did not survive FDR correction.
- **Per-category blink rates** showed consistent small-to-medium effects across all 4 threat categories (r = −0.25 to −0.45), with higher rates in the PTSD group. None survived correction (all p_BH = .128).
- **Within-PTSD correlations**: Mean blink duration trended negatively with ITI severity (Kendall's tau = −0.37, p_uncorr = .062, p_BH = .062), suggesting higher-severity PTSD may be associated with shorter blinks. No other correlations approached significance.

### Limitations and Interpretation

- **Possible blink under-detection**: Sample median blink rate (6.0/min) was well below typical adult rates (15–20/min), suggesting the eye tracker may have under-detected blinks or that the task itself induced blink suppression.
- **Redundancy of category rates**: High intercorrelation (r = 0.43–0.97) suggests individual blink tendencies dominate over stimulus-specific responses. The consistent direction across threat categories likely reflects overall blink propensity rather than category-specific effects.
- **Non-normal distributions** required non-parametric tests (Mann-Whitney U for blink rates, Kendall's tau for all correlations), which have lower power at n = 15/11.
- **ITI_PTSD non-normality** (Shapiro-Wilk p = .009) further constrained correlational analysis to rank-based methods.

---

## 3. E2: Medication–Attention Moderation

**Sample**: N = 29; 2 x 2 design (PTSD x Antipsychotic) with cell sizes n = 6–9

### Rationale

Antipsychotic medication is common in PTSD treatment and may independently affect visual attention through dopamine D2, anticholinergic, and antihistaminergic mechanisms. Given this potential confound, it was important to examine whether antipsychotic status moderates attention to threat-related stimuli.

### Key Results

- **Antipsychotic group** showed numerically higher mean dwell time across all threat categories (d = 0.52–0.71); the soldiers category had the strongest effect (d = 0.71, p = .068). None survived BH-FDR correction.
- **No differences in dwell variability or visit counts** (d < 0.40 for std dwell %; d = 0.23–0.49 for visits), consistent with a general processing slowdown rather than a change in attentional strategy.
- **2 x 2 permutation ANOVA** (10,000 permutations): No significant main effects or interactions. The strongest effect was a PTSD main effect on std_dwell_pct_angry_face (F = 3.71, p_perm = .063, p_BH = .211).
- **Descriptive interaction pattern**: The antipsychotic-related dwell increase appeared numerically larger within the PTSD subgroup (e.g., warfare: 13.3 pp difference in PTSD vs 2.2 pp in No-PTSD), but the interaction term was non-significant.

### Limitations and Interpretation

- **Catastrophically underpowered**: Cell sizes of n = 6–9 provide negligible power for a factorial design (need ~60–100 per group for medium effects of d ~ 0.6).
- **Plausible pharmacological mechanism**: Antipsychotic-induced D2/anticholinergic/antihistaminergic processing slowdown would prolong fixations globally, consistent with the observed pattern of increased dwell time without changes in variability or visit count.
- **Confounding**: Antipsychotic use correlates with symptom severity, medication side effects, and other clinical factors not controlled for in this analysis.
- **Potential PTSD x medication synergy**: PTSD-related threat capture combined with medication-induced processing slowdown could produce additive dwell increases. The numerically larger antipsychotic effect within the PTSD group is consistent with this, but the interaction was non-significant and needs testing with adequate sample sizes.

---

## 4. E3: Temporal Dynamics of Threat Bias

**Sample**: N = 29 (PTSD n = 17, No-PTSD n = 12)

### Rationale

Zvielli et al. (2015) and Schafer et al. (2016) demonstrated that within-session temporal dynamics of attentional bias carry diagnostic information beyond aggregate scores. Trial-Level Bias Score (TL-BS) variability indices — session SD, peak toward/away, and range — may differentiate groups when aggregate means do not.

### Key Results

- **Group trajectories** across 44 threat trials largely overlapped, with both groups showing generally positive threat bias (dwell on threat > neutral).
- **All 5 TL-BS indices** were non-significant after correction. The largest effect was peak_toward (d = 0.386, p_BH = .862).
- **Individual spaghetti plots** showed massive within-session variability in both groups, with trajectories oscillating widely around zero.

### Limitations and Interpretation

Two design features likely drove the null results:

1. **Non-contiguous threat trials**: The 44 threat–neutral slides were interspersed among 75 total slides (31 non-threat slides omitted from analysis). Treating them as contiguous (trial_index 1–44) breaks the assumption of continuous temporal evolution from Zvielli et al., where consecutive trials were all bias-relevant. The intervening non-threat content likely reset or disrupted any accumulating attentional pattern.

2. **Trauma-exposed comparison group**: The No-PTSD group consisted of soldiers with potential trauma exposure but no PTSD diagnosis. Unlike civilian controls, these individuals may exhibit similar threat-related attentional dynamics (hypervigilance, variable engagement with threat stimuli), making TL-BS indices indistinguishable between groups.

Additionally, **fixed trial order** confounds temporal position with stimulus category, preventing clean separation of time effects from content effects.

---

## 5. Common Limitations

- **Small samples** (N = 26–29) across all three explorations, yielding wide confidence intervals and low statistical power for the observed effect sizes.
- **BH-FDR correction** was appropriate and applied within metric families, but multiple comparison correction is inherently costly with small N and medium effects.
- **Exploratory by design**: All three analyses were hypothesis-generating, not confirmatory. Results should inform future study design, not be interpreted as definitive null findings.
- **Specialised sample**: All participants were military personnel. Findings may not generalise to civilian PTSD populations or other trauma-exposed groups.

---

## 6. Conclusion

These exploratory analyses confirm the statistical power constraints identified during hypothesis testing — the sample size is insufficient to detect the medium effects consistently observed in descriptive trends. Beyond this shared limitation, each exploration surfaced specific methodological insights:

- **E1** identified possible blink under-detection by the eye tracker (median rate well below population norms) and demonstrated that per-category blink rates are near-redundant due to high intercorrelation.
- **E2** revealed a plausible antipsychotic confound on dwell time metrics that should be controlled for in future studies, and highlighted the possibility of PTSD x medication synergy in threat processing.
- **E3** exposed a critical design assumption violation: applying TL-BS temporal analysis to non-contiguous threat trials likely invalidates the method's theoretical basis.

These insights are directly actionable for future study design: larger samples, blink detection validation, medication stratification, contiguous trial designs, and civilian control groups would address the specific limitations identified here.

---

**Source reports**:
- [E1: Blink Metrics Exploration](../exploratory_analysis/e1_blink_metrics_exploration.md)
- [E2: Medication-Attention Moderation](../exploratory_analysis/e2_medication_attention_moderation.md)
- [E3: Temporal Dynamics of Threat Bias](../exploratory_analysis/e3_temporal_dynamics_threat_bias.md)

**Date**: 2026-02-26
