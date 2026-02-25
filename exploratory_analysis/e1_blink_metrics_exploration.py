# %% [markdown]
# # E1: Exploratory Blink Metrics Analysis
#
# **Context**: The preanalysis overview (`reports/preanalysis_overview/blink_metrics_overview_report.md`)
# identified that many blink metrics suffer from structural missingness (blink duration,
# std duration, latency per category) and questionable differentiability across stimulus
# categories (very high intercorrelations for blink rate r=0.43–0.97, duration r=0.51–1.00).
#
# Based on those findings, we selected a subset of metrics that are either complete
# (no missingness) or represent global summaries, plus per-category blink rate for the
# 4 threat categories. This is an **exploratory analysis (E1)**, not a confirmatory
# hypothesis test.
#
# **Method**: Two complementary approaches:
# - **Part A**: Group comparison (PTSD vs No-PTSD)
# - **Part B**: Within-PTSD correlational analysis (ITI_PTSD as continuous IV)
#
# BH-FDR correction applied separately within each of 4 families, for both Parts A and B.

# %%
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.nonparametric.smoothers_lowess import lowess as sm_lowess

os.chdir(Path(__file__).resolve().parent.parent)

# %%
# --- Constants & helpers ---

THREAT_CATEGORIES = ['angry_face', 'anxiety_inducing', 'warfare', 'soldiers']
ALPHA = 0.05
FIG_DIR = 'figures/e1_blink_metrics_exploration'
os.makedirs(FIG_DIR, exist_ok=True)

# Colors
COLOR_PTSD = '#d9534f'
COLOR_NO_PTSD = '#5bc0de'


def cohens_d(x, y):
    """Compute Cohen's d for independent samples."""
    nx, ny = len(x), len(y)
    pooled_std = np.sqrt(((nx - 1) * x.std(ddof=1)**2 + (ny - 1) * y.std(ddof=1)**2) / (nx + ny - 2))
    return (x.mean() - y.mean()) / pooled_std


def cohens_d_ci(d, nx, ny, confidence=0.95):
    """Approximate 95% CI for Cohen's d."""
    se = np.sqrt(nx + ny) / np.sqrt(nx * ny) * np.sqrt(1 + d**2 * nx * ny / (2 * (nx + ny)))
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    return d - z * se, d + z * se


def rank_biserial_r(u_stat, nx, ny):
    """Compute rank-biserial r from Mann-Whitney U."""
    return 1 - (2 * u_stat) / (nx * ny)


def rank_biserial_ci(r, nx, ny, confidence=0.95):
    """Approximate 95% CI for rank-biserial r via Fisher z transformation."""
    n = nx + ny
    z_r = np.arctanh(r)
    se = 1 / np.sqrt(n - 3)
    z_crit = stats.norm.ppf(1 - (1 - confidence) / 2)
    lo = np.tanh(z_r - z_crit * se)
    hi = np.tanh(z_r + z_crit * se)
    return lo, hi


def pearson_ci(r, n, confidence=0.95):
    """95% CI for Pearson r via Fisher z transformation."""
    z_r = np.arctanh(r)
    se = 1 / np.sqrt(n - 3)
    z_crit = stats.norm.ppf(1 - (1 - confidence) / 2)
    lo = np.tanh(z_r - z_crit * se)
    hi = np.tanh(z_r + z_crit * se)
    return lo, hi


def kendall_ci_bootstrap(x, y, n_boot=10000, seed=42):
    """Bootstrap 95% CI for Kendall's tau_b."""
    rng = np.random.RandomState(seed)
    n = len(x)
    taus = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.randint(0, n, size=n)
        taus[i] = stats.kendalltau(x[idx], y[idx]).statistic
    lo = np.percentile(taus, 2.5)
    hi = np.percentile(taus, 97.5)
    return lo, hi


