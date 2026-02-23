# %% [markdown]
# # H4: ABV × ITI PTSD Severity Correlation
#
# **Hypothesis**: Attention bias variability (ABV) metrics — `std_dwell_pct_{threat}`
# and `std_delta_dwell_pct_{threat}` — will show positive associations with PTSD
# symptom severity (`ITI_PTSD`) within the PTSD group (n=17).
#
# **Method**: Within-group correlational analysis (PTSD only). Test selection follows
# normality checks on both variables **and** outlier detection (standardized OLS
# residuals, |z| > 3). Homoscedasticity is assessed visually via residual plots
# (reported for transparency, not used as a decision criterion at n=17). p-values are
# corrected for multiple comparisons using Benjamini-Hochberg FDR separately within
# each family of 4 tests.

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
FAMILY1_COLS = [f'std_dwell_pct_{cat}' for cat in THREAT_CATEGORIES]
FAMILY2_COLS = [f'std_delta_dwell_pct_{cat}' for cat in THREAT_CATEGORIES]
IV_COL = 'ITI_PTSD'
ALPHA = 0.05

FIG_DIR = 'figures/h4_abv_iti_correlation'
os.makedirs(FIG_DIR, exist_ok=True)

# %% [markdown]
# ## 1. Load Data — PTSD Group Only

# %%
df = pd.read_csv('data/simplified/dataset_eyetracking_metrics_clean.csv')

ptsd = df[df['if_PTSD'] == 1]

print(f"PTSD group: n = {len(ptsd)}")
print(f"\nIV: {IV_COL}")
print(f"Family 1 DVs (raw dwell variability): {FAMILY1_COLS}")
print(f"Family 2 DVs (delta dwell variability): {FAMILY2_COLS}")

# %% [markdown]
# ## 2. Descriptive Statistics

# %%
desc_rows = []
all_cols = [IV_COL] + FAMILY1_COLS + FAMILY2_COLS
for col in all_cols:
    vals = ptsd[col].dropna()
    desc_rows.append({
        'Variable': col,
        'n': len(vals),
        'Mean': vals.mean(),
        'SD': vals.std(),
        'Median': vals.median(),
        'Min': vals.min(),
        'Max': vals.max(),
    })

desc_df = pd.DataFrame(desc_rows)
print("=== Descriptive Statistics (PTSD group only) ===")
print(desc_df.to_string(index=False, float_format='%.4f'))

# %% [markdown]
# ## 3. Assumption Checks

# %%
# Shapiro-Wilk on ITI_PTSD (once)
iv_vals = ptsd[IV_COL].dropna()
sw_iv = stats.shapiro(iv_vals)
iv_normal = sw_iv.pvalue > ALPHA
print(f"Shapiro-Wilk on {IV_COL}: W = {sw_iv.statistic:.4f}, p = {sw_iv.pvalue:.4f} → {'Normal' if iv_normal else 'Non-normal'}")
print()

assumption_rows = []
for col in FAMILY1_COLS + FAMILY2_COLS:
    vals = ptsd[col].dropna()
    sw_dv = stats.shapiro(vals)
    dv_normal = sw_dv.pvalue > ALPHA
    both_normal = iv_normal and dv_normal
    assumption_rows.append({
        'DV': col,
        'Shapiro_DV_W': sw_dv.statistic,
        'Shapiro_DV_p': sw_dv.pvalue,
        'DV_Normal': dv_normal,
        'IV_Normal': iv_normal,
        'Both_Normal': both_normal,
    })

assumptions_df = pd.DataFrame(assumption_rows)

# --- Outlier detection via standardized OLS residuals ---
outlier_rows = []
for col in FAMILY1_COLS + FAMILY2_COLS:
    dv = ptsd[col].dropna()
    iv = ptsd.loc[dv.index, IV_COL]
    slope, intercept = np.polyfit(iv, dv, 1)
    fitted = intercept + slope * iv
    residuals = dv - fitted
    z_resid = (residuals - residuals.mean()) / residuals.std()
    n_outliers = int((z_resid.abs() > 3).sum())
    outlier_rows.append({'N_Outliers': n_outliers, 'Has_Outliers': n_outliers > 0})

outlier_df = pd.DataFrame(outlier_rows)
assumptions_df['N_Outliers'] = outlier_df['N_Outliers'].values
assumptions_df['Has_Outliers'] = outlier_df['Has_Outliers'].values
assumptions_df['Use_Pearson'] = assumptions_df['Both_Normal'] & ~assumptions_df['Has_Outliers']

