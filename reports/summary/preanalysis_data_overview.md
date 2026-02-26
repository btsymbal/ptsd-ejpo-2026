# Pre-Analysis Data Overview & Session Removal Summary

## Overview

Before hypothesis testing, a pre-analysis overview was conducted on the full 30-session eye-tracking metrics dataset to characterize distributional properties, detect outliers, and assess correlation structure. This overview informed two rounds of session exclusions: one session was removed for a technical recording anomaly, yielding the **29-session main dataset** used for most analyses (H1–H6, E2–E3), and three additional sessions were removed for blink data quality issues, yielding the **26-session blink-clean dataset** used exclusively for blink-related exploratory analyses (E1).

---

## Dataset Composition

The raw eye-tracking metrics dataset contained **30 sessions x 134 columns** (131 float64, 2 int64, 1 object) spanning **14 metric families** across **11 image categories**.

| Variable | Breakdown |
|----------|-----------|
| **PTSD status** | n = 17 PTSD, n = 13 No-PTSD |
| **Antipsychotic use** | n = 14 use, n = 16 non-use |
| **ITI PTSD score** | range 8–19 (M = 12.65, Mdn = 12.00, PTSD group only) |
| **ITI cPTSD score** | range 0–14 (M = 7.35, Mdn = 9.00, 4 of 17 PTSD participants scored 0) |

---

## Distributional Characteristics

Metrics fell into three distributional regimes:

| Regime | Metric Families |
|--------|----------------|
| **Approximately normal** | Mean dwell %, std dwell %, std delta dwell %, mean visits, mean blink latency (normalized), mean dwell % late, mean visits late |
| **Severely right-skewed** | Total blink count, per-category blink rate, blink interval (normalized), mean off-screen %, mean off-screen % late |
| **Intermediate** | Mean blink duration (Shapiro-Wilk p = 0.006, platykurtic rather than skewed) |

Normal-regime metrics are suitable for parametric tests; skewed metrics require non-parametric tests or log-transformation.

**Blink missingness**: Blink duration, blink latency, and std blink duration columns have **1–14 NaN values** per category (structurally missing where sessions produced zero blinks in a category). All other metric families are complete.

---

## Outlier Screening Results

Sessions were flagged across all numeric columns using the **1.5x IQR rule**. 15 of 30 sessions had zero flags.

| Session | IQR Flags | Nature |
|---------|-----------|--------|
| **UgMWkyrkRYVZ9cr9thRw** | 28 (1st) | 22 off-screen HIGH, 6 low dwell/visits — near-zero engagement |
| **DTGxc0RwsWrTMRKpenb8** | 12 (tied 2nd) | All 12 blink-related — extreme blink count (217 total) |
| **9Pd2lTJaNZ7CGrLBPjuU** | 12 (tied 2nd) | 7 blink HIGH + 5 visit HIGH — high-engagement participant, not a quality issue |

**Multivariate screening**: Mahalanobis distances were computed within seven metric subspaces using a chi-squared threshold at p < 0.01. **No multivariate outliers were detected** in any subspace.

---

## Session Removal: Main Dataset (N = 29)

**Session removed:** `UgMWkyrkRYVZ9cr9thRw`

| Evidence | Detail |
|----------|--------|
| **Off-screen gaze** | 83–93% across all 11 categories |
| **Usable slides** | Only 8% |
| **IQR flags** | 28 — most in the dataset |
| **Personnel note** | Participant may have sat too far from the screen |
| **Interpretation** | Technical recording anomaly, not clinical avoidance (uniform off-screen across all categories including neutral) |

**Output:** `data/simplified/dataset_eyetracking_metrics_clean.csv` (29 sessions)
**Used for:** H1–H6 and E2–E3 analyses

---

## Session Removal: Blink-Clean Dataset (N = 26)

Three additional sessions were removed from the 29-session dataset for blink data quality issues:

| Session | Total Blinks | Reason |
|---------|-------------|--------|
| **DTGxc0RwsWrTMRKpenb8** | 217 (72.5/min) | Extreme high — poor gaze quality likely inflates blink detection |
| **RBRGZzWIzDitollqkpzW** | 7 | Extreme low — likely tracker malfunction or data loss |
| **xn3yMJ8STzchnQPg94lH** | 4 | Extreme low — likely tracker malfunction or data loss |

**Output:** `data/simplified/dataset_eyetracking_metrics_blink_clean.csv` (26 sessions)
**Used for:** E1 (exploratory blink metrics analysis) only

---

## Blink Rate Concern

The sample's median blink rate was **5.7 blinks/min** versus the adult norm of **15–20 blinks/min**. 12 of 30 sessions (40%) fell outside the 5–40 blinks/min plausibility range. The low rates likely reflect under-detection by the eye tracker or task-induced blink suppression (sustained visual attention to slides). This concern motivated the cautious approach to blink analyses, including the creation of a separate blink-clean dataset and the treatment of blink-related findings as exploratory.

---

## Key Correlation Patterns

- **Blink rates**: Near-unity intercorrelations (r = 0.87–0.99) across all 11 categories, indicating blink rate is an individual-difference trait rather than category-specific. Per-category blink rates carry almost no category-specific information.

- **Off-screen percentages**: Near-unity intercorrelations (r = 0.87–0.99) across categories in both full and late windows, indicating off-screen gaze reflects overall data quality or disengagement rather than stimulus-specific avoidance.

- **Late-window dwell**: Correlations notably weaker than full-window (r = 0.13–0.91 vs. r = 0.38–0.93; only 38/55 pairs significant at p < 0.05 vs. all 55). Sustained attention after initial orienting carries more category-specific information, making late-window metrics potentially more sensitive to stimulus-driven effects.

---

**Source reports:**
- [Eye-Tracking Metrics Overview Report](../preanalysis_overview/eyetracking_metrics_overview_report.md) — 2026-02-19
- [Session Removal Report](../preprocessing/session_removal_report.md)
- [Blink Outlier Removal Report](../preprocessing/blink_outlier_removal_report.md)
