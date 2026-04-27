# %% [markdown]
# # Re-run H1–H6 on the Image-Cleaned Dataset and Compare
#
# Loads both the original analysis dataset
# (`data/simplified/dataset_eyetracking_metrics_clean.csv`, n=29) and the
# image-cleaned variant from Step 6
# (`data/simplified/dataset_eyetracking_metrics_clean_imageclean.csv`, n=29),
# runs the same test logic that the `hypotheses_testing/h{1..6}*.py` scripts
# use, and produces a side-by-side comparison report at
# `reports/cleanup_evaluation/07_hypotheses_comparison.md`.
#
# Test selection logic mirrors the originals:
# - Group comparisons: Shapiro on each group + Levene → Student's t /
#   Welch's t / Mann-Whitney U; effect sizes Cohen's d (parametric) or
#   rank-biserial r (non-parametric).
# - Within-PTSD correlations: Shapiro on each variable + 3σ outlier check →
#   Pearson's r (no outliers and both normal) else Kendall's τ_b.
# - All test families use Benjamini-Hochberg FDR within family.
#
# We omit the original H6 Part A (median split) and only run Part B (continuous
# correlation) to keep the comparison clean and to avoid the small-n issues of
# the median-split comparison.

# %%
import os
from pathlib import Path

os.chdir(Path(__file__).resolve().parent.parent)

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

ORIG_CSV = 'data/simplified/dataset_eyetracking_metrics_clean.csv'
CLEAN_CSV = 'data/simplified/dataset_eyetracking_metrics_clean_imageclean.csv'
REPORT_PATH = 'reports/cleanup_evaluation/07_hypotheses_comparison.md'
os.makedirs('reports/cleanup_evaluation', exist_ok=True)

THREAT_CATEGORIES = ['angry_face', 'anxiety_inducing', 'warfare', 'soldiers']
ALPHA = 0.05

# %% [markdown]
# ## Helpers (mirror logic from `hypotheses_testing/`)

# %%
def cohens_d(x, y):
    nx, ny = len(x), len(y)
    pooled_std = np.sqrt(((nx - 1) * x.std(ddof=1)**2 + (ny - 1) * y.std(ddof=1)**2) / (nx + ny - 2))
    return (x.mean() - y.mean()) / pooled_std


def rank_biserial_r(u_stat, nx, ny):
    return 1 - (2 * u_stat) / (nx * ny)


def group_compare(ptsd_vals, no_ptsd_vals):
    """Run Shapiro+Levene then choose Student/Welch/MW. Returns dict of stats."""
    nx, ny = len(ptsd_vals), len(no_ptsd_vals)
    sw_p_ptsd = stats.shapiro(ptsd_vals).pvalue
    sw_p_noptsd = stats.shapiro(no_ptsd_vals).pvalue
    lev_p = stats.levene(ptsd_vals, no_ptsd_vals).pvalue
    both_normal = sw_p_ptsd > ALPHA and sw_p_noptsd > ALPHA
    equal_var = lev_p > ALPHA
    if both_normal and equal_var:
        test_name = "Student's t"
        stat_result = stats.ttest_ind(ptsd_vals, no_ptsd_vals, equal_var=True)
        es_name, es_val = "Cohen's d", cohens_d(ptsd_vals, no_ptsd_vals)
    elif both_normal:
        test_name = "Welch's t"
        stat_result = stats.ttest_ind(ptsd_vals, no_ptsd_vals, equal_var=False)
        es_name, es_val = "Cohen's d", cohens_d(ptsd_vals, no_ptsd_vals)
    else:
        test_name = "MW-U"
        stat_result = stats.mannwhitneyu(ptsd_vals, no_ptsd_vals, alternative='two-sided')
        es_name, es_val = "rank-biserial r", rank_biserial_r(stat_result.statistic, nx, ny)
    return {
        'test': test_name,
        'statistic': stat_result.statistic,
        'p_uncorrected': stat_result.pvalue,
        'es_type': es_name,
        'es': es_val,
        'n_PTSD': nx,
        'n_no_PTSD': ny,
    }


def correlate(x, y):
    """Run Shapiro on each + 3σ outlier check → Pearson else Kendall."""
    sw_p_x = stats.shapiro(x).pvalue
    sw_p_y = stats.shapiro(y).pvalue
    has_outliers = ((np.abs((x - x.mean()) / x.std(ddof=1)) > 3).any()
                    or (np.abs((y - y.mean()) / y.std(ddof=1)) > 3).any())
    use_pearson = (sw_p_x > ALPHA) and (sw_p_y > ALPHA) and not has_outliers
    if use_pearson:
        r, p = stats.pearsonr(x, y)
        return {'test': 'Pearson r', 'r': r, 'p_uncorrected': p, 'n': len(x)}
    else:
        tau, p = stats.kendalltau(x, y)
        return {'test': "Kendall τ_b", 'r': tau, 'p_uncorrected': p, 'n': len(x)}


