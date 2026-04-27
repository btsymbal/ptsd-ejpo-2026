# Step 3 — Pooled Skewness Criterion (C3)

## Decision

We added a third (weak) criterion based on the **pooled** skewness of an image's
dwell-time distribution across all participants (PTSD + no-PTSD combined):

```python
flag_skew = abs(skewness) > SKEW_THRESHOLD     # SKEW_THRESHOLD = 1.0
```

## Rationale

If one image has a highly skewed dwell-time distribution across all participants,
nearly everyone reacts to it the same way — either everyone barely looks at it
(strong right skew because most participants pile up near 0) or everyone fixates
on it (strong left skew). In both cases the image cannot discriminate between
PTSD and no-PTSD groups, since the response is uniform regardless of group
membership. This is similar in spirit to the CV criterion (C1) but operates on
distributional shape rather than dispersion, and uses the *pooled* sample
because we want a property of the image itself.

The threshold `|skewness| > 1.0` matches the existing default in
`distributional_properties_dwell_time.py` and the prior report — it cleanly
separates 29/150 images (≈ 19 %) that visibly fail visual inspection of the
distribution.

C3 is treated as a **weak** criterion: skewness alone does not necessarily
indicate a useless image (a moderately skewed distribution can still
discriminate groups if the tails are systematically different across groups).
We therefore require C3 to **co-occur with C4** (low engagement BLUP) before
it triggers a flag — see Step 4 and Step 5.

## Scope

C3 is only evaluated for categories with a directional expectation
(`EXPECTED_SIGN[cat] is not None`). For baseline / filler categories
(`neutral`, `neutral_face`, `sad_face`) the same statistic is uninformative —
high skewness on a neutral image largely reflects partner-context heterogeneity
across slides rather than a defect of the image itself. See Step 5 for the
broader exclusion rationale.

## Counts

- **29 / 150** images have `|skew| > 1.0` overall (from `data/output/distributional_properties_per_image.csv`).
- **12** of those fall in directional categories — these are the images
  potentially flagged by C3 (the rest are in excluded categories).
- Per directional category:

| Category | n_images | C3 fires | % |
|---|---|---|---|
| angry_face | 10 | 2 | 20 % |
| anxiety_inducing | 14 | 3 | 21 % |
| combat_vehicles | 8 | 3 | 38 % |
| happy_event | 9 | 0 | 0 % |
| happy_face | 11 | 2 | 18 % |
| sleep_related | 7 | 1 | 14 % |
| soldiers | 8 | 0 | 0 % |
| warfare | 12 | 1 | 8 % |

(Excluded categories: `neutral` 12 skewed, `neutral_face` 3, `sad_face` 2 — none counted toward C3.)

## Files modified

- [`images_analysis/lmm_image_quality_evaluation.py`](../../images_analysis/lmm_image_quality_evaluation.py) — added `SKEW_THRESHOLD = 1.0` constant; wired `dist_df['skewness']` through the merge into the flagging block; computed `flag_skew`
