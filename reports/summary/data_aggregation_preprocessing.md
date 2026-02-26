# Data Aggregation & Preprocessing Summary

## Overview

Two preprocessing pipelines transform raw gaze session files into analysis-ready datasets. The first (`compute_eyetracking_metrics.py`) produces a single-row-per-session summary of eye-tracking metrics across 11 image categories. The second (`compute_temporal_threat_bias.py`) produces trial-level threat bias data for temporal dynamics analyses. Both merge clinical metadata from the merged questionnaire dataset.

---

## Pipeline 1: Eye-Tracking Metrics Dataset

**Script:** `preprocessing/compute_eyetracking_metrics.py`
**Input:** 30 raw gaze session CSVs, slide duration schedule, image category mappings, clinical metadata
**Output:** `data/simplified/dataset_eyetracking_metrics.csv` — 30 rows x 134 columns

### Aggregation Logic

Each raw session file contains timestamped gaze samples with screen coordinates, blink flags, and scene indices. The pipeline aggregates these into one row per session through the following steps:

1. **Slide-level computation** — For each slide (identified by `SCENE_INDEX`), gaze time on each image is computed from sample counts and converted to dwell percentage relative to expected slide duration.

2. **Category attribution** — Each image is mapped to one of 11 categories (e.g., `angry_face`, `warfare`, `neutral`) via a JSON lookup. Metrics are accumulated per category across all slides.

3. **Cross-slide aggregation** — Per-category metrics are averaged (mean) across all slides containing that category, producing session-level summary statistics.

### Metric Families

| Family | Description | Columns |
|--------|-------------|---------|
| Dwell time | Mean and SD of dwell percentage per category | 22 |
| Late-window dwell | Dwell percentage from 800 ms onward (sustained attention) | 11 |
| Delta dwell | SD of threat-minus-neutral dwell across threat–neutral slides | 4 |
| Visit counts | Mean gaze visits (>= 100 ms runs) per category | 11 |
| Late-window visits | Visit counts from 800 ms onward | 11 |
| Off-screen gaze | Mean off-screen percentage per category | 22 |
| Blink metrics | Blink rate, latency, duration, inter-blink intervals | 27 |

### Threat–Neutral Pairing

Four threat categories are paired with eligible neutral counterparts for delta-dwell computation:

| Threat | Neutral Counterparts | Slides |
|--------|---------------------|--------|
| angry_face | neutral_face | 10 |
| anxiety_inducing | neutral | 14 |
| warfare | happy_event, neutral | 12 |
| soldiers | happy_face, neutral, neutral_face | 8 |

Delta dwell = threat dwell % - neutral dwell %. The SD of this delta across slides is retained as the session-level variability metric.

---

## Pipeline 2: Temporal Threat Bias Datasets

**Script:** `preprocessing/compute_temporal_threat_bias.py`
**Input:** 30 raw gaze session CSVs (1 excluded for poor quality), slide duration schedule, image category mappings, clinical metadata
**Output:** Three CSV files in `data/simplified/`

### Aggregation Logic

Rather than collapsing across slides, this pipeline preserves individual trial-level threat bias values for temporal trajectory analysis (inspired by Zvielli et al., 2015).

1. **Trial-level deltas** — For each of the 44 threat–neutral slides, the threat dwell percentage minus neutral dwell percentage is computed per session.

2. **Temporal indexing** — Slides are re-indexed 1–44 in presentation order to enable within-session trajectory plots.

3. **Group aggregation** — Trial-level deltas are averaged across sessions within each group (PTSD, No-PTSD) with confidence intervals.

4. **Variability indices** — Per-session summary statistics (TL-BS mean, SD, peak toward, peak away, range) capture within-session attentional fluctuation.

### Output Files

| File | Grain | Rows | Purpose |
|------|-------|------|---------|
| `temporal_threat_bias_by_session.csv` | 1 per session x slide | 1276 | Trial-level trajectories |
| `temporal_threat_bias_aggregated.csv` | 1 per slide x group | 88 | Group-level temporal curves |
| `temporal_threat_bias_variability.csv` | 1 per session | 29 | Within-session variability indices |

---

## Metadata Merging

Both pipelines merge clinical metadata from `data/simplified/dataset_merged_1_and_2.csv` by matching on `session_id`:

| Variable | Description | Used In |
|----------|-------------|---------|
| `if_PTSD` | Binary PTSD status (0/1) | Both pipelines |
| `ITI_PTSD` | ITI PTSD symptom score | Pipeline 1 only |
| `ITI_cPTSD` | ITI complex PTSD score | Pipeline 1 only |
| `if_antipsychotic` | Binary antipsychotic medication status | Pipeline 1 only |

Pipeline 2 derives a `group` label ("PTSD" / "No-PTSD") from `if_PTSD` for aggregation and plotting.

---

## Key Design Decisions

- **Late window at 800 ms** — Separates early orienting from sustained engagement, applied to dwell time, visit counts, and off-screen metrics.
- **Visit threshold at 100 ms** — Gaze runs shorter than 100 ms are not counted as visits, filtering out saccadic transients.
- **Mean as central tendency** — Shapiro-Wilk tests confirmed normality for 93% of per-slide delta distributions, supporting the use of the mean for group-level aggregation.
- **Blink boundary splitting** — Blink runs that span scene boundaries are split into separate blinks to avoid cross-slide contamination.
- **Off-screen attribution** — Off-screen time is attributed to both image categories on a slide, since it cannot be assigned to either image specifically.