def bh_correct(p_values):
    if len(p_values) == 0:
        return []
    _, p_corr, _, _ = multipletests(p_values, alpha=ALPHA, method='fdr_bh')
    return p_corr


def expected_sign_for(hyp, cat):
    """Pre-registered expected direction. PTSD higher = positive."""
    if hyp == 'H1':  # threat dwell time
        return '+'
    if hyp == 'H2':  # threat dwell variability
        return '+'
    if hyp == 'H3':  # threat-minus-neutral SD
        return '+'
    if hyp == 'H5':  # visits to threat
        return '+'
    return None  # H4/H6 are correlations, see expected_corr_for


def expected_corr_for(hyp):
    """Within-PTSD correlation expected direction. Sign ITI relates to DV."""
    if hyp == 'H4':
        return '+'  # higher ITI → higher SD
    if hyp == 'H6':
        # avoidance hypothesis: higher ITI → lower dwell, lower visits, more off-screen
        return {  # by family prefix
            'mean_dwell_pct_': '-',
            'mean_visits_': '-',
            'mean_offscreen_pct_': '+',
        }
    return None


# %% [markdown]
# ## Load datasets

# %%
orig = pd.read_csv(ORIG_CSV)
clean = pd.read_csv(CLEAN_CSV)
print(f"Original: {orig.shape}; Cleaned: {clean.shape}")
assert sorted(orig['session_id']) == sorted(clean['session_id'])

# %% [markdown]
# ## Run all hypothesis families on both datasets
#
# Each family is one round of BH correction. The result is a long DataFrame
# with one row per (hypothesis, family, category, dataset).

# %%
def run_group_comparison_family(df, hyp, family, dv_template):
    rows = []
    ptsd = df[df['if_PTSD'] == 1]
    no_ptsd = df[df['if_PTSD'] == 0]
    pvals = []
    for cat in THREAT_CATEGORIES:
        col = dv_template.format(cat=cat)
        x = ptsd[col].dropna()
        y = no_ptsd[col].dropna()
        r = group_compare(x, y)
        r.update({'hypothesis': hyp, 'family': family, 'category': cat})
        rows.append(r)
        pvals.append(r['p_uncorrected'])
    p_BH = bh_correct(pvals)
    for i, r in enumerate(rows):
        r['p_BH'] = p_BH[i]
        r['sig_BH'] = bool(p_BH[i] < ALPHA)
    return rows


def run_within_ptsd_correlation_family(df, hyp, family, dv_template, iv_col='ITI_PTSD'):
    rows = []
    ptsd = df[df['if_PTSD'] == 1]
    pvals = []
    for cat in THREAT_CATEGORIES:
        col = dv_template.format(cat=cat)
        sub = ptsd[[iv_col, col]].dropna()
        x = sub[col].values
        y = sub[iv_col].values
        # Use pandas Series for the correlate helper's outlier check
        x_s = pd.Series(x); y_s = pd.Series(y)
        r = correlate(x_s, y_s)
        r.update({'hypothesis': hyp, 'family': family, 'category': cat})
        rows.append(r)
        pvals.append(r['p_uncorrected'])
    p_BH = bh_correct(pvals)
    for i, r in enumerate(rows):
        r['p_BH'] = p_BH[i]
        r['sig_BH'] = bool(p_BH[i] < ALPHA)
    return rows


def run_all(df):
    rows = []
    rows += run_group_comparison_family(df, 'H1', 'mean_dwell_pct',     'mean_dwell_pct_{cat}')
    rows += run_group_comparison_family(df, 'H2', 'std_dwell_pct',      'std_dwell_pct_{cat}')
    rows += run_group_comparison_family(df, 'H3', 'std_delta_dwell_pct', 'std_delta_dwell_pct_{cat}')
    rows += run_within_ptsd_correlation_family(df, 'H4', 'std_dwell_pct',      'std_dwell_pct_{cat}')
    rows += run_within_ptsd_correlation_family(df, 'H4', 'std_delta_dwell_pct', 'std_delta_dwell_pct_{cat}')
    rows += run_group_comparison_family(df, 'H5', 'mean_visits',      'mean_visits_{cat}')
    rows += run_group_comparison_family(df, 'H5', 'mean_visits_late', 'mean_visits_late_{cat}')
    rows += run_within_ptsd_correlation_family(df, 'H6', 'mean_dwell_pct',         'mean_dwell_pct_{cat}')
    rows += run_within_ptsd_correlation_family(df, 'H6', 'mean_visits',            'mean_visits_{cat}')
    rows += run_within_ptsd_correlation_family(df, 'H6', 'mean_dwell_pct_late',    'mean_dwell_pct_late_{cat}')
    rows += run_within_ptsd_correlation_family(df, 'H6', 'mean_visits_late',       'mean_visits_late_{cat}')
    rows += run_within_ptsd_correlation_family(df, 'H6', 'mean_offscreen_pct',     'mean_offscreen_pct_{cat}')
    rows += run_within_ptsd_correlation_family(df, 'H6', 'mean_offscreen_pct_late', 'mean_offscreen_pct_late_{cat}')
    return pd.DataFrame(rows)


