# %% [markdown]
# # H1: Threat Stimulus Dwell Time by PTSD Group
#
# **Hypothesis**: Participants in the PTSD group will show higher mean dwell time
# percentage on threat stimuli than the no-PTSD group across pre-defined threat
# categories.
#
# **Method**: Two-tailed group comparisons (PTSD vs no-PTSD) on mean dwell time
# percentage for 4 threat categories. Test selection follows normality and
# variance checks; p-values are corrected for multiple comparisons using
# Benjamini-Hochberg FDR.

# %%
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from statsmodels.stats.multitest import multipletests

os.chdir(Path(__file__).resolve().parent.parent)

THREAT_CATEGORIES = ['angry_face', 'anxiety_inducing', 'warfare', 'soldiers']
DV_COLS = [f'mean_dwell_pct_{cat}' for cat in THREAT_CATEGORIES]
ALPHA = 0.05

FIG_DIR = 'figures/h1_threat_dwell_time'
os.makedirs(FIG_DIR, exist_ok=True)

# %% [markdown]
# ## 1. Load Data

# %%
df = pd.read_csv('data/simplified/dataset_eyetracking_metrics_clean.csv')

ptsd = df[df['if_PTSD'] == 1]
no_ptsd = df[df['if_PTSD'] == 0]

print(f"Total participants: {len(df)}")
print(f"PTSD group:    n = {len(ptsd)}")
print(f"No-PTSD group: n = {len(no_ptsd)}")
print(f"\nThreat DV columns: {DV_COLS}")

# %% [markdown]
# ## 2. Descriptive Statistics

