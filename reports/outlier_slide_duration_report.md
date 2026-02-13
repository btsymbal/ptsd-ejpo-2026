# Outlier Slide Duration Report

## Overview

Two session-slide pairs were flagged as duration outliers during slide duration analysis. This report documents the investigation and the decision on how to handle them.

## Flagged Slides

### 1. DAccofkFpBK00oVonRAi — Slide 35

- **Expected duration**: 2500 ms
- **Observed duration**: 1437 ms (−42.5% deviation)
- **SCENE_INDEX**: 69

**Investigation**: Intra-slide time deltas are regular (~33 ms intervals, consistent with 30 Hz sampling). The slide simply has fewer rows than expected, indicating data loss rather than a recording artifact.

**Slide-boundary timing** (see `routine_exploration/outlier_slide_inspection.py`):

| Measurement | Value |
|---|---|
| Gap before slide 35 (slide 34 → 35) | 1136 ms |
| Gap after slide 35 (slide 35 → 36) | 2172 ms |
| Typical inter-slide gap (slides 30–40) | ~1098 ms |
| Excess gap before | +38 ms (normal) |
| Excess gap after | +1074 ms (abnormal) |

**Conclusion**: Data was lost at the **end** of slide 35. Approximately 1063 ms of gaze data is missing.

### 2. Y20f3G9ulPHmbLwFS3JL — Slide 37

- **Expected duration**: 2500 ms
- **Observed duration**: 6868 ms (+174.7% deviation)
- **SCENE_INDEX**: 73

**Investigation**: The excess time occurs during `no_image` periods (inter-stimulus intervals), not during actual image viewing. The gaze data recorded while the stimulus image was displayed appears normal.

**Conclusion**: A lag occurred in the transition between slides, inflating the total slide duration. However, since dwell time metrics are computed only from image-viewing periods, this does not affect the metrics.

## Decision: Keep Both Slides As-Is

**Considered alternatives**:

1. **Remove problematic slides from all sessions** — Overkill. The anomalies affect only one session each. Removing a slide from every session discards good data to "fix" a single-session problem.
2. **Remove problematic slides from affected sessions only** — Introduces unequal slide counts across sessions, which is its own source of bias.
3. **Keep as-is** — Chosen approach.

**Rationale**:

- **Slide 37**: No impact on dwell time metrics since the lag is in `no_image` periods. No correction needed.
- **Slide 35**: The ~1063 ms of lost data underestimates this slide's dwell time. However, since metrics are computed as means across many slides per session, the effect on the session-level mean is negligible (~30–35 ms shift across 30+ slides). This is well within normal noise and smaller than the bias introduced by either removal strategy.

The anomalies are documented here and in the outlier inspection notebook for transparency.

---

**Report Generated**: 2026-02-13
**Analysis Code**: `routine_exploration/outlier_slide_inspection.py`, `routine_exploration/slide_duration_analysis.py`