def run_correlation(dv_vals, iv_vals, use_pearson):
    """Run Pearson or Kendall correlation based on assumption checks."""
    if use_pearson:
        r, p = stats.pearsonr(dv_vals, iv_vals)
        ci_lo, ci_hi = pearson_ci(r, len(dv_vals))
        return "Pearson's r", r, p, ci_lo, ci_hi
    else:
        tau, p = stats.kendalltau(dv_vals, iv_vals)
        ci_lo, ci_hi = kendall_ci_bootstrap(dv_vals.values, iv_vals.values)
        return "Kendall's τ_b", tau, p, ci_lo, ci_hi

# %%
# --- Load data & split groups ---

df = pd.read_csv('data/simplified/dataset_eyetracking_metrics_blink_clean.csv')
ptsd = df[df['if_PTSD'] == 1].copy()
no_ptsd = df[df['if_PTSD'] == 0].copy()

IV_COL = 'ITI_PTSD'

# DV families
DV_FAMILIES = {
    'F1: Blink Count & Interval': ['total_blink_count', 'mean_blink_interval_norm'],
    'F2: Blink Duration': ['mean_blink_duration_ms'],
    'F3: Interval Variability': ['std_blink_interval_norm'],
    'F4: Blink Rate (Threat)': [f'mean_blink_rate_{cat}' for cat in THREAT_CATEGORIES],
}
ALL_DV_COLS = [col for cols in DV_FAMILIES.values() for col in cols]

print(f"Total sample: n = {len(df)}")
print(f"PTSD group: n = {len(ptsd)}")
print(f"No-PTSD group: n = {len(no_ptsd)}")
print(f"\nMetrics under test: {len(ALL_DV_COLS)}")
for fam, cols in DV_FAMILIES.items():
    print(f"  {fam}: {cols}")

# %% [markdown]
# ---
# # Part A: Group Comparisons (PTSD vs No-PTSD)

# %% [markdown]
# ## A1. Descriptive Statistics

# %%
desc_rows = []
for family_label, dv_cols in DV_FAMILIES.items():
    for col in dv_cols:
        for group_label, group_df in [('PTSD', ptsd), ('No-PTSD', no_ptsd)]:
            vals = group_df[col].dropna()
            desc_rows.append({
                'Family': family_label,
                'Metric': col,
                'Group': group_label,
                'n': len(vals),
                'Mean': vals.mean(),
                'SD': vals.std(),
                'Median': vals.median(),
                'Min': vals.min(),
                'Max': vals.max(),
            })

desc_df = pd.DataFrame(desc_rows)
for family_label in DV_FAMILIES:
    print(f"\n=== Descriptive Statistics — {family_label} ===")
    print(desc_df[desc_df['Family'] == family_label].to_string(index=False, float_format='%.4f'))

# %% [markdown]
# ## A2. Assumption Checks

# %%
assumption_a_rows = []
for family_label, dv_cols in DV_FAMILIES.items():
    for col in dv_cols:
        ptsd_vals = ptsd[col].dropna()
        no_ptsd_vals = no_ptsd[col].dropna()

        sw_ptsd = stats.shapiro(ptsd_vals)
        sw_no_ptsd = stats.shapiro(no_ptsd_vals)
        lev = stats.levene(ptsd_vals, no_ptsd_vals)

        assumption_a_rows.append({
            'Family': family_label,
            'Metric': col,
            'Shapiro_PTSD_W': sw_ptsd.statistic,
            'Shapiro_PTSD_p': sw_ptsd.pvalue,
            'Shapiro_NoPTSD_W': sw_no_ptsd.statistic,
            'Shapiro_NoPTSD_p': sw_no_ptsd.pvalue,
            'Levene_F': lev.statistic,
            'Levene_p': lev.pvalue,
            'Both_Normal': sw_ptsd.pvalue > ALPHA and sw_no_ptsd.pvalue > ALPHA,
            'Equal_Var': lev.pvalue > ALPHA,
        })

assumptions_a_df = pd.DataFrame(assumption_a_rows)
print("=== Part A Assumption Checks ===")
print(assumptions_a_df.to_string(index=False, float_format='%.4f'))

# %% [markdown]
# ## A3. Group Comparison Tests

