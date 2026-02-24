# %% [markdown]
# # H6: ITI Score and Avoidance-Like Gaze Behavior in PTSD Group
#
# **Hypothesis**: Within the PTSD subgroup (n=17), greater PTSD symptom severity
# (ITI score) is associated with more avoidance-like gaze toward threat stimuli —
# operationalised as lower dwell time, fewer visits, and higher off-screen looking.
#
# **Method**: Two complementary approaches:
# - **Part A**: Median-split group comparison (Higher-ITI vs Lower-ITI)
# - **Part B**: Within-group correlational analysis (ITI_PTSD as continuous IV)
#
# Across 6 DV families × 4 threat categories = 24 DVs total. BH-FDR correction
# is applied separately within each of the 6 families (4 p-values each) for both
# Parts A and B (12 correction rounds total).
#
# **Note**: This is a feasibility-limited hypothesis. With n≈8–9 per subgroup
# (Part A) and n=17 (Part B), statistical power is severely limited.

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

THREAT_CATEGORIES = ['angry_face', 'anxiety_inducing', 'warfare', 'soldiers']
IV_COL = 'ITI_PTSD'
ALPHA = 0.05

# 6 DV families
DV_FAMILIES = {
    'F1: Mean Dwell %': [f'mean_dwell_pct_{cat}' for cat in THREAT_CATEGORIES],
    'F2: Mean Visits': [f'mean_visits_{cat}' for cat in THREAT_CATEGORIES],
    'F3: Mean Dwell % (Late)': [f'mean_dwell_pct_late_{cat}' for cat in THREAT_CATEGORIES],
    'F4: Mean Visits (Late)': [f'mean_visits_late_{cat}' for cat in THREAT_CATEGORIES],
    'F5: Mean Off-Screen %': [f'mean_offscreen_pct_{cat}' for cat in THREAT_CATEGORIES],
    'F6: Mean Off-Screen % (Late)': [f'mean_offscreen_pct_late_{cat}' for cat in THREAT_CATEGORIES],
}
ALL_DV_COLS = [col for cols in DV_FAMILIES.values() for col in cols]

# Expected direction for high ITI: lower for F1-F4, higher for F5-F6
HIGHER_ITI_DIRECTION = {
    'F1: Mean Dwell %': 'lower',
    'F2: Mean Visits': 'lower',
    'F3: Mean Dwell % (Late)': 'lower',
    'F4: Mean Visits (Late)': 'lower',
    'F5: Mean Off-Screen %': 'higher',
    'F6: Mean Off-Screen % (Late)': 'higher',
}

FIG_DIR = 'figures/h6_iti_avoidance_gaze'
os.makedirs(FIG_DIR, exist_ok=True)

# Colors
COLOR_LOWER = '#5bc0de'
COLOR_HIGHER = '#d9534f'

# %%
# Load data, filter to PTSD group, compute median split
df = pd.read_csv('data/simplified/dataset_eyetracking_metrics_clean.csv')
ptsd = df[df['if_PTSD'] == 1].copy()

median_iti = ptsd[IV_COL].median()
ptsd['iti_group'] = np.where(ptsd[IV_COL] < median_iti, 'Lower-ITI', 'Higher-ITI')

lower_iti = ptsd[ptsd['iti_group'] == 'Lower-ITI']
higher_iti = ptsd[ptsd['iti_group'] == 'Higher-ITI']

print(f"PTSD group: n = {len(ptsd)}")
print(f"ITI_PTSD median = {median_iti}")
print(f"Lower-ITI (< median): n = {len(lower_iti)}")
print(f"Higher-ITI (> median): n = {len(higher_iti)}")
print(f"\n6 DV families × 4 threat categories = {len(ALL_DV_COLS)} DVs total")

# %% [markdown]
# ---
# # Part A: Median-Split Group Comparison

# %% [markdown]
# ## A1. Descriptive Statistics

