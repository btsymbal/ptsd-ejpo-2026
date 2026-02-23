# %% [markdown]
# # H5: Mean Visits to Threat Stimuli by PTSD Group
#
# **Hypothesis**: Participants in the PTSD group will show more revisits
# (higher mean visit count) to threat stimuli than the no-PTSD group, with
# combat-related categories expected to show the strongest effects. A secondary
# prediction is that the PTSD–no-PTSD difference is larger in the late viewing
# window, consistent with sustained monitoring / difficulty disengaging.
#
# **Method**: Two-tailed group comparisons (PTSD vs no-PTSD) on mean visit
# counts for 4 threat categories across two families:
# - **Family 1**: Overall mean visits (4 DVs)
# - **Family 2**: Late-window mean visits (4 DVs)
#
# Test selection follows normality and variance checks; p-values are corrected
# for multiple comparisons using Benjamini-Hochberg FDR separately within each
# family.

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
DV_COLS_F1 = [f'mean_visits_{cat}' for cat in THREAT_CATEGORIES]
DV_COLS_F2 = [f'mean_visits_late_{cat}' for cat in THREAT_CATEGORIES]
FAMILY_LABELS = ['Overall Visits', 'Late-Window Visits']
ALPHA = 0.05

FIG_DIR = 'figures/h5_mean_visits_threat'
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
print(f"\nFamily 1 DV columns: {DV_COLS_F1}")
print(f"Family 2 DV columns: {DV_COLS_F2}")

# %% [markdown]
# ## 2. Descriptive Statistics

# %%
desc_rows = []
for family_label, dv_cols in [(FAMILY_LABELS[0], DV_COLS_F1), (FAMILY_LABELS[1], DV_COLS_F2)]:
    for cat, col in zip(THREAT_CATEGORIES, dv_cols):
        for group_label, group_df in [('PTSD', ptsd), ('No-PTSD', no_ptsd)]:
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
print("=== Descriptive Statistics — Family 1: Overall Visits ===")
print(desc_df[desc_df['Family'] == FAMILY_LABELS[0]].to_string(index=False, float_format='%.4f'))
print("\n=== Descriptive Statistics — Family 2: Late-Window Visits ===")
print(desc_df[desc_df['Family'] == FAMILY_LABELS[1]].to_string(index=False, float_format='%.4f'))

# %% [markdown]
# ## 3. Assumption Checks