print("=== Assumption Checks ===")
print(assumptions_df.to_string(index=False, float_format='%.4f'))
print(f"\nOutlier summary: {assumptions_df['Has_Outliers'].sum()} of {len(assumptions_df)} pairs have outliers (|z_resid| > 3)")

# %% [markdown]
# ## 3b. Assumption Diagnostic Plots

# %%
# --- Figure 1: Outlier inspection (2×4 grid) ---
all_dvs = FAMILY1_COLS + FAMILY2_COLS
short_names = [c.replace('std_dwell_pct_', 'std_dwell_\n').replace('std_delta_dwell_pct_', 'std_delta_\n')
               for c in all_dvs]

fig, axes = plt.subplots(2, 4, figsize=(20, 10))
axes = axes.flatten()

for i, col in enumerate(all_dvs):
    ax = axes[i]
    dv = ptsd[col].dropna()
    iv = ptsd.loc[dv.index, IV_COL]
    slope, intercept = np.polyfit(iv, dv, 1)
    fitted = intercept + slope * iv
    residuals = dv - fitted
    z_resid = (residuals - residuals.mean()) / residuals.std()
    outlier_mask = z_resid.abs() > 3

    # Normal points
    ax.scatter(iv[~outlier_mask], dv[~outlier_mask], color='#d9534f', alpha=0.7,
               s=50, edgecolors='white', linewidth=0.5, label='Normal')
    # Outlier points
    if outlier_mask.any():
        ax.scatter(iv[outlier_mask], dv[outlier_mask], color='#f0ad4e', alpha=0.9,
                   s=100, edgecolors='black', linewidth=1, zorder=5, label='Outlier')
    # OLS fit line
    x_range = np.linspace(iv.min(), iv.max(), 100)
    ax.plot(x_range, intercept + slope * x_range, '--', color='#d9534f', alpha=0.6, linewidth=1.5)

    n_out = int(outlier_mask.sum())
    ax.set_title(f"{short_names[i]}\nOutliers: {n_out}", fontsize=9)
    ax.set_xlabel('ITI_PTSD')
    ax.set_ylabel('DV')
    if outlier_mask.any():
        ax.legend(fontsize=7)

fig.suptitle('Outlier Inspection — Standardized OLS Residuals (|z| > 3)', fontsize=13, y=1.02)
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/outlier_inspection.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/outlier_inspection.png')

# --- Figure 2: Homoscedasticity inspection (2×4 grid) ---
from statsmodels.nonparametric.smoothers_lowess import lowess as sm_lowess

fig, axes = plt.subplots(2, 4, figsize=(20, 10))
axes = axes.flatten()

for i, col in enumerate(all_dvs):
    ax = axes[i]
    dv = ptsd[col].dropna()
    iv = ptsd.loc[dv.index, IV_COL]
    slope, intercept = np.polyfit(iv, dv, 1)
    fitted = intercept + slope * iv
    residuals = dv - fitted
    z_resid = (residuals - residuals.mean()) / residuals.std()

    ax.scatter(fitted, z_resid, color='#d9534f', alpha=0.7, s=50, edgecolors='white', linewidth=0.5)
    ax.axhline(0, color='grey', linestyle='--', linewidth=1)

    # LOWESS smoother
    lowess_result = sm_lowess(z_resid.values, fitted.values, frac=0.6)
    ax.plot(lowess_result[:, 0], lowess_result[:, 1], color='#337ab7', linewidth=2, label='LOWESS')

    ax.set_title(short_names[i], fontsize=9)
    ax.set_xlabel('Fitted values')
    ax.set_ylabel('Std. residuals')
    ax.legend(fontsize=7)

fig.suptitle('Homoscedasticity Inspection — Residuals vs Fitted (visual only)', fontsize=13, y=1.02)
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/homoscedasticity_inspection.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/homoscedasticity_inspection.png')

# %% [markdown]
# ## 4. Correlation Tests

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
    """Run Pearson or Kendall correlation based on normality and outlier checks."""
    if use_pearson:
        r, p = stats.pearsonr(dv_vals, iv_vals)
        ci_lo, ci_hi = pearson_ci(r, len(dv_vals))
        return "Pearson's r", r, p, ci_lo, ci_hi
    else:
        tau, p = stats.kendalltau(dv_vals, iv_vals)
        ci_lo, ci_hi = kendall_ci_bootstrap(dv_vals.values, iv_vals.values)
        return "Kendall's τ_b", tau, p, ci_lo, ci_hi


