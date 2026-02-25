# %% [markdown]
# # E3: Temporal Dynamics of Threat Attentional Bias
#
# **Motivation**: Zvielli et al. (2015) and Schäfer et al. (2016) argue that
# within-session temporal dynamics of attentional bias carry diagnostic information
# beyond aggregate scores. Existing analyses (E1, E2) compute a single aggregate
# bias per participant. This exploration examines trial-level temporal trajectories
# and TL-BS variability indices.
#
# **Method**:
# - **Part A**: Group-level temporal trajectories (PTSD vs No-PTSD)
# - **Part B**: TL-BS variability indices — group comparison with BH-FDR
# - **Part C**: Individual spaghetti plots
#
# BH-FDR correction applied as a single family across 5 variability indices.

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

ALPHA = 0.05
FIG_DIR = 'figures/e3_temporal_dynamics_threat_bias'
os.makedirs(FIG_DIR, exist_ok=True)

COLOR_PTSD = '#d9534f'
COLOR_NO_PTSD = '#5bc0de'
LOWESS_FRAC = 0.3


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

# %%
# --- Load data ---

session_df = pd.read_csv('data/simplified/temporal_threat_bias_by_session.csv')
agg_df = pd.read_csv('data/simplified/temporal_threat_bias_aggregated.csv')
var_df = pd.read_csv('data/simplified/temporal_threat_bias_variability.csv')

ptsd_sessions = session_df[session_df['if_PTSD'] == 1]
no_ptsd_sessions = session_df[session_df['if_PTSD'] == 0]

n_total = session_df['session_id'].nunique()
n_ptsd = ptsd_sessions['session_id'].nunique()
n_no_ptsd = no_ptsd_sessions['session_id'].nunique()

print(f"Total sample: n = {n_total}")
print(f"PTSD group: n = {n_ptsd}")
print(f"No-PTSD group: n = {n_no_ptsd}")
print(f"Trial-level rows: {len(session_df)}")

# Detect which central measure was used
central_col = 'central_threat_delta_dwell'
# Infer from preprocessing: check if values match mean or median
# The column name is the same regardless; the report tells which was used
# We read the preprocessing report to determine this
report_path = 'reports/preprocessing/temporal_threat_bias_report.md'
central_measure = 'mean'  # default
if os.path.exists(report_path):
    with open(report_path) as f:
        for line in f:
            if 'Use **median**' in line:
                central_measure = 'median'
                break
            elif 'Use **mean**' in line:
                central_measure = 'mean'
                break

print(f"Central tendency measure: {central_measure}")

# %% [markdown]
# ---
# # Part A: Group-Level Temporal Trajectories

# %%
fig, ax = plt.subplots(figsize=(14, 6))

for group_label, color in [('PTSD', COLOR_PTSD), ('No-PTSD', COLOR_NO_PTSD)]:
    grp = agg_df[agg_df['group'] == group_label].sort_values('trial_index')
    x = grp['trial_index'].values
    y = grp[central_col].values
    ci_lo = grp['ci95_lo'].values
    ci_hi = grp['ci95_hi'].values

    ax.fill_between(x, ci_lo, ci_hi, alpha=0.15, color=color)
    ax.plot(x, y, 'o-', color=color, markersize=4, linewidth=1, alpha=0.6, label=f'{group_label} ({central_measure})')


ax.axhline(y=0, color='grey', linestyle=':', linewidth=1, alpha=0.7)
ax.set_xlabel('Trial Index (presentation order)', fontsize=11)
ax.set_ylabel(f'Threat Delta Dwell ({central_measure}, %)', fontsize=11)
ax.set_title('E3 Part A: Temporal Trajectory of Threat Attentional Bias', fontsize=13)
ax.legend(fontsize=9)
ax.set_xlim(0.5, 44.5)

# Add threat category color bands
cat_colors = {'angry_face': '#ffcccc', 'anxiety_inducing': '#ffe0b2',
              'warfare': '#c8e6c9', 'soldiers': '#bbdefb'}
prev_trial = 0
for _, row in agg_df[agg_df['group'] == 'PTSD'].sort_values('trial_index').iterrows():
    ti = row['trial_index']
    cat = row['threat_category']
    ax.axvspan(ti - 0.4, ti + 0.4, alpha=0.08, color=cat_colors.get(cat, '#eeeeee'), zorder=0)

