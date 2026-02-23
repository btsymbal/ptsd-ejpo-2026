# Skill: Hypothesis Testing

Reusable workflow for running hypothesis tests (group comparisons or correlational analyses) on eye-tracking metrics from the PTSD dataset.

## File Naming Convention

- **Notebook**: `hypotheses_testing/h{N}_{short_name}.py` (percent format)
- **Report**: `reports/hypotheses_testing/h{N}_{short_name}.md`
- **Figures**: `figures/h{N}_{short_name}/`

Where `{N}` is the hypothesis number and `{short_name}` is a brief snake_case descriptor.

## Dataset

- **File**: `data/simplified/dataset_eyetracking_metrics_clean.csv`
- **Participants**: 29 (17 PTSD, 12 no-PTSD)
- **Group variable**: `if_PTSD` (1 = PTSD, 0 = no-PTSD)
- **Severity variable**: `ITI_PTSD` (meaningful for PTSD group only)

---

## Group Comparison Decision Tree

For each dependent variable in the test family:

1. **Normality**: Shapiro-Wilk on each group (alpha = 0.05)
2. **Variance equality**: Levene's test (alpha = 0.05)
3. **Test selection**:
   - Both normal + equal variance -> Student's t-test (`equal_var=True`)
   - Both normal + unequal variance -> Welch's t-test (`equal_var=False`)
   - Either non-normal -> Mann-Whitney U (two-sided)
4. **Effect size**:
   - Cohen's d for t-tests (with pooled SD), plus 95% CI
   - Rank-biserial r for Mann-Whitney U (from U statistic), plus 95% CI via Fisher z
5. **Multiple comparison correction**: Benjamini-Hochberg FDR (`statsmodels.stats.multitest.multipletests`, method='fdr_bh') across all p-values in the test family

## Group Comparison Notebook Template

```
Cell 1  [markdown] - Hypothesis statement, method summary
Cell 2  [code]     - Imports + os.chdir(Path(__file__).resolve().parent.parent)
Cell 3  [code]     - Load data, define DV columns, print group sizes
Cell 4  [code]     - Descriptive statistics per group per DV
Cell 5  [code]     - Assumption checks (Shapiro-Wilk, Levene's)
Cell 6  [code]     - Statistical tests with effect sizes and CIs
Cell 7  [code]     - BH correction, results table
Cell 8  [code]     - Results summary (formatted console output)
Cell 9  [code]     - Visualization 1: Violin + strip plot
Cell 10 [code]     - Visualization 2: Forest plot (effect sizes + CIs)
Cell 11 [code]     - Visualization 3: Bar chart (group means with 95% CI)
```

### Group comparison helper functions

- `cohens_d(x, y)` - pooled SD Cohen's d
- `cohens_d_ci(d, nx, ny)` - approximate 95% CI
- `rank_biserial_r(u_stat, nx, ny)` - from Mann-Whitney U
- `rank_biserial_ci(r, nx, ny)` - via Fisher z transformation

---

## Correlational Analysis Decision Tree

For within-group correlational analyses (e.g., ABV × symptom severity):

1. **Normality**: Shapiro-Wilk on both the DV and IV (alpha = 0.05)
2. **Outlier detection**: Fit simple OLS (DV ~ IV via `np.polyfit`), compute standardized residuals, flag any |z| > 3 as outlier
3. **Test selection**:
   - Both normal **AND** no outliers -> **Pearson's r** (CI via Fisher z transformation)
   - Either non-normal **OR** outliers present -> **Kendall's τ_b** (CI via bootstrap, 10,000 resamples); preferred over Spearman for n < 20 due to better small-sample properties and tie handling
4. **Homoscedasticity**: Visual inspection via residual-vs-fitted plots with LOWESS smoother (reported for transparency, not used as a decision criterion — formal tests are underpowered at small n)
5. **Multiple comparison correction**: Benjamini-Hochberg FDR applied **separately** within each family of tests (not pooled across families)

## Correlation Notebook Template