# --- Family 1: std_dwell_pct ---
results_f1 = []
for i, cat in enumerate(THREAT_CATEGORIES):
    col = f'std_dwell_pct_{cat}'
    dv = ptsd[col].dropna()
    iv = ptsd.loc[dv.index, IV_COL]
    use_pearson = assumptions_df.iloc[i]['Use_Pearson']
    test_name, coef, p_val, ci_lo, ci_hi = run_correlation(dv, iv, use_pearson)
    results_f1.append({
        'Category': cat,
        'Test': test_name,
        'Coefficient': coef,
        'p_uncorrected': p_val,
        'CI_lo': ci_lo,
        'CI_hi': ci_hi,
    })

results_f1_df = pd.DataFrame(results_f1)
print("=== Family 1: std_dwell_pct (raw dwell variability) ===")
print(results_f1_df.to_string(index=False, float_format='%.4f'))

# --- Family 2: std_delta_dwell_pct ---
results_f2 = []
for i, cat in enumerate(THREAT_CATEGORIES):
    col = f'std_delta_dwell_pct_{cat}'
    dv = ptsd[col].dropna()
    iv = ptsd.loc[dv.index, IV_COL]
    use_pearson = assumptions_df.iloc[i + 4]['Use_Pearson']
    test_name, coef, p_val, ci_lo, ci_hi = run_correlation(dv, iv, use_pearson)
    results_f2.append({
        'Category': cat,
        'Test': test_name,
        'Coefficient': coef,
        'p_uncorrected': p_val,
        'CI_lo': ci_lo,
        'CI_hi': ci_hi,
    })

results_f2_df = pd.DataFrame(results_f2)
print("\n=== Family 2: std_delta_dwell_pct (delta dwell variability) ===")
print(results_f2_df.to_string(index=False, float_format='%.4f'))

# %% [markdown]
# ## 5. Benjamini-Hochberg Correction

# %%
# Family 1
reject1, p_bh1, _, _ = multipletests(results_f1_df['p_uncorrected'], alpha=ALPHA, method='fdr_bh')
results_f1_df['p_BH'] = p_bh1
results_f1_df['Significant_BH'] = reject1

print("=== Family 1 Results with BH Correction ===")
display_cols = ['Category', 'Test', 'Coefficient', 'p_uncorrected', 'p_BH', 'CI_lo', 'CI_hi', 'Significant_BH']
print(results_f1_df[display_cols].to_string(index=False, float_format='%.4f'))

# Family 2
reject2, p_bh2, _, _ = multipletests(results_f2_df['p_uncorrected'], alpha=ALPHA, method='fdr_bh')
results_f2_df['p_BH'] = p_bh2
results_f2_df['Significant_BH'] = reject2

print("\n=== Family 2 Results with BH Correction ===")
print(results_f2_df[display_cols].to_string(index=False, float_format='%.4f'))

# %% [markdown]
# ## 6. Results Summary

# %%
print("\n" + "=" * 90)
print("RESULTS SUMMARY — H4: ABV × ITI PTSD Severity Correlation")
print("=" * 90)

for family_label, res_df in [("Family 1: std_dwell_pct", results_f1_df),
                              ("Family 2: std_delta_dwell_pct", results_f2_df)]:
    print(f"\n--- {family_label} ---")
    for _, r in res_df.iterrows():
        sig_label = "SIGNIFICANT" if r['Significant_BH'] else "not significant"
        print(f"\n  {r['Category']}:")
        print(f"    Test: {r['Test']}, coef = {r['Coefficient']:.4f}")
        print(f"    p (uncorrected) = {r['p_uncorrected']:.4f}, p (BH) = {r['p_BH']:.4f} → {sig_label}")
        print(f"    95% CI [{r['CI_lo']:.4f}, {r['CI_hi']:.4f}]")

any_sig = results_f1_df['Significant_BH'].any() or results_f2_df['Significant_BH'].any()
print(f"\nOverall: H4 {'supported' if any_sig else 'NOT supported'} at α = {ALPHA} (BH-corrected)")
print("=" * 90)

# %% [markdown]
# ## 7. Visualization 1 — Scatterplots (Family 1: std_dwell_pct)

# %%
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
axes = axes.flatten()

for i, cat in enumerate(THREAT_CATEGORIES):
    ax = axes[i]
    col = f'std_dwell_pct_{cat}'
    x = ptsd[IV_COL]
    y = ptsd[col]

    ax.scatter(x, y, color='#d9534f', alpha=0.7, s=50, edgecolors='white', linewidth=0.5)

    # Linear fit line
    mask = x.notna() & y.notna()
    z = np.polyfit(x[mask], y[mask], 1)
    p_line = np.poly1d(z)
    x_range = np.linspace(x.min(), x.max(), 100)
    ax.plot(x_range, p_line(x_range), '--', color='#d9534f', alpha=0.6, linewidth=1.5)

    r = results_f1_df.iloc[i]
    ax.set_title(f"{cat}\n{r['Test']}: {r['Coefficient']:.3f}, p = {r['p_uncorrected']:.3f}", fontsize=10)
    ax.set_xlabel('ITI_PTSD')
    ax.set_ylabel(f'SD Dwell %')