# %%
results_a_rows = []
for i, row in assumptions_a_df.iterrows():
    col = row['Metric']
    family_label = row['Family']
    ptsd_vals = ptsd[col].dropna()
    no_ptsd_vals = no_ptsd[col].dropna()
    nx, ny = len(ptsd_vals), len(no_ptsd_vals)

    both_normal = row['Both_Normal']
    equal_var = row['Equal_Var']

    if both_normal and equal_var:
        test_name = "Student's t-test"
        stat_result = stats.ttest_ind(ptsd_vals, no_ptsd_vals, equal_var=True)
        test_stat, p_val = stat_result.statistic, stat_result.pvalue
        d = cohens_d(ptsd_vals, no_ptsd_vals)
        ci_lo, ci_hi = cohens_d_ci(d, nx, ny)
        es_name = "Cohen's d"
        es_val = d
    elif both_normal and not equal_var:
        test_name = "Welch's t-test"
        stat_result = stats.ttest_ind(ptsd_vals, no_ptsd_vals, equal_var=False)
        test_stat, p_val = stat_result.statistic, stat_result.pvalue
        d = cohens_d(ptsd_vals, no_ptsd_vals)
        ci_lo, ci_hi = cohens_d_ci(d, nx, ny)
        es_name = "Cohen's d"
        es_val = d
    else:
        test_name = "Mann-Whitney U"
        stat_result = stats.mannwhitneyu(ptsd_vals, no_ptsd_vals, alternative='two-sided')
        test_stat, p_val = stat_result.statistic, stat_result.pvalue
        r = rank_biserial_r(test_stat, nx, ny)
        ci_lo, ci_hi = rank_biserial_ci(r, nx, ny)
        es_name = "rank-biserial r"
        es_val = r

    results_a_rows.append({
        'Family': family_label,
        'Metric': col,
        'Test': test_name,
        'Statistic': test_stat,
        'p_uncorrected': p_val,
        'Effect_Size_Type': es_name,
        'Effect_Size': es_val,
        'CI_lo': ci_lo,
        'CI_hi': ci_hi,
    })

results_a_df = pd.DataFrame(results_a_rows)

# %% [markdown]
# ## A4. BH-FDR Correction (Group Comparisons)

# %%
results_a_df['p_BH'] = np.nan
results_a_df['Significant_BH'] = False

for family_label in DV_FAMILIES:
    mask = results_a_df['Family'] == family_label
    p_vals = results_a_df.loc[mask, 'p_uncorrected'].values
    if len(p_vals) > 1:
        reject, p_bh, _, _ = multipletests(p_vals, alpha=ALPHA, method='fdr_bh')
        results_a_df.loc[mask, 'p_BH'] = p_bh
        results_a_df.loc[mask, 'Significant_BH'] = reject
    else:
        # Single test in family — no correction needed
        results_a_df.loc[mask, 'p_BH'] = p_vals[0]
        results_a_df.loc[mask, 'Significant_BH'] = p_vals[0] < ALPHA

# %%
print("\n" + "=" * 95)
print("RESULTS — Part A: Group Comparisons (PTSD vs No-PTSD)")
print("=" * 95)

for family_label in DV_FAMILIES:
    fam = results_a_df[results_a_df['Family'] == family_label]
    print(f"\n--- {family_label} ---")
    for _, r in fam.iterrows():
        sig_label = "SIGNIFICANT" if r['Significant_BH'] else "not significant"
        print(f"\n  {r['Metric']}:")
        print(f"    Test: {r['Test']}, stat = {r['Statistic']:.4f}")
        print(f"    p (uncorrected) = {r['p_uncorrected']:.4f}, p (BH) = {r['p_BH']:.4f} → {sig_label}")
        print(f"    {r['Effect_Size_Type']} = {r['Effect_Size']:.4f}, 95% CI [{r['CI_lo']:.4f}, {r['CI_hi']:.4f}]")

any_sig_a = results_a_df['Significant_BH'].any()
print(f"\nPart A overall: {'At least one significant result' if any_sig_a else 'No significant results'} at α = {ALPHA} (BH-corrected)")
print("=" * 95)

# %% [markdown]
# ## A5. Visualizations — Group Comparisons