# %%
desc_rows = []
for cat in THREAT_CATEGORIES:
    col = f'mean_dwell_pct_{cat}'
    for group_label, group_df in [('PTSD', ptsd), ('No-PTSD', no_ptsd)]:
        vals = group_df[col].dropna()
        desc_rows.append({
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
print("=== Descriptive Statistics ===")
print(desc_df.to_string(index=False, float_format='%.4f'))

# %% [markdown]
# ## 3. Assumption Checks

# %%
assumption_rows = []
for cat in THREAT_CATEGORIES:
    col = f'mean_dwell_pct_{cat}'
    ptsd_vals = ptsd[col].dropna()
    no_ptsd_vals = no_ptsd[col].dropna()

    sw_ptsd = stats.shapiro(ptsd_vals)
    sw_no_ptsd = stats.shapiro(no_ptsd_vals)
    lev = stats.levene(ptsd_vals, no_ptsd_vals)

    assumption_rows.append({
        'Category': cat,
        'Shapiro_PTSD_W': sw_ptsd.statistic,
        'Shapiro_PTSD_p': sw_ptsd.pvalue,
        'Shapiro_NoPTSD_W': sw_no_ptsd.statistic,
        'Shapiro_NoPTSD_p': sw_no_ptsd.pvalue,
        'Levene_F': lev.statistic,
        'Levene_p': lev.pvalue,
        'Both_Normal': sw_ptsd.pvalue > ALPHA and sw_no_ptsd.pvalue > ALPHA,
        'Equal_Var': lev.pvalue > ALPHA,
    })

assumptions_df = pd.DataFrame(assumption_rows)
print("=== Assumption Checks ===")
print(assumptions_df.to_string(index=False, float_format='%.4f'))

# %% [markdown]
# ## 4. Statistical Tests

# %%
def cohens_d(x, y):
    """Compute Cohen's d for independent samples."""
    nx, ny = len(x), len(y)
    pooled_std = np.sqrt(((nx - 1) * x.std(ddof=1)**2 + (ny - 1) * y.std(ddof=1)**2) / (nx + ny - 2))
    return (x.mean() - y.mean()) / pooled_std


def cohens_d_ci(d, nx, ny, confidence=0.95):
    """Approximate 95% CI for Cohen's d using the variance formula."""
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


results_rows = []
for i, cat in enumerate(THREAT_CATEGORIES):
    col = f'mean_dwell_pct_{cat}'
    ptsd_vals = ptsd[col].dropna()
    no_ptsd_vals = no_ptsd[col].dropna()
    nx, ny = len(ptsd_vals), len(no_ptsd_vals)

    row = assumptions_df.iloc[i]
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

    results_rows.append({
        'Category': cat,
        'Test': test_name,
        'Statistic': test_stat,
        'p_uncorrected': p_val,
        'Effect_Size_Type': es_name,
        'Effect_Size': es_val,
        'CI_lo': ci_lo,
        'CI_hi': ci_hi,
    })

results_df = pd.DataFrame(results_rows)

# %% [markdown]
# ## 5. Benjamini-Hochberg Correction

# %%
reject, p_corrected, _, _ = multipletests(results_df['p_uncorrected'], alpha=ALPHA, method='fdr_bh')
results_df['p_BH'] = p_corrected
results_df['Significant_BH'] = reject

print("=== Results with BH Correction ===")
display_cols = ['Category', 'Test', 'Statistic', 'p_uncorrected', 'p_BH',
                'Effect_Size_Type', 'Effect_Size', 'CI_lo', 'CI_hi', 'Significant_BH']
print(results_df[display_cols].to_string(index=False, float_format='%.4f'))

# %% [markdown]
# ## 6. Results Summary

# %%
print("\n" + "=" * 90)
print("RESULTS SUMMARY — H1: Threat Dwell Time × PTSD Group")
print("=" * 90)
for _, r in results_df.iterrows():
    sig_label = "SIGNIFICANT" if r['Significant_BH'] else "not significant"
    print(f"\n  {r['Category']}:")
    print(f"    Test: {r['Test']}, stat = {r['Statistic']:.4f}")
    print(f"    p (uncorrected) = {r['p_uncorrected']:.4f}, p (BH) = {r['p_BH']:.4f} → {sig_label}")
    print(f"    {r['Effect_Size_Type']} = {r['Effect_Size']:.4f}, 95% CI [{r['CI_lo']:.4f}, {r['CI_hi']:.4f}]")

any_sig = results_df['Significant_BH'].any()
print(f"\nOverall: H1 {'supported' if any_sig else 'NOT supported'} at α = {ALPHA} (BH-corrected)")
print("=" * 90)

# %% [markdown]
# ## 7. Visualization 1 — Violin + Strip Plot

# %%
plot_df = df[['if_PTSD'] + DV_COLS].copy()
plot_df['Group'] = plot_df['if_PTSD'].map({1: 'PTSD', 0: 'No-PTSD'})
plot_long = plot_df.melt(id_vars=['Group'], value_vars=DV_COLS,
                          var_name='Category', value_name='Mean Dwell %')
plot_long['Category'] = plot_long['Category'].str.replace('mean_dwell_pct_', '', regex=False)

fig, ax = plt.subplots(figsize=(10, 6))
sns.violinplot(data=plot_long, x='Category', y='Mean Dwell %', hue='Group',
               split=True, inner=None, palette={'PTSD': '#d9534f', 'No-PTSD': '#5bc0de'},
               alpha=0.4, ax=ax)
sns.stripplot(data=plot_long, x='Category', y='Mean Dwell %', hue='Group',
              dodge=True, palette={'PTSD': '#d9534f', 'No-PTSD': '#5bc0de'},
              size=5, alpha=0.7, ax=ax)

handles, labels = ax.get_legend_handles_labels()
ax.legend(handles[:2], labels[:2], title='Group', loc='upper right')
ax.set_title('Mean Dwell Time % on Threat Stimuli by PTSD Group')
ax.set_xlabel('Threat Category')
ax.set_ylabel('Mean Dwell Time (%)')

fig.savefig(f'{FIG_DIR}/violin_threat_dwell_by_group.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/violin_threat_dwell_by_group.png')

# %% [markdown]
# ## 8. Visualization 2 — Forest Plot (Effect Sizes)

# %%
fig, ax = plt.subplots(figsize=(8, 5))
y_pos = np.arange(len(results_df))

for i, (_, r) in enumerate(results_df.iterrows()):
    color = '#d9534f' if r['Significant_BH'] else '#333333'
    ax.errorbar(r['Effect_Size'], i, xerr=[[r['Effect_Size'] - r['CI_lo']], [r['CI_hi'] - r['Effect_Size']]],
                fmt='o', color=color, markersize=8, capsize=5, linewidth=2)

ax.axvline(x=0, color='grey', linestyle='--', linewidth=1)
ax.set_yticks(y_pos)
ax.set_yticklabels(results_df['Category'])
ax.set_xlabel('Effect Size (with 95% CI)')
ax.set_title('Forest Plot — Effect Sizes for Threat Dwell Time (PTSD vs No-PTSD)')
ax.invert_yaxis()

fig.savefig(f'{FIG_DIR}/forest_plot_effect_sizes.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/forest_plot_effect_sizes.png')

# %% [markdown]
# ## 9. Visualization 3 — Bar Chart (Group Means ± SE)

# %%
bar_rows = []
for cat in THREAT_CATEGORIES:
    col = f'mean_dwell_pct_{cat}'
    for group_label, group_df in [('PTSD', ptsd), ('No-PTSD', no_ptsd)]:
        vals = group_df[col].dropna()
        bar_rows.append({
            'Category': cat,
            'Group': group_label,
            'Mean': vals.mean(),
            'SE': vals.std() / np.sqrt(len(vals)),
        })

bar_df = pd.DataFrame(bar_rows)

fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(THREAT_CATEGORIES))
width = 0.35

ptsd_means = bar_df[bar_df['Group'] == 'PTSD']['Mean'].values
ptsd_se = bar_df[bar_df['Group'] == 'PTSD']['SE'].values
no_ptsd_means = bar_df[bar_df['Group'] == 'No-PTSD']['Mean'].values
no_ptsd_se = bar_df[bar_df['Group'] == 'No-PTSD']['SE'].values

ax.bar(x - width / 2, ptsd_means, width, yerr=ptsd_se, label='PTSD',
       color='#d9534f', alpha=0.7, capsize=5)
ax.bar(x + width / 2, no_ptsd_means, width, yerr=no_ptsd_se, label='No-PTSD',
       color='#5bc0de', alpha=0.7, capsize=5)

ax.set_xticks(x)
ax.set_xticklabels(THREAT_CATEGORIES)
ax.set_xlabel('Threat Category')
ax.set_ylabel('Mean Dwell Time (%) ± SE')
ax.set_title('Mean Dwell Time % on Threat Stimuli by Group')
ax.legend(title='Group')

fig.savefig(f'{FIG_DIR}/bar_threat_dwell_by_group.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/bar_threat_dwell_by_group.png')