fig.suptitle('ABV (Raw Dwell Variability) vs ITI_PTSD — PTSD Group', fontsize=13, y=1.02)
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/scatterplots_family1_std_dwell.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/scatterplots_family1_std_dwell.png')

# %% [markdown]
# ## 8. Visualization 2 — Scatterplots (Family 2: std_delta_dwell_pct)

# %%
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
axes = axes.flatten()

for i, cat in enumerate(THREAT_CATEGORIES):
    ax = axes[i]
    col = f'std_delta_dwell_pct_{cat}'
    x = ptsd[IV_COL]
    y = ptsd[col]

    ax.scatter(x, y, color='#d9534f', alpha=0.7, s=50, edgecolors='white', linewidth=0.5)

    mask = x.notna() & y.notna()
    z = np.polyfit(x[mask], y[mask], 1)
    p_line = np.poly1d(z)
    x_range = np.linspace(x.min(), x.max(), 100)
    ax.plot(x_range, p_line(x_range), '--', color='#d9534f', alpha=0.6, linewidth=1.5)

    r = results_f2_df.iloc[i]
    ax.set_title(f"{cat}\n{r['Test']}: {r['Coefficient']:.3f}, p = {r['p_uncorrected']:.3f}", fontsize=10)
    ax.set_xlabel('ITI_PTSD')
    ax.set_ylabel(f'SD Delta Dwell %')

fig.suptitle('ABV (Delta Dwell Variability) vs ITI_PTSD — PTSD Group', fontsize=13, y=1.02)
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/scatterplots_family2_std_delta_dwell.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/scatterplots_family2_std_delta_dwell.png')

# %% [markdown]
# ## 9. Visualization 3 — Forest Plots

# %%
for family_label, res_df, fname in [
    ("Family 1: Raw Dwell Variability", results_f1_df, "forest_plot_family1.png"),
    ("Family 2: Delta Dwell Variability", results_f2_df, "forest_plot_family2.png"),
]:
    fig, ax = plt.subplots(figsize=(8, 5))
    y_pos = np.arange(len(res_df))

    for i, (_, r) in enumerate(res_df.iterrows()):
        color = '#d9534f' if r['Significant_BH'] else '#333333'
        ax.errorbar(r['Coefficient'], i,
                    xerr=[[r['Coefficient'] - r['CI_lo']], [r['CI_hi'] - r['Coefficient']]],
                    fmt='o', color=color, markersize=8, capsize=5, linewidth=2)

    ax.axvline(x=0, color='grey', linestyle='--', linewidth=1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(res_df['Category'])
    ax.set_xlabel('Correlation Coefficient (with 95% CI)')
    ax.set_title(f'Forest Plot — {family_label} × ITI_PTSD')
    ax.invert_yaxis()

    fig.savefig(f'{FIG_DIR}/{fname}', dpi=600, bbox_inches='tight')
    plt.close(fig)
    print(f'Saved: {FIG_DIR}/{fname}')

# %% [markdown]
# ## 10. Visualization 4 — Correlation Heatmap

# %%
all_dv_cols = FAMILY1_COLS + FAMILY2_COLS
all_coefs = list(results_f1_df['Coefficient']) + list(results_f2_df['Coefficient'])
all_labels = [c.replace('std_dwell_pct_', 'std_dwell_\n').replace('std_delta_dwell_pct_', 'std_delta_\n')
              for c in all_dv_cols]

heatmap_data = pd.DataFrame(
    np.array(all_coefs).reshape(-1, 1),
    index=all_labels,
    columns=[IV_COL],
)

fig, ax = plt.subplots(figsize=(4, 8))
sns.heatmap(heatmap_data, annot=True, fmt='.3f', cmap='RdBu_r', center=0,
            vmin=-1, vmax=1, linewidths=0.5, ax=ax, cbar_kws={'label': 'Correlation'})
ax.set_title(f'Correlation with {IV_COL}\n(PTSD group, n=17)')
fig.tight_layout()
fig.savefig(f'{FIG_DIR}/correlation_heatmap.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {FIG_DIR}/correlation_heatmap.png')
