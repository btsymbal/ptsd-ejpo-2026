# Eye-Tracking Attentional Bias in PTSD

Eye-tracking study of attentional bias toward threat stimuli in Ukrainian military personnel with and without PTSD. The project includes raw gaze data preprocessing, hypothesis-driven analysis (6 confirmatory + 3 exploratory), and production-ready manuscript materials.

**Design**: Between-group comparison (PTSD vs no-PTSD) of dwell time, visit counts, blink metrics, and temporal dynamics across four threat categories (angry faces, anxiety-inducing, warfare, soldiers). Within-PTSD analyses examine correlations with symptom severity (ITI_PTSD) and medication moderation effects.

**Sample**: 30 sessions (17 PTSD, 13 no-PTSD), reduced to 29 after gaze quality exclusion and 26 after blink outlier removal.

## Technical Requirements

Python 3.10+ with the following packages:

```
pandas>=2.2.3
numpy>=2.2.4
scipy>=1.15.2
matplotlib>=3.10.1
seaborn>=0.13.2
statsmodels>=0.14.4
```

Install with:

```bash
pip install pandas numpy scipy matplotlib seaborn statsmodels
```

## Repository Structure

```
ptsd_clean/
├── preprocessing/              # 10 scripts — raw data → analysis-ready datasets
├── preanalysis_overview/       # 2 scripts — descriptive statistics & outlier checks
├── hypotheses_testing/         # 6 scripts — H1–H6 confirmatory analyses
├── exploratory_analysis/       # 3 scripts — E1–E3 exploratory analyses
├── routine_exploration/        # 7 files — ad hoc quality checks
├── materials/                  # Reference data (clinical table, slide configs, preregistration)
├── reports/                    # 22 markdown reports organized by analysis phase
├── production/                 # Manuscript, 21 figures, 14 tables
├── figures/                    # All analysis-generated figures by topic
└── data/                       # Raw and processed datasets (see Data Directory)
```

## Preprocessing (`preprocessing/`)

Two core pipelines produce all analysis datasets:

| Script | Description |
|--------|-------------|
| **`compute_eyetracking_metrics.py`** | Main pipeline: 30 raw gaze CSVs → single 134-column dataset with dwell time, visit counts, and blink metrics per category per session |
| **`compute_temporal_threat_bias.py`** | Trial-level temporal threat bias extraction: produces per-session, aggregated, and variability index files |

Supporting scripts:

| Script | Description |
|--------|-------------|
| `preprocess_ptsd_table.py` | Clean clinical XLSX: extract session IDs, normalize missing values, convert qualitative to binary |
| `identify_antipsychotics.py` | Classify medications as antipsychotic/non-antipsychotic from Ukrainian treatment names |
| `merge_datasets_15.py` | Merge 15-row eye-tracking metrics with clinical data (inner join on session ID) |
| `merge_datasets_1_and_2_15.py` | Merge two 15-row datasets into full 30-row dataset |
| `remove_session_UgMWkyrkRYVZ9cr9thRw.py` | Remove 1 session with 83–93% off-screen gaze (technical anomaly) |
| `remove_blink_outlier_sessions.py` | Remove 3 sessions with extreme blink counts (4, 7, and 217 blinks) |
| `extract_image_pair_ids.py` | Parse dataset columns to extract image pair mappings to JSON |
| `slide_categories.py` | Map slide numbers to threat/neutral category pairs |

## Analysis Notebooks

