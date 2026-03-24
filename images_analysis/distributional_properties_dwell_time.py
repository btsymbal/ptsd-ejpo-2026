# %% [markdown]
# # Distributional Properties of Dwell Time Per Image (All Participants)
#
# **Goal**: Identify images whose dwell_pct distribution across all participants
# (PTSD and no-PTSD combined) is highly skewed and/or has low CV, indicating
# uniform participant responses that reduce discriminative power between groups.
#
# **Metrics**: skewness, excess kurtosis, coefficient of variation (CV = SD/Mean)
#
# **Flags**:
# - |skewness| > 1.0 — highly skewed distribution
# - CV < 0.5 — low variability relative to mean (uniform responses)
# - Both — **problematic**: stereotyped, lopsided response pattern

# %%
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

os.chdir(Path(__file__).resolve().parent.parent)

SKEW_THRESHOLD = 1.0
CV_LOW_THRESHOLD = 0.5
FIG_DIR = 'figures/images_analysis/distributional_properties'
REPORT_DIR = 'reports/images_analysis'
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# %% [markdown]
# ## 1. Load Data

# %%
df = pd.read_csv('data/simplified/dataset_image_dwell_times_clean.csv')

n_sessions = df['session_id'].nunique()
image_ids = sorted(df['image_id'].unique())
categories = sorted(df['category'].unique())
cat_map = df.drop_duplicates('image_id').set_index('image_id')['category'].to_dict()

print(f"Total observations: {len(df)}")
print(f"Sessions:           {n_sessions}")
print(f"Unique images:      {len(image_ids)}")
print(f"Categories:         {len(categories)}")

# %% [markdown]
# ## 2. Compute Per-Image Distributional Statistics

# %%
rows = []
for img in image_ids:
    vals = df.loc[df['image_id'] == img, 'dwell_pct'].dropna()
    rows.append({
        'image_id': img,
        'category': cat_map[img],
        'n': len(vals),
        'mean': vals.mean(),
        'SD': vals.std(),
        'median': vals.median(),
        'skewness': stats.skew(vals, bias=False),
        'kurtosis': stats.kurtosis(vals, bias=False),
        'min': vals.min(),
        'max': vals.max(),
    })

stats_df = pd.DataFrame(rows)
stats_df['CV'] = np.where(stats_df['mean'] > 0, stats_df['SD'] / stats_df['mean'], np.nan)
stats_df['abs_skewness'] = stats_df['skewness'].abs()

print(f"Stats table: {stats_df.shape[0]} images")
print(f"Images with zero mean (CV undefined): {stats_df['CV'].isna().sum()}")

# %% [markdown]
# ## 3. Summary of Distributional Statistics

# %%
print("=== Distribution of per-image metrics across all 150 images ===\n")
print(stats_df[['mean', 'SD', 'CV', 'skewness', 'kurtosis']].describe()
      .to_string(float_format='%.4f'))

print("\n\n=== Per-category averages ===\n")
cat_summary = (
    stats_df.groupby('category')[['mean', 'SD', 'CV', 'skewness', 'kurtosis']]
    .mean()
    .sort_values('skewness', ascending=False)
)
print(cat_summary.to_string(float_format='%.4f'))

# %% [markdown]
# ## 4. Flag Problematic Images

# %%
stats_df['flag_skewed'] = stats_df['abs_skewness'] > SKEW_THRESHOLD
stats_df['flag_low_cv'] = stats_df['CV'] < CV_LOW_THRESHOLD
stats_df['flag_problematic'] = stats_df['flag_skewed'] & stats_df['flag_low_cv']

n_skewed = stats_df['flag_skewed'].sum()
n_low_cv = stats_df['flag_low_cv'].sum()
n_problematic = stats_df['flag_problematic'].sum()

print(f"Highly skewed (|skew| > {SKEW_THRESHOLD}):  {n_skewed}/{len(stats_df)}")
print(f"Low CV (CV < {CV_LOW_THRESHOLD}):              {n_low_cv}/{len(stats_df)}")
print(f"Problematic (both):                {n_problematic}/{len(stats_df)}")

print("\n=== Flag counts per category ===\n")
flag_by_cat = (
    stats_df.groupby('category')[['flag_skewed', 'flag_low_cv', 'flag_problematic']]
    .sum()
    .astype(int)
)
flag_by_cat.columns = ['Skewed', 'Low CV', 'Problematic']
print(flag_by_cat.to_string())

# %% [markdown]
# ## 5. Highly Skewed Images (|skewness| > 1.0)