```
Cell 1  [markdown] - Hypothesis statement, method summary
Cell 2  [code]     - Imports + os.chdir(Path(__file__).resolve().parent.parent)
Cell 3  [code]     - Load data, filter to relevant subgroup, print sample size
Cell 4  [code]     - Descriptive statistics (single group: IV + all DVs)
Cell 5  [code]     - Assumption checks (Shapiro-Wilk on IV once + each DV, outlier detection via OLS residuals)
Cell 5b [code]     - Assumption diagnostic plots (outlier inspection + homoscedasticity)
Cell 6  [code]     - Correlation tests per family (Pearson or Kendall dispatch based on Use_Pearson)
Cell 7  [code]     - BH correction (separate per family), results tables
Cell 8  [code]     - Results summary (formatted console output)
Cell 9  [code]     - Scatterplots Family 1 (2×2 grid, linear fit line)
Cell 10 [code]     - Scatterplots Family 2 (2×2 grid, linear fit line)
Cell 11 [code]     - Forest plots (one per family)
Cell 12 [code]     - Correlation heatmap (all DVs × IV)
```

### Correlation helper functions

- `pearson_ci(r, n)` - 95% CI via Fisher z transformation
- `kendall_ci_bootstrap(x, y, n_boot=10000, seed=42)` - bootstrap 95% CI for τ_b
- `run_correlation(dv_vals, iv_vals, use_pearson)` - dispatches to Pearson or Kendall based on normality + outlier check

---

## Required imports (both types)

```python
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from statsmodels.stats.multitest import multipletests

os.chdir(Path(__file__).resolve().parent.parent)
```

## Report Template Structure

```markdown
# H{N}: {Title}

**Notebook**: `hypotheses_testing/h{N}_{short_name}.py`

## Hypothesis
{Formal H statement}

## Method
- Participants, DVs, group variable or IV, test family size
- Test selection logic
- Effect size / correlation measures
- Multiple comparison correction

## Results

### Descriptive statistics
{Table: Variable | Group | n | Mean | SD | Median | Min | Max}

### Assumption checks
{Table: Shapiro per group/variable, Levene (if group comparison), decisions}

### Primary results (BH-corrected)
{Table: Category | Test | Statistic/Coefficient | p_uncorr | p_BH | Effect Size/CI | Significant}

### Secondary results (uncorrected)
{Brief narrative for exploratory context}

### Figures
{Figures with relative paths: ../../figures/h{N}_{short_name}/...}

## Conclusion
{Whether hypothesis is supported, caveats about sample size and power}
```

## Figure Conventions

### Group comparisons
- Color palette: PTSD = `#d9534f`, No-PTSD = `#5bc0de`
- Three standard plots: violin + strip, forest plot, bar chart

### Correlations
- Single color: `#d9534f` for all scatter points
- Scatterplots: one figure per family (2×2 grid), linear fit line (dashed), subplot titles show test name + coefficient + p
- Forest plots: one per family, x-axis = correlation coefficient, horizontal error bars = 95% CI, significant in red, non-significant in dark gray, reference line at x=0
- Correlation heatmap: all DVs as rows, IV as column, `RdBu_r` colormap centered at 0, annotated with coefficient values
- Outlier inspection plot: 2×4 grid (all DVs), scatterplot with OLS fit line, outliers (|z_resid| > 3) highlighted in orange (`#f0ad4e`) with larger markers, normal points in `#d9534f`
- Homoscedasticity plot: 2×4 grid (all DVs), standardized residuals vs fitted values, horizontal reference line at y=0, LOWESS smoother in blue (`#337ab7`)

### Common
- Save to `figures/h{N}_{short_name}/` (create with `os.makedirs(..., exist_ok=True)`)
- Format: PNG at 600 dpi

## Reference Implementations

- **Group comparison**: `hypotheses_testing/h1_threat_dwell_time.py` and `reports/hypotheses_testing/h1_threat_dwell_time.md`
- **Correlation**: `hypotheses_testing/h4_abv_iti_correlation.py` and `reports/hypotheses_testing/h4_abv_iti_correlation.md`
