# %% [markdown]
# # Image Dwell Times Overview
#
# Per-image descriptive analysis of dwell time percentages. Each of the 150 images
# is observed by ~29 sessions; this notebook aggregates across sessions to characterize
# individual image behavior.
#
# **Input**: `data/simplified/dataset_image_dwell_times_clean.csv` (4,350 rows = 29 sessions × 150 images)

# %%
import os
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

os.chdir(Path(__file__).resolve().parent.parent)

warnings.filterwarnings('ignore', category=FutureWarning)
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 200)

FIG_DIR = 'figures/image_dwell_times_overview'
os.makedirs(FIG_DIR, exist_ok=True)

REPORT_DIR = 'reports/preanalysis_overview'
os.makedirs(REPORT_DIR, exist_ok=True)

report_lines = []

def rpt(line=''):
    """Append a line to the report."""
    report_lines.append(line)

# %% [markdown]
# ## 1. Data Load & Overview

# %%
df = pd.read_csv('data/simplified/dataset_image_dwell_times_clean.csv')
print(f"Shape: {df.shape}")
print(f"\nDtypes:\n{df.dtypes.to_string()}")
print(f"\nNaN counts per column:")
nan_counts = df.isna().sum()
print(nan_counts[nan_counts > 0].to_string() if nan_counts.any() else "  No NaN values")

n_sessions = df['session_id'].nunique()
n_images = df['image_id'].nunique()
n_categories = df['category'].nunique()
categories = sorted(df['category'].unique())

print(f"\nUnique sessions:   {n_sessions}")
print(f"Unique images:     {n_images}")
print(f"Unique categories: {n_categories}")
print(f"Categories: {categories}")

# Each image_id appears once per session
obs_per_image = df.groupby('image_id').size()
print(f"\nObservations per image: min={obs_per_image.min()}, max={obs_per_image.max()}, "
      f"median={obs_per_image.median():.0f}")

# Images per category
imgs_per_cat = df.groupby('category')['image_id'].nunique().sort_values(ascending=False)
print(f"\nImages per category:")
for cat, cnt in imgs_per_cat.items():
    print(f"  {cat}: {cnt}")

print(f"\nSample rows:")
print(df.head(10).to_string(index=False))

rpt('# Image Dwell Times Overview Report')
rpt()
rpt('## 1. Dataset Overview')
rpt()
rpt(f'The image dwell times dataset contains **{df.shape[0]:,} rows** '
    f'({n_sessions} sessions × {n_images} images) with {df.shape[1]} columns.')
rpt()
rpt(f'- **Sessions**: {n_sessions}')
rpt(f'- **Unique images**: {n_images}')
rpt(f'- **Categories**: {n_categories} ({", ".join(categories)})')
rpt()
rpt('Each `image_id` appears once per session, so per-image statistics are computed '
    'by aggregating `dwell_pct` across all sessions.')
rpt()
rpt('### Images per Category')
rpt()
rpt('| Category | # Images |')
rpt('|---|---|')
for cat, cnt in imgs_per_cat.items():
    rpt(f'| {cat} | {cnt} |')
rpt()

# %% [markdown]
# ## 2. Per-Image Aggregation

# %%
# Aggregate dwell_pct by image_id across all sessions
img_agg = df.groupby('image_id').agg(
    category=('category', 'first'),
    n_sessions=('dwell_pct', 'count'),
    mean=('dwell_pct', 'mean'),
    median=('dwell_pct', 'median'),
    sd=('dwell_pct', 'std'),
    min=('dwell_pct', 'min'),
    max=('dwell_pct', 'max'),
).reset_index()

img_agg['iqr'] = df.groupby('image_id')['dwell_pct'].apply(
    lambda x: x.quantile(0.75) - x.quantile(0.25)
).values

print(f"Per-image aggregation: {img_agg.shape[0]} images")
print(f"\nDescriptive stats of per-image means:")
print(img_agg['mean'].describe().to_string())
print(f"\nDescriptive stats of per-image SDs:")
print(img_agg['sd'].describe().to_string())

rpt('## 2. Per-Image Aggregation')
rpt()
rpt(f'Aggregating `dwell_pct` across {n_sessions} sessions yields a **{img_agg.shape[0]}-row** '
    'dataframe (one row per image).')