# %%
skewed_df = (
    stats_df[stats_df['flag_skewed']]
    .sort_values('abs_skewness', ascending=False)
    .reset_index(drop=True)
)
skewed_df.index = skewed_df.index + 1
skewed_df.index.name = 'Rank'

pos_skew = (skewed_df['skewness'] > 0).sum()
neg_skew = (skewed_df['skewness'] < 0).sum()
print(f"Positively skewed (right-tail): {pos_skew}")
print(f"Negatively skewed (left-tail):  {neg_skew}\n")

print(skewed_df[['image_id', 'category', 'n', 'mean', 'SD', 'CV', 'skewness', 'kurtosis']]
      .to_string(float_format='%.4f'))

# %% [markdown]
# ## 6. Low-CV Images (CV < 0.5)

# %%
low_cv_df = (
    stats_df[stats_df['flag_low_cv']]
    .sort_values('CV', ascending=True)
    .reset_index(drop=True)
)
low_cv_df.index = low_cv_df.index + 1
low_cv_df.index.name = 'Rank'

print(f"Images with CV < {CV_LOW_THRESHOLD}: {len(low_cv_df)}\n")
print(low_cv_df[['image_id', 'category', 'n', 'mean', 'SD', 'CV', 'skewness', 'kurtosis']]
      .to_string(float_format='%.4f'))

# %% [markdown]
# ## 7. Problematic Images (Skewed AND Low CV)

# %%
prob_df = (
    stats_df[stats_df['flag_problematic']]
    .sort_values('CV', ascending=True)
    .reset_index(drop=True)
)
prob_df.index = prob_df.index + 1
prob_df.index.name = 'Rank'

print(f"Problematic images: {len(prob_df)}\n")
if len(prob_df) > 0:
    print(prob_df[['image_id', 'category', 'n', 'mean', 'SD', 'CV', 'skewness', 'kurtosis']]
          .to_string(float_format='%.4f'))
else:
    print("No images meet both criteria.")

# %% [markdown]
# ## 8. Excluding Neutral Images

# %%
no_neutral = stats_df[stats_df['category'] != 'neutral']
print(f"Excluding neutral: {len(no_neutral)} images\n")
print(f"Highly skewed: {no_neutral['flag_skewed'].sum()}/{len(no_neutral)}")
print(f"Low CV:        {no_neutral['flag_low_cv'].sum()}/{len(no_neutral)}")
print(f"Problematic:   {no_neutral['flag_problematic'].sum()}/{len(no_neutral)}")

print("\n=== Per-category (excl. neutral) ===\n")
flag_by_cat_nn = (
    no_neutral.groupby('category')[['flag_skewed', 'flag_low_cv', 'flag_problematic']]
    .sum()
    .astype(int)
)
flag_by_cat_nn.columns = ['Skewed', 'Low CV', 'Problematic']
print(flag_by_cat_nn.to_string())

# %% [markdown]
# ## 9. Visualization

# %%
cmap = plt.colormaps.get_cmap('tab20').resampled(len(categories))
cat_colors = {cat: cmap(i) for i, cat in enumerate(categories)}

# --- Figure 1: Skewness vs CV scatter ---
fig, ax = plt.subplots(figsize=(10, 8))

for cat in categories:
    subset = stats_df[stats_df['category'] == cat]
    ax.scatter(subset['CV'], subset['skewness'], color=cat_colors[cat],
               label=cat, s=40, alpha=0.8, edgecolors='white', linewidth=0.5)

ax.axhline(y=SKEW_THRESHOLD, color='red', linestyle='--', linewidth=0.8, alpha=0.7)
ax.axhline(y=-SKEW_THRESHOLD, color='red', linestyle='--', linewidth=0.8, alpha=0.7)
ax.axvline(x=CV_LOW_THRESHOLD, color='orange', linestyle='--', linewidth=0.8, alpha=0.7)

ax.fill_between([0, CV_LOW_THRESHOLD], SKEW_THRESHOLD, ax.get_ylim()[1] if ax.get_ylim()[1] > SKEW_THRESHOLD else SKEW_THRESHOLD + 1,
                alpha=0.08, color='red', label='_nolegend_')
ax.fill_between([0, CV_LOW_THRESHOLD], -SKEW_THRESHOLD, ax.get_ylim()[0] if ax.get_ylim()[0] < -SKEW_THRESHOLD else -SKEW_THRESHOLD - 1,
                alpha=0.08, color='red', label='_nolegend_')

prob_points = stats_df[stats_df['flag_problematic']]
for _, r in prob_points.iterrows():
    ax.annotate(r['image_id'], (r['CV'], r['skewness']),
                fontsize=5, alpha=0.7, xytext=(4, 4),
                textcoords='offset points')

