# Step 2 — Effect-Size Criterion (C2) with p-value Confidence Gate

## Decision

The previous effect-size flag fired on **any** wrong-direction effect, regardless
of the test's p-value. A wrong-direction effect from a test with `p_uncorrected = 0.99`
is statistical noise, not evidence the image fails its theoretical purpose. We
add a p-value confidence gate:

```python
flag_es = (wrong_direction)  AND  ((1 - p_uncorrected) >= P_CONFIDENCE_MIN)
```

with `P_CONFIDENCE_MIN = 0.5`, i.e. only count wrong-direction effects from
tests with `p_uncorrected ≤ 0.5`. We deliberately do **not** require formal
significance (`p ≤ 0.05`) — given n = 17 PTSD vs n = 12 no-PTSD per image,
that gate would yield essentially zero flags. `p ≤ 0.5` keeps wrong-direction
results that are at least as plausible as chance.

C2 is automatically skipped for categories with no directional expectation
(`neutral`, `neutral_face`, `sad_face` after Step 1) — the function returns
`False` when `EXPECTED_SIGN[cat] is None`.

## Quantitative impact

|  | Old C2 (no p-gate, prior expected dirs) | New C2 (p ≤ 0.5, updated dirs) |
|---|---|---|
| Total ES flags | 38 | **8** |

Of the 30 images that *were* ES-flagged but no longer are, the breakdown by reason:

| Reason | Count | Notes |
|---|---|---|
| `neutral_face` lost expectation (Step 1) | 8 | All 8 wrong-direction `neutral_face` flags removed |
| `sad_face` lost expectation (Step 1) | 3 | All 3 wrong-direction `sad_face` flags removed |
| Wrong-direction but `p > 0.5` (new gate) | 19 | Most of these had `p_uncorrected > 0.7` |

The remaining 8 flagged images are wrong-direction with `p_uncorrected ≤ 0.5`:

| image_id | category | ES Type | Effect Size | p_uncorrected | Expected |
|---|---|---|---|---|---|
| Byi3ZPboRuWBVDB9i8iTHA | angry_face | Cohen's d | -0.425 | 0.269 | positive |
| fefWMtd9R8KSv7H2BTpIrw | anxiety_inducing | rank-biserial | -0.225 | 0.318 | positive |
| F-zQ4ls4SyqcPxvljy9n0Q | combat_vehicles | Cohen's d | -0.312 | 0.416 | positive |
| 68123428 | happy_face | Cohen's d | +0.262 | 0.492 | negative |
| LT6YQ4czS9Wle5QjrZ76dQ | happy_face | rank-biserial | +0.157 | 0.491 | negative |
| YaLqQjVwQz6vQerO40WDBg | sleep_related | rank-biserial | -0.206 | 0.362 | positive |
| WMKKOlK4QrGOs3Cn2b_lZg | soldiers | rank-biserial | -0.319 | 0.155 | positive |
| R0NAzO_VSdqYLe6zb_H3-Q | warfare | Cohen's d | -0.327 | 0.393 | positive |

These are images where the test was reasonably informative (p ≤ 0.5) **and** the
direction is clearly opposite to theory — the most defensible candidates for
removal on theoretical-validity grounds.

## Edge case

`Jk-2DYfARdOZFHZl54GTYw` (neutral_face) has `Effect_Size = -0.441`,
`p_uncorrected = 0.049` — a strong, near-significant effect. Under the old rule
it was flagged by C2; under the new rule it is **not** flagged by C2 because
neutral_face no longer has a directional expectation. It is still flagged (by
C1, CV = 1.10), so it ends up in the kept-out list either way — but the
flagging *reason* is now noise, not "wrong direction".

## Files modified

- [`images_analysis/lmm_image_quality_evaluation.py`](../../images_analysis/lmm_image_quality_evaluation.py) — added `P_CONFIDENCE_MIN = 0.5` constant; updated `check_es` to add the p-gate
