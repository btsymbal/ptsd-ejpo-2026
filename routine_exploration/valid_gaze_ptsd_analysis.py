# %% [markdown]
# # Valid Gaze Proportion & PTSD Analysis
#
# This notebook investigates the relationship between PTSD status and eye-tracking
# data quality (valid gaze proportion) across 30 sessions.
#
# **Analyses:**
# 1. Group comparison of mean valid gaze proportion (PTSD vs no-PTSD)
# 2. Correlation between ITI_PTSD severity and mean valid gaze proportion (PTSD group only)
# 3. Correlation between slide number and mean valid gaze proportion (all sessions)
# 4. Slide-number correlation by PTSD group, with line plot

# %%
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

os.chdir(Path(__file__).resolve().parent.parent)

# %% [markdown]
# ## Dataset Formation

# %%
gaze_dir = Path('data/output/valid_gaze_proportion')
gaze_files = sorted(gaze_dir.glob('*.csv'))

frames = []
for f in gaze_files:
    session_id = f.stem
    df = pd.read_csv(f)
    df['session_id'] = session_id
    frames.append(df)

all_slides_df = pd.concat(frames, ignore_index=True)

session_means = (
    all_slides_df
    .groupby('session_id')['valid_gaze_proportion']
    .mean()
    .reset_index()
    .rename(columns={'valid_gaze_proportion': 'mean_valid_gaze_proportion'})
)

metadata = pd.read_csv('data/simplified/dataset_merged_1_and_2.csv',
                        usecols=['sessions', 'if_PTSD', 'ITI_PTSD'])

merged = session_means.merge(metadata, left_on='session_id', right_on='sessions', how='left')

assert merged['if_PTSD'].notna().all(), 'Some sessions did not match metadata!'

merged = merged.drop(columns=['sessions'])

# Attach PTSD info to per-slide data as well
all_slides_df = all_slides_df.merge(
    merged[['session_id', 'if_PTSD', 'ITI_PTSD']], on='session_id', how='left'
)

print(f'Total sessions: {len(merged)}')
print(f'PTSD group: {(merged["if_PTSD"] == 1).sum()}')
print(f'No-PTSD group: {(merged["if_PTSD"] == 0).sum()}')
print(f'\nPer-slide rows: {len(all_slides_df)}')

# %%
os.makedirs('data/output/valid_gaze_proportion/merged', exist_ok=True)
merged.to_csv('data/output/valid_gaze_proportion/merged/valid_gaze_ptsd_merged.csv', index=False)
print('Saved: data/output/valid_gaze_proportion/merged/valid_gaze_ptsd_merged.csv')

# %% [markdown]
# ## Analysis 1: Group Comparison (PTSD vs No-PTSD)

# %%
ptsd_vals = merged.loc[merged['if_PTSD'] == 1, 'mean_valid_gaze_proportion']
no_ptsd_vals = merged.loc[merged['if_PTSD'] == 0, 'mean_valid_gaze_proportion']

print('=== Descriptive Statistics ===')
for label, vals in [('PTSD', ptsd_vals), ('No-PTSD', no_ptsd_vals)]:
    print(f'{label}: n={len(vals)}, mean={vals.mean():.4f}, std={vals.std():.4f}, median={vals.median():.4f}')

shapiro_ptsd = stats.shapiro(ptsd_vals)
shapiro_no_ptsd = stats.shapiro(no_ptsd_vals)
print(f'\nShapiro-Wilk PTSD:    W={shapiro_ptsd.statistic:.4f}, p={shapiro_ptsd.pvalue:.4f}')
print(f'Shapiro-Wilk No-PTSD: W={shapiro_no_ptsd.statistic:.4f}, p={shapiro_no_ptsd.pvalue:.4f}')

both_normal = shapiro_ptsd.pvalue > 0.05 and shapiro_no_ptsd.pvalue > 0.05

