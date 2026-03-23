# %% [markdown]
# # Per-Image Dwell Time: PTSD vs No-PTSD Group Comparisons
#
# **Goal**: Test whether dwell time percentage differs between PTSD and no-PTSD
# groups for each individual image (150 images), using the appropriate statistical
# test based on assumption checks.
#
# **Method**: Two-tailed group comparisons (PTSD vs no-PTSD) on dwell_pct for each
# image. Test selection follows normality and variance checks; p-values are
# corrected for multiple comparisons using Benjamini-Hochberg FDR.

# %%
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

os.chdir(Path(__file__).resolve().parent.parent)

ALPHA = 0.05
FIG_DIR = 'figures/images_analysis/group_comparisons_dwell_time'
REPORT_DIR = 'reports/images_analysis'
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# %% [markdown]
# ## 1. Load Data

# %%
df = pd.read_csv('data/simplified/dataset_image_dwell_times_clean.csv')

ptsd = df[df['if_PTSD'] == 1]
no_ptsd = df[df['if_PTSD'] == 0]

n_ptsd_sessions = ptsd['session_id'].nunique()
n_no_ptsd_sessions = no_ptsd['session_id'].nunique()
image_ids = sorted(df['image_id'].unique())

print(f"Total observations: {len(df)}")
print(f"PTSD sessions:    n = {n_ptsd_sessions}")
print(f"No-PTSD sessions: n = {n_no_ptsd_sessions}")
print(f"Unique images:    {len(image_ids)}")

# %% [markdown]
# ## 2. Descriptive Statistics

# %%
desc_rows = []
for img in image_ids:
    for group_label, group_df in [('PTSD', ptsd), ('No-PTSD', no_ptsd)]:
        vals = group_df[group_df['image_id'] == img]['dwell_pct'].dropna()
        desc_rows.append({
            'Image_ID': img,
            'Category': group_df[group_df['image_id'] == img]['category'].iloc[0] if len(vals) > 0 else '',
            'Group': group_label,
            'n': len(vals),
            'Mean': vals.mean(),
            'SD': vals.std(),
            'Median': vals.median(),
        })

desc_df = pd.DataFrame(desc_rows)
print("=== Descriptive Statistics (first 20 rows) ===")
print(desc_df.head(20).to_string(index=False, float_format='%.4f'))
print(f"... ({len(desc_df)} total rows)")

# %% [markdown]
# ## 3. Assumption Checks