# %%
# --- Violin + strip plots: Global metrics ---
global_cols = ['total_blink_count', 'mean_blink_duration_ms', 'mean_blink_interval_norm', 'std_blink_interval_norm']

fig, axes = plt.subplots(1, 4, figsize=(18, 5))
for i, col in enumerate(global_cols):
    ax = axes[i]
    plot_data = df[['if_PTSD', col]].dropna().copy()
    plot_data['Group'] = plot_data['if_PTSD'].map({1: 'PTSD', 0: 'No-PTSD'})

    sns.violinplot(data=plot_data, x='Group', y=col, order=['PTSD', 'No-PTSD'],
                   palette={'PTSD': COLOR_PTSD, 'No-PTSD': COLOR_NO_PTSD},
                   inner=None, alpha=0.4, ax=ax)
    sns.stripplot(data=plot_data, x='Group', y=col, order=['PTSD', 'No-PTSD'],
                  palette={'PTSD': COLOR_PTSD, 'No-PTSD': COLOR_NO_PTSD},
                  size=5, alpha=0.7, ax=ax)
    ax.set_title(col, fontsize=9)
    ax.set_xlabel('')

fig.suptitle('E1 Part A: Global Blink Metrics by Group', fontsize=13, y=1.02)
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/violin_strip_global.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/violin_strip_global.png')

# %%
# --- Violin + strip plots: Blink rate by threat category ---
rate_cols = [f'mean_blink_rate_{cat}' for cat in THREAT_CATEGORIES]

fig, axes = plt.subplots(1, 4, figsize=(18, 5))
for i, (cat, col) in enumerate(zip(THREAT_CATEGORIES, rate_cols)):
    ax = axes[i]
    plot_data = df[['if_PTSD', col]].dropna().copy()
    plot_data['Group'] = plot_data['if_PTSD'].map({1: 'PTSD', 0: 'No-PTSD'})

    sns.violinplot(data=plot_data, x='Group', y=col, order=['PTSD', 'No-PTSD'],
                   palette={'PTSD': COLOR_PTSD, 'No-PTSD': COLOR_NO_PTSD},
                   inner=None, alpha=0.4, ax=ax)
    sns.stripplot(data=plot_data, x='Group', y=col, order=['PTSD', 'No-PTSD'],
                  palette={'PTSD': COLOR_PTSD, 'No-PTSD': COLOR_NO_PTSD},
                  size=5, alpha=0.7, ax=ax)
    ax.set_title(cat, fontsize=9)
    ax.set_xlabel('')

fig.suptitle('E1 Part A: Blink Rate (Threat Categories) by Group', fontsize=13, y=1.02)
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/violin_strip_blink_rate.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/violin_strip_blink_rate.png')

# %%
# --- Forest plot of effect sizes (all 8 metrics) ---
fig, ax = plt.subplots(figsize=(10, 6))
y_pos = np.arange(len(results_a_df))
labels = []
for _, r in results_a_df.iterrows():
    color = '#d9534f' if r['Significant_BH'] else '#333333'
    idx = len(labels)
    ax.errorbar(r['Effect_Size'], idx,
                xerr=[[r['Effect_Size'] - r['CI_lo']], [r['CI_hi'] - r['Effect_Size']]],
                fmt='o', color=color, markersize=8, capsize=5, linewidth=2)
    short_name = r['Metric'].replace('mean_blink_rate_', 'rate: ')
    labels.append(f"{short_name} ({r['Effect_Size_Type']})")

ax.axvline(x=0, color='grey', linestyle='--', linewidth=1)
ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=8)
ax.set_xlabel('Effect Size (95% CI)')
ax.set_title('E1 Part A: Effect Sizes — PTSD vs No-PTSD')
ax.invert_yaxis()
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/forest_plot_part_a.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/forest_plot_part_a.png')