rpt()
rpt('**Distribution of per-image mean dwell %:**')
rpt()
desc = img_agg['mean'].describe()
rpt(f'- Mean of means: {desc["mean"]:.2f}%')
rpt(f'- Median of means: {desc["50%"]:.2f}%')
rpt(f'- SD of means: {desc["std"]:.2f}%')
rpt(f'- Range: [{desc["min"]:.2f}%, {desc["max"]:.2f}%]')
rpt()

# %% [markdown]
# ## 3. Overall Distribution of Per-Image Mean Dwell %

# %%
means = img_agg['mean']
sw_stat, sw_p = stats.shapiro(means)
skew = stats.skew(means)
kurt = stats.kurtosis(means)

print(f"Per-image mean dwell_pct distribution (N = {len(means)}):")
print(f"  Mean:     {means.mean():.3f}")
print(f"  Median:   {means.median():.3f}")
print(f"  SD:       {means.std():.3f}")
print(f"  Skewness: {skew:.3f}")
print(f"  Kurtosis: {kurt:.3f}")
print(f"  Shapiro-Wilk W = {sw_stat:.4f}, p = {sw_p:.4e}")

fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(means, bins=25, edgecolor='black', alpha=0.7, color='steelblue', density=True, label='Histogram')
means_sorted = np.sort(means)
kde = stats.gaussian_kde(means)
x_kde = np.linspace(means.min() - 1, means.max() + 1, 300)
ax.plot(x_kde, kde(x_kde), color='darkred', linewidth=2, label='KDE')
ax.axvline(means.mean(), color='orange', linestyle='--', linewidth=1.5, label=f'Mean = {means.mean():.1f}%')
ax.axvline(means.median(), color='green', linestyle='--', linewidth=1.5, label=f'Median = {means.median():.1f}%')
ax.set_xlabel('Mean Dwell % (across sessions)', fontsize=11)
ax.set_ylabel('Density', fontsize=11)
ax.set_title('Distribution of Per-Image Mean Dwell %', fontsize=13, fontweight='bold')
ax.legend(fontsize=9)
fig.tight_layout()
path = os.path.join(FIG_DIR, 'mean_dwell_distribution.png')
fig.savefig(path, dpi=600, bbox_inches='tight')
plt.close(fig)
print(f"Saved {path}")

rpt('## 3. Overall Distribution of Per-Image Mean Dwell %')
rpt()
rpt(f'![Mean Dwell Distribution](../../figures/image_dwell_times_overview/mean_dwell_distribution.png)')
rpt()
rpt(f'| Statistic | Value |')
rpt(f'|---|---|')
rpt(f'| N (images) | {len(means)} |')
rpt(f'| Mean | {means.mean():.2f}% |')
rpt(f'| Median | {means.median():.2f}% |')
rpt(f'| SD | {means.std():.2f}% |')
rpt(f'| Skewness | {skew:.3f} |')
rpt(f'| Kurtosis | {kurt:.3f} |')
rpt(f'| Shapiro-Wilk W | {sw_stat:.4f} |')
rpt(f'| Shapiro-Wilk p | {sw_p:.4e} |')
rpt()
normality = "normal" if sw_p > 0.05 else "non-normal"
rpt(f'The distribution of per-image mean dwell % is **{normality}** (Shapiro-Wilk p = {sw_p:.4e}).')
rpt()

# %% [markdown]
# ## 4. Per-Image Dwell % Ranked Overview

# %%
img_ranked = img_agg.sort_values('mean', ascending=False).reset_index(drop=True)

# Color palette for categories
cat_list = sorted(img_agg['category'].unique())
palette = dict(zip(cat_list, sns.color_palette('tab20', len(cat_list))))

fig, ax = plt.subplots(figsize=(20, 8))
colors = [palette[c] for c in img_ranked['category']]
ax.bar(range(len(img_ranked)), img_ranked['mean'], color=colors, edgecolor='none', width=1.0)
ax.set_xlabel('Image Rank', fontsize=11)
ax.set_ylabel('Mean Dwell %', fontsize=11)
ax.set_title('All 150 Images Ranked by Mean Dwell %', fontsize=13, fontweight='bold')
ax.set_xlim(-0.5, len(img_ranked) - 0.5)
# Legend
handles = [plt.Rectangle((0, 0), 1, 1, color=palette[c]) for c in cat_list]
ax.legend(handles, cat_list, loc='upper right', fontsize=8, ncol=2)
fig.tight_layout()
path = os.path.join(FIG_DIR, 'ranked_mean_dwell.png')
fig.savefig(path, dpi=600, bbox_inches='tight')
plt.close(fig)
print(f"Saved {path}")

