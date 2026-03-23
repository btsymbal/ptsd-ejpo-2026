# %% [markdown]
# # Coefficient of Variation of Dwell Time Per Image Per Group
#
# **Goal**: Quantify within-group variability of dwell_pct for each image
# using CV (SD / Mean). High CV indicates inconsistent attentional response
# across participants within a group.
#
# **Thresholds**:
# - CV > 1.0 — **high** variability (SD exceeds the mean)
# - CV > 0.5 — **moderate-to-high** variability

# %%
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

os.chdir(Path(__file__).resolve().parent.parent)

CV_HIGH = 1.0
CV_MODERATE = 0.5
FIG_DIR = 'figures/images_analysis'
REPORT_DIR = 'reports/images_analysis'
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# %% [markdown]
# ## 1. Load Data

# %%
df = pd.read_csv('data/simplified/dataset_image_dwell_times_clean.csv')

ptsd = df[df['if_PTSD'] == 1]
no_ptsd = df[df['if_PTSD'] == 0]

n_ptsd = ptsd['session_id'].nunique()
n_no_ptsd = no_ptsd['session_id'].nunique()
image_ids = sorted(df['image_id'].unique())

print(f"Total observations: {len(df)}")
print(f"PTSD sessions:    n = {n_ptsd}")
print(f"No-PTSD sessions: n = {n_no_ptsd}")
print(f"Unique images:    {len(image_ids)}")

# %% [markdown]
# ## 2. Compute CV Per Image Per Group

# %%
grouped = df.groupby(['image_id', 'if_PTSD'])['dwell_pct'].agg(
    ['mean', 'std', 'count']
).reset_index()
grouped.columns = ['image_id', 'if_PTSD', 'Mean', 'SD', 'n']

grouped['CV'] = np.where(grouped['Mean'] > 0, grouped['SD'] / grouped['Mean'], np.nan)

cat_map = df.drop_duplicates('image_id').set_index('image_id')['category'].to_dict()
grouped['Category'] = grouped['image_id'].map(cat_map)
grouped['Group'] = grouped['if_PTSD'].map({1: 'PTSD', 0: 'No-PTSD'})

cv_df = grouped[['image_id', 'Category', 'Group', 'n', 'Mean', 'SD', 'CV']].copy()

print(f"CV table shape: {cv_df.shape}")
print(f"Images with zero mean (CV undefined): {cv_df['CV'].isna().sum()}")

# %% [markdown]
# ## 3. CV Summary Statistics

# %%
for group in ['PTSD', 'No-PTSD']:
    subset = cv_df[cv_df['Group'] == group]['CV'].dropna()
    print(f"\n{group} group CV distribution:")
    print(f"  Median: {subset.median():.4f}")
    print(f"  Mean:   {subset.mean():.4f}")
    print(f"  Min:    {subset.min():.4f}")
    print(f"  Max:    {subset.max():.4f}")
    print(f"  CV > {CV_HIGH} (high): {(subset > CV_HIGH).sum()}/{len(subset)}")
    print(f"  CV > {CV_MODERATE} (moderate-to-high): {(subset > CV_MODERATE).sum()}/{len(subset)}")

# %% [markdown]
# ## 4. PTSD Group — Images Sorted by CV (Descending)

# %%
ptsd_cv = (
    cv_df[cv_df['Group'] == 'PTSD']
    .sort_values('CV', ascending=False)
    .reset_index(drop=True)
)
ptsd_cv.index = ptsd_cv.index + 1
ptsd_cv.index.name = 'Rank'

ptsd_cv['Flag'] = np.where(
    ptsd_cv['CV'] > CV_HIGH, 'HIGH',
    np.where(ptsd_cv['CV'] > CV_MODERATE, 'moderate', '')
)

print("=== PTSD Group: Images by CV (descending) ===")
print(ptsd_cv.to_string(float_format='%.4f'))

# %% [markdown]
# ## 5. No-PTSD Group — Images Sorted by CV (Descending)