# %%
# --- Bar chart with 95% CI error bars ---
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Panel 1: Global metrics
ax = axes[0]
global_desc = desc_df[desc_df['Metric'].isin(global_cols)].copy()
metrics_unique = global_cols
x = np.arange(len(metrics_unique))
width = 0.35
for j, group_label in enumerate(['PTSD', 'No-PTSD']):
    g = global_desc[global_desc['Group'] == group_label]
    means = [g[g['Metric'] == m]['Mean'].values[0] for m in metrics_unique]
    ci95 = [1.96 * g[g['Metric'] == m]['SD'].values[0] / np.sqrt(g[g['Metric'] == m]['n'].values[0])
            for m in metrics_unique]
    offset = -width / 2 if j == 0 else width / 2
    color = COLOR_PTSD if group_label == 'PTSD' else COLOR_NO_PTSD
    ax.bar(x + offset, means, width, yerr=ci95, label=group_label,
           color=color, alpha=0.7, capsize=5)
ax.set_xticks(x)
ax.set_xticklabels([m.replace('mean_', '').replace('_', '\n') for m in metrics_unique], fontsize=8)
ax.set_title('Global Blink Metrics')
ax.legend()

# Panel 2: Blink rate by threat category
ax = axes[1]
rate_desc = desc_df[desc_df['Metric'].isin(rate_cols)].copy()
x = np.arange(len(THREAT_CATEGORIES))
for j, group_label in enumerate(['PTSD', 'No-PTSD']):
    g = rate_desc[rate_desc['Group'] == group_label]
    means = [g[g['Metric'] == f'mean_blink_rate_{cat}']['Mean'].values[0] for cat in THREAT_CATEGORIES]
    ci95 = [1.96 * g[g['Metric'] == f'mean_blink_rate_{cat}']['SD'].values[0] /
            np.sqrt(g[g['Metric'] == f'mean_blink_rate_{cat}']['n'].values[0])
            for cat in THREAT_CATEGORIES]
    offset = -width / 2 if j == 0 else width / 2
    color = COLOR_PTSD if group_label == 'PTSD' else COLOR_NO_PTSD
    ax.bar(x + offset, means, width, yerr=ci95, label=group_label,
           color=color, alpha=0.7, capsize=5)
ax.set_xticks(x)
ax.set_xticklabels(THREAT_CATEGORIES, fontsize=8, rotation=20)
ax.set_title('Blink Rate (Threat Categories)')
ax.legend()

fig.suptitle('E1 Part A: Group Means ± 95% CI — PTSD vs No-PTSD', fontsize=13, y=1.02)
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/bar_chart_part_a.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/bar_chart_part_a.png')

# %% [markdown]
# ---
# # Part B: Correlational Analysis (within PTSD group)

# %% [markdown]
# ## B1. Assumption Checks

# %%
iv_vals = ptsd[IV_COL].dropna()
sw_iv = stats.shapiro(iv_vals)
iv_normal = sw_iv.pvalue > ALPHA
print(f"Shapiro-Wilk on {IV_COL}: W = {sw_iv.statistic:.4f}, p = {sw_iv.pvalue:.4f} → {'Normal' if iv_normal else 'Non-normal'}")
print()

assumption_b_rows = []
for col in ALL_DV_COLS:
    dv = ptsd[col].dropna()
    iv = ptsd.loc[dv.index, IV_COL]
    sw_dv = stats.shapiro(dv)
    dv_normal = sw_dv.pvalue > ALPHA
    both_normal = iv_normal and dv_normal

    # Outlier detection via standardized OLS residuals
    slope, intercept = np.polyfit(iv, dv, 1)
    fitted = intercept + slope * iv
    residuals = dv - fitted
    z_resid = (residuals - residuals.mean()) / residuals.std()
    n_outliers = int((z_resid.abs() > 3).sum())

    assumption_b_rows.append({
        'Metric': col,
        'Shapiro_DV_W': sw_dv.statistic,
        'Shapiro_DV_p': sw_dv.pvalue,
        'DV_Normal': dv_normal,
        'IV_Normal': iv_normal,
        'Both_Normal': both_normal,
        'N_Outliers': n_outliers,
        'Has_Outliers': n_outliers > 0,
        'Use_Pearson': both_normal and n_outliers == 0,
    })

assumptions_b_df = pd.DataFrame(assumption_b_rows)
print("=== Part B Assumption Checks ===")
print(assumptions_b_df.to_string(index=False, float_format='%.4f'))
print(f"\nOutlier summary: {assumptions_b_df['Has_Outliers'].sum()} of {len(assumptions_b_df)} DVs have outliers (|z_resid| > 3)")