ax.set_xlabel('Coefficient of Variation (SD / Mean)')
ax.set_ylabel('Skewness')
ax.set_title('Skewness vs CV of Dwell Time Per Image (All Participants)')
ax.legend(fontsize=7, title='Category', loc='best')

fname = f'{FIG_DIR}/skewness_vs_cv_scatter.png'
fig.savefig(fname, dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {fname}')

# %%
# --- Figure 2: Skewness bar chart (all images sorted) ---
data = stats_df.sort_values('skewness', ascending=True)
fig_height = max(6, len(data) * 0.22)
fig, ax = plt.subplots(figsize=(10, fig_height))

colors = [cat_colors[c] for c in data['category']]
ax.barh(range(len(data)), data['skewness'].values, color=colors, height=0.7)

ax.axvline(x=SKEW_THRESHOLD, color='red', linestyle='--', linewidth=1,
           label=f'skewness = ±{SKEW_THRESHOLD}')
ax.axvline(x=-SKEW_THRESHOLD, color='red', linestyle='--', linewidth=1)

ax.set_yticks(range(len(data)))
ax.set_yticklabels(data['image_id'].values, fontsize=5)
ax.set_xlabel('Skewness')
ax.set_title('Skewness of Dwell Time Per Image — All Participants')

handles = [plt.Rectangle((0, 0), 1, 1, color=cat_colors[c], label=c) for c in categories]
handles.append(plt.Line2D([0], [0], color='red', linestyle='--', label=f'±{SKEW_THRESHOLD}'))
ax.legend(handles=handles, loc='lower right', fontsize=7, title='Category')

fname = f'{FIG_DIR}/skewness_barplot_all.png'
fig.savefig(fname, dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {fname}')

# %%
# --- Figure 2b: Histograms for highly skewed images (5x6 grid) ---
skewed_sorted = (
    stats_df[stats_df['flag_skewed']]
    .sort_values('abs_skewness', ascending=False)
    .reset_index(drop=True)
)

n_rows, n_cols = 5, 6
fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 15))
axes_flat = axes.flatten()

for i, (_, r) in enumerate(skewed_sorted.iterrows()):
    ax = axes_flat[i]
    vals = df.loc[df['image_id'] == r['image_id'], 'dwell_pct']
    ax.hist(vals, bins=np.arange(0, 105, 5), color=cat_colors[r['category']],
            edgecolor='white', linewidth=0.5, alpha=0.85)
    ax.axvline(x=vals.mean(), color='black', linestyle='--', linewidth=0.8)
    ax.set_xlim(0, 100)
    ax.set_xticks(np.arange(0, 101, 20))
    ax.set_title(f"{r['image_id']}\n{r['category']}  skew={r['skewness']:.2f}",
                 fontsize=7, pad=3)
    ax.tick_params(labelsize=6)

# hide unused subplot
for j in range(len(skewed_sorted), len(axes_flat)):
    axes_flat[j].set_visible(False)

fig.legend(
    [plt.Line2D([0], [0], color='black', linestyle='--', linewidth=0.8)],
    ['Mean dwell time'],
    loc='upper right', fontsize=8, framealpha=0.9,
)
fig.suptitle(f'Dwell Time Distributions — {len(skewed_sorted)} Highly Skewed Images '
             f'(|skewness| > {SKEW_THRESHOLD})', fontsize=12, y=1.01)
fig.supxlabel('Dwell Time (%)', fontsize=10)
fig.supylabel('Count (participants)', fontsize=10)
fig.tight_layout()