# %%
no_ptsd_cv = (
    cv_df[cv_df['Group'] == 'No-PTSD']
    .sort_values('CV', ascending=False)
    .reset_index(drop=True)
)
no_ptsd_cv.index = no_ptsd_cv.index + 1
no_ptsd_cv.index.name = 'Rank'

no_ptsd_cv['Flag'] = np.where(
    no_ptsd_cv['CV'] > CV_HIGH, 'HIGH',
    np.where(no_ptsd_cv['CV'] > CV_MODERATE, 'moderate', '')
)

print("=== No-PTSD Group: Images by CV (descending) ===")
print(no_ptsd_cv.to_string(float_format='%.4f'))

# %% [markdown]
# ## 6. Excluding Neutral Images
#
# Neutral images dominate the high-CV ranks because their lower mean dwell times
# inflate the SD/Mean ratio. The tables below exclude the "neutral" category to
# focus on stimulus-relevant images.

# %%
ptsd_cv_no_neutral = (
    ptsd_cv[ptsd_cv['Category'] != 'neutral']
    .sort_values('CV', ascending=False)
    .reset_index(drop=True)
)
ptsd_cv_no_neutral.index = ptsd_cv_no_neutral.index + 1
ptsd_cv_no_neutral.index.name = 'Rank'

print("=== PTSD Group (excl. neutral): Images by CV (descending) ===")
print(ptsd_cv_no_neutral.to_string(float_format='%.4f'))

# %%
no_ptsd_cv_no_neutral = (
    no_ptsd_cv[no_ptsd_cv['Category'] != 'neutral']
    .sort_values('CV', ascending=False)
    .reset_index(drop=True)
)
no_ptsd_cv_no_neutral.index = no_ptsd_cv_no_neutral.index + 1
no_ptsd_cv_no_neutral.index.name = 'Rank'

print("=== No-PTSD Group (excl. neutral): Images by CV (descending) ===")
print(no_ptsd_cv_no_neutral.to_string(float_format='%.4f'))

# %% [markdown]
# ## 7. Visualization

# %%
categories = sorted(cv_df['Category'].unique())
cmap = plt.colormaps.get_cmap('tab20').resampled(len(categories))
cat_colors = {cat: cmap(i) for i, cat in enumerate(categories)}

for group_label, group_data in [('PTSD', ptsd_cv), ('No-PTSD', no_ptsd_cv)]:
    data = group_data.sort_values('CV', ascending=True)
    fig_height = max(6, len(data) * 0.22)
    fig, ax = plt.subplots(figsize=(10, fig_height))

    colors = [cat_colors[c] for c in data['Category']]
    ax.barh(range(len(data)), data['CV'].values, color=colors, height=0.7)

    ax.axvline(x=CV_MODERATE, color='orange', linestyle='--', linewidth=1,
               label=f'CV = {CV_MODERATE} (moderate)')
    ax.axvline(x=CV_HIGH, color='red', linestyle='--', linewidth=1,
               label=f'CV = {CV_HIGH} (high)')

    ax.set_yticks(range(len(data)))
    ax.set_yticklabels(data['image_id'].values, fontsize=5)
    ax.set_xlabel('Coefficient of Variation (SD / Mean)')
    ax.set_title(f'CV of Dwell Time Per Image — {group_label} Group')

    handles = [plt.Rectangle((0, 0), 1, 1, color=cat_colors[c], label=c)
               for c in categories]
    handles += [
        plt.Line2D([0], [0], color='orange', linestyle='--', label=f'CV = {CV_MODERATE}'),
        plt.Line2D([0], [0], color='red', linestyle='--', label=f'CV = {CV_HIGH}'),
    ]
    ax.legend(handles=handles, loc='lower right', fontsize=7, title='Category')

    fname = f'{FIG_DIR}/cv_barplot_{group_label.lower().replace("-", "_")}.png'
    fig.savefig(fname, dpi=600, bbox_inches='tight')
    plt.close(fig)
    print(f'Saved: {fname}')

# %% [markdown]
# ## 8. Write Report