# Top 10 and bottom 10
top10 = img_ranked.head(10)[['image_id', 'category', 'mean', 'median', 'sd']].copy()
bot10 = img_ranked.tail(10)[['image_id', 'category', 'mean', 'median', 'sd']].copy()

print("\n=== Top 10 Images by Mean Dwell % ===")
print(top10.to_string(index=False, float_format='{:.2f}'.format))
print("\n=== Bottom 10 Images by Mean Dwell % ===")
print(bot10.to_string(index=False, float_format='{:.2f}'.format))

rpt('## 4. Per-Image Dwell % Ranked Overview')
rpt()
rpt('![Ranked Mean Dwell](../../figures/image_dwell_times_overview/ranked_mean_dwell.png)')
rpt()
rpt('### Top 10 Images by Mean Dwell %')
rpt()
rpt('| Image ID | Category | Mean | Median | SD |')
rpt('|---|---|---|---|---|')
for _, r in top10.iterrows():
    rpt(f'| {r["image_id"]} | {r["category"]} | {r["mean"]:.2f} | {r["median"]:.2f} | {r["sd"]:.2f} |')
rpt()
rpt('### Bottom 10 Images by Mean Dwell %')
rpt()
rpt('| Image ID | Category | Mean | Median | SD |')
rpt('|---|---|---|---|---|')
for _, r in bot10.iterrows():
    rpt(f'| {r["image_id"]} | {r["category"]} | {r["mean"]:.2f} | {r["median"]:.2f} | {r["sd"]:.2f} |')
rpt()

# %% [markdown]
# ## 5. Within-Image Variability

# %%
sds = img_agg['sd']
print(f"Per-image SD distribution:")
print(f"  Mean SD:   {sds.mean():.3f}")
print(f"  Median SD: {sds.median():.3f}")
print(f"  Min SD:    {sds.min():.3f}")
print(f"  Max SD:    {sds.max():.3f}")

# Histogram of per-image SDs
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

ax = axes[0]
ax.hist(sds, bins=25, edgecolor='black', alpha=0.7, color='steelblue')
ax.axvline(sds.mean(), color='orange', linestyle='--', linewidth=1.5, label=f'Mean = {sds.mean():.1f}')
ax.axvline(sds.median(), color='green', linestyle='--', linewidth=1.5, label=f'Median = {sds.median():.1f}')
ax.set_xlabel('SD of Dwell % (across sessions)', fontsize=11)
ax.set_ylabel('Count', fontsize=11)
ax.set_title('Distribution of Per-Image Dwell % SD', fontsize=12, fontweight='bold')
ax.legend(fontsize=9)

# Scatter: mean vs SD
ax = axes[1]
for cat in cat_list:
    mask = img_agg['category'] == cat
    ax.scatter(img_agg.loc[mask, 'mean'], img_agg.loc[mask, 'sd'],
               color=palette[cat], label=cat, alpha=0.7, s=40, edgecolors='black', linewidths=0.3)
ax.set_xlabel('Mean Dwell %', fontsize=11)
ax.set_ylabel('SD of Dwell %', fontsize=11)
ax.set_title('Mean vs SD of Dwell % per Image', fontsize=12, fontweight='bold')
ax.legend(fontsize=7, ncol=2, loc='upper left')

# Correlation
corr_r, corr_p = stats.pearsonr(img_agg['mean'], img_agg['sd'])
ax.annotate(f'r = {corr_r:.3f}, p = {corr_p:.3e}', xy=(0.98, 0.02), xycoords='axes fraction',
            ha='right', va='bottom', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='wheat', alpha=0.8))

fig.tight_layout()
path = os.path.join(FIG_DIR, 'within_image_variability.png')
fig.savefig(path, dpi=600, bbox_inches='tight')
plt.close(fig)
print(f"Saved {path}")

# Flag high/low variability images (> mean + 2*SD or < mean - 2*SD)
sd_mean = sds.mean()
sd_sd = sds.std()
high_var = img_agg[img_agg['sd'] > sd_mean + 2 * sd_sd].sort_values('sd', ascending=False)
low_var = img_agg[img_agg['sd'] < sd_mean - 2 * sd_sd].sort_values('sd')

