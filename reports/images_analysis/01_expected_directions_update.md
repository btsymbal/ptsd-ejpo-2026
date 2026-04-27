# Step 1 — Update of Expected-Direction Table

## Decision

We removed the directional expectation from any category whose expected sign was
inferred from the **opposite image in the slide pair**, rather than from a
direct hypothesis about how PTSD changes attention to that category itself.

The reasoning: in this paradigm two images appear side-by-side per slide, but
participants can also look outside both images (off-screen / between images).
"PTSD looks more at A" therefore does **not** mathematically imply
"PTSD looks less at B" — total dwell time is not constrained to the two AOIs.
A directional expectation should be motivated by the category's own content
(e.g. angry faces trigger hypervigilance, happy events fail to engage an
anhedonistic mood), not by what its slide-mate is doing.

## Categories affected

Two expectations were removed:

| Category | Old sign | Old rationale | New sign | Reason for change |
|---|---|---|---|---|
| `neutral_face` | `negative` | "hypervigilance to threat (opposite image)" | `None` | Opposite image is angry/sad; no direct content-based prediction for neutral faces themselves |
| `sad_face` | `positive` | "anhedonistic subtype (opposite image)" | `None` | Opposite image is happy; no direct content-based prediction for sad faces themselves |

A small consistency fix was also applied: `dwell_time_group_comparisons.py`
listed `sleep_related` as `None` while `lmm_image_quality_evaluation.py`
listed it as `positive`. Both files now agree on `'positive'` (PTSD group
expected to dwell longer due to sleep-related symptoms).

## Updated table (authoritative)

| Category | Expected sign | Rationale | Direct or inferred? |
|---|---|---|---|
| angry_face | positive | hypervigilance to threat | direct |
| anxiety_inducing | positive | hypervigilance to potential (hidden) threat | direct |
| combat_vehicles | positive | emotionally driven memories | direct |
| happy_event | negative | anhedonistic subtype | direct |
| happy_face | negative | anhedonistic subtype | direct |
| neutral | — | no consistent pattern (paired with diverse images) | — |
| neutral_face | — | no direct expectation (former direction was inferred from opposite threat image) | dropped |
| sad_face | — | no direct expectation (former direction was inferred from opposite happy image) | dropped |
| sleep_related | positive | PTSD group expected to dwell longer due to sleep-related symptoms | direct |
| soldiers | positive | hypervigilance to threat | direct |
| warfare | positive | hypervigilance to threat | direct |

## Implication for flagging

- Effect-size–based flagging (criterion C2, see Step 2) requires a directional
  expectation. With this update, **C2 will no longer fire on `neutral_face`
  or `sad_face` images** — they can only be flagged via the noise-based
  criteria (C1 = CV, or C3 ∧ C4 = skewness ∧ low-engagement BLUP).
- This is the intended consequence: we never had a defensible direct
  prediction about how PTSD should engage with these two categories, so we
  should not treat "wrong-direction effect" as a quality failure for them.

## Files modified

- [`images_analysis/lmm_image_quality_evaluation.py`](../../images_analysis/lmm_image_quality_evaluation.py) — `EXPECTED_SIGN` and `EXPECTED_RATIONALE` updated
- [`images_analysis/dwell_time_group_comparisons.py`](../../images_analysis/dwell_time_group_comparisons.py) — same two dicts and the markdown comment block above them updated for consistency
