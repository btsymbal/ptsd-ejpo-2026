# Gaze Data Quality Check Report

## Overview

The study preregistered three gaze data quality criteria:

1. **Trial-level**: A trial (slide) is usable if valid gaze proportion >= 50%.
2. **Session-level**: A participant is included if >= 60% of their trials are usable.
3. **Category-level**: Each participant contributes >= 5 usable trials per image category.

This report documents the results of applying these criteria and the decision to retain all sessions and trials despite some failing these checks.

## Results

The dataset contains 30 sessions, each with 75 slides.

### Trial-Level Check (valid gaze >= 50%)

- 21 of 30 sessions had at least one slide below the 50% valid gaze threshold.
- 324 total session-slide pairs were flagged across the dataset.

### Session-Level Check (>= 60% usable slides)

3 of 30 sessions failed the 60% usable-slides threshold:

| Session ID | Usable Slides (%) |
|---|---|
| UgMWkyrkRYVZ9cr9thRw | 8.0% |
| xx19J8Xeoc4thStIAtUe | 45.3% |
| DTGxc0RwsWrTMRKpenb8 | 57.3% |

### Category-Level Check (>= 5 usable trials per category)

- 6 of 30 sessions had at least one category with fewer than 5 usable trials.

## Deviation from Preregistration: Decision to Retain All Data

Despite the failures above, all sessions and trials are retained. The justification rests on several converging issues with the preregistered exclusion rules.

### The validity definition is flawed

The valid gaze proportion is defined by a screen-boundary criterion: gaze coordinates that fall outside the screen area are classified as invalid. This conflates two very different phenomena — genuine tracking failure (hardware dropout, calibration loss) and off-screen gaze (the participant looking away from the screen). In PTSD eye-tracking paradigms, gaze avoidance of threatening stimuli is a theoretically meaningful behaviour. Excluding trials where participants looked away from trauma-related images would systematically remove the very signal the study aims to measure.

### Thresholds were arbitrary

The 50%, 60%, and 5-trial thresholds were chosen before data collection without prior knowledge of the data distribution. There is no empirical or theoretical basis for these specific cut-offs, and small changes to them would produce meaningfully different inclusion sets.

### Worst sessions show tracking, not failure

Inspection of the three failing sessions shows that valid gaze proportions fluctuate across slides but never flatline at zero for the entire session. This pattern is consistent with calibration drift or avoidance behaviour rather than complete tracking failure. The eye tracker was recording gaze throughout; the coordinates simply fell outside the screen boundary more often.

### Small sample size

With only 30 participants, excluding even 3 sessions reduces the sample by 10% and disproportionately reduces statistical power. The cost of exclusion is high relative to the uncertain benefit.

### Trial and category removal introduces its own biases

Removing flagged trials creates unequal trial counts across sessions, complicating within-subject comparisons. Removing entire sessions discards all data from those participants, including slides where gaze quality was adequate. Neither approach is clearly preferable to retaining the full dataset.

## Conclusion

All 30 sessions and all trials are retained for analysis. The preregistered exclusion criteria are not applied because the validity metric conflates tracking failure with meaningful gaze behaviour, the thresholds lack empirical grounding, and the worst-case sessions show continuous tracking rather than hardware failure. This deviation is documented here for transparency.

---

**Report Generated**: 2026-02-17
**Analysis Code**: `routine_exploration/valid_gaze_proportion.py`