orig_results = run_all(orig)
clean_results = run_all(clean)
orig_results['dataset'] = 'orig'
clean_results['dataset'] = 'clean'

# %% [markdown]
# ## Build comparison

# %%
# Long form
long = pd.concat([orig_results, clean_results], ignore_index=True)
key_cols = ['hypothesis', 'family', 'category']
metric_cols = ['test', 'p_uncorrected', 'p_BH', 'sig_BH']

# Detect which is correlation vs group-comparison rows by presence of 'es' or 'r' field
def es_or_r(row):
    return row['es'] if 'es' in row and not pd.isna(row.get('es', np.nan)) else row.get('r', np.nan)

long['effect'] = long.apply(es_or_r, axis=1)

orig_w = long[long['dataset'] == 'orig'].set_index(key_cols)[['test', 'effect', 'p_uncorrected', 'p_BH', 'sig_BH']]
clean_w = long[long['dataset'] == 'clean'].set_index(key_cols)[['test', 'effect', 'p_uncorrected', 'p_BH', 'sig_BH']]
combined = orig_w.join(clean_w, lsuffix='_orig', rsuffix='_clean').reset_index()

# Compute deltas
combined['delta_effect'] = combined['effect_clean'] - combined['effect_orig']
combined['delta_p_unc'] = combined['p_uncorrected_clean'] - combined['p_uncorrected_orig']

# Determine 'expected' direction per row
def expected_for(row):
    hyp, fam = row['hypothesis'], row['family']
    if hyp in ('H1', 'H2', 'H3', 'H5'):
        return '+'
    if hyp == 'H4':
        return '+'
    if hyp == 'H6':
        if fam.startswith('mean_offscreen'):
            return '+'
        if fam.startswith('mean_dwell') or fam.startswith('mean_visits'):
            return '-'
    return None

combined['expected'] = combined.apply(expected_for, axis=1)


def improvement_label(row):
    """Did the cleaned result move in the expected direction (and lower p)?"""
    e = row['expected']
    if e is None:
        return '—'
    moved = (row['delta_effect'] > 0) if e == '+' else (row['delta_effect'] < 0)
    p_better = row['delta_p_unc'] < 0
    if moved and p_better:
        return 'improved'
    if moved and not p_better:
        return 'effect↑ p↑'
    if (not moved) and p_better:
        return 'p↓ effect↓'
    return 'regressed'

combined['change'] = combined.apply(improvement_label, axis=1)

# %% [markdown]
# ## Print summary table

# %%
print("=" * 110)
print("HYPOTHESIS RE-EVALUATION — original vs. image-cleaned (n = 29)")
print("=" * 110)
for hyp in ['H1', 'H2', 'H3', 'H4', 'H5', 'H6']:
    sub = combined[combined['hypothesis'] == hyp]
    print(f"\n--- {hyp} ---")
    print(sub[['family', 'category', 'test_orig', 'effect_orig', 'p_uncorrected_orig',
                'effect_clean', 'p_uncorrected_clean', 'delta_effect', 'change']]
          .to_string(index=False, float_format='%.3f'))

# Aggregate counters
n_improved = (combined['change'] == 'improved').sum()
n_regressed = (combined['change'] == 'regressed').sum()
n_total_directional = combined['expected'].notna().sum()
n_sig_orig = combined['sig_BH_orig'].sum()
n_sig_clean = combined['sig_BH_clean'].sum()
print(f"\nDirectional rows: {n_total_directional}; improved: {n_improved}; regressed: {n_regressed}")
print(f"BH-significant rows: orig={n_sig_orig}, clean={n_sig_clean}")

# %% [markdown]
# ## Write Markdown report

# %%
def fmt(x, n=3):
    if pd.isna(x):
        return '—'
    return f'{x:+.{n}f}' if isinstance(x, float) else str(x)