levene_result = stats.levene(ptsd_vals, no_ptsd_vals)
print(f'Levene test: F={levene_result.statistic:.4f}, p={levene_result.pvalue:.4f}')

if both_normal:
    if levene_result.pvalue > 0.05:
        test_name = "Student's t-test"
        stat, p = stats.ttest_ind(ptsd_vals, no_ptsd_vals, equal_var=True)
    else:
        test_name = "Welch's t-test"
        stat, p = stats.ttest_ind(ptsd_vals, no_ptsd_vals, equal_var=False)
else:
    test_name = 'Mann-Whitney U'
    stat, p = stats.mannwhitneyu(ptsd_vals, no_ptsd_vals, alternative='two-sided')

sig = 'significant' if p < 0.05 else 'not significant'
print(f'\n{test_name}: statistic={stat:.4f}, p={p:.4f} ({sig})')

# %% [markdown]
# ## Analysis 2: Correlation — ITI_PTSD vs Mean Valid Gaze (PTSD only)

# %%
ptsd_only = merged[merged['if_PTSD'] == 1].copy()
iti_vals = ptsd_only['ITI_PTSD']
gaze_vals = ptsd_only['mean_valid_gaze_proportion']
n = len(ptsd_only)

shapiro_iti = stats.shapiro(iti_vals)
shapiro_gaze = stats.shapiro(gaze_vals)
print(f'Shapiro-Wilk ITI_PTSD:    W={shapiro_iti.statistic:.4f}, p={shapiro_iti.pvalue:.4f}')
print(f'Shapiro-Wilk mean gaze:   W={shapiro_gaze.statistic:.4f}, p={shapiro_gaze.pvalue:.4f}')

both_normal_corr = shapiro_iti.pvalue > 0.05 and shapiro_gaze.pvalue > 0.05
severely_non_normal = shapiro_iti.pvalue < 0.01 or shapiro_gaze.pvalue < 0.01

if both_normal_corr:
    corr_name = 'Pearson'
    r, p = stats.pearsonr(iti_vals, gaze_vals)
elif not severely_non_normal and n >= 20:
    corr_name = 'Spearman'
    r, p = stats.spearmanr(iti_vals, gaze_vals)
else:
    corr_name = "Kendall's tau"
    r, p = stats.kendalltau(iti_vals, gaze_vals)

sig = 'significant' if p < 0.05 else 'not significant'
print(f'\n{corr_name} correlation: r={r:.4f}, p={p:.4f} ({sig})')

# %% [markdown]
# ## Analysis 3: Slide-Number Correlation (All Sessions)

# %%
slide_means = (
    all_slides_df
    .groupby('slide_number')['valid_gaze_proportion']
    .mean()
    .reset_index()
    .sort_values('slide_number')
)

shapiro_slide = stats.shapiro(slide_means['valid_gaze_proportion'])
print(f'Shapiro-Wilk (75 slide means): W={shapiro_slide.statistic:.4f}, p={shapiro_slide.pvalue:.4f}')

if shapiro_slide.pvalue > 0.05:
    corr_name = 'Pearson'
    r, p = stats.pearsonr(slide_means['slide_number'], slide_means['valid_gaze_proportion'])
else:
    corr_name = 'Spearman'
    r, p = stats.spearmanr(slide_means['slide_number'], slide_means['valid_gaze_proportion'])

sig = 'significant' if p < 0.05 else 'not significant'
print(f'{corr_name} correlation (slide number vs mean gaze): r={r:.4f}, p={p:.4f} ({sig})')

# %%
# Scatter + regression fit for all sessions
x = slide_means['slide_number'].values
y = slide_means['valid_gaze_proportion'].values
slope, intercept = np.polyfit(x, y, 1)

fig, ax = plt.subplots(figsize=(12, 5))
ax.scatter(x, y, color='black', s=20, alpha=0.6, label='Slide means')
ax.plot(x, slope * x + intercept, color='black', linewidth=2,
        label=f'Fit (r={r:.3f}, p<0.001)' if p < 0.001 else f'Fit (r={r:.3f}, p={p:.3f})')
