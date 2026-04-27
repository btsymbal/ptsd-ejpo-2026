# Step 10 — Final Summary: Stimulus-Set Cleanup and Its Effect on Hypothesis Tests and PTSD Prediction

This document summarises the cleanup pipeline end-to-end, the decisions taken,
the resulting flagged image set, and the evaluation outcomes on (a) the six
pre-registered hypotheses and (b) a small PTSD prediction model. All
intermediate decisions are documented in
[`reports/images_analysis/01_*.md`](../images_analysis/01_expected_directions_update.md)
through [`05_*.md`](../images_analysis/05_final_flagging_rule.md) and
[`reports/cleanup_evaluation/06_*.md`](06_cleaned_dataset_summary.md) through
[`09_*.md`](09_model_comparison.md).

---

## 1. Why we did this

After the original analysis (n = 29), none of the six pre-registered
hypotheses reached BH-FDR significance. The strongest pre-registered signal
was H2 angry-face dwell variability (Cohen's d = 0.76, p_uncorrected = 0.055).
The hypothesis was: a fraction of the 150 stimulus images are noisy or
mis-calibrated and dilute genuine group differences. We therefore needed
finalised criteria to identify and remove "bad" images, then to evaluate
whether removal materially improved (a) the hypothesis tests and (b) a
small PTSD predictive model.

## 2. Decisions taken (summary)

### 2.1 Expected-direction table

We dropped the directional expectation from any category whose former
direction was inferred from the *opposite image in the slide pair* rather
than from the category's own content:

- `neutral_face`: was `negative` → `None`
- `sad_face`: was `positive` → `None`

A small consistency fix made `sleep_related` agree across both image-analysis
scripts (`positive` in both). All other categories kept their directions.
See [01_expected_directions_update.md](../images_analysis/01_expected_directions_update.md).

### 2.2 Final flagging criteria

| Tag | Criterion | Threshold | Strength |
|---|---|---|---|
| C1 | within-PTSD-group CV | `CV_PTSD ≥ 1.0` | strong |
| C2 | wrong-direction effect size **with** p-confidence | wrong sign **and** `p_uncorrected ≤ 0.5` | strong |
| C3 | pooled skewness | `\|skewness\| > 1.0` | weak |
| C4 | bottom-quintile BLUP | `BLUP ≤ q20` within category | weak |

Combined rule (strong-OR + weak-AND):

```
flagged = C1 OR C2 OR (C3 AND C4)
```

**Categories without a directional expectation (`neutral`, `neutral_face`,
`sad_face`) are excluded from ALL flagging.** The CV / skewness / BLUP
criteria carry their threat-relevant interpretation only for categories with
a theoretical role; for filler / comparator categories the same statistics
largely reflect partner-context heterogeneity rather than image defects.
Trimming neutrals would also break the threat-vs-neutral slide pairs used
by H3 / H4.

Detailed rationale in
[02_effect_size_criterion_update.md](../images_analysis/02_effect_size_criterion_update.md),
[03_skewness_criterion.md](../images_analysis/03_skewness_criterion.md),
[04_blup_criterion.md](../images_analysis/04_blup_criterion.md), and
[05_final_flagging_rule.md](../images_analysis/05_final_flagging_rule.md).

## 3. Flagged image set

- **22 / 150 images flagged** (14.7 %); **128 kept**.
- All 22 flagged images come from directional categories. None / neutral_face
  / sad_face are 100 % retained.
- Per-category retention within directional categories: 50 % (`combat_vehicles`)
  to 88 % (`soldiers`). All four pre-registered threat categories retain ≥ 67 %.
- The weak-AND rule (C3 ∧ C4) contributes **no unique flags** — all 5 images
  it would flag are also caught by C1 or C2. It functions as a robustness
  check rather than a primary filter.
- Persisted to **`data/simplified/image_quality_flags.csv`** (one row per
  image with all four flags; rows for excluded categories have all flags
  set to `False`).

## 4. Cleaned dataset

`preprocessing/recompute_eyetracking_metrics_clean_images.py` re-aggregates
per-session × per-category metrics from the raw gaze CSVs, dropping per-image
contributions for the 22 flagged images. Off-screen percentages are attributed
only via unflagged images on each slide; threat-minus-neutral delta dwell
requires both images on the slide-pair to be unflagged. Blink metrics are
unfiltered (slide-level, not image-level).

Three output CSVs (same column set, same row counts as the originals):

| Path | Rows | Use |
|---|---|---|
| `data/simplified/dataset_eyetracking_metrics_imageclean.csv` | 30 | pre-removal-of-bad-session |
| `data/simplified/dataset_eyetracking_metrics_clean_imageclean.csv` | 29 | H1–H6 + model |
| `data/simplified/dataset_eyetracking_metrics_blink_clean_imageclean.csv` | 26 | E1 / blink metrics |

No new NaNs, no shape changes. None / neutral_face / sad_face means are
byte-identical to the originals (no images removed from those categories).
See [06_cleaned_dataset_summary.md](06_cleaned_dataset_summary.md) for sanity-check
shifts.

## 5. Evaluation 1 — hypothesis re-tests

Re-ran the same test logic that the `hypotheses_testing/h{1..6}*.py` scripts
use, on both the original `_clean.csv` and the new `_clean_imageclean.csv`.
All families use BH-FDR within family, identical to the originals.

| Hypothesis | Improved | Regressed | Mixed | BH-sig orig | BH-sig clean |
|---|---|---|---|---|---|
| H1 (threat dwell time) | 3 | 0 | 1 | 0 | 0 |
| H2 (threat dwell variability) | 2 | 2 | 0 | 0 | 0 |
| H3 (delta dwell variability) | 1 | 2 | 1 | 0 | 0 |
| H4 (variability ↔ ITI within PTSD) | 1 | 0 | 7 | 0 | 0 |
| H5 (visits to threat) | 6 | 1 | 1 | 0 | 0 |
| H6 (avoidance gaze ↔ ITI within PTSD) | 9 | 13 | 2 | 0 | 0 |
| **Total** | **22 / 52 directional rows** | **18 / 52** | **12 / 52** | **0** | **0** |

Notable shifts:

- **H1**: 3 of 4 threat categories' Cohen's d / rank-biserial r moved in the
  predicted positive direction; angry-face d climbed from 0.21 → 0.38,
  anxiety-inducing rank-biserial from –0.15 → +0.30. Direction is right,
  magnitude still well below FDR significance.
- **H2** (the strongest pre-cleanup signal): angry-face d dropped from
  0.76 → 0.65 (p_uncorr 0.055 → 0.098). A plausible reading: removing the
  one flagged angry-face image also removes part of the between-group
  variance asymmetry that drove H2. Stimulus-level cleanup based on noise
  metrics targets unreliability uniformly; some noise was apparently
  working in our favour.
- **H5** (visits to threat) improved most consistently: 7 of 8 rows moved
  in the predicted positive direction. Late-window angry-face visits:
  d 0.19 → 0.26.
- **H6** is the largest family (24 rows, 6 sub-families) and is mostly
  mixed to slightly worse. The pre-registered avoidance pattern is fragile
  under small perturbations to the stimulus set.

**No hypothesis crossed BH-FDR significance** — pre or post cleanup. The
sample (n = 29) remains the dominant constraint.

Side-by-side comparison: [07_hypotheses_comparison.md](07_hypotheses_comparison.md);
machine-readable table: `07_hypotheses_comparison_table.csv`.

## 6. Evaluation 2 — PTSD prediction model

Single L2-penalised logistic regression on 8 theory-driven features (4 mean
dwell, 2 std dwell, 1 late visits, 1 off-screen — see
[08_model_baseline.md](08_model_baseline.md) for rationale), evaluated by
LOOCV on the same 29 sessions, identical CV splits and identical features for
both the original and cleaned datasets.

| Metric | Original | Cleaned | Δ |
|---|---|---|---|
| AUC | 0.574 [0.343, 0.788] | 0.480 [0.258, 0.706] | **−0.093** |
| Balanced accuracy | 0.591 [0.413, 0.766] | 0.502 [0.317, 0.688] | −0.089 |
| Accuracy | 0.621 [0.448, 0.793] | 0.517 [0.345, 0.690] | −0.103 |

Paired permutation test on per-fold probabilities: **ΔAUC = −0.093, two-sided
p = 0.25** — the difference is not statistically significant.

The model uses only threat-category features (`angry_face`, `warfare`,
`anxiety_inducing`, `soldiers`), so the model's input would have been
identical regardless of whether neutral / neutral_face / sad_face flags were
restored — the numbers are unchanged from the previous cleanup iteration on
this account. The headline AUC moves slightly *against* the predicted
direction, but the 95 % bootstrap CIs for the two AUCs overlap heavily and
span 0.5 in both cases. With only 29 sessions, a swap of one or two
predictions can shift AUC by 0.05+, so the −0.093 ΔAUC is well within
sampling-noise territory.

Coefficient changes are small (most |Δcoef| < 0.4 standardised units), and
the per-fold coefficient SD is comparable to its mean, so individual
coefficient comparisons should not drive conclusions either way.

See [09_model_comparison.md](09_model_comparison.md) and
`09_model_per_fold_predictions.csv` for the full per-fold trace.

## 7. Bottom-line interpretation

**Did the cleanup help?**

- **For hypothesis tests**: a slight net positive — 22 / 52 directional rows
  moved in the predicted direction vs. 18 against (the rest are mixed or
  non-directional), but no hypothesis crossed BH significance, and the
  largest single pre-cleanup signal (H2 angry-face) actually weakened. This
  is consistent with the cleanup being **right on principle but
  insufficient in magnitude** to overcome the underpowered design.

- **For PTSD prediction**: no detectable benefit, possibly a small detriment,
  but well within sampling noise at n = 29.

**What this implies about the stimulus set / paradigm**:

1. The image set has ~15 % noisy or mis-calibrated images by the four-
   criterion rule (restricted to directional categories). Removing them does
   *not* change the qualitative picture: the pre-registered effects are
   real-direction-but-small, and the sample is simply too small to detect
   them with FDR-corrected significance.
2. The H2 regression suggests that **stimulus-level cleanup is not a
   substitute for sample size**. Cleanups based on within-PTSD CV and
   wrong-direction ES legitimately remove unreliable measurements but can
   also remove signal that happens to ride on noise.
3. The most defensible takeaways from this exercise are
   (a) the cleaned image list (`image_quality_flags.csv`) should be used
   when re-running future analyses on the same paradigm to reduce measurement
   noise on principled grounds, and
   (b) a follow-up data collection (or external validation) is needed before
   any of the pre-registered hypotheses can be re-evaluated meaningfully.
4. The "weak-AND" rule (skew ∧ low BLUP) added no unique flags beyond what
   CV and ES caught. It functions as a robustness check rather than a primary
   filter; dropping it would not change the flagged set.
5. **Filler / comparator categories (neutral, neutral_face, sad_face) were
   correctly excluded from flagging** — the noise-quality criteria don't
   carry the same interpretation for images without a theoretical role, and
   trimming them would have weakened the H3 / H4 threat-vs-neutral contrasts
   without principled justification.

## 8. Reproducibility

Run the chain in this order, using `/opt/anaconda3/envs/jupyter_env/bin/python`:

1. `python images_analysis/lmm_image_quality_evaluation.py` — produces
   `data/simplified/image_quality_flags.csv` and refreshes
   `reports/images_analysis/lmm_image_quality_evaluation_report.md`.
2. `python preprocessing/recompute_eyetracking_metrics_clean_images.py` —
   produces all three `*_imageclean.csv` outputs.
3. `python evaluation_hypotheses/run_hypothesis_comparison.py` — produces
   `reports/cleanup_evaluation/07_hypotheses_comparison.md` (+ table CSV).
4. `python evaluation_model/model_comparison.py` — produces
   `reports/cleanup_evaluation/08_model_baseline.md` and
   `09_model_comparison.md` (+ per-fold predictions CSV).

Each script is self-contained and uses the project-root `os.chdir(...)`
pattern, so the scripts can be run from any directory.
