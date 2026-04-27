# Step 4 — Bottom-Quintile BLUP Criterion (C4)

## Decision

We added a fourth (weakest) criterion based on the per-category LMM image BLUP
(Best Linear Unbiased Predictor) — the image's intercept random effect from the
model `dwell_pct ~ if_PTSD + (1 | image) + VC(participant)` fit separately per
category:

```python
flag_blup = BLUP <= BLUP within-category q20         # BLUP_QUANTILE = 0.20
```

## Rationale & caveats

The intercept BLUP captures each image's deviation from its category mean,
after removing group and participant effects. A low BLUP means the image is
absolutely unengaging compared to its category siblings: people look at it less
than other images of the same kind. An unengaging image contributes little to
the group-discrimination signal — there's nothing to differentiate.

**Important caveat (acknowledged in the script and prior report)**: the
intercept BLUP measures *overall engagement*, not *PTSD-specific response*.
A random-slope LMM `(1 + if_PTSD | image)` would give the latter directly, but
statsmodels' MixedLM did not converge such models reliably in earlier tries.
This is why C4 is treated as the **weakest** criterion and only contributes to
flagging when it co-occurs with C3 (high pooled skewness) — see Step 5.

We use a **within-category** quantile so that categories with naturally lower
engagement are not penalised against more arousing categories. 20 % per
category gives roughly 1–3 candidate images per directional category.

## Scope

Like C3, C4 is only evaluated for categories with a directional expectation.
For `neutral`, `neutral_face`, `sad_face`, BLUP simply measures relative
engagement among siblings of varying partner contexts — low engagement on a
neutral filler is not a quality defect, it's expected behaviour. See Step 5.

## Per-category BLUP cutoffs

| Category | BLUP q20 cutoff | n_flag (bottom quintile) | Eligible for flagging? |
|---|---|---|---|
| angry_face | -1.10 | 2 | yes |
| anxiety_inducing | -1.42 | 3 | yes |
| combat_vehicles | -1.44 | 2 | yes |
| happy_event | -2.25 | 2 | yes |
| happy_face | -1.88 | 3 | yes |
| neutral | -1.08 | 0 | **no — excluded** |
| neutral_face | -1.67 | 0 | **no — excluded** |
| sad_face | -1.10 | 0 | **no — excluded** |
| sleep_related | -1.70 | 2 | yes |
| soldiers | -1.24 | 2 | yes |
| warfare | -1.93 | 3 | yes |

Total bottom-quintile candidates in directional categories: **19**.
Within those, **5** also have `|skewness| > 1.0` (i.e. C3 ∧ C4 fires for 5 images).

## How it actually contributes

C4 alone never flags an image — the combined rule (Step 5) requires
`C3 ∧ C4`. Of the 5 images where both fire, **0** are not already flagged by
C1 or C2 — i.e. the weak-AND rule contributes no unique flags in the final
set. It still serves as a robustness check: it confirms that the noisy or
wrong-direction images flagged by C1/C2 also tend to be unengaging and skewed,
giving a coherent multi-criterion picture.

## Files modified

- [`images_analysis/lmm_image_quality_evaluation.py`](../../images_analysis/lmm_image_quality_evaluation.py) — added `BLUP_QUANTILE = 0.20` constant; computed `flag_blup` per category from `cat_data['BLUP'].quantile(0.20)`
