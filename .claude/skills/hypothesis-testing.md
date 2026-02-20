# Skill: Hypothesis Testing

Reusable workflow for running a hypothesis test comparing PTSD vs no-PTSD groups on a set of dependent variables from the eye-tracking metrics dataset.

## File Naming Convention

- **Notebook**: `hypotheses_testing/h{N}_{short_name}.py` (percent format)
- **Report**: `reports/hypotheses_testing/h{N}_{short_name}.md`
- **Figures**: `figures/h{N}_{short_name}/`

Where `{N}` is the hypothesis number and `{short_name}` is a brief snake_case descriptor.

## Dataset

- **File**: `data/simplified/dataset_eyetracking_metrics_clean.csv`
- **Participants**: 29 (17 PTSD, 12 no-PTSD)
- **Group variable**: `if_PTSD` (1 = PTSD, 0 = no-PTSD)

## Statistical Decision Tree

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

## Notebook Template Structure

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
Cell 11 [code]     - Visualization 3: Bar chart (group means +/- SE)
```

### Required imports

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

### Helper functions

Include these in the notebook for effect size computation:

- `cohens_d(x, y)` - pooled SD Cohen's d
- `cohens_d_ci(d, nx, ny)` - approximate 95% CI
- `rank_biserial_r(u_stat, nx, ny)` - from Mann-Whitney U
- `rank_biserial_ci(r, nx, ny)` - via Fisher z transformation

## Report Template Structure

```markdown
# H{N}: {Title}

**Notebook**: `hypotheses_testing/h{N}_{short_name}.py`

## Hypothesis
{Formal H statement}

## Method
- Participants, DVs, group variable, test family size
- Test selection logic
- Effect size measures
- Multiple comparison correction

## Results

### Descriptive statistics
{Table: Category | Group | n | Mean | SD | Median | Min | Max}

### Assumption checks
{Table: Shapiro per group, Levene, decisions}

### Primary results (BH-corrected)
{Table: Category | Test | Statistic | p_uncorr | p_BH | Effect Size | CI | Significant}

### Secondary results (uncorrected)
{Brief narrative for exploratory context}

### Figures
{Three figures with relative paths: ../../figures/h{N}_{short_name}/...}

## Conclusion
{Whether hypothesis is supported, caveats about sample size and power}
```

## Figure Conventions

- Save to `figures/h{N}_{short_name}/` (create with `os.makedirs(..., exist_ok=True)`)
- Format: PNG at 600 dpi
- Color palette: PTSD = `#d9534f`, No-PTSD = `#5bc0de`
- Three standard plots per hypothesis:
  1. Violin + strip plot (split violins, individual points)
  2. Forest plot (effect sizes with 95% CIs, reference line at 0)
  3. Bar chart (group means with SE error bars)

## Reference Implementation

See `hypotheses_testing/h1_threat_dwell_time.py` and `reports/hypotheses_testing/h1_threat_dwell_time.md` for a complete working example.