# %%
desc_rows = []
for family_label, dv_cols in DV_FAMILIES.items():
    for cat, col in zip(THREAT_CATEGORIES, dv_cols):
        for group_label, group_df in [('Lower-ITI', lower_iti), ('Higher-ITI', higher_iti)]:
            vals = group_df[col].dropna()
            desc_rows.append({
                'Family': family_label,
                'Category': cat,
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
assumption_rows = []
for family_label, dv_cols in DV_FAMILIES.items():
    for cat, col in zip(THREAT_CATEGORIES, dv_cols):
        lo_vals = lower_iti[col].dropna()
        hi_vals = higher_iti[col].dropna()

        sw_lo = stats.shapiro(lo_vals)
        sw_hi = stats.shapiro(hi_vals)
        lev = stats.levene(lo_vals, hi_vals)

        assumption_rows.append({
            'Family': family_label,
            'Category': cat,
            'Shapiro_Lower_W': sw_lo.statistic,
            'Shapiro_Lower_p': sw_lo.pvalue,
            'Shapiro_Higher_W': sw_hi.statistic,
            'Shapiro_Higher_p': sw_hi.pvalue,
            'Levene_F': lev.statistic,
            'Levene_p': lev.pvalue,
            'Both_Normal': sw_lo.pvalue > ALPHA and sw_hi.pvalue > ALPHA,
            'Equal_Var': lev.pvalue > ALPHA,
        })

assumptions_a_df = pd.DataFrame(assumption_rows)
for family_label in DV_FAMILIES:
    print(f"\n=== Assumption Checks — {family_label} ===")
    fam = assumptions_a_df[assumptions_a_df['Family'] == family_label]
    print(fam.to_string(index=False, float_format='%.4f'))

# %% [markdown]
# ## A3. Helper Functions

# %%
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


def run_group_tests(dv_cols, assumptions_family):
    """Run group comparison tests for a family of DVs (Lower-ITI vs Higher-ITI)."""
    rows = []
    for i, col in enumerate(dv_cols):
        lo_vals = lower_iti[col].dropna()
        hi_vals = higher_iti[col].dropna()
        nx, ny = len(lo_vals), len(hi_vals)

        row = assumptions_family.iloc[i]
        both_normal = row['Both_Normal']
        equal_var = row['Equal_Var']

        if both_normal and equal_var:
            test_name = "Student's t-test"
            stat_result = stats.ttest_ind(hi_vals, lo_vals, equal_var=True)
            test_stat, p_val = stat_result.statistic, stat_result.pvalue
            d = cohens_d(hi_vals, lo_vals)
            ci_lo, ci_hi = cohens_d_ci(d, ny, nx)
            es_name = "Cohen's d"
            es_val = d
        elif both_normal and not equal_var:
            test_name = "Welch's t-test"
            stat_result = stats.ttest_ind(hi_vals, lo_vals, equal_var=False)
            test_stat, p_val = stat_result.statistic, stat_result.pvalue
            d = cohens_d(hi_vals, lo_vals)
            ci_lo, ci_hi = cohens_d_ci(d, ny, nx)
            es_name = "Cohen's d"
            es_val = d
        else:
            test_name = "Mann-Whitney U"
            stat_result = stats.mannwhitneyu(hi_vals, lo_vals, alternative='two-sided')
            test_stat, p_val = stat_result.statistic, stat_result.pvalue
            r = rank_biserial_r(test_stat, ny, nx)
            ci_lo, ci_hi = rank_biserial_ci(r, ny, nx)
            es_name = "rank-biserial r"
            es_val = r

        rows.append({
            'Category': THREAT_CATEGORIES[i],
            'Test': test_name,
            'Statistic': test_stat,
            'p_uncorrected': p_val,
            'Effect_Size_Type': es_name,
            'Effect_Size': es_val,
            'CI_lo': ci_lo,
            'CI_hi': ci_hi,
        })
    return pd.DataFrame(rows)

# %% [markdown]
# ## A4. Group Comparison Tests (All 6 Families)

# %%
results_a = {}
for family_label, dv_cols in DV_FAMILIES.items():
    assumptions_fam = assumptions_a_df[assumptions_a_df['Family'] == family_label].reset_index(drop=True)
    res = run_group_tests(dv_cols, assumptions_fam)

    # BH-FDR correction within family
    reject, p_bh, _, _ = multipletests(res['p_uncorrected'], alpha=ALPHA, method='fdr_bh')
    res['p_BH'] = p_bh
    res['Significant_BH'] = reject
    results_a[family_label] = res

    print(f"\n=== {family_label} — Group Comparison (Higher-ITI vs Lower-ITI) ===")
    display_cols = ['Category', 'Test', 'Statistic', 'p_uncorrected', 'p_BH',
                    'Effect_Size_Type', 'Effect_Size', 'CI_lo', 'CI_hi', 'Significant_BH']
    print(res[display_cols].to_string(index=False, float_format='%.4f'))

# %% [markdown]
# ## A5. Part A Results Summary

# %%
print("\n" + "=" * 95)
print("RESULTS SUMMARY — Part A: Median-Split Group Comparison (Higher-ITI vs Lower-ITI)")
print("=" * 95)

any_sig_a = False
for family_label, res in results_a.items():
    expected = HIGHER_ITI_DIRECTION[family_label]
    print(f"\n--- {family_label} (expected direction for higher ITI: {expected}) ---")
    for _, r in res.iterrows():
        sig_label = "SIGNIFICANT" if r['Significant_BH'] else "not significant"
        print(f"\n  {r['Category']}:")
        print(f"    Test: {r['Test']}, stat = {r['Statistic']:.4f}")
        print(f"    p (uncorrected) = {r['p_uncorrected']:.4f}, p (BH) = {r['p_BH']:.4f} → {sig_label}")
        print(f"    {r['Effect_Size_Type']} = {r['Effect_Size']:.4f}, 95% CI [{r['CI_lo']:.4f}, {r['CI_hi']:.4f}]")
    if res['Significant_BH'].any():
        any_sig_a = True

print(f"\nPart A overall: {'At least one significant result' if any_sig_a else 'No significant results'} at α = {ALPHA} (BH-corrected)")
print("=" * 95)

# %% [markdown]
# ## A6. Visualization A1 — Violin + Strip Plots

# %%
fig, axes = plt.subplots(2, 3, figsize=(20, 12))
axes = axes.flatten()

for idx, (family_label, dv_cols) in enumerate(DV_FAMILIES.items()):
    ax = axes[idx]
    plot_df = ptsd[['iti_group'] + dv_cols].copy()
    plot_long = plot_df.melt(id_vars=['iti_group'], value_vars=dv_cols,
                              var_name='DV', value_name='Value')
    # Shorten category names for display
    for cat in THREAT_CATEGORIES:
        plot_long['DV'] = plot_long['DV'].str.replace(f'.*_{cat}$', cat, regex=True)

    sns.violinplot(data=plot_long, x='DV', y='Value', hue='iti_group',
                   split=True, inner=None,
                   palette={'Lower-ITI': COLOR_LOWER, 'Higher-ITI': COLOR_HIGHER},
                   alpha=0.4, ax=ax)
    sns.stripplot(data=plot_long, x='DV', y='Value', hue='iti_group',
                  dodge=True,
                  palette={'Lower-ITI': COLOR_LOWER, 'Higher-ITI': COLOR_HIGHER},
                  size=4, alpha=0.7, ax=ax)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[:2], labels[:2], title='ITI Group', fontsize=7, loc='upper right')
    ax.set_title(family_label, fontsize=10)
    ax.set_xlabel('')
    ax.tick_params(axis='x', rotation=20, labelsize=8)

fig.suptitle('H6 Part A: Gaze Metrics by ITI Subgroup (PTSD group, median split)', fontsize=13, y=1.02)
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/violin_strip_all_families.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/violin_strip_all_families.png')

# %% [markdown]
# ## A7. Visualization A2 — Forest Plot (All Families)

# %%
fig, axes = plt.subplots(2, 3, figsize=(20, 12))
axes = axes.flatten()

for idx, (family_label, res) in enumerate(results_a.items()):
    ax = axes[idx]
    y_pos = np.arange(len(res))
    for i, (_, r) in enumerate(res.iterrows()):
        color = '#d9534f' if r['Significant_BH'] else '#333333'
        ax.errorbar(r['Effect_Size'], i,
                     xerr=[[r['Effect_Size'] - r['CI_lo']], [r['CI_hi'] - r['Effect_Size']]],
                     fmt='o', color=color, markersize=8, capsize=5, linewidth=2)
    ax.axvline(x=0, color='grey', linestyle='--', linewidth=1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(res['Category'])
    ax.set_xlabel('Effect Size (95% CI)')
    ax.set_title(f'{family_label}', fontsize=10)
    ax.invert_yaxis()

fig.suptitle('H6 Part A: Effect Sizes — Higher-ITI vs Lower-ITI (PTSD group)', fontsize=13, y=1.02)
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/forest_plot_part_a.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/forest_plot_part_a.png')

# %% [markdown]
# ## A8. Visualization A3 — Bar Charts (Group Means with 95% CI)

# %%
fig, axes = plt.subplots(2, 3, figsize=(20, 12))
axes = axes.flatten()

for idx, (family_label, dv_cols) in enumerate(DV_FAMILIES.items()):
    ax = axes[idx]
    bar_rows = []
    for cat, col in zip(THREAT_CATEGORIES, dv_cols):
        for group_label, group_df in [('Lower-ITI', lower_iti), ('Higher-ITI', higher_iti)]:
            vals = group_df[col].dropna()
            bar_rows.append({
                'Category': cat,
                'Group': group_label,
                'Mean': vals.mean(),
                'CI95': 1.96 * vals.std() / np.sqrt(len(vals)),
            })
    bar_df = pd.DataFrame(bar_rows)

    x = np.arange(len(THREAT_CATEGORIES))
    width = 0.35
    lo_means = bar_df[bar_df['Group'] == 'Lower-ITI']['Mean'].values
    lo_ci = bar_df[bar_df['Group'] == 'Lower-ITI']['CI95'].values
    hi_means = bar_df[bar_df['Group'] == 'Higher-ITI']['Mean'].values
    hi_ci = bar_df[bar_df['Group'] == 'Higher-ITI']['CI95'].values

    ax.bar(x - width / 2, lo_means, width, yerr=lo_ci, label='Lower-ITI',
           color=COLOR_LOWER, alpha=0.7, capsize=5)
    ax.bar(x + width / 2, hi_means, width, yerr=hi_ci, label='Higher-ITI',
           color=COLOR_HIGHER, alpha=0.7, capsize=5)

    ax.set_xticks(x)
    ax.set_xticklabels(THREAT_CATEGORIES, rotation=20, fontsize=8)
    ax.set_title(family_label, fontsize=10)
    ax.legend(title='ITI Group', fontsize=7)

fig.suptitle('H6 Part A: Group Means ± 95% CI — Higher-ITI vs Lower-ITI', fontsize=13, y=1.02)
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/bar_charts_part_a.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/bar_charts_part_a.png')

# %% [markdown]
# ---
# # Part B: Correlational Analysis

# %% [markdown]
# ## B1. Assumption Checks

# %%
# Shapiro-Wilk on ITI_PTSD (once)
iv_vals = ptsd[IV_COL].dropna()
sw_iv = stats.shapiro(iv_vals)
iv_normal = sw_iv.pvalue > ALPHA
print(f"Shapiro-Wilk on {IV_COL}: W = {sw_iv.statistic:.4f}, p = {sw_iv.pvalue:.4f} → {'Normal' if iv_normal else 'Non-normal'}")
print()

assumption_b_rows = []
for col in ALL_DV_COLS:
    vals = ptsd[col].dropna()
    sw_dv = stats.shapiro(vals)
    dv_normal = sw_dv.pvalue > ALPHA
    both_normal = iv_normal and dv_normal

    # Outlier detection via standardized OLS residuals
    dv = ptsd[col].dropna()
    iv = ptsd.loc[dv.index, IV_COL]
    slope, intercept = np.polyfit(iv, dv, 1)
    fitted = intercept + slope * iv
    residuals = dv - fitted
    z_resid = (residuals - residuals.mean()) / residuals.std()
    n_outliers = int((z_resid.abs() > 3).sum())

    assumption_b_rows.append({
        'DV': col,
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
print(f"\nOutlier summary: {assumptions_b_df['Has_Outliers'].sum()} of {len(assumptions_b_df)} pairs have outliers (|z_resid| > 3)")

# %% [markdown]
# ## B2. Assumption Diagnostic Plots

# %%
# --- Outlier inspection grid (4×6 = 24 DVs) ---
short_names = []
for col in ALL_DV_COLS:
    name = col
    for prefix in ['mean_dwell_pct_late_', 'mean_dwell_pct_', 'mean_visits_late_',
                    'mean_visits_', 'mean_offscreen_pct_late_', 'mean_offscreen_pct_']:
        if col.startswith(prefix):
            family_tag = prefix.rstrip('_').replace('mean_', '').replace('_', ' ')
            cat = col[len(prefix):]
            name = f"{family_tag}\n{cat}"
            break
    short_names.append(name)

fig, axes = plt.subplots(4, 6, figsize=(30, 20))
axes = axes.flatten()

for i, col in enumerate(ALL_DV_COLS):
    ax = axes[i]
    dv = ptsd[col].dropna()
    iv = ptsd.loc[dv.index, IV_COL]
    slope, intercept = np.polyfit(iv, dv, 1)
    fitted = intercept + slope * iv
    residuals = dv - fitted
    z_resid = (residuals - residuals.mean()) / residuals.std()
    outlier_mask = z_resid.abs() > 3

    ax.scatter(iv[~outlier_mask], dv[~outlier_mask], color=COLOR_HIGHER, alpha=0.7,
               s=50, edgecolors='white', linewidth=0.5, label='Normal')
    if outlier_mask.any():
        ax.scatter(iv[outlier_mask], dv[outlier_mask], color='#f0ad4e', alpha=0.9,
                   s=100, edgecolors='black', linewidth=1, zorder=5, label='Outlier')
    x_range = np.linspace(iv.min(), iv.max(), 100)
    ax.plot(x_range, intercept + slope * x_range, '--', color=COLOR_HIGHER, alpha=0.6, linewidth=1.5)

    n_out = int(outlier_mask.sum())
    ax.set_title(f"{short_names[i]}\nOutliers: {n_out}", fontsize=8)
    ax.set_xlabel('ITI_PTSD', fontsize=7)
    ax.set_ylabel('DV', fontsize=7)
    ax.tick_params(labelsize=6)
    if outlier_mask.any():
        ax.legend(fontsize=6)

fig.suptitle('H6 Part B: Outlier Inspection — Standardized OLS Residuals (|z| > 3)', fontsize=13, y=1.01)
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/outlier_inspection.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/outlier_inspection.png')

# --- Homoscedasticity inspection grid (4×6) ---
fig, axes = plt.subplots(4, 6, figsize=(30, 20))
axes = axes.flatten()

for i, col in enumerate(ALL_DV_COLS):
    ax = axes[i]
    dv = ptsd[col].dropna()
    iv = ptsd.loc[dv.index, IV_COL]
    slope, intercept = np.polyfit(iv, dv, 1)
    fitted = intercept + slope * iv
    residuals = dv - fitted
    z_resid = (residuals - residuals.mean()) / residuals.std()

    ax.scatter(fitted, z_resid, color=COLOR_HIGHER, alpha=0.7, s=50, edgecolors='white', linewidth=0.5)
    ax.axhline(0, color='grey', linestyle='--', linewidth=1)

    lowess_result = sm_lowess(z_resid.values, fitted.values, frac=0.6)
    ax.plot(lowess_result[:, 0], lowess_result[:, 1], color='#337ab7', linewidth=2, label='LOWESS')

    ax.set_title(short_names[i], fontsize=8)
    ax.set_xlabel('Fitted values', fontsize=7)
    ax.set_ylabel('Std. residuals', fontsize=7)
    ax.tick_params(labelsize=6)
    ax.legend(fontsize=6)

fig.suptitle('H6 Part B: Homoscedasticity Inspection — Residuals vs Fitted (visual only)', fontsize=13, y=1.01)
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/homoscedasticity_inspection.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/homoscedasticity_inspection.png')

# %% [markdown]
# ## B3. Correlation Helper Functions

# %%
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

# %% [markdown]
# ## B4. Correlation Tests (All 6 Families)

# %%
results_b = {}
dv_idx = 0
for family_label, dv_cols in DV_FAMILIES.items():
    corr_rows = []
    for i, col in enumerate(dv_cols):
        dv = ptsd[col].dropna()
        iv = ptsd.loc[dv.index, IV_COL]
        use_pearson = assumptions_b_df.iloc[dv_idx + i]['Use_Pearson']
        test_name, coef, p_val, ci_lo, ci_hi = run_correlation(dv, iv, use_pearson)
        corr_rows.append({
            'Category': THREAT_CATEGORIES[i],
            'Test': test_name,
            'Coefficient': coef,
            'p_uncorrected': p_val,
            'CI_lo': ci_lo,
            'CI_hi': ci_hi,
        })
    dv_idx += len(dv_cols)

    res_df = pd.DataFrame(corr_rows)
    reject, p_bh, _, _ = multipletests(res_df['p_uncorrected'], alpha=ALPHA, method='fdr_bh')
    res_df['p_BH'] = p_bh
    res_df['Significant_BH'] = reject
    results_b[family_label] = res_df

    print(f"\n=== {family_label} — Correlation with ITI_PTSD ===")
    display_cols = ['Category', 'Test', 'Coefficient', 'p_uncorrected', 'p_BH',
                    'CI_lo', 'CI_hi', 'Significant_BH']
    print(res_df[display_cols].to_string(index=False, float_format='%.4f'))

# %% [markdown]
# ## B5. Part B Results Summary

# %%
print("\n" + "=" * 95)
print("RESULTS SUMMARY — Part B: Correlational Analysis (ITI_PTSD × Gaze DVs)")
print("=" * 95)

any_sig_b = False
for family_label, res_df in results_b.items():
    expected = HIGHER_ITI_DIRECTION[family_label]
    expected_sign = 'negative' if expected == 'lower' else 'positive'
    print(f"\n--- {family_label} (expected: {expected_sign} correlation) ---")
    for _, r in res_df.iterrows():
        sig_label = "SIGNIFICANT" if r['Significant_BH'] else "not significant"
        print(f"\n  {r['Category']}:")
        print(f"    Test: {r['Test']}, coef = {r['Coefficient']:.4f}")
        print(f"    p (uncorrected) = {r['p_uncorrected']:.4f}, p (BH) = {r['p_BH']:.4f} → {sig_label}")
        print(f"    95% CI [{r['CI_lo']:.4f}, {r['CI_hi']:.4f}]")
    if res_df['Significant_BH'].any():
        any_sig_b = True

print(f"\nPart B overall: {'At least one significant result' if any_sig_b else 'No significant results'} at α = {ALPHA} (BH-corrected)")
print("=" * 95)

# %% [markdown]
# ## B6. Visualization B1 — Scatterplots (One 2×2 Grid per Family)

# %%
for family_label, dv_cols in DV_FAMILIES.items():
    res_df = results_b[family_label]
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes_flat = axes.flatten()

    for i, (cat, col) in enumerate(zip(THREAT_CATEGORIES, dv_cols)):
        ax = axes_flat[i]
        x = ptsd[IV_COL]
        y = ptsd[col]

        ax.scatter(x, y, color=COLOR_HIGHER, alpha=0.7, s=50, edgecolors='white', linewidth=0.5)

        mask = x.notna() & y.notna()
        z = np.polyfit(x[mask], y[mask], 1)
        p_line = np.poly1d(z)
        x_range = np.linspace(x.min(), x.max(), 100)
        ax.plot(x_range, p_line(x_range), '--', color=COLOR_HIGHER, alpha=0.6, linewidth=1.5)

        r = res_df.iloc[i]
        ax.set_title(f"{cat}\n{r['Test']}: {r['Coefficient']:.3f}, p = {r['p_uncorrected']:.3f}", fontsize=10)
        ax.set_xlabel('ITI_PTSD')
        ax.set_ylabel(col)

    safe_name = family_label.replace(':', '').replace(' ', '_').replace('%', 'pct').replace('(', '').replace(')', '').lower()
    fig.suptitle(f'{family_label} vs ITI_PTSD — PTSD Group', fontsize=13, y=1.02)
    fig.tight_layout()
    fig.savefig(f'{FIG_DIR}/scatterplots_{safe_name}.png', dpi=600, bbox_inches='tight')
    plt.close(fig)
    print(f'Saved: {FIG_DIR}/scatterplots_{safe_name}.png')

# %% [markdown]
# ## B7. Visualization B2 — Forest Plots (All Families)

# %%
fig, axes = plt.subplots(2, 3, figsize=(20, 12))
axes = axes.flatten()

for idx, (family_label, res_df) in enumerate(results_b.items()):
    ax = axes[idx]
    y_pos = np.arange(len(res_df))
    for i, (_, r) in enumerate(res_df.iterrows()):
        color = '#d9534f' if r['Significant_BH'] else '#333333'
        ax.errorbar(r['Coefficient'], i,
                     xerr=[[r['Coefficient'] - r['CI_lo']], [r['CI_hi'] - r['Coefficient']]],
                     fmt='o', color=color, markersize=8, capsize=5, linewidth=2)
    ax.axvline(x=0, color='grey', linestyle='--', linewidth=1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(res_df['Category'])
    ax.set_xlabel('Correlation Coefficient (95% CI)')
    ax.set_title(f'{family_label}', fontsize=10)
    ax.invert_yaxis()

fig.suptitle('H6 Part B: Correlation Coefficients — ITI_PTSD × Gaze DVs', fontsize=13, y=1.02)
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/forest_plot_part_b.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/forest_plot_part_b.png')

# %% [markdown]
# ## B8. Visualization B3 — Correlation Heatmap (All 24 DVs)

# %%
all_coefs = []
all_labels = []
for family_label, res_df in results_b.items():
    for _, r in res_df.iterrows():
        all_coefs.append(r['Coefficient'])
        # Create short label
        short_family = family_label.split(': ')[1] if ': ' in family_label else family_label
        all_labels.append(f"{short_family}\n{r['Category']}")

heatmap_data = pd.DataFrame(
    np.array(all_coefs).reshape(-1, 1),
    index=all_labels,
    columns=[IV_COL],
)

fig, ax = plt.subplots(figsize=(5, 14))
sns.heatmap(heatmap_data, annot=True, fmt='.3f', cmap='RdBu_r', center=0,
            vmin=-1, vmax=1, linewidths=0.5, ax=ax, cbar_kws={'label': 'Correlation'})
ax.set_title(f'Correlation with {IV_COL}\n(PTSD group, n={len(ptsd)})')
ax.tick_params(axis='y', labelsize=8)
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/correlation_heatmap.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/correlation_heatmap.png')

# %% [markdown]
# ---
# # Combined Summary

# %%
print("\n" + "=" * 95)
print("COMBINED SUMMARY — H6: ITI Score and Avoidance-Like Gaze Behavior in PTSD Group")
print("=" * 95)

print(f"\nSample: PTSD group only (n = {len(ptsd)})")
print(f"ITI_PTSD median = {median_iti}, split: Lower-ITI (n={len(lower_iti)}) vs Higher-ITI (n={len(higher_iti)})")
print(f"6 DV families × 4 threat categories = 24 DVs")

print("\n--- Part A: Median-Split Group Comparison ---")
for family_label, res in results_a.items():
    n_sig = res['Significant_BH'].sum()
    print(f"  {family_label}: {n_sig}/4 significant (BH-corrected)")

print("\n--- Part B: Correlational Analysis ---")
for family_label, res_df in results_b.items():
    n_sig = res_df['Significant_BH'].sum()
    print(f"  {family_label}: {n_sig}/4 significant (BH-corrected)")

any_sig_overall = any_sig_a or any_sig_b
print(f"\nOverall: H6 {'supported (at least partially)' if any_sig_overall else 'NOT supported'} at α = {ALPHA} (BH-corrected)")
print("\nNote: With n≈8-9 per subgroup (Part A) and n=17 (Part B), statistical power is")
print("severely limited. These results should be interpreted as exploratory/feasibility findings.")
print("=" * 95)