# %%
assumption_rows = []
for img in image_ids:
    ptsd_vals = ptsd[ptsd['image_id'] == img]['dwell_pct'].dropna()
    no_ptsd_vals = no_ptsd[no_ptsd['image_id'] == img]['dwell_pct'].dropna()

    sw_ptsd = stats.shapiro(ptsd_vals)
    sw_no_ptsd = stats.shapiro(no_ptsd_vals)
    lev = stats.levene(ptsd_vals, no_ptsd_vals)

    assumption_rows.append({
        'Image_ID': img,
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
print("=== Assumption Checks (first 10 rows) ===")
print(assumptions_df.head(10).to_string(index=False, float_format='%.4f'))

n_both_normal = assumptions_df['Both_Normal'].sum()
n_equal_var = assumptions_df['Equal_Var'].sum()
print(f"\nBoth normal: {n_both_normal}/{len(assumptions_df)}")
print(f"Equal variance: {n_equal_var}/{len(assumptions_df)}")

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


# Build image_id → category lookup
img_category = df.drop_duplicates('image_id').set_index('image_id')['category'].to_dict()

results_rows = []
for i, img in enumerate(image_ids):
    ptsd_vals = ptsd[ptsd['image_id'] == img]['dwell_pct'].dropna()
    no_ptsd_vals = no_ptsd[no_ptsd['image_id'] == img]['dwell_pct'].dropna()
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
        df_val = nx + ny - 2
    elif both_normal and not equal_var:
        test_name = "Welch's t-test"
        stat_result = stats.ttest_ind(ptsd_vals, no_ptsd_vals, equal_var=False)
        test_stat, p_val = stat_result.statistic, stat_result.pvalue
        d = cohens_d(ptsd_vals, no_ptsd_vals)
        ci_lo, ci_hi = cohens_d_ci(d, nx, ny)
        es_name = "Cohen's d"
        es_val = d
        # Welch-Satterthwaite df
        s1, s2 = ptsd_vals.std(ddof=1), no_ptsd_vals.std(ddof=1)
        num = (s1**2 / nx + s2**2 / ny)**2
        denom = (s1**2 / nx)**2 / (nx - 1) + (s2**2 / ny)**2 / (ny - 1)
        df_val = num / denom
    else:
        test_name = "Mann-Whitney U"
        stat_result = stats.mannwhitneyu(ptsd_vals, no_ptsd_vals, alternative='two-sided')
        test_stat, p_val = stat_result.statistic, stat_result.pvalue
        r = rank_biserial_r(test_stat, nx, ny)
        ci_lo, ci_hi = rank_biserial_ci(r, nx, ny)
        # Negate so positive = PTSD higher (same convention as Cohen's d)
        r = -r
        ci_lo, ci_hi = -ci_hi, -ci_lo
        es_name = "rank-biserial r"
        es_val = r
        df_val = np.nan

    results_rows.append({
        'Image_ID': img,
        'Category': img_category.get(img, ''),
        'Test': test_name,
        'Statistic': test_stat,
        'df': df_val,
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

print("=== Results with BH Correction (first 20 rows) ===")
display_cols = ['Image_ID', 'Category', 'Test', 'Statistic', 'df', 'p_uncorrected', 'p_BH',
                'Effect_Size_Type', 'Effect_Size', 'CI_lo', 'CI_hi', 'Significant_BH']
print(results_df[display_cols].head(20).to_string(index=False, float_format='%.4f'))

# %% [markdown]
# ## 6. Results Summary

# %%
n_sig = results_df['Significant_BH'].sum()
n_sig_uncorr = (results_df['p_uncorrected'] < ALPHA).sum()
n_total = len(results_df)

print("\n" + "=" * 90)
print("RESULTS SUMMARY — Per-Image Dwell Time × PTSD Group")
print("=" * 90)
print(f"\nTotal images tested: {n_total}")
print(f"Significant before correction (p < {ALPHA}): {n_sig_uncorr}")
print(f"Significant after BH correction: {n_sig}")

test_counts = results_df['Test'].value_counts()
print(f"\nTests used:")
for test, count in test_counts.items():
    print(f"  {test}: {count}")

# --- Significant before correction ---
if n_sig_uncorr > 0:
    print(f"\n--- Significant before correction (p_uncorrected < {ALPHA}) ---")
    sig_uncorr_df = results_df[results_df['p_uncorrected'] < ALPHA].sort_values('p_uncorrected')
    for _, r in sig_uncorr_df.iterrows():
        print(f"\n  {r['Image_ID']} ({r['Category']}):")
        if not np.isnan(r['df']):
            print(f"    Test: {r['Test']}, stat = {r['Statistic']:.4f}, df = {r['df']:.1f}")
        else:
            print(f"    Test: {r['Test']}, U = {r['Statistic']:.4f}")
        print(f"    p (uncorrected) = {r['p_uncorrected']:.4f}, p (BH) = {r['p_BH']:.4f}")
        print(f"    {r['Effect_Size_Type']} = {r['Effect_Size']:.4f}, 95% CI [{r['CI_lo']:.4f}, {r['CI_hi']:.4f}]")
else:
    print(f"\nNo images significant even before correction.")

# --- Significant after BH correction ---
if n_sig > 0:
    print(f"\n--- Significant after BH correction (p_BH < {ALPHA}) ---")
    sig_df = results_df[results_df['Significant_BH']].sort_values('p_BH')
    for _, r in sig_df.iterrows():
        print(f"\n  {r['Image_ID']} ({r['Category']}):")
        if not np.isnan(r['df']):
            print(f"    Test: {r['Test']}, stat = {r['Statistic']:.4f}, df = {r['df']:.1f}")
        else:
            print(f"    Test: {r['Test']}, U = {r['Statistic']:.4f}")
        print(f"    p (uncorrected) = {r['p_uncorrected']:.4f}, p (BH) = {r['p_BH']:.4f}")
        print(f"    {r['Effect_Size_Type']} = {r['Effect_Size']:.4f}, 95% CI [{r['CI_lo']:.4f}, {r['CI_hi']:.4f}]")
else:
    print("\nNo images showed significant group differences after BH correction.")

print("=" * 90)

# %% [markdown]
# ## 6b. Expected Directions & Unexpected-Direction Images
#
# Expected direction of effect size (positive = PTSD higher dwell time):
#
# | Category          | Expected sign | Rationale                                          |
# |-------------------|---------------|----------------------------------------------------|
# | angry_face        | positive      | hypervigilance to threat                            |
# | anxiety_inducing  | positive      | hypervigilance to potential (hidden) threat          |
# | combat_vehicles   | positive      | emotionally driven memories                         |
# | happy_event       | negative      | anhedonistic subtype                                |
# | happy_face        | negative      | anhedonistic subtype                                |
# | neutral           | —             | no consistent pattern (paired with diverse images)  |
# | neutral_face      | negative      | hypervigilance to threat (opposite image)            |
# | sad_face          | positive      | anhedonistic subtype (opposite image)               |
# | sleep_related     | —             | no strong theoretical expectation                   |
# | soldiers          | positive      | hypervigilance to threat                            |
# | warfare           | positive      | hypervigilance to threat                            |

# %%
# Expected sign of effect size per category (positive = PTSD higher dwell time).
# None = no directional expectation.
EXPECTED_SIGN = {
    'angry_face': 'positive',
    'anxiety_inducing': 'positive',
    'combat_vehicles': 'positive',
    'happy_event': 'negative',
    'happy_face': 'negative',
    'neutral': None,
    'neutral_face': 'negative',
    'sad_face': 'positive',
    'sleep_related': None,
    'soldiers': 'positive',
    'warfare': 'positive',
}

EXPECTED_RATIONALE = {
    'angry_face': 'hypervigilance to threat',
    'anxiety_inducing': 'hypervigilance to potential (hidden) threat',
    'combat_vehicles': 'emotionally driven memories',
    'happy_event': 'anhedonistic subtype',
    'happy_face': 'anhedonistic subtype',
    'neutral': 'no consistent pattern (paired with diverse images)',
    'neutral_face': 'hypervigilance to threat (opposite image)',
    'sad_face': 'anhedonistic subtype (opposite image)',
    'sleep_related': 'no strong theoretical expectation',
    'soldiers': 'hypervigilance to threat',
    'warfare': 'hypervigilance to threat',
}

unexpected_rows = []
for _, r in results_df.iterrows():
    expected = EXPECTED_SIGN.get(r['Category'])
    if expected is None:
        continue
    es = r['Effect_Size']
    if (expected == 'positive' and es < 0) or (expected == 'negative' and es > 0):
        unexpected_rows.append(r)

unexpected_df = pd.DataFrame(unexpected_rows)

print(f"\n{'=' * 90}")
print("EXPECTED vs OBSERVED DIRECTION OF EFFECT")
print("=" * 90)
print("\nExpected directions (positive = PTSD higher dwell time):")
for cat, sign in sorted(EXPECTED_SIGN.items()):
    sign_str = sign if sign else '—'
    print(f"  {cat:20s} {sign_str:>10s}   ({EXPECTED_RATIONALE[cat]})")

n_directional = len(results_df[results_df['Category'].map(EXPECTED_SIGN).notna()])
n_unexpected = len(unexpected_df)
print(f"\nImages with directional expectation: {n_directional}")
print(f"Images with unexpected direction:    {n_unexpected}/{n_directional}")

if n_unexpected > 0:
    print(f"\n--- Images with unexpected effect size direction ---")
    for _, r in unexpected_df.sort_values('p_uncorrected').iterrows():
        expected = EXPECTED_SIGN[r['Category']]
        observed = 'positive' if r['Effect_Size'] > 0 else 'negative'
        print(f"\n  {r['Image_ID']} ({r['Category']}):")
        print(f"    Expected: {expected}, Observed: {observed}")
        print(f"    {r['Effect_Size_Type']} = {r['Effect_Size']:.4f}, 95% CI [{r['CI_lo']:.4f}, {r['CI_hi']:.4f}]")
        print(f"    p (uncorrected) = {r['p_uncorrected']:.4f}")

print("=" * 90)

# %% [markdown]
# ## 7. Visualization — Forest Plots of Effect Sizes (per category)

# %%
categories = sorted(results_df['Category'].unique())

MARKER_D = 'o'       # circle for Cohen's d
MARKER_R = 'D'       # diamond for rank-biserial r

for cat in categories:
    cat_data = results_df[results_df['Category'] == cat].sort_values('Effect_Size').reset_index(drop=True)
    n_cat = len(cat_data)
    n_sig_cat = cat_data['Significant_BH'].sum()
    n_sig_uncorr_cat = (cat_data['p_uncorrected'] < ALPHA).sum()
    fig_height = max(4, n_cat * 0.32)

    fig, ax = plt.subplots(figsize=(10, fig_height))
    y_pos = np.arange(n_cat)

    for i, (_, r) in enumerate(cat_data.iterrows()):
        if r['Significant_BH']:
            color = '#d9534f'
        elif r['p_uncorrected'] < ALPHA:
            color = '#f0ad4e'
        else:
            color = '#333333'
        marker = MARKER_D if r['Effect_Size_Type'] == "Cohen's d" else MARKER_R
        ax.errorbar(r['Effect_Size'], i,
                    xerr=[[r['Effect_Size'] - r['CI_lo']], [r['CI_hi'] - r['Effect_Size']]],
                    fmt=marker, color=color, markersize=5, capsize=3, linewidth=1.2)

    ax.axvline(x=0, color='grey', linestyle='--', linewidth=1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(cat_data['Image_ID'].values, fontsize=7)
    ax.set_xlabel('Effect Size (with 95% CI)\n← No-PTSD higher dwell time    |    PTSD higher dwell time →')
    ax.set_title(f'Forest Plot — {cat} (PTSD vs No-PTSD)')

    handles = [
        plt.Line2D([0], [0], marker=MARKER_D, color='grey', linestyle='None',
                   markersize=6, label="Cohen's d (parametric)"),
        plt.Line2D([0], [0], marker=MARKER_R, color='grey', linestyle='None',
                   markersize=6, label='rank-biserial r (non-parametric)'),
        plt.Line2D([0], [0], marker='s', color='#d9534f', linestyle='None',
                   markersize=6, label=f'Significant BH (n={n_sig_cat})'),
        plt.Line2D([0], [0], marker='s', color='#f0ad4e', linestyle='None',
                   markersize=6, label=f'Significant uncorrected (n={n_sig_uncorr_cat})'),
        plt.Line2D([0], [0], marker='s', color='#333333', linestyle='None',
                   markersize=6, label=f'Not significant (n={n_cat - n_sig_uncorr_cat})'),
    ]
    ax.legend(handles=handles, loc='lower right', fontsize=7)

    fname = f'{FIG_DIR}/forest_plot_{cat}.png'
    fig.savefig(fname, dpi=600, bbox_inches='tight')
    plt.close(fig)
    print(f'Saved: {fname}')

# %% [markdown]
# ## 8. Write Report

# %%
report_lines = [
    '# Per-Image Dwell Time: PTSD vs No-PTSD Group Comparisons',
    '',
    '## Overview',
    '',
    f'- **Total images tested**: {n_total}',
    f'- **PTSD sessions**: {n_ptsd_sessions}',
    f'- **No-PTSD sessions**: {n_no_ptsd_sessions}',
    f'- **Alpha**: {ALPHA}',
    f'- **Multiple comparison correction**: Benjamini-Hochberg FDR',
    '',
    '## Test Selection Summary',
    '',
]
for test, count in test_counts.items():
    report_lines.append(f'- {test}: {count} images')

report_lines += [
    '',
    '## Results',
    '',
    f'- **Significant before correction (p < {ALPHA})**: {n_sig_uncorr}/{n_total}',
    f'- **Significant after BH correction**: {n_sig}/{n_total}',
    '',
]

# --- Significant before correction ---
report_lines.append('### Significant Before Correction')
report_lines.append('')
if n_sig_uncorr > 0:
    report_lines.append('| Image ID | Category | Test | Statistic | df | p (uncorr) | p (BH) | Effect Size Type | Effect Size | 95% CI |')
    report_lines.append('|----------|----------|------|-----------|----|------------|--------|------------------|-------------|--------|')
    sig_uncorr_df = results_df[results_df['p_uncorrected'] < ALPHA].sort_values('p_uncorrected')
    for _, r in sig_uncorr_df.iterrows():
        df_str = f"{r['df']:.1f}" if not np.isnan(r['df']) else '—'
        report_lines.append(
            f"| {r['Image_ID']} | {r['Category']} | {r['Test']} | {r['Statistic']:.4f} | {df_str} | {r['p_uncorrected']:.4f} | {r['p_BH']:.4f} | {r['Effect_Size_Type']} | {r['Effect_Size']:.4f} | [{r['CI_lo']:.4f}, {r['CI_hi']:.4f}] |"
        )
    report_lines.append('')
else:
    report_lines.append('No images significant even before correction.')
    report_lines.append('')

# --- Significant after BH correction ---
report_lines.append('### Significant After BH Correction')
report_lines.append('')
if n_sig > 0:
    report_lines.append('| Image ID | Category | Test | Statistic | df | p (uncorr) | p (BH) | Effect Size Type | Effect Size | 95% CI |')
    report_lines.append('|----------|----------|------|-----------|----|------------|--------|------------------|-------------|--------|')
    sig_df = results_df[results_df['Significant_BH']].sort_values('p_BH')
    for _, r in sig_df.iterrows():
        df_str = f"{r['df']:.1f}" if not np.isnan(r['df']) else '—'
        report_lines.append(
            f"| {r['Image_ID']} | {r['Category']} | {r['Test']} | {r['Statistic']:.4f} | {df_str} | {r['p_uncorrected']:.4f} | {r['p_BH']:.4f} | {r['Effect_Size_Type']} | {r['Effect_Size']:.4f} | [{r['CI_lo']:.4f}, {r['CI_hi']:.4f}] |"
        )
    report_lines.append('')
else:
    report_lines.append('No images showed significant group differences after BH correction.')
    report_lines.append('')

# --- Full results table ---
report_lines += [
    '### Full Results Table',
    '',
    '| Image ID | Category | Test | Statistic | df | p (uncorr) | p (BH) | Significant (BH) | Effect Size Type | Effect Size | 95% CI |',
    '|----------|----------|------|-----------|----|------------|--------|------------------|------------------|-------------|--------|',
]
for _, r in results_df.sort_values('p_BH').iterrows():
    df_str = f"{r['df']:.1f}" if not np.isnan(r['df']) else '—'
    sig_str = 'Yes' if r['Significant_BH'] else 'No'
    report_lines.append(
        f"| {r['Image_ID']} | {r['Category']} | {r['Test']} | {r['Statistic']:.4f} | {df_str} | {r['p_uncorrected']:.4f} | {r['p_BH']:.4f} | {sig_str} | {r['Effect_Size_Type']} | {r['Effect_Size']:.4f} | [{r['CI_lo']:.4f}, {r['CI_hi']:.4f}] |"
    )

# --- Expected directions & unexpected images ---
report_lines += [
    '',
    '## Expected vs Observed Direction of Effect',
    '',
    'Expected direction of effect size (positive = PTSD higher dwell time):',
    '',
    '| Category | Expected sign | Rationale |',
    '|----------|---------------|-----------|',
]
for cat in sorted(EXPECTED_SIGN.keys()):
    sign = EXPECTED_SIGN[cat] if EXPECTED_SIGN[cat] else '—'
    report_lines.append(f'| {cat} | {sign} | {EXPECTED_RATIONALE[cat]} |')

report_lines += [
    '',
    f'Images with directional expectation: {n_directional}',
    f'Images with **unexpected direction**: {n_unexpected}/{n_directional}',
    '',
]

if n_unexpected > 0:
    report_lines.append('### Images With Unexpected Effect Size Direction')
    report_lines.append('')
    report_lines.append('| Image ID | Category | Expected | Observed | Effect Size Type | Effect Size | 95% CI | p (uncorr) |')
    report_lines.append('|----------|----------|----------|----------|------------------|-------------|--------|------------|')
    for _, r in unexpected_df.sort_values('p_uncorrected').iterrows():
        expected = EXPECTED_SIGN[r['Category']]
        observed = 'positive' if r['Effect_Size'] > 0 else 'negative'
        report_lines.append(
            f"| {r['Image_ID']} | {r['Category']} | {expected} | {observed} | {r['Effect_Size_Type']} | {r['Effect_Size']:.4f} | [{r['CI_lo']:.4f}, {r['CI_hi']:.4f}] | {r['p_uncorrected']:.4f} |"
        )
    report_lines.append('')
else:
    report_lines.append('No images showed an unexpected direction of effect.')
    report_lines.append('')

report_lines += [
    '## Figures',
    '',
]
for cat in categories:
    report_lines.append(f'- Forest plot ({cat}): `{FIG_DIR}/forest_plot_{cat}.png`')
report_lines.append('')

report_path = os.path.join(REPORT_DIR, 'dwell_time_group_comparisons_report.md')
with open(report_path, 'w') as f:
    f.write('\n'.join(report_lines) + '\n')
print(f"Report written to {report_path}")