# %%
assumption_rows = []
for family_label, dv_cols in [(FAMILY_LABELS[0], DV_COLS_F1), (FAMILY_LABELS[1], DV_COLS_F2)]:
    for cat, col in zip(THREAT_CATEGORIES, dv_cols):
        ptsd_vals = ptsd[col].dropna()
        no_ptsd_vals = no_ptsd[col].dropna()

        sw_ptsd = stats.shapiro(ptsd_vals)
        sw_no_ptsd = stats.shapiro(no_ptsd_vals)
        lev = stats.levene(ptsd_vals, no_ptsd_vals)

        assumption_rows.append({
            'Family': family_label,
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
print("=== Assumption Checks — Family 1: Overall Visits ===")
print(assumptions_df[assumptions_df['Family'] == FAMILY_LABELS[0]].to_string(index=False, float_format='%.4f'))
print("\n=== Assumption Checks — Family 2: Late-Window Visits ===")
print(assumptions_df[assumptions_df['Family'] == FAMILY_LABELS[1]].to_string(index=False, float_format='%.4f'))

# %% [markdown]
# ## 4. Statistical Tests — Family 1 (Overall Visits)

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


def run_tests(categories, dv_cols, assumptions_family):
    """Run statistical tests for a family of DVs."""
    rows = []
    for i, (cat, col) in enumerate(zip(categories, dv_cols)):
        ptsd_vals = ptsd[col].dropna()
        no_ptsd_vals = no_ptsd[col].dropna()
        nx, ny = len(ptsd_vals), len(no_ptsd_vals)

        row = assumptions_family.iloc[i]
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

        rows.append({
            'Category': cat,
            'Test': test_name,
            'Statistic': test_stat,
            'p_uncorrected': p_val,
            'Effect_Size_Type': es_name,
            'Effect_Size': es_val,
            'CI_lo': ci_lo,
            'CI_hi': ci_hi,
        })
    return pd.DataFrame(rows)


assumptions_f1 = assumptions_df[assumptions_df['Family'] == FAMILY_LABELS[0]].reset_index(drop=True)
results_f1 = run_tests(THREAT_CATEGORIES, DV_COLS_F1, assumptions_f1)

print("=== Statistical Tests — Family 1: Overall Visits ===")
print(results_f1.to_string(index=False, float_format='%.4f'))

# %% [markdown]
# ## 5. BH Correction — Family 1

# %%
reject_f1, p_bh_f1, _, _ = multipletests(results_f1['p_uncorrected'], alpha=ALPHA, method='fdr_bh')
results_f1['p_BH'] = p_bh_f1
results_f1['Significant_BH'] = reject_f1

display_cols = ['Category', 'Test', 'Statistic', 'p_uncorrected', 'p_BH',
                'Effect_Size_Type', 'Effect_Size', 'CI_lo', 'CI_hi', 'Significant_BH']
print("=== Family 1 Results with BH Correction ===")
print(results_f1[display_cols].to_string(index=False, float_format='%.4f'))

# %% [markdown]
# ## 6. Statistical Tests — Family 2 (Late-Window Visits)

# %%
assumptions_f2 = assumptions_df[assumptions_df['Family'] == FAMILY_LABELS[1]].reset_index(drop=True)
results_f2 = run_tests(THREAT_CATEGORIES, DV_COLS_F2, assumptions_f2)

print("=== Statistical Tests — Family 2: Late-Window Visits ===")
print(results_f2.to_string(index=False, float_format='%.4f'))

# %% [markdown]
# ## 7. BH Correction — Family 2

# %%
reject_f2, p_bh_f2, _, _ = multipletests(results_f2['p_uncorrected'], alpha=ALPHA, method='fdr_bh')
results_f2['p_BH'] = p_bh_f2
results_f2['Significant_BH'] = reject_f2

print("=== Family 2 Results with BH Correction ===")
print(results_f2[display_cols].to_string(index=False, float_format='%.4f'))

# %% [markdown]
# ## 8. Results Summary

# %%
for family_label, results in [(FAMILY_LABELS[0], results_f1), (FAMILY_LABELS[1], results_f2)]:
    print("\n" + "=" * 90)
    print(f"RESULTS SUMMARY — H5: Mean Visits to Threat Stimuli × PTSD Group — {family_label}")
    print("=" * 90)
    for _, r in results.iterrows():
        sig_label = "SIGNIFICANT" if r['Significant_BH'] else "not significant"
        print(f"\n  {r['Category']}:")
        print(f"    Test: {r['Test']}, stat = {r['Statistic']:.4f}")
        print(f"    p (uncorrected) = {r['p_uncorrected']:.4f}, p (BH) = {r['p_BH']:.4f} → {sig_label}")
        print(f"    {r['Effect_Size_Type']} = {r['Effect_Size']:.4f}, 95% CI [{r['CI_lo']:.4f}, {r['CI_hi']:.4f}]")

    any_sig = results['Significant_BH'].any()
    print(f"\n  {family_label}: H5 {'supported' if any_sig else 'NOT supported'} at α = {ALPHA} (BH-corrected)")
    print("=" * 90)

# %% [markdown]
# ## 9. Visualization 1 — Violin + Strip Plot (Family 1: Overall Visits)

# %%
plot_df = df[['if_PTSD'] + DV_COLS_F1].copy()
plot_df['Group'] = plot_df['if_PTSD'].map({1: 'PTSD', 0: 'No-PTSD'})
plot_long = plot_df.melt(id_vars=['Group'], value_vars=DV_COLS_F1,
                          var_name='Category', value_name='Mean Visits')
plot_long['Category'] = plot_long['Category'].str.replace('mean_visits_', '', regex=False)

fig, ax = plt.subplots(figsize=(10, 6))
sns.violinplot(data=plot_long, x='Category', y='Mean Visits', hue='Group',
               split=True, inner=None, palette={'PTSD': '#d9534f', 'No-PTSD': '#5bc0de'},
               alpha=0.4, ax=ax)
sns.stripplot(data=plot_long, x='Category', y='Mean Visits', hue='Group',
              dodge=True, palette={'PTSD': '#d9534f', 'No-PTSD': '#5bc0de'},
              size=5, alpha=0.7, ax=ax)

handles, labels = ax.get_legend_handles_labels()
ax.legend(handles[:2], labels[:2], title='Group', loc='upper right')
ax.set_title('Mean Visits to Threat Stimuli by PTSD Group (Overall)')
ax.set_xlabel('Threat Category')
ax.set_ylabel('Mean Visit Count')

fig.savefig(f'{FIG_DIR}/violin_visits_overall_by_group.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/violin_visits_overall_by_group.png')

# %% [markdown]
# ## 10. Visualization 2 — Violin + Strip Plot (Family 2: Late-Window Visits)

# %%
plot_df2 = df[['if_PTSD'] + DV_COLS_F2].copy()
plot_df2['Group'] = plot_df2['if_PTSD'].map({1: 'PTSD', 0: 'No-PTSD'})
plot_long2 = plot_df2.melt(id_vars=['Group'], value_vars=DV_COLS_F2,
                            var_name='Category', value_name='Mean Visits (Late)')
plot_long2['Category'] = plot_long2['Category'].str.replace('mean_visits_late_', '', regex=False)

fig, ax = plt.subplots(figsize=(10, 6))
sns.violinplot(data=plot_long2, x='Category', y='Mean Visits (Late)', hue='Group',
               split=True, inner=None, palette={'PTSD': '#d9534f', 'No-PTSD': '#5bc0de'},
               alpha=0.4, ax=ax)
sns.stripplot(data=plot_long2, x='Category', y='Mean Visits (Late)', hue='Group',
              dodge=True, palette={'PTSD': '#d9534f', 'No-PTSD': '#5bc0de'},
              size=5, alpha=0.7, ax=ax)

handles, labels = ax.get_legend_handles_labels()
ax.legend(handles[:2], labels[:2], title='Group', loc='upper right')
ax.set_title('Mean Visits to Threat Stimuli by PTSD Group (Late Window)')
ax.set_xlabel('Threat Category')
ax.set_ylabel('Mean Visit Count (Late Window)')

fig.savefig(f'{FIG_DIR}/violin_visits_late_by_group.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/violin_visits_late_by_group.png')

# %% [markdown]
# ## 11. Visualization 3 — Forest Plot (Both Families)

# %%
fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

for ax, family_label, results in zip(axes, FAMILY_LABELS, [results_f1, results_f2]):
    y_pos = np.arange(len(results))
    for i, (_, r) in enumerate(results.iterrows()):
        color = '#d9534f' if r['Significant_BH'] else '#333333'
        ax.errorbar(r['Effect_Size'], i,
                     xerr=[[r['Effect_Size'] - r['CI_lo']], [r['CI_hi'] - r['Effect_Size']]],
                     fmt='o', color=color, markersize=8, capsize=5, linewidth=2)
    ax.axvline(x=0, color='grey', linestyle='--', linewidth=1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(results['Category'])
    ax.set_xlabel('Effect Size (with 95% CI)')
    ax.set_title(f'Forest Plot — {family_label}')
    ax.invert_yaxis()

fig.suptitle('Effect Sizes for Mean Visits to Threat Stimuli (PTSD vs No-PTSD)', fontsize=13, y=1.02)
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/forest_plot_effect_sizes.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/forest_plot_effect_sizes.png')

# %% [markdown]
# ## 12. Visualization 4 — Bar Chart (Family 1: Overall Visits)

# %%
bar_rows = []
for cat in THREAT_CATEGORIES:
    col = f'mean_visits_{cat}'
    for group_label, group_df in [('PTSD', ptsd), ('No-PTSD', no_ptsd)]:
        vals = group_df[col].dropna()
        bar_rows.append({
            'Category': cat,
            'Group': group_label,
            'Mean': vals.mean(),
            'CI95': 1.96 * vals.std() / np.sqrt(len(vals)),
        })

bar_df = pd.DataFrame(bar_rows)

fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(THREAT_CATEGORIES))
width = 0.35

ptsd_means = bar_df[bar_df['Group'] == 'PTSD']['Mean'].values
ptsd_ci = bar_df[bar_df['Group'] == 'PTSD']['CI95'].values
no_ptsd_means = bar_df[bar_df['Group'] == 'No-PTSD']['Mean'].values
no_ptsd_ci = bar_df[bar_df['Group'] == 'No-PTSD']['CI95'].values

ax.bar(x - width / 2, ptsd_means, width, yerr=ptsd_ci, label='PTSD',
       color='#d9534f', alpha=0.7, capsize=5)
ax.bar(x + width / 2, no_ptsd_means, width, yerr=no_ptsd_ci, label='No-PTSD',
       color='#5bc0de', alpha=0.7, capsize=5)

ax.set_xticks(x)
ax.set_xticklabels(THREAT_CATEGORIES)
ax.set_xlabel('Threat Category')
ax.set_ylabel('Mean Visit Count (95% CI)')
ax.set_title('Mean Visits to Threat Stimuli by Group (Overall)')
ax.legend(title='Group')

fig.savefig(f'{FIG_DIR}/bar_visits_overall_by_group.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/bar_visits_overall_by_group.png')

# %% [markdown]
# ## 13. Visualization 5 — Bar Chart (Family 2: Late-Window Visits)

# %%
bar_rows2 = []
for cat in THREAT_CATEGORIES:
    col = f'mean_visits_late_{cat}'
    for group_label, group_df in [('PTSD', ptsd), ('No-PTSD', no_ptsd)]:
        vals = group_df[col].dropna()
        bar_rows2.append({
            'Category': cat,
            'Group': group_label,
            'Mean': vals.mean(),
            'CI95': 1.96 * vals.std() / np.sqrt(len(vals)),
        })

bar_df2 = pd.DataFrame(bar_rows2)

fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(THREAT_CATEGORIES))

ptsd_means2 = bar_df2[bar_df2['Group'] == 'PTSD']['Mean'].values
ptsd_ci2 = bar_df2[bar_df2['Group'] == 'PTSD']['CI95'].values
no_ptsd_means2 = bar_df2[bar_df2['Group'] == 'No-PTSD']['Mean'].values
no_ptsd_ci2 = bar_df2[bar_df2['Group'] == 'No-PTSD']['CI95'].values

ax.bar(x - width / 2, ptsd_means2, width, yerr=ptsd_ci2, label='PTSD',
       color='#d9534f', alpha=0.7, capsize=5)
ax.bar(x + width / 2, no_ptsd_means2, width, yerr=no_ptsd_ci2, label='No-PTSD',
       color='#5bc0de', alpha=0.7, capsize=5)

ax.set_xticks(x)
ax.set_xticklabels(THREAT_CATEGORIES)
ax.set_xlabel('Threat Category')
ax.set_ylabel('Mean Visit Count — Late Window (95% CI)')
ax.set_title('Mean Visits to Threat Stimuli by Group (Late Window)')
ax.legend(title='Group')

fig.savefig(f'{FIG_DIR}/bar_visits_late_by_group.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/bar_visits_late_by_group.png')