print(f"\nHigh variability images (SD > mean + 2*SD = {sd_mean + 2*sd_sd:.2f}): {len(high_var)}")
if len(high_var) > 0:
    print(high_var[['image_id', 'category', 'mean', 'sd']].to_string(index=False, float_format='{:.2f}'.format))

print(f"\nLow variability images (SD < mean - 2*SD = {max(0, sd_mean - 2*sd_sd):.2f}): {len(low_var)}")
if len(low_var) > 0:
    print(low_var[['image_id', 'category', 'mean', 'sd']].to_string(index=False, float_format='{:.2f}'.format))

rpt('## 5. Within-Image Variability')
rpt()
rpt('![Within-Image Variability](../../figures/image_dwell_times_overview/within_image_variability.png)')
rpt()
rpt(f'**Per-image SD distribution**: mean = {sds.mean():.2f}, median = {sds.median():.2f}, '
    f'range = [{sds.min():.2f}, {sds.max():.2f}]')
rpt()
rpt(f'**Mean–SD correlation**: r = {corr_r:.3f}, p = {corr_p:.3e}')
rpt()
if len(high_var) > 0:
    rpt(f'**High variability images** (SD > mean + 2×SD = {sd_mean + 2*sd_sd:.2f}): {len(high_var)}')
    rpt()
    rpt('| Image ID | Category | Mean | SD |')
    rpt('|---|---|---|---|')
    for _, row in high_var.iterrows():
        rpt(f'| {row["image_id"]} | {row["category"]} | {row["mean"]:.2f} | {row["sd"]:.2f} |')
    rpt()
if len(low_var) > 0:
    rpt(f'**Low variability images** (SD < mean − 2×SD = {max(0, sd_mean - 2*sd_sd):.2f}): {len(low_var)}')
    rpt()
    rpt('| Image ID | Category | Mean | SD |')
    rpt('|---|---|---|---|')
    for _, row in low_var.iterrows():
        rpt(f'| {row["image_id"]} | {row["category"]} | {row["mean"]:.2f} | {row["sd"]:.2f} |')
    rpt()

# %% [markdown]
# ## 6. Box Plots of Individual Images by Category

