# %% [markdown]
# # E2: Medication-Attention Moderation
#
# **Context**: This exploratory analysis examines whether antipsychotic medication
# status moderates attention metrics (dwell time, dwell variability, visits) across
# threat categories. The dataset has N=29, with a 2×2 factorial design
# (PTSD × antipsychotic). Cell sizes are small (6–9), so Part B uses permutation
# ANOVA rather than parametric ANOVA.
#
# **Method**: Two complementary approaches:
# - **Part A**: Group comparison (Antipsychotic vs No-Antipsychotic)
# - **Part B**: Permutation ANOVA (if_PTSD × if_antipsychotic interaction)
#
# BH-FDR correction applied separately within each of 3 families.

# %%
import os
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multitest import multipletests

os.chdir(Path(__file__).resolve().parent.parent)

# %%
# --- Constants & helpers ---

THREAT_CATEGORIES = ['angry_face', 'anxiety_inducing', 'warfare', 'soldiers']
ALPHA = 0.05
N_PERM = 10000
SEED = 42
FIG_DIR = 'figures/e2_medication_attention_moderation'
os.makedirs(FIG_DIR, exist_ok=True)

# Colors
COLOR_ANTI = '#e67e22'
COLOR_NO_ANTI = '#3498db'
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


# DV families
DV_FAMILIES = {
    'F1: Mean Dwell %': [f'mean_dwell_pct_{cat}' for cat in THREAT_CATEGORIES],
    'F2: Attention Bias Variability (Std Dwell %)': [f'std_dwell_pct_{cat}' for cat in THREAT_CATEGORIES],
    'F3: Mean Visits': [f'mean_visits_{cat}' for cat in THREAT_CATEGORIES],
}
ALL_DV_COLS = [col for cols in DV_FAMILIES.values() for col in cols]

# %%
# --- Load data & split groups ---

df = pd.read_csv('data/simplified/dataset_eyetracking_metrics_clean.csv')
anti = df[df['if_antipsychotic'] == 1].copy()
no_anti = df[df['if_antipsychotic'] == 0].copy()

print(f"Total sample: n = {len(df)}")
print(f"Antipsychotic group: n = {len(anti)}")
print(f"No-Antipsychotic group: n = {len(no_anti)}")
print(f"\nMetrics under test: {len(ALL_DV_COLS)}")
for fam, cols in DV_FAMILIES.items():
    print(f"  {fam}: {cols}")

# 2×2 cell sizes
print("\n=== 2×2 Cell Sizes (PTSD × Antipsychotic) ===")
ct = pd.crosstab(df['if_PTSD'], df['if_antipsychotic'],
                 rownames=['if_PTSD'], colnames=['if_antipsychotic'])
print(ct)

# %% [markdown]
# ---
# # Part A: Group Comparisons (Antipsychotic vs No-Antipsychotic)

# %% [markdown]
# ## A1. Descriptive Statistics

