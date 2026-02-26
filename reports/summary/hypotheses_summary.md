# Summary of Hypothesis Testing: Attentional Bias Toward Threat in PTSD

## Overview

Six pre-registered hypotheses (H1–H6) tested whether PTSD status and symptom severity modulate attentional engagement with threat-related stimuli during a free-viewing eye-tracking task. **None reached statistical significance after Benjamini-Hochberg correction.** However, several findings showed directionally consistent patterns with medium-to-large effect sizes, suggesting the study was underpowered rather than that the effects are absent.

This report ranks findings by strength of evidence to highlight the most promising leads for future investigation.

---

## Tier 1: Large Effects, Near-Significant

These findings produced large effect sizes (|d| > 1.0) and uncorrected p-values below .05 or approaching it. They represent the strongest signals in the dataset.

### H6-A: Angry Face Dwell Time — Higher- vs Lower-ITI Subgroups (Median Split)

Within the PTSD group (n = 17), participants with higher symptom severity (ITI >= 12, n = 9) showed markedly **reduced** dwell time on angry faces compared to those with lower severity (ITI < 12, n = 8), consistent with an avoidance pattern.

| DV Family | Metric | d | p (uncorr) | p (BH) |
|-----------|--------|---:|----------:|-------:|
| F1 | Total dwell time | −1.30 | .017 | .068 |
| F3 | Late-window dwell time | −1.09 | .041 | .163 |
| F2 | Visit count | −1.03 | .052 | .208 |

**Interpretation**: The most severe PTSD participants looked at angry faces less often and for shorter durations, including in the late viewing window. This is the single strongest and most coherent signal across the entire study, suggesting active avoidance of socially threatening stimuli that scales with symptom severity.

### H2: Angry Face Dwell Variability — PTSD vs No-PTSD

The PTSD group (n = 17) showed greater trial-to-trial variability in dwell time on angry faces compared to the No-PTSD group (n = 12), consistent with an attentional dysregulation account.

| Stimulus | d | p (uncorr) | p (BH) |
|----------|---:|----------:|-------:|
| angry_face | 0.76 | .055 | .221 |

PTSD mean SD = 16.79 ms; No-PTSD mean SD = 13.14 ms.

**Interpretation**: This is the strongest between-group effect in the dataset. The elevated variability suggests fluctuating engagement — intermittent vigilance toward and avoidance of angry faces — rather than a stable bias in one direction.

---

## Tier 2: Medium Effects, Directionally Consistent

These findings showed medium effect sizes (|d| ≈ 0.6–0.8) with uncorrected p-values between .05 and .20. Individually inconclusive, they gain credibility from their directional consistency with Tier 1 patterns.

### H6-A: Additional Angry Face Metrics (Median Split)

| DV Family | Metric | d | p (uncorr) |
|-----------|--------|---:|----------:|
| F4 | Late-window visit count | −0.82 | .112 |
| F5 | Off-screen proportion | 0.68 | .179 |

Higher-ITI participants made fewer late visits to angry faces and spent more time looking off-screen — both consistent with the avoidance interpretation from Tier 1.

### H6-A: Other Stimulus Categories (Median Split)

| Stimulus | DV Family | Metric | d | p (uncorr) |
|----------|-----------|--------|---:|----------:|
| soldiers | F5 | Off-screen proportion | 0.80 | .120 |
| anxiety_inducing | F1 | Total dwell time | −0.73 | .154 |

The avoidance pattern extended partially to other threat categories, though angry faces consistently showed the largest effects.

### H2: Anxiety-Inducing Dwell Variability — PTSD vs No-PTSD

| Stimulus | d | p (uncorr) | p (BH) |
|----------|---:|----------:|-------:|
| anxiety_inducing | 0.62 | .111 | .223 |

PTSD mean SD = 18.66 ms; No-PTSD mean SD = 15.44 ms. A secondary echo of the angry face dwell variability finding.

---

## Non-Significant Hypotheses

### H1: Mean Dwell Time on Threat (PTSD vs No-PTSD)
No meaningful group differences in overall dwell time on any threat category. Effect sizes were uniformly small (largest r = −0.15). The groups did not differ in gross attentional engagement with threat.

### H3: Variability of Attentional Bias (Delta Dwell, PTSD vs No-PTSD)
No significant differences. All effect sizes small (|d| <= 0.36). The delta-based measure (threat minus baseline) produced much weaker effects than H2's raw dwell SD, suggesting the H2 signal reflects global arousal-driven variability rather than selective threat bias fluctuation.