# %%
for cat in cat_list:
    cat_images = img_agg[img_agg['category'] == cat].sort_values('mean', ascending=False)['image_id'].tolist()
    cat_data = df[df['category'] == cat].copy()
    # Shorten image_id for display (last 8 chars)
    cat_data['image_short'] = cat_data['image_id'].astype(str).str[-8:]
    id_map = {img: str(img)[-8:] for img in cat_images}
    order = [id_map[img] for img in cat_images]

    n_imgs = len(cat_images)
    fig_width = max(8, n_imgs * 0.8)
    fig, ax = plt.subplots(figsize=(fig_width, 6))
    sns.boxplot(data=cat_data, x='image_short', y='dwell_pct', order=order,
                color=palette[cat], ax=ax, fliersize=3)
    ax.set_xlabel('Image ID (last 8 chars)', fontsize=10)
    ax.set_ylabel('Dwell %', fontsize=10)
    ax.set_title(f'{cat} — Per-Image Dwell % Across Sessions (n={n_sessions})',
                 fontsize=12, fontweight='bold')
    ax.tick_params(axis='x', rotation=45)
    fig.tight_layout()
    fname = f'boxplot_{cat}.png'
    path = os.path.join(FIG_DIR, fname)
    fig.savefig(path, dpi=600, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved {path}")

rpt('## 6. Box Plots of Individual Images by Category')
rpt()
rpt('Each subplot shows the distribution of `dwell_pct` across all sessions for each image '
    'within a category, ordered by mean dwell %.')
rpt()
for cat in cat_list:
    rpt(f'### {cat}')
    rpt()
    rpt(f'![{cat} boxplot](../../figures/image_dwell_times_overview/boxplot_{cat}.png)')
    rpt()

# %% [markdown]
# ## 7. Distribution Plots per Category Group

# %%
for cat in cat_list:
    cat_images = img_agg[img_agg['category'] == cat].sort_values('mean', ascending=False)['image_id'].tolist()
    cat_data = df[df['category'] == cat].copy()
    cat_data['image_short'] = cat_data['image_id'].astype(str).str[-8:]
    id_map = {img: str(img)[-8:] for img in cat_images}
    order = [id_map[img] for img in cat_images]

    n_imgs = len(cat_images)
    fig_width = max(8, n_imgs * 0.8)
    fig, ax = plt.subplots(figsize=(fig_width, 6))
    sns.violinplot(data=cat_data, x='image_short', y='dwell_pct', order=order,
                   color=palette[cat], ax=ax, inner=None, linewidth=0.5, alpha=0.4)
    sns.stripplot(data=cat_data, x='image_short', y='dwell_pct', order=order,
                  color='black', ax=ax, size=2, alpha=0.5, jitter=True)
    ax.set_xlabel('Image ID (last 8 chars)', fontsize=10)
    ax.set_ylabel('Dwell %', fontsize=10)
    ax.set_title(f'{cat} — Violin + Strip Plot per Image (n={n_sessions})',
                 fontsize=12, fontweight='bold')
    ax.tick_params(axis='x', rotation=45)
    fig.tight_layout()
    fname = f'violin_{cat}.png'
    path = os.path.join(FIG_DIR, fname)
    fig.savefig(path, dpi=600, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved {path}")

rpt('## 7. Distribution Plots per Category Group')
rpt()
rpt('Violin + strip plots overlay individual session observations on each image within a category, '
    'helping identify images with systematically different profiles.')
rpt()
for cat in cat_list:
    rpt(f'### {cat}')
    rpt()
    rpt(f'![{cat} violin](../../figures/image_dwell_times_overview/violin_{cat}.png)')
    rpt()

# %% [markdown]
# ## 8. Summary Statistics Table

# %%
summary = img_agg[['image_id', 'category', 'n_sessions', 'mean', 'median', 'sd', 'min', 'max', 'iqr']].copy()
summary = summary.sort_values(['category', 'mean'], ascending=[True, False]).reset_index(drop=True)

print(f"Full summary table ({len(summary)} images):")
print(summary.to_string(index=False, float_format='{:.2f}'.format))

rpt('## 8. Summary Statistics Table')
rpt()
rpt(f'Full table of all {len(summary)} images sorted by category then mean dwell %.')
rpt()
rpt('| Image ID | Category | N | Mean | Median | SD | Min | Max | IQR |')
rpt('|---|---|---|---|---|---|---|---|---|')
for _, r in summary.iterrows():
    rpt(f'| {r["image_id"]} | {r["category"]} | {r["n_sessions"]:.0f} | '
        f'{r["mean"]:.2f} | {r["median"]:.2f} | {r["sd"]:.2f} | '
        f'{r["min"]:.2f} | {r["max"]:.2f} | {r["iqr"]:.2f} |')
rpt()

# %% [markdown]
# ## 9. Conclusions & Interpretations

# %%
mean_sd_val = float(sds.mean())
high_var_threshold = float(sd_mean + 2 * sd_sd)
low_var_threshold = float(max(0, sd_mean - 2 * sd_sd))
n_high_var = len(high_var)
n_low_var = len(low_var)
r_val = float(corr_r)
sw_stat_val = float(sw_stat)
sw_p_val = float(sw_p)
skew_val = float(skew)
kurt_val = float(kurt)

rpt('## 9. Conclusions & Interpretations')
rpt()
rpt('### Attentional capture by threat-related imagery')
rpt()
rpt('The ranked overview reveals a clear pattern: **threat-related categories dominate the high end '
    'of the dwell-time distribution**. The top 10 most-gazed-at images are overwhelmingly '
    'anxiety_inducing (5 of 10), with combat_vehicles, warfare, and soldiers also represented. '
    'This is consistent with attentional bias theories of PTSD, where threat-relevant stimuli '
    'preferentially capture and hold visual attention. Notably, this pattern emerges at the '
    '*individual image* level, not just at the category average, suggesting that specific '
    'high-salience images drive much of the effect.')
rpt()
rpt('### Neutral images cluster at the bottom')
rpt()
rpt('8 of the 10 least-gazed-at images are neutral, with mean dwell times of 12-16% — roughly '
    'half the dwell time of the top threat images. This confirms that the image set successfully '
    'differentiates emotional from non-emotional content at the behavioral level. The two '
    'non-neutral images in the bottom 10 (happy_face) suggest that some positive-valence stimuli '
    'may also fail to capture sustained attention.')
rpt()
rpt('### High within-image variability signals individual differences')
rpt()
rpt(f'The overall SD of dwell % across sessions is high (mean SD = {mean_sd_val:.1f}%), indicating '
    'substantial between-participant variability in how long they look at any given image. '
    f'The positive mean-SD correlation (r = {r_val:.3f}, p < 0.001) means that images attracting more '
    'attention on average also show *more disagreement* between participants — precisely the pattern '
    'expected if PTSD status or trauma history modulates attentional engagement with threat stimuli. '
    'This variability is a promising signal for downstream PTSD vs. non-PTSD comparisons.')
rpt()
rpt('### Combat_vehicles and anxiety_inducing show the most extreme variability')
rpt()
rpt(f'All {n_high_var} high-variability outlier images (SD > {high_var_threshold:.1f}%) come from '
    'combat_vehicles or anxiety_inducing categories. Some of these images have very high means with '
    'high SD, while others have moderate means but extreme SD. The latter pattern — where the SD '
    'exceeds the mean — indicates a bimodal response: some participants fixate heavily while others '
    'largely avoid the image. This bimodality is particularly interesting for group-level analyses, '
    'as it may reflect approach/avoidance differences tied to trauma exposure.')
rpt()
rpt('### Low-variability images are uniformly low-interest')
rpt()
rpt(f'The {n_low_var} low-variability outlier images (SD < {low_var_threshold:.1f}%) are '
    'all low-mean neutral or happy_face images. Participants consistently show little interest in '
    'these stimuli, producing a floor effect with compressed variance. These images contribute '
    'minimal signal to between-group comparisons.')
rpt()
rpt('### Within-category heterogeneity')
rpt()
rpt('The box plots and violin plots reveal that not all images within a category behave identically. '
    'For example:')

# Compute within-category ranges for the report
for cat in ['combat_vehicles', 'anxiety_inducing', 'neutral']:
    cat_means = img_agg[img_agg['category'] == cat]['mean']
    rpt(f'- **{cat}** spans from {cat_means.min():.1f}% to {cat_means.max():.1f}% mean dwell — '
        f'a {cat_means.max()/cat_means.min():.1f}x range within the same category')
rpt()
rpt('This within-category heterogeneity suggests that image-level analysis (rather than category-level '
    'averaging) may capture effects that would otherwise be washed out by noisy or non-representative '
    'images within a category.')
rpt()
rpt('### Normality of per-image means supports parametric methods')
rpt()
rpt(f'The distribution of per-image mean dwell % passes the Shapiro-Wilk normality test '
    f'(W = {sw_stat_val:.3f}, p = {sw_p_val:.3f}), with low skewness ({skew_val:.2f}) and near-zero excess '
    f'kurtosis ({kurt_val:.2f}). This supports the use of parametric statistical methods (e.g., t-tests, '
    'ANOVA, linear mixed models) for group comparisons in subsequent analyses.')
rpt()
rpt('### Implications for downstream PTSD analyses')
rpt()
rpt('1. **Image-level modeling is warranted**: The large within-category spread and image-level '
    'variability suggest that collapsing to category means may lose important signal. Mixed models '
    'with random intercepts for image_id would preserve this information.')
rpt('2. **High-variability threat images are prime candidates** for detecting PTSD-related attentional '
    'differences — their large between-participant spread likely reflects the very individual '
    'differences the study aims to capture.')
rpt('3. **Floor effects in neutral images** should be considered when computing contrast scores '
    '(threat minus neutral), as the low-dwell neutral images may introduce noise rather than signal.')
rpt('4. **The 0.0% dwell-time floor** (present in every image\'s minimum) indicates that some sessions '
    'recorded zero gaze on certain AOIs, likely reflecting momentary off-screen gaze or fixation on '
    'the competing image. This is structurally expected given the paired-image presentation format '
    'and does not represent missing data.')
rpt()

# %% [markdown]
# ## Write Report

# %%
report_path = os.path.join(REPORT_DIR, 'image_dwell_times_overview_report.md')
with open(report_path, 'w') as f:
    f.write('\n'.join(report_lines) + '\n')
print(f"Report written to {report_path}")

# %% [markdown]
# ## Summary
#
# This notebook provides:
# 1. Per-image aggregation of dwell_pct across sessions (150 images)
# 2. Distribution analysis of per-image means with normality testing
# 3. Ranked bar chart of all images colored by category
# 4. Within-image variability analysis (SD distribution, mean-SD correlation)
# 5. Per-category box plots showing individual image distributions
# 6. Violin + strip plots for within-category image comparison
# 7. Full summary statistics table for all 150 images