# %%
desc_rows = []
for family_label, dv_cols in DV_FAMILIES.items():
    for col in dv_cols:
        for group_label, group_df in [('Anti', anti), ('No-Anti', no_anti)]:
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
        anti_vals = anti[col].dropna()
        no_anti_vals = no_anti[col].dropna()

        sw_anti = stats.shapiro(anti_vals)
        sw_no_anti = stats.shapiro(no_anti_vals)
        lev = stats.levene(anti_vals, no_anti_vals)

        assumption_a_rows.append({
            'Family': family_label,
            'Metric': col,
            'Shapiro_Anti_W': sw_anti.statistic,
            'Shapiro_Anti_p': sw_anti.pvalue,
            'Shapiro_NoAnti_W': sw_no_anti.statistic,
            'Shapiro_NoAnti_p': sw_no_anti.pvalue,
            'Levene_F': lev.statistic,
            'Levene_p': lev.pvalue,
            'Both_Normal': sw_anti.pvalue > ALPHA and sw_no_anti.pvalue > ALPHA,
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
    anti_vals = anti[col].dropna()
    no_anti_vals = no_anti[col].dropna()
    nx, ny = len(anti_vals), len(no_anti_vals)

    both_normal = row['Both_Normal']
    equal_var = row['Equal_Var']

    if both_normal and equal_var:
        test_name = "Student's t-test"
        stat_result = stats.ttest_ind(anti_vals, no_anti_vals, equal_var=True)
        test_stat, p_val = stat_result.statistic, stat_result.pvalue
        d = cohens_d(anti_vals, no_anti_vals)
        ci_lo, ci_hi = cohens_d_ci(d, nx, ny)
        es_name = "Cohen's d"
        es_val = d
    elif both_normal and not equal_var:
        test_name = "Welch's t-test"
        stat_result = stats.ttest_ind(anti_vals, no_anti_vals, equal_var=False)
        test_stat, p_val = stat_result.statistic, stat_result.pvalue
        d = cohens_d(anti_vals, no_anti_vals)
        ci_lo, ci_hi = cohens_d_ci(d, nx, ny)
        es_name = "Cohen's d"
        es_val = d
    else:
        test_name = "Mann-Whitney U"
        stat_result = stats.mannwhitneyu(anti_vals, no_anti_vals, alternative='two-sided')
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
        results_a_df.loc[mask, 'p_BH'] = p_vals[0]
        results_a_df.loc[mask, 'Significant_BH'] = p_vals[0] < ALPHA

# %% [markdown]
# ## A5. Results Display

# %%
print("\n" + "=" * 95)
print("RESULTS — Part A: Group Comparisons (Antipsychotic vs No-Antipsychotic)")
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
# ## A6. Visualizations — Group Comparisons

# %%
# --- Violin + strip plots: 3×4 grid (rows=families, cols=categories) ---
fig, axes = plt.subplots(3, 4, figsize=(20, 14))

for row_i, (family_label, dv_cols) in enumerate(DV_FAMILIES.items()):
    for col_i, col in enumerate(dv_cols):
        ax = axes[row_i, col_i]
        plot_data = df[['if_antipsychotic', col]].dropna().copy()
        plot_data['Group'] = plot_data['if_antipsychotic'].map({1: 'Anti', 0: 'No-Anti'})

        sns.violinplot(data=plot_data, x='Group', y=col, order=['Anti', 'No-Anti'],
                       palette={'Anti': COLOR_ANTI, 'No-Anti': COLOR_NO_ANTI},
                       inner=None, alpha=0.4, ax=ax)
        sns.stripplot(data=plot_data, x='Group', y=col, order=['Anti', 'No-Anti'],
                      palette={'Anti': COLOR_ANTI, 'No-Anti': COLOR_NO_ANTI},
                      size=5, alpha=0.7, ax=ax)

        cat_name = col.split('_')[-2] + '_' + col.split('_')[-1] if 'face' in col else col.split('_')[-1]
        if row_i == 0:
            ax.set_title(THREAT_CATEGORIES[col_i], fontsize=10, fontweight='bold')
        ax.set_xlabel('')
        if col_i == 0:
            ax.set_ylabel(family_label.split(':')[0], fontsize=9)
        else:
            ax.set_ylabel('')

fig.suptitle('E2 Part A: Attention Metrics by Antipsychotic Status', fontsize=14, y=1.02)
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/violin_strip_part_a.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/violin_strip_part_a.png')

# %%
# --- Forest plot of effect sizes (all 12 metrics) ---
fig, ax = plt.subplots(figsize=(10, 8))
labels = []
for idx, (_, r) in enumerate(results_a_df.iterrows()):
    color = '#d9534f' if r['Significant_BH'] else '#333333'
    ax.errorbar(r['Effect_Size'], idx,
                xerr=[[r['Effect_Size'] - r['CI_lo']], [r['CI_hi'] - r['Effect_Size']]],
                fmt='o', color=color, markersize=8, capsize=5, linewidth=2)
    short_name = r['Metric']
    for prefix in ['mean_dwell_pct_', 'std_dwell_pct_', 'mean_visits_']:
        short_name = short_name.replace(prefix, '')
    labels.append(f"{r['Family'].split(':')[0]}: {short_name} ({r['Effect_Size_Type']})")

ax.axvline(x=0, color='grey', linestyle='--', linewidth=1)
ax.set_yticks(np.arange(len(results_a_df)))
ax.set_yticklabels(labels, fontsize=8)
ax.set_xlabel('Effect Size (95% CI)')
ax.set_title('E2 Part A: Effect Sizes — Antipsychotic vs No-Antipsychotic')
ax.invert_yaxis()
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/forest_plot_part_a.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/forest_plot_part_a.png')

# %%
# --- Bar chart with 95% CI error bars: 3 panels ---
fig, axes = plt.subplots(1, 3, figsize=(20, 6))

for panel_i, (family_label, dv_cols) in enumerate(DV_FAMILIES.items()):
    ax = axes[panel_i]
    fam_desc = desc_df[desc_df['Family'] == family_label]
    x = np.arange(len(THREAT_CATEGORIES))
    width = 0.35

    for j, group_label in enumerate(['Anti', 'No-Anti']):
        g = fam_desc[fam_desc['Group'] == group_label]
        means = [g[g['Metric'] == col]['Mean'].values[0] for col in dv_cols]
        ci95 = [1.96 * g[g['Metric'] == col]['SD'].values[0] /
                np.sqrt(g[g['Metric'] == col]['n'].values[0]) for col in dv_cols]
        offset = -width / 2 if j == 0 else width / 2
        color = COLOR_ANTI if group_label == 'Anti' else COLOR_NO_ANTI
        ax.bar(x + offset, means, width, yerr=ci95, label=group_label,
               color=color, alpha=0.7, capsize=5)

    ax.set_xticks(x)
    ax.set_xticklabels(THREAT_CATEGORIES, fontsize=8, rotation=20)
    ax.set_title(family_label, fontsize=10)
    ax.legend()

fig.suptitle('E2 Part A: Group Means ± 95% CI — Anti vs No-Anti', fontsize=13, y=1.02)
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/bar_chart_part_a.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/bar_chart_part_a.png')

# %% [markdown]
# ---
# # Part B: Permutation ANOVA (if_PTSD × if_antipsychotic)

# %% [markdown]
# ## B1. Descriptive Statistics per Cell

# %%
print("=== 2×2 Cell Descriptive Statistics ===\n")
cell_desc_rows = []
for family_label, dv_cols in DV_FAMILIES.items():
    for col in dv_cols:
        for ptsd_val in [0, 1]:
            for anti_val in [0, 1]:
                cell = df[(df['if_PTSD'] == ptsd_val) & (df['if_antipsychotic'] == anti_val)]
                vals = cell[col].dropna()
                label = f"PTSD={ptsd_val}, Anti={anti_val}"
                cell_desc_rows.append({
                    'Family': family_label,
                    'Metric': col,
                    'Cell': label,
                    'if_PTSD': ptsd_val,
                    'if_antipsychotic': anti_val,
                    'n': len(vals),
                    'Mean': vals.mean(),
                    'SD': vals.std(),
                    'SE': vals.std() / np.sqrt(len(vals)) if len(vals) > 0 else np.nan,
                })

cell_desc_df = pd.DataFrame(cell_desc_rows)
for family_label in DV_FAMILIES:
    print(f"\n--- {family_label} ---")
    sub = cell_desc_df[cell_desc_df['Family'] == family_label]
    print(sub[['Metric', 'Cell', 'n', 'Mean', 'SD']].to_string(index=False, float_format='%.4f'))

# %% [markdown]
# ## B2. Assumption Checks (per cell)

# %%
assumption_b_rows = []
for family_label, dv_cols in DV_FAMILIES.items():
    for col in dv_cols:
        cell_vals = []
        sw_results = []
        for ptsd_val in [0, 1]:
            for anti_val in [0, 1]:
                cell = df[(df['if_PTSD'] == ptsd_val) & (df['if_antipsychotic'] == anti_val)]
                vals = cell[col].dropna()
                cell_vals.append(vals)
                if len(vals) >= 3:
                    sw = stats.shapiro(vals)
                    sw_results.append({
                        'cell': f'PTSD={ptsd_val},Anti={anti_val}',
                        'W': sw.statistic, 'p': sw.pvalue,
                        'normal': sw.pvalue > ALPHA
                    })

        # Levene's across all 4 cells
        lev = stats.levene(*[v for v in cell_vals if len(v) >= 2])

        all_normal = all(r['normal'] for r in sw_results)
        assumption_b_rows.append({
            'Family': family_label,
            'Metric': col,
            'All_Cells_Normal': all_normal,
            'Levene_F': lev.statistic,
            'Levene_p': lev.pvalue,
            'Equal_Var': lev.pvalue > ALPHA,
            'SW_details': sw_results,
        })

assumptions_b_df = pd.DataFrame(assumption_b_rows)
print("=== Part B Assumption Checks ===")
for _, row in assumptions_b_df.iterrows():
    print(f"\n  {row['Metric']}:")
    for sw in row['SW_details']:
        norm_label = 'Normal' if sw['normal'] else 'Non-normal'
        print(f"    {sw['cell']}: W = {sw['W']:.4f}, p = {sw['p']:.4f} → {norm_label}")
    print(f"    Levene: F = {row['Levene_F']:.4f}, p = {row['Levene_p']:.4f} → {'Equal' if row['Equal_Var'] else 'Unequal'} var")
    print(f"    All normal: {row['All_Cells_Normal']}, Equal var: {row['Equal_Var']}")

print("\nNote: Permutation ANOVA used regardless of assumption violations (small cell sizes).")

# %% [markdown]
# ## B3. Permutation ANOVA

# %%
def permutation_anova_2way(df_input, dv_col, factor1='if_PTSD', factor2='if_antipsychotic',
                           n_perm=N_PERM, seed=SEED):
    """Two-way permutation ANOVA with Type II SS.

    Returns dict with observed F-stats and permutation p-values for:
    main effect of factor1, main effect of factor2, and interaction.
    """
    rng = np.random.RandomState(seed)
    data = df_input[[dv_col, factor1, factor2]].dropna().copy()

    # Observed model
    formula = f'{dv_col} ~ C({factor1}) * C({factor2})'
    model = ols(formula, data=data).fit()
    obs_table = anova_lm(model, typ=2)

    effects = [f'C({factor1})', f'C({factor2})', f'C({factor1}):C({factor2})']
    effect_labels = [factor1, factor2, f'{factor1}:{factor2}']
    obs_F = {}
    for effect, label in zip(effects, effect_labels):
        obs_F[label] = obs_table.loc[effect, 'F']

    # Permutation
    count_ge = {label: 0 for label in effect_labels}
    n = len(data)

    for i in range(n_perm):
        perm_data = data.copy()
        perm_idx = rng.permutation(n)
        perm_data[dv_col] = data[dv_col].values[perm_idx]

        try:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                perm_model = ols(formula, data=perm_data).fit()
                perm_table = anova_lm(perm_model, typ=2)

            for effect, label in zip(effects, effect_labels):
                if perm_table.loc[effect, 'F'] >= obs_F[label]:
                    count_ge[label] += 1
        except Exception:
            continue

    p_perm = {label: (count_ge[label] + 1) / (n_perm + 1) for label in effect_labels}

    return {
        'obs_F': obs_F,
        'p_perm': p_perm,
        'obs_table': obs_table,
    }


# %%
# --- Run permutation ANOVA for all 12 DVs ---
perm_results = {}
for family_label, dv_cols in DV_FAMILIES.items():
    for col in dv_cols:
        print(f"Running permutation ANOVA: {col} ...", flush=True)
        result = permutation_anova_2way(df, col)
        perm_results[col] = result
        for label in result['obs_F']:
            print(f"  {label}: F = {result['obs_F'][label]:.4f}, p_perm = {result['p_perm'][label]:.4f}")

print("\nAll permutation ANOVAs complete.")

# %% [markdown]
# ## B4. BH-FDR Correction (Permutation ANOVA)

# %%
# Collect all results into a DataFrame
perm_rows = []
effect_labels = ['if_PTSD', 'if_antipsychotic', 'if_PTSD:if_antipsychotic']

for family_label, dv_cols in DV_FAMILIES.items():
    for col in dv_cols:
        res = perm_results[col]
        for label in effect_labels:
            perm_rows.append({
                'Family': family_label,
                'Metric': col,
                'Effect': label,
                'F_obs': res['obs_F'][label],
                'p_perm': res['p_perm'][label],
            })

perm_df = pd.DataFrame(perm_rows)

# BH-FDR: 9 rounds (3 effects × 3 families, 4 p-values each)
perm_df['p_BH'] = np.nan
perm_df['Significant_BH'] = False

for effect in effect_labels:
    for family_label in DV_FAMILIES:
        mask = (perm_df['Effect'] == effect) & (perm_df['Family'] == family_label)
        p_vals = perm_df.loc[mask, 'p_perm'].values
        if len(p_vals) > 1:
            reject, p_bh, _, _ = multipletests(p_vals, alpha=ALPHA, method='fdr_bh')
            perm_df.loc[mask, 'p_BH'] = p_bh
            perm_df.loc[mask, 'Significant_BH'] = reject
        else:
            perm_df.loc[mask, 'p_BH'] = p_vals[0]
            perm_df.loc[mask, 'Significant_BH'] = p_vals[0] < ALPHA

# %% [markdown]
# ## B5. Results Display

# %%
print("\n" + "=" * 100)
print("RESULTS — Part B: Permutation ANOVA (if_PTSD × if_antipsychotic)")
print("=" * 100)

for effect in effect_labels:
    print(f"\n{'='*60}")
    print(f"Effect: {effect}")
    print(f"{'='*60}")
    for family_label in DV_FAMILIES:
        fam = perm_df[(perm_df['Effect'] == effect) & (perm_df['Family'] == family_label)]
        print(f"\n  --- {family_label} ---")
        for _, r in fam.iterrows():
            sig_label = "SIGNIFICANT" if r['Significant_BH'] else "not significant"
            print(f"    {r['Metric']}:")
            print(f"      F = {r['F_obs']:.4f}, p_perm = {r['p_perm']:.4f}, p_BH = {r['p_BH']:.4f} → {sig_label}")

any_sig_b = perm_df['Significant_BH'].any()
print(f"\nPart B overall: {'At least one significant result' if any_sig_b else 'No significant results'} at α = {ALPHA} (BH-corrected)")
print("=" * 100)

# %% [markdown]
# ## B6. Post-hoc (conditional on significant interaction)

# %%
sig_interactions = perm_df[(perm_df['Effect'] == 'if_PTSD:if_antipsychotic') & (perm_df['Significant_BH'])]

if len(sig_interactions) > 0:
    print("=== Post-hoc: Simple Effects for Significant Interactions ===\n")
    posthoc_rows = []
    for _, row in sig_interactions.iterrows():
        col = row['Metric']
        print(f"\n--- {col} ---")

        # Simple effect of antipsychotic within each PTSD level
        for ptsd_val, ptsd_label in [(0, 'No-PTSD'), (1, 'PTSD')]:
            sub = df[df['if_PTSD'] == ptsd_val]
            g1 = sub[sub['if_antipsychotic'] == 1][col].dropna()
            g2 = sub[sub['if_antipsychotic'] == 0][col].dropna()
            if len(g1) >= 2 and len(g2) >= 2:
                u_stat, p_val = stats.mannwhitneyu(g1, g2, alternative='two-sided')
                r_rb = rank_biserial_r(u_stat, len(g1), len(g2))
                print(f"  Anti vs No-Anti within {ptsd_label}: U = {u_stat:.1f}, p = {p_val:.4f}, r = {r_rb:.4f}")
                posthoc_rows.append({
                    'Metric': col, 'Comparison': f'Anti effect within {ptsd_label}',
                    'U': u_stat, 'p': p_val, 'rank_biserial_r': r_rb
                })

        # Simple effect of PTSD within each antipsychotic level
        for anti_val, anti_label in [(0, 'No-Anti'), (1, 'Anti')]:
            sub = df[df['if_antipsychotic'] == anti_val]
            g1 = sub[sub['if_PTSD'] == 1][col].dropna()
            g2 = sub[sub['if_PTSD'] == 0][col].dropna()
            if len(g1) >= 2 and len(g2) >= 2:
                u_stat, p_val = stats.mannwhitneyu(g1, g2, alternative='two-sided')
                r_rb = rank_biserial_r(u_stat, len(g1), len(g2))
                print(f"  PTSD vs No-PTSD within {anti_label}: U = {u_stat:.1f}, p = {p_val:.4f}, r = {r_rb:.4f}")
                posthoc_rows.append({
                    'Metric': col, 'Comparison': f'PTSD effect within {anti_label}',
                    'U': u_stat, 'p': p_val, 'rank_biserial_r': r_rb
                })

    posthoc_df = pd.DataFrame(posthoc_rows) if posthoc_rows else None
else:
    print("No significant interactions after BH correction — post-hoc not performed.")
    posthoc_df = None

# %% [markdown]
# ## B7. Visualizations — Permutation ANOVA

# %%
# --- Interaction plots: 3×4 grid, line plots of cell means ± SE ---
fig, axes = plt.subplots(3, 4, figsize=(20, 14))

for row_i, (family_label, dv_cols) in enumerate(DV_FAMILIES.items()):
    for col_i, col in enumerate(dv_cols):
        ax = axes[row_i, col_i]

        for anti_val, anti_label, color, ls in [(0, 'No-Anti', COLOR_NO_ANTI, '-'),
                                                  (1, 'Anti', COLOR_ANTI, '--')]:
            means = []
            ses = []
            for ptsd_val in [0, 1]:
                cell = df[(df['if_PTSD'] == ptsd_val) & (df['if_antipsychotic'] == anti_val)]
                vals = cell[col].dropna()
                means.append(vals.mean())
                ses.append(vals.std() / np.sqrt(len(vals)) if len(vals) > 0 else 0)

            ax.errorbar([0, 1], means, yerr=ses, marker='o', color=color,
                       linestyle=ls, linewidth=2, capsize=5, label=anti_label)

        ax.set_xticks([0, 1])
        ax.set_xticklabels(['No-PTSD', 'PTSD'], fontsize=9)
        if row_i == 0:
            ax.set_title(THREAT_CATEGORIES[col_i], fontsize=10, fontweight='bold')
        if col_i == 0:
            ax.set_ylabel(family_label.split(':')[0], fontsize=9)
        else:
            ax.set_ylabel('')
        if row_i == 0 and col_i == 3:
            ax.legend(fontsize=8)

fig.suptitle('E2 Part B: Interaction Plots (PTSD × Antipsychotic)', fontsize=14, y=1.02)
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/interaction_plots_part_b.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/interaction_plots_part_b.png')

# %%
# --- Heatmap of permutation p-values: DVs × effects ---
effect_short = {'if_PTSD': 'PTSD', 'if_antipsychotic': 'Anti', 'if_PTSD:if_antipsychotic': 'Interaction'}

heatmap_data = perm_df.pivot_table(index='Metric', columns='Effect', values='p_BH')
heatmap_data = heatmap_data.rename(columns=effect_short)
heatmap_data = heatmap_data[['PTSD', 'Anti', 'Interaction']]

# Reorder rows by family
ordered_metrics = ALL_DV_COLS
heatmap_data = heatmap_data.loc[ordered_metrics]

# Short names for display
short_names = []
for m in ordered_metrics:
    for prefix in ['mean_dwell_pct_', 'std_dwell_pct_', 'mean_visits_']:
        if m.startswith(prefix):
            family_prefix = prefix.replace('mean_dwell_pct_', 'Dwell: ').replace('std_dwell_pct_', 'StdDwell: ').replace('mean_visits_', 'Visits: ')
            short_names.append(family_prefix + m.replace(prefix, ''))
            break
heatmap_data.index = short_names

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(heatmap_data, annot=True, fmt='.3f', cmap='RdYlGn_r', vmin=0, vmax=1,
            linewidths=0.5, ax=ax, cbar_kws={'label': 'p (BH-corrected)'})

# Mark significant cells
for i in range(heatmap_data.shape[0]):
    for j in range(heatmap_data.shape[1]):
        val = heatmap_data.iloc[i, j]
        if val < ALPHA:
            ax.text(j + 0.5, i + 0.8, '*', ha='center', va='center',
                    fontsize=16, fontweight='bold', color='black')

ax.set_title('E2 Part B: Permutation ANOVA p-values (BH-corrected)', fontsize=12)
ax.set_ylabel('')
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/heatmap_pvalues_part_b.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/heatmap_pvalues_part_b.png')

# %% [markdown]
# ---
# # Summary

# %%
print("\n" + "=" * 100)
print("COMBINED SUMMARY — E2: Medication-Attention Moderation")
print("=" * 100)

print(f"\nSample: n = {len(df)}")
print("2×2 Cell Sizes:")
print(ct.to_string())
print(f"\nMetrics: {len(ALL_DV_COLS)} DVs across 3 families")

print("\n--- Part A: Group Comparisons (Antipsychotic vs No-Antipsychotic) ---")
for family_label in DV_FAMILIES:
    fam = results_a_df[results_a_df['Family'] == family_label]
    n_sig = fam['Significant_BH'].sum()
    n_total = len(fam)
    print(f"  {family_label}: {n_sig}/{n_total} significant (BH-corrected)")

print("\n--- Part B: Permutation ANOVA (if_PTSD × if_antipsychotic) ---")
for effect in effect_labels:
    e_short = effect_short[effect]
    for family_label in DV_FAMILIES:
        fam = perm_df[(perm_df['Effect'] == effect) & (perm_df['Family'] == family_label)]
        n_sig = fam['Significant_BH'].sum()
        n_total = len(fam)
        print(f"  {e_short} — {family_label}: {n_sig}/{n_total} significant (BH-corrected)")

any_sig_overall = any_sig_a or any_sig_b
print(f"\nOverall: {'At least one significant result found' if any_sig_overall else 'No significant results'} at α = {ALPHA} (BH-corrected)")
print("\nCaveats:")
print("  - Very small cell sizes (n = 6–9) limit statistical power")
print("  - Exploratory analysis (E2) — results are hypothesis-generating, not confirmatory")
print("  - Multiple comparisons corrected via BH-FDR within families")
print("  - Unbalanced design; Type II SS used for ANOVA")
print("=" * 100)