# %%
def format_cv_table(data, group_label):
    lines = [
        f'### {group_label} Group',
        '',
        '| Rank | Image ID | Category | n | Mean | SD | CV | Flag |',
        '|------|----------|----------|---|------|----|----|------|',
    ]
    for rank, (_, r) in enumerate(data.iterrows(), 1):
        lines.append(
            f"| {rank} | {r['image_id']} | {r['Category']} | {r['n']:.0f} | "
            f"{r['Mean']:.4f} | {r['SD']:.4f} | {r['CV']:.4f} | {r['Flag']} |"
        )
    lines.append('')
    return lines


report = [
    '# Coefficient of Variation of Dwell Time Per Image Per Group',
    '',
    '## Overview',
    '',
    f'- **Dataset**: dataset_image_dwell_times_clean.csv',
    f'- **Total observations**: {len(df)}',
    f'- **PTSD sessions**: {n_ptsd}',
    f'- **No-PTSD sessions**: {n_no_ptsd}',
    f'- **Unique images**: {len(image_ids)}',
    f'- **CV threshold (high)**: {CV_HIGH}',
    f'- **CV threshold (moderate-to-high)**: {CV_MODERATE}',
    '',
    '## CV Summary Statistics',
    '',
]

for group in ['PTSD', 'No-PTSD']:
    subset = cv_df[cv_df['Group'] == group]['CV'].dropna()
    report += [
        f'**{group}**: median = {subset.median():.4f}, mean = {subset.mean():.4f}, '
        f'min = {subset.min():.4f}, max = {subset.max():.4f}  ',
        f'High CV (> {CV_HIGH}): {(subset > CV_HIGH).sum()}/{len(subset)} images  ',
        f'Moderate-to-high CV (> {CV_MODERATE}): {(subset > CV_MODERATE).sum()}/{len(subset)} images',
        '',
    ]

report += ['## Images Sorted by CV (Descending)', '']
report += format_cv_table(ptsd_cv, 'PTSD')
report += format_cv_table(no_ptsd_cv, 'No-PTSD')

report += ['## Images Sorted by CV — Excluding Neutral (Descending)', '']
report += format_cv_table(ptsd_cv_no_neutral, 'PTSD (excl. neutral)')
report += format_cv_table(no_ptsd_cv_no_neutral, 'No-PTSD (excl. neutral)')

report += ['## High-CV Images (CV > 1.0)', '']
for group_label, data in [('PTSD', ptsd_cv), ('No-PTSD', no_ptsd_cv)]:
    high = data[data['CV'] > CV_HIGH]
    report.append(f'**{group_label}**: {len(high)} images with CV > {CV_HIGH}')
    report.append('')
    if len(high) > 0:
        report.append('| Image ID | Category | Mean | SD | CV |')
        report.append('|----------|----------|------|----|----|')
        for _, r in high.iterrows():
            report.append(
                f"| {r['image_id']} | {r['Category']} | "
                f"{r['Mean']:.4f} | {r['SD']:.4f} | {r['CV']:.4f} |"
            )
        report.append('')

report += ['## High-CV Images Excluding Neutral (CV > 1.0)', '']
for group_label, data in [('PTSD', ptsd_cv_no_neutral), ('No-PTSD', no_ptsd_cv_no_neutral)]:
    high = data[data['CV'] > CV_HIGH]
    report.append(f'**{group_label}**: {len(high)} images with CV > {CV_HIGH}')
    report.append('')
    if len(high) > 0:
        report.append('| Image ID | Category | Mean | SD | CV |')
        report.append('|----------|----------|------|----|----|')
        for _, r in high.iterrows():
            report.append(
                f"| {r['image_id']} | {r['Category']} | "
                f"{r['Mean']:.4f} | {r['SD']:.4f} | {r['CV']:.4f} |"
            )
        report.append('')

report += [
    '## Figures',
    '',
    f'- PTSD CV bar plot: `{FIG_DIR}/cv_barplot_ptsd.png`',
    f'- No-PTSD CV bar plot: `{FIG_DIR}/cv_barplot_no_ptsd.png`',
    '',
]

report_path = os.path.join(REPORT_DIR, 'cv_dwell_time_per_image_report.md')
with open(report_path, 'w') as f:
    f.write('\n'.join(report) + '\n')
print(f"Report written to {report_path}")