# %% [markdown]
# ## B2. Correlation Tests

# %%
results_b_rows = []
dv_idx = 0
for family_label, dv_cols in DV_FAMILIES.items():
    for j, col in enumerate(dv_cols):
        dv = ptsd[col].dropna()
        iv = ptsd.loc[dv.index, IV_COL]
        use_pearson = assumptions_b_df.iloc[dv_idx + j]['Use_Pearson']
        test_name, coef, p_val, ci_lo, ci_hi = run_correlation(dv, iv, use_pearson)
        results_b_rows.append({
            'Family': family_label,
            'Metric': col,
            'Test': test_name,
            'Coefficient': coef,
            'p_uncorrected': p_val,
            'CI_lo': ci_lo,
            'CI_hi': ci_hi,
        })
    dv_idx += len(dv_cols)

results_b_df = pd.DataFrame(results_b_rows)

# %% [markdown]
# ## B3. BH-FDR Correction (Correlations)

# %%
results_b_df['p_BH'] = np.nan
results_b_df['Significant_BH'] = False

for family_label in DV_FAMILIES:
    mask = results_b_df['Family'] == family_label
    p_vals = results_b_df.loc[mask, 'p_uncorrected'].values
    if len(p_vals) > 1:
        reject, p_bh, _, _ = multipletests(p_vals, alpha=ALPHA, method='fdr_bh')
        results_b_df.loc[mask, 'p_BH'] = p_bh
        results_b_df.loc[mask, 'Significant_BH'] = reject
    else:
        results_b_df.loc[mask, 'p_BH'] = p_vals[0]
        results_b_df.loc[mask, 'Significant_BH'] = p_vals[0] < ALPHA

# %%
print("\n" + "=" * 95)
print("RESULTS — Part B: Correlational Analysis (ITI_PTSD × Blink Metrics, PTSD group)")
print("=" * 95)

for family_label in DV_FAMILIES:
    fam = results_b_df[results_b_df['Family'] == family_label]
    print(f"\n--- {family_label} ---")
    for _, r in fam.iterrows():
        sig_label = "SIGNIFICANT" if r['Significant_BH'] else "not significant"
        print(f"\n  {r['Metric']}:")
        print(f"    Test: {r['Test']}, coef = {r['Coefficient']:.4f}")
        print(f"    p (uncorrected) = {r['p_uncorrected']:.4f}, p (BH) = {r['p_BH']:.4f} → {sig_label}")
        print(f"    95% CI [{r['CI_lo']:.4f}, {r['CI_hi']:.4f}]")

any_sig_b = results_b_df['Significant_BH'].any()
print(f"\nPart B overall: {'At least one significant result' if any_sig_b else 'No significant results'} at α = {ALPHA} (BH-corrected)")
print("=" * 95)

# %% [markdown]
# ## B4. Visualizations — Correlations

# %%
# --- Scatter plots with regression lines (all 8 metrics) ---
n_metrics = len(ALL_DV_COLS)
n_cols_plot = 4
n_rows_plot = 2

fig, axes = plt.subplots(n_rows_plot, n_cols_plot, figsize=(20, 10))
axes_flat = axes.flatten()