lines = [
    '# Step 7 — Hypothesis Re-Evaluation Comparison',
    '',
    'Re-runs H1–H6 on both the original analysis dataset (n = 29) and the',
    'image-cleaned variant from Step 6, with identical test selection logic.',
    'Each family receives Benjamini-Hochberg FDR correction (4 tests per family).',
    '',
    'Within each row, `effect_orig` / `effect_clean` is Cohen\'s d, rank-biserial r,',
    'Pearson r, or Kendall τ_b depending on which test was selected (column `test_*`).',
    'The `change` column tags whether the cleaned dataset moved in the pre-registered',
    'direction *and* lowered the uncorrected p-value:',
    '',
    '- **improved** — moved as predicted, p decreased',
    '- **regressed** — moved opposite to prediction, p increased',
    '- **effect↑ p↑** — moved as predicted but p increased (effect strengthened, less precise)',
    '- **p↓ effect↓** — opposite direction but p decreased (different finding, more precise)',
    '- **—** — no directional expectation (none of H1–H6 currently)',
    '',
    f'**Aggregate**: {n_improved} of {n_total_directional} rows improved; '
    f'{n_regressed} regressed.  '
    f'BH-significant rows: orig = {n_sig_orig}, clean = {n_sig_clean}.',
    '',
]

for hyp in ['H1', 'H2', 'H3', 'H4', 'H5', 'H6']:
    sub = combined[combined['hypothesis'] == hyp].sort_values(['family', 'category'])
    titles = {
        'H1': 'H1 — Threat Stimulus Dwell Time × PTSD Group',
        'H2': 'H2 — Threat Dwell-Time Variability × PTSD Group',
        'H3': 'H3 — Threat-minus-Neutral Bias Variability × PTSD Group',
        'H4': 'H4 — Within-PTSD Correlation: Variability vs. ITI_PTSD',
        'H5': 'H5 — Visits to Threat Stimuli × PTSD Group',
        'H6': 'H6 — Within-PTSD Correlation: Avoidance-Like Gaze vs. ITI_PTSD',
    }
    lines.append(f'## {titles[hyp]}')
    lines.append('')
    lines.append('| Family | Category | Test (orig) | effect_orig | p_unc orig | p_BH orig | effect_clean | p_unc clean | p_BH clean | Δeffect | Δp_unc | change |')
    lines.append('|---|---|---|---|---|---|---|---|---|---|---|---|')
    for _, r in sub.iterrows():
        lines.append(
            f"| {r['family']} | {r['category']} | {r['test_orig']} | "
            f"{r['effect_orig']:+.3f} | {r['p_uncorrected_orig']:.3f} | {r['p_BH_orig']:.3f} | "
            f"{r['effect_clean']:+.3f} | {r['p_uncorrected_clean']:.3f} | {r['p_BH_clean']:.3f} | "
            f"{r['delta_effect']:+.3f} | {r['delta_p_unc']:+.3f} | {r['change']} |"
        )
    sub_dir = sub[sub['expected'].notna()]
    n_imp = (sub_dir['change'] == 'improved').sum()
    n_reg = (sub_dir['change'] == 'regressed').sum()
    sig_o = int(sub['sig_BH_orig'].sum())
    sig_c = int(sub['sig_BH_clean'].sum())
    lines.append('')
    lines.append(f'**{hyp} summary**: {n_imp}/{len(sub_dir)} rows improved, {n_reg}/{len(sub_dir)} regressed; '
                 f'BH-sig orig={sig_o}, clean={sig_c}.')
    lines.append('')

# Overall verdict
lines.append('## Overall verdict')
lines.append('')
lines.append(f'- **{n_improved}/{n_total_directional}** directional rows improved across all 6 hypotheses.')
lines.append(f'- **{n_regressed}/{n_total_directional}** regressed.')
lines.append(f'- BH-significant findings: **orig = {n_sig_orig}**, **clean = {n_sig_clean}**.')
lines.append('')
if n_improved > n_regressed:
    lines.append('Image cleanup moved more results in the predicted direction than against it.')
elif n_regressed > n_improved:
    lines.append('Image cleanup moved more results against the predicted direction than toward it.')
else:
    lines.append('Image cleanup produced a roughly equal mix of improvements and regressions.')
if n_sig_clean > n_sig_orig:
    lines.append(f'BH-significance count increased by {n_sig_clean - n_sig_orig}.')
elif n_sig_clean < n_sig_orig:
    lines.append(f'BH-significance count decreased by {n_sig_orig - n_sig_clean}.')
else:
    lines.append('BH-significance count is unchanged.')
lines.append('')
lines.append(f'See `data/simplified/image_quality_flags.csv` for the flag table and '
             f'`reports/cleanup_evaluation/06_cleaned_dataset_summary.md` for the per-category retention rates.')

with open(REPORT_PATH, 'w') as f:
    f.write('\n'.join(lines) + '\n')
print(f"\nReport written: {REPORT_PATH}")

# Persist the combined table for later inspection
combined.to_csv('reports/cleanup_evaluation/07_hypotheses_comparison_table.csv', index=False)
print("Wrote: reports/cleanup_evaluation/07_hypotheses_comparison_table.csv")