fname = f'{FIG_DIR}/skewed_images_histograms.png'
fig.savefig(fname, dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {fname}')

# %%
# --- Figure 3: CV bar chart (all images sorted ascending) ---
data = stats_df.sort_values('CV', ascending=True)
fig_height = max(6, len(data) * 0.22)
fig, ax = plt.subplots(figsize=(10, fig_height))

colors = [cat_colors[c] for c in data['category']]
ax.barh(range(len(data)), data['CV'].values, color=colors, height=0.7)

ax.axvline(x=CV_LOW_THRESHOLD, color='orange', linestyle='--', linewidth=1,
           label=f'CV = {CV_LOW_THRESHOLD}')

ax.set_yticks(range(len(data)))
ax.set_yticklabels(data['image_id'].values, fontsize=5)
ax.set_xlabel('Coefficient of Variation (SD / Mean)')
ax.set_title('CV of Dwell Time Per Image — All Participants')

handles = [plt.Rectangle((0, 0), 1, 1, color=cat_colors[c], label=c) for c in categories]
handles.append(plt.Line2D([0], [0], color='orange', linestyle='--', label=f'CV = {CV_LOW_THRESHOLD}'))
ax.legend(handles=handles, loc='lower right', fontsize=7, title='Category')

fname = f'{FIG_DIR}/cv_barplot_all.png'
fig.savefig(fname, dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {fname}')

# %%
# --- Figure 4: Skewness by category boxplot ---
cat_order = (
    stats_df.groupby('category')['skewness'].median()
    .sort_values(ascending=False).index.tolist()
)
box_data = [stats_df.loc[stats_df['category'] == c, 'skewness'].values for c in cat_order]

fig, ax = plt.subplots(figsize=(10, 6))
bp = ax.boxplot(box_data, vert=False, patch_artist=True, tick_labels=cat_order)
for patch, cat in zip(bp['boxes'], cat_order):
    patch.set_facecolor(cat_colors[cat])
    patch.set_alpha(0.7)

ax.axvline(x=SKEW_THRESHOLD, color='red', linestyle='--', linewidth=0.8)
ax.axvline(x=-SKEW_THRESHOLD, color='red', linestyle='--', linewidth=0.8)
ax.set_xlabel('Skewness')
ax.set_title('Distribution of Per-Image Skewness by Category')

fname = f'{FIG_DIR}/skewness_by_category_boxplot.png'
fig.savefig(fname, dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {fname}')

# %%
# --- Figure 5: CV by category boxplot ---
cat_order_cv = (
    stats_df.groupby('category')['CV'].median()
    .sort_values(ascending=True).index.tolist()
)
box_data_cv = [stats_df.loc[stats_df['category'] == c, 'CV'].dropna().values
               for c in cat_order_cv]

fig, ax = plt.subplots(figsize=(10, 6))
bp = ax.boxplot(box_data_cv, vert=False, patch_artist=True, tick_labels=cat_order_cv)
for patch, cat in zip(bp['boxes'], cat_order_cv):
    patch.set_facecolor(cat_colors[cat])
    patch.set_alpha(0.7)

ax.axvline(x=CV_LOW_THRESHOLD, color='orange', linestyle='--', linewidth=0.8)
ax.set_xlabel('Coefficient of Variation (SD / Mean)')
ax.set_title('Distribution of Per-Image CV by Category')

fname = f'{FIG_DIR}/cv_by_category_boxplot.png'
fig.savefig(fname, dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {fname}')

# %%
# --- Figure 6: Kurtosis vs skewness scatter ---
fig, ax = plt.subplots(figsize=(10, 8))

for cat in categories:
    subset = stats_df[stats_df['category'] == cat]
    ax.scatter(subset['skewness'], subset['kurtosis'], color=cat_colors[cat],
               label=cat, s=40, alpha=0.8, edgecolors='white', linewidth=0.5)

ax.axvline(x=SKEW_THRESHOLD, color='red', linestyle='--', linewidth=0.8, alpha=0.7)
ax.axvline(x=-SKEW_THRESHOLD, color='red', linestyle='--', linewidth=0.8, alpha=0.7)
ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5, alpha=0.5)

ax.set_xlabel('Skewness')
ax.set_ylabel('Excess Kurtosis')
ax.set_title('Kurtosis vs Skewness of Dwell Time Per Image (All Participants)')
ax.legend(fontsize=7, title='Category', loc='best')

fname = f'{FIG_DIR}/kurtosis_vs_skewness_scatter.png'
fig.savefig(fname, dpi=600, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {fname}')

# %% [markdown]
# ## 10. Write Report

# %%
report = [
    '# Distributional Properties of Dwell Time Per Image (All Participants)',
    '',
    '## Overview',
    '',
    f'- **Dataset**: dataset_image_dwell_times_clean.csv',
    f'- **Total observations**: {len(df)}',
    f'- **Sessions**: {n_sessions}',
    f'- **Unique images**: {len(image_ids)}',
    f'- **Categories**: {len(categories)}',
    f'- **Skewness threshold**: |skewness| > {SKEW_THRESHOLD}',
    f'- **CV threshold**: CV < {CV_LOW_THRESHOLD}',
    '',
    '## Distributional Statistics Summary',
    '',
]

desc = stats_df[['mean', 'SD', 'CV', 'skewness', 'kurtosis']].describe()
report.append('| Statistic | Mean | SD | CV | Skewness | Kurtosis |')
report.append('|-----------|------|----|----|----------|----------|')
for idx in desc.index:
    report.append(
        f"| {idx} | {desc.loc[idx, 'mean']:.4f} | {desc.loc[idx, 'SD']:.4f} | "
        f"{desc.loc[idx, 'CV']:.4f} | {desc.loc[idx, 'skewness']:.4f} | "
        f"{desc.loc[idx, 'kurtosis']:.4f} |"
    )
report.append('')

report += [
    '## Flagged Images',
    '',
    f'- **Highly skewed** (|skewness| > {SKEW_THRESHOLD}): {n_skewed}/{len(stats_df)}',
    f'- **Low CV** (CV < {CV_LOW_THRESHOLD}): {n_low_cv}/{len(stats_df)}',
    f'- **Problematic** (both): {n_problematic}/{len(stats_df)}',
    '',
]

# Problematic images table
report += ['### Problematic Images (Skewed AND Low CV)', '']
if n_problematic > 0:
    report.append('| Image ID | Category | n | Mean | SD | CV | Skewness | Kurtosis |')
    report.append('|----------|----------|---|------|----|----|----------|----------|')
    for _, r in prob_df.iterrows():
        report.append(
            f"| {r['image_id']} | {r['category']} | {r['n']:.0f} | "
            f"{r['mean']:.4f} | {r['SD']:.4f} | {r['CV']:.4f} | "
            f"{r['skewness']:.4f} | {r['kurtosis']:.4f} |"
        )
    report.append('')
else:
    report += ['No images meet both criteria.', '']

# Highly skewed table
report += ['### Highly Skewed Images', '']
report.append('| Image ID | Category | n | Mean | SD | CV | Skewness | Kurtosis |')
report.append('|----------|----------|---|------|----|----|----------|----------|')
for _, r in skewed_df.iterrows():
    report.append(
        f"| {r['image_id']} | {r['category']} | {r['n']:.0f} | "
        f"{r['mean']:.4f} | {r['SD']:.4f} | {r['CV']:.4f} | "
        f"{r['skewness']:.4f} | {r['kurtosis']:.4f} |"
    )
report.append('')

# Low-CV table
report += ['### Low-CV Images', '']
report.append('| Image ID | Category | n | Mean | SD | CV | Skewness | Kurtosis |')
report.append('|----------|----------|---|------|----|----|----------|----------|')
for _, r in low_cv_df.iterrows():
    report.append(
        f"| {r['image_id']} | {r['category']} | {r['n']:.0f} | "
        f"{r['mean']:.4f} | {r['SD']:.4f} | {r['CV']:.4f} | "
        f"{r['skewness']:.4f} | {r['kurtosis']:.4f} |"
    )
report.append('')

# Category-level summary
report += ['## Category-Level Summary', '']
report.append('| Category | Images | Skewed | Low CV | Problematic | Mean Skewness | Mean CV |')
report.append('|----------|--------|--------|--------|-------------|---------------|---------|')
for cat in sorted(categories):
    c = stats_df[stats_df['category'] == cat]
    report.append(
        f"| {cat} | {len(c)} | {c['flag_skewed'].sum()} | "
        f"{c['flag_low_cv'].sum()} | {c['flag_problematic'].sum()} | "
        f"{c['skewness'].mean():.4f} | {c['CV'].mean():.4f} |"
    )
report.append('')

# Excluding neutral
nn = stats_df[stats_df['category'] != 'neutral']
report += [
    '## Excluding Neutral Images',
    '',
    f'- **Images**: {len(nn)}',
    f'- **Highly skewed**: {nn["flag_skewed"].sum()}/{len(nn)}',
    f'- **Low CV**: {nn["flag_low_cv"].sum()}/{len(nn)}',
    f'- **Problematic**: {nn["flag_problematic"].sum()}/{len(nn)}',
    '',
]

# Figures
report += [
    '## Figures',
    '',
    f'- Skewness vs CV scatter: `{FIG_DIR}/skewness_vs_cv_scatter.png`',
    f'- Skewed images histograms: `{FIG_DIR}/skewed_images_histograms.png`',
    f'- Skewness bar plot: `{FIG_DIR}/skewness_barplot_all.png`',
    f'- CV bar plot: `{FIG_DIR}/cv_barplot_all.png`',
    f'- Skewness by category: `{FIG_DIR}/skewness_by_category_boxplot.png`',
    f'- CV by category: `{FIG_DIR}/cv_by_category_boxplot.png`',
    f'- Kurtosis vs skewness: `{FIG_DIR}/kurtosis_vs_skewness_scatter.png`',
    '',
]

report_path = os.path.join(REPORT_DIR, 'distributional_properties_dwell_time_report.md')
with open(report_path, 'w') as f:
    f.write('\n'.join(report) + '\n')
print(f"Report written to {report_path}")