for i, col in enumerate(ALL_DV_COLS):
    ax = axes_flat[i]
    dv = ptsd[col].dropna()
    iv = ptsd.loc[dv.index, IV_COL]

    # Outlier detection
    slope, intercept = np.polyfit(iv, dv, 1)
    fitted = intercept + slope * iv
    residuals = dv - fitted
    z_resid = (residuals - residuals.mean()) / residuals.std()
    outlier_mask = z_resid.abs() > 3

    ax.scatter(iv[~outlier_mask], dv[~outlier_mask], color=COLOR_PTSD, alpha=0.7,
               s=50, edgecolors='white', linewidth=0.5, label='Normal')
    if outlier_mask.any():
        ax.scatter(iv[outlier_mask], dv[outlier_mask], color='#f0ad4e', alpha=0.9,
                   s=100, edgecolors='black', linewidth=1, zorder=5, label='Outlier')

    x_range = np.linspace(iv.min(), iv.max(), 100)
    ax.plot(x_range, intercept + slope * x_range, '--', color=COLOR_PTSD, alpha=0.6, linewidth=1.5)

    # Add LOWESS
    lowess_result = sm_lowess(dv.values, iv.values, frac=0.6)
    ax.plot(lowess_result[:, 0], lowess_result[:, 1], color='#337ab7', linewidth=2, label='LOWESS')

    r_row = results_b_df[results_b_df['Metric'] == col].iloc[0]
    ax.set_title(f"{col.replace('mean_blink_rate_', 'rate: ')}\n{r_row['Test']}: {r_row['Coefficient']:.3f}, p = {r_row['p_uncorrected']:.3f}",
                 fontsize=8)
    ax.set_xlabel('ITI_PTSD', fontsize=8)
    ax.set_ylabel(col.split('_')[-1] if 'rate' in col else col, fontsize=7)
    ax.tick_params(labelsize=7)
    if outlier_mask.any():
        ax.legend(fontsize=6)

fig.suptitle('E1 Part B: Blink Metrics vs ITI_PTSD — Scatter Plots (PTSD Group)', fontsize=13, y=1.02)
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/scatterplots_part_b.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/scatterplots_part_b.png')

# %%
# --- Forest plot of correlation coefficients ---
fig, ax = plt.subplots(figsize=(10, 6))
labels = []
for idx, (_, r) in enumerate(results_b_df.iterrows()):
    color = '#d9534f' if r['Significant_BH'] else '#333333'
    ax.errorbar(r['Coefficient'], idx,
                xerr=[[r['Coefficient'] - r['CI_lo']], [r['CI_hi'] - r['Coefficient']]],
                fmt='o', color=color, markersize=8, capsize=5, linewidth=2)
    short_name = r['Metric'].replace('mean_blink_rate_', 'rate: ')
    labels.append(f"{short_name} ({r['Test']})")

ax.axvline(x=0, color='grey', linestyle='--', linewidth=1)
ax.set_yticks(np.arange(len(results_b_df)))
ax.set_yticklabels(labels, fontsize=8)
ax.set_xlabel('Correlation Coefficient (95% CI)')
ax.set_title('E1 Part B: Correlation Coefficients — ITI_PTSD × Blink Metrics')
ax.invert_yaxis()
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/forest_plot_part_b.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/forest_plot_part_b.png')

# %% [markdown]
# ---
# # Summary

# %%
print("\n" + "=" * 95)
print("COMBINED SUMMARY — E1: Exploratory Blink Metrics Analysis")
print("=" * 95)

print(f"\nSample: n = {len(df)} (PTSD: {len(ptsd)}, No-PTSD: {len(no_ptsd)})")
print(f"Metrics: {len(ALL_DV_COLS)} DVs across 4 families")

print("\n--- Part A: Group Comparisons (PTSD vs No-PTSD) ---")
for family_label in DV_FAMILIES:
    fam = results_a_df[results_a_df['Family'] == family_label]
    n_sig = fam['Significant_BH'].sum()
    n_total = len(fam)
    print(f"  {family_label}: {n_sig}/{n_total} significant (BH-corrected)")

print("\n--- Part B: Correlational Analysis (ITI_PTSD, within PTSD group, n=15) ---")
for family_label in DV_FAMILIES:
    fam = results_b_df[results_b_df['Family'] == family_label]
    n_sig = fam['Significant_BH'].sum()
    n_total = len(fam)
    print(f"  {family_label}: {n_sig}/{n_total} significant (BH-corrected)")

any_sig_overall = any_sig_a or any_sig_b
print(f"\nOverall: {'At least one significant result found' if any_sig_overall else 'No significant results'} at α = {ALPHA} (BH-corrected)")
print("\nNote: This is an exploratory analysis with a small sample (n=26). Results should be")
print("interpreted cautiously and treated as hypothesis-generating, not confirmatory.")
print("=" * 95)