fig.tight_layout()
fig.savefig(f'{FIG_DIR}/temporal_trajectory_mean_median.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/temporal_trajectory_mean_median.png')

# %% [markdown]
# ---
# # Part B: TL-BS Variability Indices

# %% [markdown]
# ## B1. Descriptive Statistics

# %%
TL_BS_COLS = ['tl_bs_mean', 'tl_bs_sd', 'tl_bs_peak_toward', 'tl_bs_peak_away', 'tl_bs_range']

desc_rows = []
for col in TL_BS_COLS:
    for group_label, group_data in [('PTSD', var_df[var_df['if_PTSD'] == 1]),
                                     ('No-PTSD', var_df[var_df['if_PTSD'] == 0])]:
        vals = group_data[col].dropna()
        desc_rows.append({
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
print("=== Descriptive Statistics — TL-BS Variability Indices ===")
print(desc_df.to_string(index=False, float_format='%.4f'))

# %% [markdown]
# ## B2. Assumption Checks

# %%
ptsd_var = var_df[var_df['if_PTSD'] == 1]
no_ptsd_var = var_df[var_df['if_PTSD'] == 0]

assumption_rows = []
for col in TL_BS_COLS:
    ptsd_vals = ptsd_var[col].dropna()
    no_ptsd_vals = no_ptsd_var[col].dropna()

    sw_ptsd = stats.shapiro(ptsd_vals)
    sw_no_ptsd = stats.shapiro(no_ptsd_vals)
    lev = stats.levene(ptsd_vals, no_ptsd_vals)

    assumption_rows.append({
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

assumptions_df = pd.DataFrame(assumption_rows)
print("\n=== Assumption Checks ===")
print(assumptions_df.to_string(index=False, float_format='%.4f'))

# %% [markdown]
# ## B3. Group Comparison Tests

# %%
results_rows = []
for i, row in assumptions_df.iterrows():
    col = row['Metric']
    ptsd_vals = ptsd_var[col].dropna()
    no_ptsd_vals = no_ptsd_var[col].dropna()
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

    results_rows.append({
        'Metric': col,
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
# ## B4. BH-FDR Correction

# %%
p_vals = results_df['p_uncorrected'].values
if len(p_vals) > 1:
    reject, p_bh, _, _ = multipletests(p_vals, alpha=ALPHA, method='fdr_bh')
    results_df['p_BH'] = p_bh
    results_df['Significant_BH'] = reject
else:
    results_df['p_BH'] = p_vals
    results_df['Significant_BH'] = p_vals < ALPHA

print("\n" + "=" * 95)
print("RESULTS — Part B: TL-BS Variability Indices (PTSD vs No-PTSD)")
print("=" * 95)

for _, r in results_df.iterrows():
    sig_label = "SIGNIFICANT" if r['Significant_BH'] else "not significant"
    print(f"\n  {r['Metric']}:")
    print(f"    Test: {r['Test']}, stat = {r['Statistic']:.4f}")
    print(f"    p (uncorrected) = {r['p_uncorrected']:.4f}, p (BH) = {r['p_BH']:.4f} → {sig_label}")
    print(f"    {r['Effect_Size_Type']} = {r['Effect_Size']:.4f}, 95% CI [{r['CI_lo']:.4f}, {r['CI_hi']:.4f}]")

any_sig = results_df['Significant_BH'].any()
print(f"\nPart B overall: {'At least one significant result' if any_sig else 'No significant results'} at α = {ALPHA} (BH-corrected)")
print("=" * 95)

# %% [markdown]
# ## B5. Visualizations — Variability Indices

# %%
# --- Violin + strip plots: 2x3 grid ---
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
axes_flat = axes.flatten()

for i, col in enumerate(TL_BS_COLS):
    ax = axes_flat[i]
    plot_data = var_df[['if_PTSD', col]].dropna().copy()
    plot_data['Group'] = plot_data['if_PTSD'].map({1: 'PTSD', 0: 'No-PTSD'})

    sns.violinplot(data=plot_data, x='Group', y=col, order=['PTSD', 'No-PTSD'],
                   palette={'PTSD': COLOR_PTSD, 'No-PTSD': COLOR_NO_PTSD},
                   inner=None, alpha=0.4, ax=ax)
    sns.stripplot(data=plot_data, x='Group', y=col, order=['PTSD', 'No-PTSD'],
                  palette={'PTSD': COLOR_PTSD, 'No-PTSD': COLOR_NO_PTSD},
                  size=5, alpha=0.7, ax=ax)

    r_row = results_df[results_df['Metric'] == col].iloc[0]
    sig_marker = '*' if r_row['Significant_BH'] else ''
    ax.set_title(f"{col}\np(BH) = {r_row['p_BH']:.3f}{sig_marker}", fontsize=9)
    ax.set_xlabel('')

# Hide unused subplot
axes_flat[5].set_visible(False)

fig.suptitle('E3 Part B: TL-BS Variability Indices by Group', fontsize=13, y=1.02)
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/violin_variability_indices.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/violin_variability_indices.png')

# %%
# --- Forest plot of effect sizes ---
fig, ax = plt.subplots(figsize=(10, 5))
labels = []
for idx, (_, r) in enumerate(results_df.iterrows()):
    color = '#d9534f' if r['Significant_BH'] else '#333333'
    ax.errorbar(r['Effect_Size'], idx,
                xerr=[[r['Effect_Size'] - r['CI_lo']], [r['CI_hi'] - r['Effect_Size']]],
                fmt='o', color=color, markersize=8, capsize=5, linewidth=2)
    labels.append(f"{r['Metric']} ({r['Effect_Size_Type']})")

ax.axvline(x=0, color='grey', linestyle='--', linewidth=1)
ax.set_yticks(np.arange(len(results_df)))
ax.set_yticklabels(labels, fontsize=9)
ax.set_xlabel('Effect Size (95% CI)')
ax.set_title('E3 Part B: Effect Sizes — PTSD vs No-PTSD (TL-BS Indices)')
ax.invert_yaxis()
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/forest_plot_variability.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/forest_plot_variability.png')

# %% [markdown]
# ---
# # Part C: Individual Trajectories (Spaghetti Plots)

# %%
# --- Side-by-side spaghetti plots ---
fig, axes = plt.subplots(1, 2, figsize=(18, 6), sharey=True)

for ax, (group_label, color) in zip(axes, [('PTSD', COLOR_PTSD), ('No-PTSD', COLOR_NO_PTSD)]):
    grp = session_df[session_df['group'] == group_label]
    all_y = []

    for sid, sub in grp.groupby('session_id'):
        sub = sub.sort_values('trial_index')
        ax.plot(sub['trial_index'], sub['threat_delta_dwell'],
                color=color, alpha=0.2, linewidth=0.7)
        all_y.append(sub.set_index('trial_index')['threat_delta_dwell'])

    # Group LOWESS mean
    group_agg = grp.groupby('trial_index')['threat_delta_dwell'].mean().reset_index()
    lowess_result = sm_lowess(group_agg['threat_delta_dwell'].values,
                               group_agg['trial_index'].values, frac=LOWESS_FRAC)
    ax.plot(lowess_result[:, 0], lowess_result[:, 1], color=color,
            linewidth=3, label='Group LOWESS')

    ax.axhline(y=0, color='grey', linestyle=':', linewidth=1, alpha=0.7)
    ax.set_xlabel('Trial Index', fontsize=11)
    ax.set_title(f'{group_label} (n = {grp["session_id"].nunique()})', fontsize=12)
    ax.legend(fontsize=9)
    ax.set_xlim(0.5, 44.5)

axes[0].set_ylabel('Threat Delta Dwell (%)', fontsize=11)

fig.suptitle('E3 Part C: Individual Temporal Trajectories', fontsize=13, y=1.02)
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/spaghetti_individual_trajectories.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/spaghetti_individual_trajectories.png')

# %%
# --- Combined spaghetti plot ---
fig, ax = plt.subplots(figsize=(14, 6))

for group_label, color in [('PTSD', COLOR_PTSD), ('No-PTSD', COLOR_NO_PTSD)]:
    grp = session_df[session_df['group'] == group_label]

    for sid, sub in grp.groupby('session_id'):
        sub = sub.sort_values('trial_index')
        ax.plot(sub['trial_index'], sub['threat_delta_dwell'],
                color=color, alpha=0.1, linewidth=0.5)

    group_agg = grp.groupby('trial_index')['threat_delta_dwell'].mean().reset_index()
    lowess_result = sm_lowess(group_agg['threat_delta_dwell'].values,
                               group_agg['trial_index'].values, frac=LOWESS_FRAC)
    ax.plot(lowess_result[:, 0], lowess_result[:, 1], color=color,
            linewidth=3, label=f'{group_label} LOWESS')

ax.axhline(y=0, color='grey', linestyle=':', linewidth=1, alpha=0.7)
ax.set_xlabel('Trial Index (presentation order)', fontsize=11)
ax.set_ylabel('Threat Delta Dwell (%)', fontsize=11)
ax.set_title('E3 Part C: Combined Individual Trajectories', fontsize=13)
ax.legend(fontsize=10)
ax.set_xlim(0.5, 44.5)

fig.tight_layout()
fig.savefig(f'{FIG_DIR}/spaghetti_combined.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/spaghetti_combined.png')

# %% [markdown]
# ---
# # Summary & Report Generation

# %%
print("\n" + "=" * 95)
print("COMBINED SUMMARY — E3: Temporal Dynamics of Threat Attentional Bias")
print("=" * 95)

print(f"\nSample: n = {n_total} (PTSD: {n_ptsd}, No-PTSD: {n_no_ptsd})")
print(f"Threat slides: 44 (trial-level)")
print(f"Central tendency: {central_measure}")

print("\n--- Part A: Temporal Trajectories ---")
ptsd_agg = agg_df[agg_df['group'] == 'PTSD']
no_ptsd_agg = agg_df[agg_df['group'] == 'No-PTSD']
print(f"  PTSD group {central_measure} range: [{ptsd_agg[central_col].min():.2f}, {ptsd_agg[central_col].max():.2f}]")
print(f"  No-PTSD group {central_measure} range: [{no_ptsd_agg[central_col].min():.2f}, {no_ptsd_agg[central_col].max():.2f}]")

print("\n--- Part B: TL-BS Variability Indices ---")
for _, r in results_df.iterrows():
    sig_label = "SIGNIFICANT" if r['Significant_BH'] else "n.s."
    print(f"  {r['Metric']}: {r['Effect_Size_Type']} = {r['Effect_Size']:.3f}, p(BH) = {r['p_BH']:.4f} [{sig_label}]")

print(f"\nPart B: {'At least one significant result' if any_sig else 'No significant results'} at α = {ALPHA}")

print("\nNote: This is an exploratory analysis with a small sample (N=29). Results should be")
print("interpreted cautiously and treated as hypothesis-generating, not confirmatory.")
print("=" * 95)

# %%
# --- Generate report ---
os.makedirs('reports/exploratory_analysis', exist_ok=True)

# Build descriptive stats table
desc_lines = ["| Metric | Group | n | Mean | SD | Median | Min | Max |",
              "|--------|-------|---|------|----|--------|-----|-----|"]
for _, r in desc_df.iterrows():
    desc_lines.append(f"| `{r['Metric']}` | {r['Group']} | {r['n']} | {r['Mean']:.2f} | {r['SD']:.2f} | {r['Median']:.2f} | {r['Min']:.2f} | {r['Max']:.2f} |")

# Build assumption checks table
assump_lines = ["| Metric | Shapiro PTSD (W, p) | Shapiro No-PTSD (W, p) | Levene (F, p) | Both Normal | Equal Var |",
                "|--------|---------------------|------------------------|---------------|------------|-----------|"]
for _, r in assumptions_df.iterrows():
    assump_lines.append(
        f"| `{r['Metric']}` | {r['Shapiro_PTSD_W']:.3f}, {r['Shapiro_PTSD_p']:.4f} | "
        f"{r['Shapiro_NoPTSD_W']:.3f}, {r['Shapiro_NoPTSD_p']:.4f} | "
        f"{r['Levene_F']:.3f}, {r['Levene_p']:.4f} | "
        f"{'Yes' if r['Both_Normal'] else 'No'} | {'Yes' if r['Equal_Var'] else 'No'} |"
    )

# Build results table
results_lines = ["| Metric | Test | Statistic | p (uncorr.) | p (BH) | Effect Size | 95% CI | Sig. |",
                 "|--------|------|-----------|-------------|--------|-------------|--------|------|"]
for _, r in results_df.iterrows():
    sig = "Yes" if r['Significant_BH'] else "No"
    results_lines.append(
        f"| `{r['Metric']}` | {r['Test']} | {r['Statistic']:.3f} | {r['p_uncorrected']:.4f} | "
        f"{r['p_BH']:.4f} | {r['Effect_Size_Type']} = {r['Effect_Size']:.3f} | "
        f"[{r['CI_lo']:.3f}, {r['CI_hi']:.3f}] | {sig} |"
    )

report_lines = [
    "# E3: Temporal Dynamics of Threat Attentional Bias",
    "",
    "## 1. Motivation",
    "",
    "Zvielli et al. (2015) and Schäfer et al. (2016) demonstrate that within-session",
    "temporal dynamics of attentional bias carry diagnostic information beyond aggregate",
    "scores. This exploratory analysis examines trial-level temporal trajectories and",
    "TL-BS (Trial-Level Bias Score) variability indices for threat attentional bias,",
    "comparing PTSD and No-PTSD groups.",
    "",
    "## 2. Method",
    "",
    "### Participants",
    "",
    f"- Total: N = {n_total}",
    f"- PTSD: n = {n_ptsd}",
    f"- No-PTSD: n = {n_no_ptsd}",
    "- Excluded: `UgMWkyrkRYVZ9cr9thRw` (poor gaze quality)",
    "",
    "### Variables",
    "",
    "| Variable | Description |",
    "|----------|------------|",
    "| `threat_delta_dwell` | Threat dwell % − neutral dwell % per slide |",
    "| `trial_index` | Presentation order (1–44) of threat–neutral slides |",
    "| `tl_bs_mean` | Session mean of 44 trial-level deltas |",
    "| `tl_bs_sd` | Session SD of 44 trial-level deltas |",
    "| `tl_bs_peak_toward` | Max positive delta (strongest threat bias) |",
    "| `tl_bs_peak_away` | Min delta (strongest avoidance) |",
    "| `tl_bs_range` | peak_toward − peak_away |",
    "",
    "### Analysis Approach",
    "",
    "- **Part A**: Group-level temporal trajectories with 95% CI bands",
    f"- **Part B**: Group comparisons on 5 TL-BS variability indices; assumption-driven",
    "  test selection (Student's t / Welch's t / Mann-Whitney U); BH-FDR correction",
    "  as a single family",
    "- **Part C**: Individual spaghetti plots to visualize within-session variability",
    "",
    "## 3. Part A — Group-Level Temporal Trajectories",
    "",
    f"Central tendency: **{central_measure}** (selected based on Shapiro-Wilk distribution",
    "checks on per-slide delta distributions in preprocessing).",
    "",
    f"- PTSD group {central_measure} range: [{ptsd_agg[central_col].min():.2f}, {ptsd_agg[central_col].max():.2f}]",
    f"- No-PTSD group {central_measure} range: [{no_ptsd_agg[central_col].min():.2f}, {no_ptsd_agg[central_col].max():.2f}]",
    "",
    "Both groups show generally positive threat bias (above zero) across most trials,",
    "indicating a slight tendency to dwell more on threat images than neutral counterparts.",
    "",
    f"![Temporal Trajectory](../../figures/e3_temporal_dynamics_threat_bias/temporal_trajectory_mean_median.png)",
    "",
    "## 4. Part B — TL-BS Variability Indices",
    "",
    "### Descriptive Statistics",
    "",
] + desc_lines + [
    "",
    "### Assumption Checks",
    "",
] + assump_lines + [
    "",
    "### Results",
    "",
] + results_lines + [
    "",
    f"**Overall:** {'At least one significant result' if any_sig else 'No significant results'} at α = {ALPHA} (BH-corrected).",
    "",
    f"![Violin Plots](../../figures/e3_temporal_dynamics_threat_bias/violin_variability_indices.png)",
    "",
    f"![Forest Plot](../../figures/e3_temporal_dynamics_threat_bias/forest_plot_variability.png)",
    "",
    "## 5. Part C — Individual Trajectories",
    "",
    "Spaghetti plots show substantial within-session variability for both groups.",
    "Individual trajectories oscillate widely around zero, consistent with trial-level",
    "attentional bias being highly variable.",
    "",
    f"![Side-by-Side Spaghetti](../../figures/e3_temporal_dynamics_threat_bias/spaghetti_individual_trajectories.png)",
    "",
    f"![Combined Spaghetti](../../figures/e3_temporal_dynamics_threat_bias/spaghetti_combined.png)",
    "",
    "## 6. Summary & Interpretation",
    "",
    "### Key Findings",
    "",
]

# Dynamically generate key findings
findings = []
findings.append(f"1. Both groups show generally positive threat bias across the 44 trial presentations, with largely overlapping trajectories and 95% CI bands.")

n_sig = results_df['Significant_BH'].sum()
if n_sig > 0:
    sig_metrics = results_df[results_df['Significant_BH']]['Metric'].tolist()
    findings.append(f"2. {n_sig} of 5 TL-BS variability indices showed significant group differences (BH-corrected): {', '.join(sig_metrics)}.")
else:
    findings.append(f"2. None of the 5 TL-BS variability indices showed significant group differences after BH-FDR correction.")

findings.append("3. Individual trajectories show substantial within-session variability in both groups.")
findings.append("4. The null results likely reflect methodological limitations (non-contiguous trial selection) and the trauma-exposed nature of the comparison group (see below).")

report_lines += findings + [
    "",
    "### Caveats",
    "",
    "- Small sample size (N=29) limits statistical power",
    "- Exploratory analysis — results are hypothesis-generating, not confirmatory",
    "- Trial order confounded with threat category (slides presented in fixed order)",
    "- No correction for multiple comparisons across Parts A–C (only within Part B)",
    "",
    "### Why This Approach May Not Differentiate Groups",
    "",
    "Two design features likely contribute to the null results:",
    "",
    "1. **Non-contiguous threat trial selection.** The 44 threat–neutral slides are interspersed",
    "   among 75 total slides (31 non-threat slides omitted). The temporal trajectory treats these",
    "   44 trials as contiguous (trial_index 1–44), but participants actually experienced interleaved",
    "   non-threat content between them. This breaks the assumption of continuous temporal evolution",
    "   that Zvielli et al. (2015) relied on, where consecutive trials were all bias-relevant. The",
    "   gaps between threat trials likely reset or disrupt any accumulating attentional pattern.",
    "",
    "2. **Trauma-exposed comparison group.** The No-PTSD group consists of soldiers potentially",
    "   exposed to trauma but without a PTSD diagnosis. Unlike civilian controls, these individuals",
    "   may exhibit similar threat-related attentional dynamics (hypervigilance, variable engagement",
    "   with threat stimuli) as the PTSD group, making temporal variability indices indistinguishable",
    "   between groups. A civilian control group might show different temporal patterns.",
    "",
    "## 7. Metadata",
    "",
    "| Field | Value |",
    "|-------|-------|",
    "| Analysis ID | E3 |",
    f"| Script | `exploratory_analysis/e3_temporal_dynamics_threat_bias.py` |",
    f"| Datasets | `temporal_threat_bias_by_session.csv`, `temporal_threat_bias_aggregated.csv`, `temporal_threat_bias_variability.csv` |",
    f"| N | {n_total} (PTSD: {n_ptsd}, No-PTSD: {n_no_ptsd}) |",
    f"| DVs | 5 TL-BS variability indices |",
    f"| Alpha | {ALPHA} |",
    f"| FDR | BH (single family of 5 tests) |",
    f"| Central Tendency | {central_measure} |",
    f"| LOWESS frac | {LOWESS_FRAC} |",
    f"| Date | {pd.Timestamp.now().strftime('%Y-%m-%d')} |",
    "",
]

report_path_out = 'reports/exploratory_analysis/e3_temporal_dynamics_threat_bias.md'
with open(report_path_out, 'w') as f:
    f.write('\n'.join(report_lines))

print(f"\nReport saved to {report_path_out}")