ax.set_xlabel('Slide Number')
ax.set_ylabel('Mean Valid Gaze Proportion')
ax.set_title('Gaze Quality vs Slide Number (All Sessions)')
ax.legend()
ax.set_xlim(1, 75)

os.makedirs('figures/valid_gaze_ptsd_analysis', exist_ok=True)
fig.savefig('figures/valid_gaze_ptsd_analysis/gaze_vs_slide_regression_all.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print('Saved: figures/valid_gaze_ptsd_analysis/gaze_vs_slide_regression_all.png')

# %%
# Slide-number correlation by PTSD group
for group_val, group_label in [(1, 'PTSD'), (0, 'No-PTSD')]:
    group_slide_means = (
        all_slides_df[all_slides_df['if_PTSD'] == group_val]
        .groupby('slide_number')['valid_gaze_proportion']
        .mean()
        .reset_index()
        .sort_values('slide_number')
    )
    sw = stats.shapiro(group_slide_means['valid_gaze_proportion'])
    if sw.pvalue > 0.05:
        cname = 'Pearson'
        r, p = stats.pearsonr(group_slide_means['slide_number'],
                              group_slide_means['valid_gaze_proportion'])
    else:
        cname = 'Spearman'
        r, p = stats.spearmanr(group_slide_means['slide_number'],
                               group_slide_means['valid_gaze_proportion'])
    sig = 'significant' if p < 0.05 else 'not significant'
    print(f'{group_label}: {cname} r={r:.4f}, p={p:.4f} ({sig})')

# %%
# Line plot: mean valid gaze proportion by slide number
slide_all = (
    all_slides_df.groupby('slide_number')['valid_gaze_proportion'].mean()
    .reset_index().sort_values('slide_number')
)
slide_ptsd = (
    all_slides_df[all_slides_df['if_PTSD'] == 1]
    .groupby('slide_number')['valid_gaze_proportion'].mean()
    .reset_index().sort_values('slide_number')
)
slide_no_ptsd = (
    all_slides_df[all_slides_df['if_PTSD'] == 0]
    .groupby('slide_number')['valid_gaze_proportion'].mean()
    .reset_index().sort_values('slide_number')
)

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(slide_all['slide_number'], slide_all['valid_gaze_proportion'],
        color='black', label='All', linewidth=1.5)
ax.plot(slide_ptsd['slide_number'], slide_ptsd['valid_gaze_proportion'],
        color='red', label='PTSD', linewidth=1.2, alpha=0.8)
ax.plot(slide_no_ptsd['slide_number'], slide_no_ptsd['valid_gaze_proportion'],
        color='blue', label='No-PTSD', linewidth=1.2, alpha=0.8)

# Regression fit lines
for src, color, label in [(slide_all, 'black', 'All'),
                          (slide_ptsd, 'red', 'PTSD'),
                          (slide_no_ptsd, 'blue', 'No-PTSD')]:
    xv = src['slide_number'].values
    yv = src['valid_gaze_proportion'].values
    sl, ic = np.polyfit(xv, yv, 1)
    ax.plot(xv, sl * xv + ic, color=color, linewidth=2, linestyle='--', alpha=0.7,
            label=f'{label} fit')

ax.set_xlabel('Slide Number')
ax.set_ylabel('Mean Valid Gaze Proportion')
ax.set_title('Valid Gaze Proportion by Slide Number')
ax.legend()
ax.set_xlim(1, 75)

os.makedirs('figures/valid_gaze_ptsd_analysis', exist_ok=True)
fig.savefig('figures/valid_gaze_ptsd_analysis/gaze_vs_slide_number.png', dpi=600, bbox_inches='tight')
plt.close(fig)
print('Saved: figures/valid_gaze_ptsd_analysis/gaze_vs_slide_number.png')