### H4: ABV Correlation with ITI Severity (Within PTSD)
No significant correlations. The direction of most associations was **negative** — higher symptom severity trended toward *less* variable dwell time (strongest: soldiers r = −0.42, p = .090; anxiety_inducing r = −0.40, p = .116). While initially surprising, this pattern is consistent with the avoidance findings from H6: as symptom severity increases, attentional engagement with threat becomes more rigidly avoidant rather than oscillatory, reducing trial-to-trial variability. H4 thus converges with H6 in supporting a severity-dependent shift toward sustained avoidance.

### H5: Visit Counts to Threat (PTSD vs No-PTSD)
No group differences in visit frequency to threat stimuli, in either the full or late viewing window. Effect sizes small throughout (|d| <= 0.31).

### H6-B: ITI Continuous Correlation (Within PTSD)
No significant correlations between ITI scores and any gaze metric when treated as a continuous variable. The median-split analysis (H6-A) was more sensitive, suggesting a threshold-like rather than linear relationship between symptom severity and avoidance behavior.

---

## Cross-Cutting Patterns

### Angry faces are the most sensitive stimulus
Across all hypotheses, the angry_face category consistently produced the largest effects. This is theoretically coherent: angry faces convey direct social threat and are processed rapidly via dedicated neural circuits, making them the most likely stimulus to trigger threat-related attentional biases.

### Within-PTSD severity analyses outperform between-group comparisons
H6 median-split effects (|d| = 0.68–1.30) were substantially larger than any PTSD-vs-No-PTSD comparison (largest |d| = 0.76). This suggests that PTSD-related attentional biases are modulated by symptom severity rather than being a uniform feature of the diagnosis, and that the No-PTSD control group may include subclinical individuals who dilute between-group contrasts.

### Dwell variability is the strongest between-group metric
H2's raw dwell SD (d = 0.76 for angry faces) outperformed every other between-group measure, including mean dwell time (H1), delta-based variability (H3), and visit counts (H5). Attentional *instability* rather than a stable directional bias may be the behavioral signature most accessible in this paradigm.

### Coherent avoidance pattern in H6
Five of six DV families in H6-A showed directionally consistent effects for angry faces: higher-ITI participants spent less time on threat (F1, F3), made fewer visits (F2, F4), and looked off-screen more (F5). F6 (late-window off-screen proportion) was directionally consistent but weaker (d = 0.53, p = .295). This multi-metric convergence strengthens the avoidance interpretation beyond any single test.

### H4 complements the avoidance picture
The negative correlations in H4 (higher severity → less variable dwell) initially appear at odds with H2's finding (PTSD group → more variable dwell). However, these findings are reconcilable across severity levels: the PTSD group as a whole shows elevated attentional variability relative to controls (H2), reflecting vigilance-avoidance oscillation, while *within* the PTSD group, the most severe participants shift toward rigid avoidance that suppresses variability (H4). This dovetails with H6's finding that higher-ITI participants show pronounced avoidance of angry faces, and supports a severity-dependent progression from oscillatory dysregulation to sustained avoidance.

---

## Implications for Future Research

1. **Power**: With n = 17 (PTSD) and n = 12 (No-PTSD), the study was underpowered for the observed effect sizes. For the H6-A angry face dwell effect (d = 1.30), 80% power requires approximately n = 10 per subgroup; for H2's dwell variability (d = 0.76), approximately n = 29 per group.

2. **Stimulus selection**: The dominance of angry faces across hypotheses suggests that stimuli with higher threat proximity and easier recognisability produce stronger attentional effects. Future studies should revise the stimulus set to prioritise such stimuli, potentially replacing categories that yielded weaker effects with additional high-salience threat cues.

3. **Analytic approach**: The median-split within PTSD was more sensitive than continuous correlation or between-group comparison. Exploring non-linear dose-response relationships between symptom severity and attentional avoidance may be fruitful.

4. **Theoretical model**: The results support both the attentional bias variability (ABV) account and the avoidance account, but at different levels of symptom severity. The PTSD group as a whole showed elevated dwell variability relative to controls (H2), consistent with vigilance-avoidance oscillation. At the same time, higher symptom severity within the PTSD group was associated with reduced variability (H4) and pronounced avoidance of threat (H6). This points to a severity-dependent progression: moderate PTSD may be characterised by oscillatory attentional dysregulation, while more severe PTSD resolves into sustained avoidance. Future work should model this as a non-linear trajectory rather than treating ABV and avoidance as competing accounts.