All notebooks use [percent format](https://jupytext.readthedocs.io/en/latest/formats-scripts.html) (`.py` files with `# %%` cell markers), compatible with VS Code, PyCharm, and Jupyter.

### Pre-Analysis Overview (`preanalysis_overview/`)

| Script | Description |
|--------|-------------|
| `eyetracking_metrics_overview.py` | Descriptive statistics, distributional checks, and outlier flagging for the full 30-session dataset |
| `blink_metrics_overview.py` | Same for the 26-session blink-cleaned dataset; previews PTSD and antipsychotic group differences |

### Hypothesis Testing (`hypotheses_testing/`)

| Script | Hypothesis |
|--------|------------|
| `h1_threat_dwell_time.py` | **H1**: PTSD group shows higher mean dwell time % on threat stimuli |
| `h2_threat_dwell_variability.py` | **H2**: PTSD group shows higher within-participant SD of dwell time on threat |
| `h3_attention_bias_variability.py` | **H3**: PTSD group shows higher across-slide attention bias variability (threat minus neutral delta) |
| `h4_abv_iti_correlation.py` | **H4**: Within PTSD group — attention bias variability correlates with symptom severity (ITI_PTSD) |
| `h5_mean_visits_threat.py` | **H5**: PTSD group shows more revisits (higher visit count) to threat stimuli |
| `h6_iti_avoidance_gaze.py` | **H6**: Within PTSD — higher symptom severity correlates with avoidance-like gaze (lower dwell, fewer visits, more off-screen) |

All hypothesis scripts use normality/variance checks to select parametric vs non-parametric tests, with Benjamini-Hochberg FDR correction per family.

### Exploratory Analysis (`exploratory_analysis/`)

| Script | Analysis |
|--------|----------|
| `e1_blink_metrics_exploration.py` | **E1**: Blink metrics group comparison (PTSD vs no-PTSD) and within-PTSD ITI correlation |
| `e2_medication_attention_moderation.py` | **E2**: Antipsychotic medication moderation of attention metrics (2x2 PTSD x antipsychotic design with permutation ANOVA) |
| `e3_temporal_dynamics_threat_bias.py` | **E3**: Within-session temporal trajectories of threat bias with trial-level variability indices |

## Reports (`reports/`)

22 markdown reports organized into 6 subdirectories:

| Directory | Contents |
|-----------|----------|
| `summary/` | **4 summary reports** — best entry point for understanding results: `preanalysis_data_overview.md`, `data_aggregation_preprocessing.md`, `hypotheses_summary.md`, `exploratory_summary.md` |
| `preprocessing/` | 5 reports covering metrics extraction, temporal bias, session removals, antipsychotic classification |
| `preanalysis_overview/` | 2 reports on descriptive statistics and outlier checks |
| `hypotheses_testing/` | 6 reports (one per hypothesis H1–H6) |
| `exploratory_analysis/` | 3 reports (one per exploratory analysis E1–E3) |
| `routine_exploration/` | 2 reports on gaze quality and slide duration checks |

## Production (`production/`)

Publication-ready manuscript materials:

- **`manuscript.md`** — full manuscript text
- **`figures/`** — 21 PNG figures (Figures 1–6 main + S1–S13 supplementary)
- **`tables/`** — 14 markdown tables (Tables 1–7 main + S1–S7 supplementary)

## Data Directory (`data/`)

```
data/
├── raw_sessions/       # 30 raw gaze CSV files (not tracked, needed to re-run preprocessing)
├── simplified/         # Processed analysis-ready datasets (6 key files tracked, see below)
├── additional/         # Preprocessed clinical data variants (generated by preprocessing)
└── output/             # Intermediate QA outputs (generated by routine exploration)
    ├── slides_duration/
    └── valid_gaze_proportion/
```

### Tracked Datasets (`data/simplified/`)

These 6 files are version-controlled so that analysis scripts can run without re-running the full preprocessing pipeline:

| File | Rows | Used By |
|------|------|---------|
| `dataset_eyetracking_metrics.csv` | 30 | Pre-analysis overview |
| `dataset_eyetracking_metrics_clean.csv` | 29 | H1–H6, E2 (main analysis dataset) |
| `dataset_eyetracking_metrics_blink_clean.csv` | 26 | E1, blink overview |
| `temporal_threat_bias_by_session.csv` | 1,276 | E3 (trial-level data) |
| `temporal_threat_bias_aggregated.csv` | 88 | E3 (group-level aggregates) |
| `temporal_threat_bias_variability.csv` | 29 | E3 (session variability indices) |

All other files in `data/` are generated by preprocessing or exploration scripts and are not tracked.

## Data Pipeline Flow

```
materials/PTSD_Anima_Table_05_08.xlsx ──► preprocess_ptsd_table.py
                                             │
data/raw_sessions/ (30 CSVs) ──► compute_eyetracking_metrics.py
                                             │
                                             ▼
                              dataset_eyetracking_metrics.csv (30 rows)
                                             │
                              remove_session_*.py (gaze quality filter)
                                             │
                                             ▼
                              dataset_eyetracking_metrics_clean.csv (29 rows)
                                             │
                              remove_blink_outlier_sessions.py
                                             │
                                             ▼
                              dataset_eyetracking_metrics_blink_clean.csv (26 rows)

data/raw_sessions/ (30 CSVs) ──► compute_temporal_threat_bias.py
                                             │
                                             ▼
                              temporal_threat_bias_by_session.csv (1,276 rows)
                              temporal_threat_bias_aggregated.csv (88 rows)
                              temporal_threat_bias_variability.csv (29 rows)
```

## Running Scripts

Every script resolves the project root automatically via `os.chdir(Path(__file__).resolve().parent.parent)`, so scripts work from any directory:

```bash
# From project root
python preprocessing/compute_eyetracking_metrics.py

# Or from the script's directory
cd preprocessing
python compute_eyetracking_metrics.py
```

To re-run the full pipeline from scratch, you need the 30 raw gaze CSVs in `data/raw_sessions/` and the clinical XLSX in `materials/`. To run only the analysis scripts (hypothesis testing, exploratory), the tracked datasets in `data/simplified/` are sufficient.
