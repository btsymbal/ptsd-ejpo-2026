# Blink Outlier Session Removal Report

## Decision Chain

### 1. Context

Upcoming blink-related hypothesis tests require clean
blink data. Sessions with extreme blink counts — either implausibly high or
implausibly low — would distort group-level statistics and violate the
assumptions underlying these analyses.

### 2. Outlier Evidence

Three sessions were identified as significant blink-metric outliers in the
eye-tracking metrics overview analysis:

- **DTGxc0RwsWrTMRKpenb8**: 217 total blinks (72.5 blinks/min) — extreme high
  blink count with 12 IQR outlier flags, all blink-related. Poor gaze quality
  likely inflates blink detection.
- **RBRGZzWIzDitollqkpzW**: 7 total blinks — very low count, flagged HIGH on
  blink interval metrics.
- **xn3yMJ8STzchnQPg94lH**: 4 total blinks — very low count, flagged HIGH on
  blink interval metrics.

### 3. Conclusion

These three sessions represent measurement anomalies rather than meaningful
clinical variation. The extreme high-blink session likely reflects poor gaze
tracking inflating blink detection, while the two low-blink sessions suggest
tracker malfunction or data loss. Including them would compromise the validity
of blink-related analyses.

### 4. Action Taken

- Sessions `DTGxc0RwsWrTMRKpenb8`, `RBRGZzWIzDitollqkpzW`, and
  `xn3yMJ8STzchnQPg94lH` removed from the eye-tracking metrics dataset
- Cleaned dataset exported to
  `data/simplified/dataset_eyetracking_metrics_blink_clean.csv`
  (26 sessions, down from 29)

## Supporting Evidence

- [Eye-Tracking Metrics Overview Report](../preanalysis_exploration/eyetracking_metrics_overview_report.md)
  (sections 4 and 6)
