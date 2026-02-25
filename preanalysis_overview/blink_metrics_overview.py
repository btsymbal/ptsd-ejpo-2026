# %% [markdown]
# # Blink Metrics Overview & Outlier Detection (Blink-Clean Dataset)
#
# Descriptive overview of blink variables in the blink-cleaned eye-tracking
# dataset, outlier flagging, distributional checks, and PTSD/antipsychotic
# group visual previews.
#
# **Input**: `data/simplified/dataset_eyetracking_metrics_blink_clean.csv`
# (26 sessions × 134 columns)
#
# **Removed sessions** (4 from original 30):
# - UgMWkyrkRYVZ9cr9thRw — poor gaze quality (8.0% usable slides)
# - DTGxc0RwsWrTMRKpenb8 — extreme high blink count (217 blinks, 72.5/min)
# - RBRGZzWIzDitollqkpzW — very low blink count (7 blinks)
# - xn3yMJ8STzchnQPg94lH — very low blink count (4 blinks)

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

FIG_DIR = 'figures/blink_metrics_overview'
os.makedirs(FIG_DIR, exist_ok=True)

REMOVED_SESSIONS = [
    'UgMWkyrkRYVZ9cr9thRw',  # poor gaze quality
    'DTGxc0RwsWrTMRKpenb8',  # extreme high blink count (217)
    'RBRGZzWIzDitollqkpzW',  # very low blink count (7)
    'xn3yMJ8STzchnQPg94lH',  # very low blink count (4)
]

# %% [markdown]
# ## 1. Data Load & Column Groups

# %%
df = pd.read_csv('data/simplified/dataset_eyetracking_metrics_blink_clean.csv')
print(f"Shape: {df.shape}")
print(f"\nDtypes:\n{df.dtypes.value_counts()}")
print(f"\nNaN counts per column (blink columns only):")
nan_counts = df.isna().sum()
blink_nans = nan_counts[nan_counts.index.str.contains('blink') & (nan_counts > 0)]
print(blink_nans.to_string() if len(blink_nans) > 0 else "  No NaN values in blink columns")

# %%
# Define blink column groups
meta_cols = ['session_id', 'if_PTSD', 'ITI_PTSD', 'ITI_cPTSD', 'if_antipsychotic']

global_blink_cols = ['total_blink_count', 'mean_blink_duration_ms',
                     'mean_blink_interval_norm', 'std_blink_interval_norm']
mean_blink_rate_cols = [c for c in df.columns if c.startswith('mean_blink_rate_')]
mean_blink_duration_cols = [c for c in df.columns
                            if c.startswith('mean_blink_duration_') and c != 'mean_blink_duration_ms']
std_blink_duration_cols = [c for c in df.columns if c.startswith('std_blink_duration_')]
mean_blink_latency_norm_cols = [c for c in df.columns if c.startswith('mean_blink_latency_norm_')]

all_blink_cols = (global_blink_cols + mean_blink_rate_cols + mean_blink_duration_cols
                  + std_blink_duration_cols + mean_blink_latency_norm_cols)

print(f"\nBlink column groups:")
print(f"  global_blink:              {len(global_blink_cols)}")
print(f"  mean_blink_rate:           {len(mean_blink_rate_cols)}")
print(f"  mean_blink_duration:       {len(mean_blink_duration_cols)}")
print(f"  std_blink_duration:        {len(std_blink_duration_cols)}")
print(f"  mean_blink_latency_norm:   {len(mean_blink_latency_norm_cols)}")
print(f"  Total blink columns:       {len(all_blink_cols)}")
print(f"  Metadata columns:          {len(meta_cols)}")

# %% [markdown]
# ## 2. Metadata Overview

# %%
print("=== Group Counts ===")
print(f"\nPTSD status (if_PTSD):")
ptsd_counts = df['if_PTSD'].value_counts().sort_index()
for val, cnt in ptsd_counts.items():
    label = 'PTSD' if val == 1 else 'Non-PTSD'
    print(f"  {label}: n = {cnt}")

print(f"\nAntipsychotic use (if_antipsychotic):")
ap_counts = df['if_antipsychotic'].value_counts().sort_index()
for val, cnt in ap_counts.items():
    label = 'Yes' if val == 1 else 'No'
    print(f"  {label}: n = {cnt}")

# ITI descriptives for PTSD group only
ptsd_rows = df[df['if_PTSD'] == 1]
print(f"\n=== ITI Scores (PTSD group only, n = {len(ptsd_rows)}) ===")
for col in ['ITI_PTSD', 'ITI_cPTSD']:
    vals = ptsd_rows[col].dropna()
    print(f"\n{col} (n = {len(vals)}):")
    print(f"  Mean: {vals.mean():.2f}, Median: {vals.median():.2f}, SD: {vals.std():.2f}")
    print(f"  Min: {vals.min():.1f}, Max: {vals.max():.1f}")
    print(f"  Zero count: {(vals == 0).sum()}")

# %%
# Metadata visualizations
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Bar chart: PTSD status
ax = axes[0, 0]
bars = ax.bar(['Non-PTSD', 'PTSD'], [ptsd_counts.get(0, 0), ptsd_counts.get(1, 0)],
              color=['steelblue', 'salmon'], edgecolor='black')
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            str(int(bar.get_height())), ha='center', fontsize=11)
ax.set_ylabel('Count')
ax.set_title('PTSD Status', fontsize=11, fontweight='bold')

# Bar chart: Antipsychotic use
ax = axes[0, 1]
bars = ax.bar(['No', 'Yes'], [ap_counts.get(0, 0), ap_counts.get(1, 0)],
              color=['steelblue', 'salmon'], edgecolor='black')
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            str(int(bar.get_height())), ha='center', fontsize=11)
ax.set_ylabel('Count')
ax.set_title('Antipsychotic Use', fontsize=11, fontweight='bold')

# Histogram: ITI_PTSD (PTSD group only)
ax = axes[1, 0]
ax.hist(ptsd_rows['ITI_PTSD'].dropna(), bins=8, edgecolor='black', alpha=0.7, color='salmon')
ax.set_xlabel('ITI_PTSD Score')
ax.set_ylabel('Count')
ax.set_title('ITI_PTSD (PTSD group only)', fontsize=11, fontweight='bold')

# Histogram: ITI_cPTSD (PTSD group only)
ax = axes[1, 1]
ax.hist(ptsd_rows['ITI_cPTSD'].dropna(), bins=8, edgecolor='black', alpha=0.7, color='salmon')
ax.set_xlabel('ITI_cPTSD Score')
ax.set_ylabel('Count')
ax.set_title('ITI_cPTSD (PTSD group only)', fontsize=11, fontweight='bold')

fig.suptitle('Metadata Overview (n = 26, blink-clean)', fontsize=13, fontweight='bold', y=1.02)
fig.tight_layout()
path = os.path.join(FIG_DIR, 'metadata_overview.png')
fig.savefig(path, dpi=600, bbox_inches='tight')
plt.close(fig)
print(f"Saved {path}")

# %% [markdown]
# ## 3. Descriptive Statistics

# %%
def descriptive_table(columns, label):
    """Compute descriptive stats + Shapiro-Wilk for a set of columns."""
    rows = []
    for col in columns:
        vals = df[col].dropna()
        if len(vals) < 3:
            rows.append({'variable': col, 'n': len(vals), 'mean': np.nan})
            continue
        sw_stat, sw_p = stats.shapiro(vals)
        rows.append({
            'variable': col,
            'n': len(vals),
            'mean': vals.mean(),
            'median': vals.median(),
            'sd': vals.std(),
            'min': vals.min(),
            'max': vals.max(),
            'skewness': stats.skew(vals),
            'kurtosis': stats.kurtosis(vals),
            'shapiro_W': sw_stat,
            'shapiro_p': sw_p,
        })
    result = pd.DataFrame(rows)
    print(f"\n{'='*80}")
    print(f"  {label}")
    print(f"{'='*80}")
    print(result.to_string(index=False, float_format='{:.4f}'.format))
    return result

desc_global_blink = descriptive_table(global_blink_cols, 'Global Blink Metrics')
desc_blink_rate = descriptive_table(mean_blink_rate_cols, 'Mean Blink Rate by Category')
desc_blink_duration = descriptive_table(mean_blink_duration_cols, 'Mean Blink Duration by Category')
desc_std_blink_duration = descriptive_table(std_blink_duration_cols, 'Std Blink Duration by Category')
desc_blink_latency = descriptive_table(mean_blink_latency_norm_cols,
                                       'Mean Blink Latency (Normalized) by Category')

# %% [markdown]
# ## 4. Distributional Plots

# %%
def plot_hist_grid(columns, title, filename, ncols=4):
    """Plot histograms with KDE overlay in a grid."""
    n = len(columns)
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(4 * ncols, 3.5 * nrows))
    axes = np.atleast_2d(axes)

    for i, col in enumerate(columns):
        ax = axes[i // ncols, i % ncols]
        vals = df[col].dropna()
        ax.hist(vals, bins=12, edgecolor='black', alpha=0.7, density=True)
        if len(vals) >= 3 and vals.std() > 0:
            xmin, xmax = vals.min(), vals.max()
            x = np.linspace(xmin - (xmax - xmin) * 0.1, xmax + (xmax - xmin) * 0.1, 200)
            try:
                kde = stats.gaussian_kde(vals)
                ax.plot(x, kde(x), color='red', linewidth=1.5)
            except np.linalg.LinAlgError:
                pass
        short_name = col.replace('mean_blink_rate_', 'rate_') \
                         .replace('mean_blink_latency_norm_', 'lat_') \
                         .replace('std_blink_duration_', 'std_dur_') \
                         .replace('mean_blink_duration_ms', 'mean_duration_ms') \
                         .replace('mean_blink_duration_', 'dur_') \
                         .replace('mean_blink_interval_norm', 'mean_interval_norm') \
                         .replace('std_blink_interval_norm', 'std_interval_norm')
        ax.set_title(short_name, fontsize=10)
        ax.tick_params(labelsize=8)

    # Hide unused axes
    for i in range(n, nrows * ncols):
        axes[i // ncols, i % ncols].set_visible(False)

    fig.suptitle(title, fontsize=13, fontweight='bold', y=1.02)
    fig.tight_layout()
    path = os.path.join(FIG_DIR, filename)
    fig.savefig(path, dpi=600, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved {path}")

# %%
plot_hist_grid(global_blink_cols, 'Global Blink Metrics', 'hist_global_blink.png', ncols=4)
plot_hist_grid(mean_blink_rate_cols, 'Mean Blink Rate by Category', 'hist_mean_blink_rate.png', ncols=4)
plot_hist_grid(mean_blink_duration_cols, 'Mean Blink Duration by Category',
               'hist_mean_blink_duration.png', ncols=4)
plot_hist_grid(std_blink_duration_cols, 'Std Blink Duration by Category',
               'hist_std_blink_duration.png', ncols=4)
plot_hist_grid(mean_blink_latency_norm_cols, 'Mean Blink Latency (Normalized) by Category',
               'hist_mean_blink_latency_norm.png', ncols=4)

# %% [markdown]
# ## 5. Outlier Detection

# %% [markdown]
# ### 5a. Univariate Outliers (1.5×IQR)

# %%
outlier_flags = pd.DataFrame(index=df['session_id'])
for col in all_blink_cols:
    vals = df[col]
    q1, q3 = vals.quantile(0.25), vals.quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    outlier_flags[col] = ((vals.values < lower) | (vals.values > upper))

outlier_flags['total_flags'] = outlier_flags.sum(axis=1)
outlier_flags = outlier_flags.sort_values('total_flags', ascending=False)

print("Univariate outlier flag counts per session (blink columns only):")
print(outlier_flags[['total_flags']].to_string())

# %%
# Detailed breakdown of flagged variables per session
print("\nDetailed outlier breakdown (sessions with >= 1 flag):")
flag_cols = [c for c in outlier_flags.columns if c != 'total_flags']
for sid in outlier_flags.index:
    n_flags = outlier_flags.loc[sid, 'total_flags']
    if n_flags == 0:
        continue
    print(f"\n  {sid} ({n_flags} flags):")
    for col in flag_cols:
        if outlier_flags.loc[sid, col]:
            val = df.loc[df['session_id'] == sid, col].values[0]
            vals = df[col]
            q1, q3 = vals.quantile(0.25), vals.quantile(0.75)
            iqr = q3 - q1
            direction = "HIGH" if val > q3 + 1.5 * iqr else "LOW"
            print(f"    {col} = {val:.2f} ({direction})")

# %% [markdown]
# ### 5b. Outlier Box Plots

# %%
def plot_outlier_boxplots(columns, title, filename, ncols=4):
    """Box plots with IQR whiskers and individual points overlaid."""
    n = len(columns)
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(4 * ncols, 4.5 * nrows))
    axes = np.atleast_2d(axes)

    for i, col in enumerate(columns):
        ax = axes[i // ncols, i % ncols]
        vals = df[col].dropna()
        ax.boxplot(vals, whis=1.5, widths=0.5, patch_artist=True,
                   boxprops=dict(facecolor='lightblue', edgecolor='black'),
                   medianprops=dict(color='black', linewidth=1.5))

        # Overlay individual points with jitter
        jitter = np.random.normal(0, 0.04, size=len(vals))
        ax.scatter(1 + jitter, vals.values, c='steelblue', s=20, alpha=0.7,
                   edgecolors='black', linewidth=0.3, zorder=5)

        short_name = col.replace('mean_blink_rate_', 'rate_') \
                        .replace('mean_blink_latency_norm_', 'lat_') \
                        .replace('std_blink_duration_', 'std_dur_') \
                        .replace('mean_blink_duration_ms', 'mean_duration_ms') \
                        .replace('mean_blink_duration_', 'dur_') \
                        .replace('total_blink_count', 'total_count') \
                        .replace('mean_blink_interval_norm', 'mean_interval_norm') \
                        .replace('std_blink_interval_norm', 'std_interval_norm')
        ax.set_title(short_name, fontsize=9)
        ax.set_xticks([])
        ax.tick_params(labelsize=8)

    # Hide unused axes
    for j in range(n, nrows * ncols):
        axes[j // ncols, j % ncols].set_visible(False)

    fig.suptitle(title, fontsize=12, fontweight='bold')
    fig.tight_layout()
    path = os.path.join(FIG_DIR, filename)
    fig.savefig(path, dpi=600, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved {path}")

plot_outlier_boxplots(
    global_blink_cols,
    'Outlier Box Plots: Global Blink Metrics', 'outlier_boxplot_global_blink.png')

plot_outlier_boxplots(
    ['total_blink_count'] + mean_blink_rate_cols,
    'Outlier Box Plots: Blink Rate', 'outlier_boxplot_blink_rate.png')

plot_outlier_boxplots(
    mean_blink_duration_cols,
    'Outlier Box Plots: Blink Duration', 'outlier_boxplot_blink_duration.png')

plot_outlier_boxplots(
    std_blink_duration_cols,
    'Outlier Box Plots: Std Blink Duration', 'outlier_boxplot_std_blink_duration.png')

plot_outlier_boxplots(
    mean_blink_latency_norm_cols,
    'Outlier Box Plots: Blink Latency (Normalized)', 'outlier_boxplot_blink_latency.png')

# %% [markdown]
# ### 5c. Multivariate Outliers (Mahalanobis Distance)

# %%
def mahalanobis_outliers(columns, label, p_threshold=0.01):
    """Compute Mahalanobis distance and flag outliers using chi-squared critical value."""
    sub = df[columns].dropna()
    if len(sub) < len(columns) + 1:
        print(f"  {label}: too few complete cases ({len(sub)}) for {len(columns)} variables, skipping")
        return None

    X = sub.values
    mean = X.mean(axis=0)
    cov = np.cov(X, rowvar=False)

    # Regularize if singular
    try:
        cov_inv = np.linalg.inv(cov)
    except np.linalg.LinAlgError:
        cov_inv = np.linalg.pinv(cov)

    diff = X - mean
    md = np.sqrt(np.sum(diff @ cov_inv * diff, axis=1))

    chi2_crit = np.sqrt(stats.chi2.ppf(1 - p_threshold, df=len(columns)))

    result = pd.DataFrame({
        'session_id': df.loc[sub.index, 'session_id'].values,
        'mahalanobis_d': md,
        'is_outlier': md > chi2_crit,
    }).sort_values('mahalanobis_d', ascending=False)

    print(f"\n{label} (chi2 crit = {chi2_crit:.2f}, p < {p_threshold}):")
    print(result.to_string(index=False, float_format='{:.3f}'.format))
    return result

md_blink_rate = mahalanobis_outliers(
    ['total_blink_count'] + mean_blink_rate_cols + ['mean_blink_interval_norm', 'mean_blink_duration_ms'],
    'Blink Metrics (rate + interval + duration)'
)

md_blink_duration = mahalanobis_outliers(
    mean_blink_duration_cols,
    'Blink Duration by Category'
)

md_blink_latency = mahalanobis_outliers(
    mean_blink_latency_norm_cols,
    'Blink Latency (Normalized) by Category'
)

# %% [markdown]
# ## 6. Correlation Structure

# %%
def plot_corr_heatmap(columns, title, filename):
    """Plot and save a correlation heatmap."""
    sub = df[columns].dropna()
    corr = sub.corr()
    short_labels = [c.replace('mean_blink_rate_', '')
                      .replace('mean_blink_latency_norm_', '')
                      .replace('std_blink_duration_', 'std_')
                      .replace('mean_blink_duration_ms', 'mean_duration_ms')
                      .replace('mean_blink_duration_', '')
                     for c in columns]

    fig, ax = plt.subplots(figsize=(max(8, len(columns) * 0.8), max(6, len(columns) * 0.7)))
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                vmin=-1, vmax=1, xticklabels=short_labels, yticklabels=short_labels,
                ax=ax, square=True, linewidths=0.5)
    ax.set_title(title, fontsize=12, fontweight='bold')
    fig.tight_layout()
    path = os.path.join(FIG_DIR, filename)
    fig.savefig(path, dpi=600, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved {path}")

# %%
plot_corr_heatmap(mean_blink_rate_cols, 'Correlation: Blink Rate by Category',
                  'corr_blink_rate.png')
plot_corr_heatmap(mean_blink_duration_cols, 'Correlation: Blink Duration by Category',
                  'corr_blink_duration.png')
plot_corr_heatmap(mean_blink_latency_norm_cols, 'Correlation: Blink Latency (Normalized)',
                  'corr_blink_latency.png')

# %%
# Correlation significance thresholds
n = len(df)
t_05 = stats.t.ppf(1 - 0.025, df=n - 2)
t_01 = stats.t.ppf(1 - 0.005, df=n - 2)
r_crit_05 = np.sqrt(t_05**2 / (t_05**2 + n - 2))
r_crit_01 = np.sqrt(t_01**2 / (t_01**2 + n - 2))
print(f"Correlation significance thresholds (n = {n}):")
print(f"  |r| >= {r_crit_05:.3f} for p < 0.05")
print(f"  |r| >= {r_crit_01:.3f} for p < 0.01")

# Pairwise significance for each correlation matrix
for cols, label in [(mean_blink_rate_cols, 'Blink Rate'),
                    (mean_blink_duration_cols, 'Blink Duration'),
                    (mean_blink_latency_norm_cols, 'Blink Latency (Normalized)')]:
    sub = df[cols].dropna()
    corr = sub.corr()
    mask = np.tril(np.ones_like(corr, dtype=bool), k=-1)
    r_vals = corr.where(mask)
    min_r = r_vals.min().min()
    max_r = r_vals.max().max()
    n_pairs = mask.sum().sum()
    n_sig_05 = (r_vals.abs() >= r_crit_05).sum().sum()
    n_sig_01 = (r_vals.abs() >= r_crit_01).sum().sum()
    print(f"\n{label}: {n_pairs} pairs, r range [{min_r:.3f}, {max_r:.3f}]")
    print(f"  Significant at p < 0.05: {n_sig_05}/{n_pairs}")
    print(f"  Significant at p < 0.01: {n_sig_01}/{n_pairs}")
    # Print pairs that are sig at .05 but not .01
    not_01 = r_vals[(r_vals.abs() >= r_crit_05) & (r_vals.abs() < r_crit_01)]
    for c1 in not_01.columns:
        for c2 in not_01.index:
            val = not_01.loc[c2, c1]
            if pd.notna(val):
                short1 = c1.split('_')[-1] if '_' in c1 else c1
                short2 = c2.split('_')[-1] if '_' in c2 else c2
                print(f"  p<0.05 only: {short1}–{short2} (r = {val:.3f})")

# %% [markdown]
# ## 7. Blink Rate Plausibility

# %%
# Estimate session duration from slide structure:
# 75 slides, 8 slides at 1500ms, 67 slides at 2500ms
slides_1500 = 8
slides_2500 = 75 - slides_1500
session_duration_ms = slides_1500 * 1500 + slides_2500 * 2500
session_duration_min = session_duration_ms / 60000

print(f"Estimated session duration: {session_duration_ms} ms = {session_duration_min:.2f} min")

df['blinks_per_min'] = df['total_blink_count'] / session_duration_min

print(f"\nBlink rate (blinks/min):")
print(f"  Mean: {df['blinks_per_min'].mean():.1f}")
print(f"  Median: {df['blinks_per_min'].median():.1f}")
print(f"  Range: {df['blinks_per_min'].min():.1f} – {df['blinks_per_min'].max():.1f}")
print(f"  Typical range: 15–20 blinks/min")

implausible = df[(df['blinks_per_min'] < 5) | (df['blinks_per_min'] > 40)]
print(f"\nImplausible blink rate sessions (< 5 or > 40 /min): {len(implausible)}")
if len(implausible) > 0:
    for _, row in implausible.iterrows():
        print(f"  {row['session_id']}: {row['blinks_per_min']:.1f} /min "
              f"(total={int(row['total_blink_count'])})")

plausible = df[(df['blinks_per_min'] >= 5) & (df['blinks_per_min'] <= 40)]
print(f"\nPlausible sessions (5-40 /min): {len(plausible)}/{len(df)}")

# %% [markdown]
# ## 8. PTSD-Group Visual Preview

# %%
def plot_group_violins(columns, group_col, title, filename, ncols=4):
    """Side-by-side violin plots split by a binary group variable."""
    n = len(columns)
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.5 * ncols, 4 * nrows))
    axes = np.atleast_2d(axes)

    for i, col in enumerate(columns):
        ax = axes[i // ncols, i % ncols]
        data_plot = df[[col, group_col]].dropna()
        groups = sorted(data_plot[group_col].unique())
        group_data = [data_plot[data_plot[group_col] == g][col].values for g in groups]

        parts = ax.violinplot(group_data, positions=range(len(groups)),
                              showmedians=True, showextrema=True)
        for pc in parts['bodies']:
            pc.set_alpha(0.6)

        # Overlay individual points
        for j, g in enumerate(groups):
            vals = data_plot[data_plot[group_col] == g]
            jitter = np.random.normal(0, 0.04, size=len(vals))
            ax.scatter(j + jitter, vals[col].values, c='black', s=15, alpha=0.7, zorder=5)

        ax.set_xticks(range(len(groups)))
        group_labels = [str(int(g)) if g == g else str(g) for g in groups]
        if group_col == 'if_PTSD':
            group_labels = ['No PTSD' if g == '0' else 'PTSD' for g in group_labels]
        elif group_col == 'if_antipsychotic':
            group_labels = ['No' if g == '0' else 'Yes' for g in group_labels]
        ax.set_xticklabels(group_labels, fontsize=9)

        short_name = col.replace('mean_blink_rate_', 'rate_') \
                         .replace('mean_blink_latency_norm_', 'lat_') \
                         .replace('std_blink_duration_', 'std_dur_') \
                         .replace('mean_blink_duration_ms', 'mean_duration_ms') \
                         .replace('mean_blink_duration_', 'dur_') \
                         .replace('total_blink_count', 'total_count') \
                         .replace('mean_blink_interval_norm', 'mean_interval_norm') \
                         .replace('std_blink_interval_norm', 'std_interval_norm')
        ax.set_title(short_name, fontsize=10)
        ax.tick_params(labelsize=8)

    for i in range(n, nrows * ncols):
        axes[i // ncols, i % ncols].set_visible(False)

    fig.suptitle(title, fontsize=13, fontweight='bold', y=1.02)
    fig.tight_layout()
    path = os.path.join(FIG_DIR, filename)
    fig.savefig(path, dpi=600, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved {path}")

# %%
plot_group_violins(global_blink_cols, 'if_PTSD',
                   'Global Blink Metrics by PTSD Status', 'ptsd_global_blink.png')
plot_group_violins(mean_blink_rate_cols, 'if_PTSD',
                   'Blink Rate by PTSD Status', 'ptsd_blink_rate.png')
plot_group_violins(mean_blink_duration_cols, 'if_PTSD',
                   'Blink Duration by PTSD Status', 'ptsd_blink_duration.png')
plot_group_violins(std_blink_duration_cols, 'if_PTSD',
                   'Std Blink Duration by PTSD Status', 'ptsd_std_blink_duration.png')
plot_group_violins(mean_blink_latency_norm_cols, 'if_PTSD',
                   'Blink Latency (Normalized) by PTSD Status', 'ptsd_blink_latency.png')

# %% [markdown]
# ## 9. Antipsychotic-Group Visual Preview

# %%
plot_group_violins(global_blink_cols, 'if_antipsychotic',
                   'Global Blink Metrics by Antipsychotic Use',
                   'antipsychotic_global_blink.png')
plot_group_violins(mean_blink_rate_cols, 'if_antipsychotic',
                   'Blink Rate by Antipsychotic Use',
                   'antipsychotic_blink_rate.png')
plot_group_violins(mean_blink_duration_cols, 'if_antipsychotic',
                   'Blink Duration by Antipsychotic Use',
                   'antipsychotic_blink_duration.png')
plot_group_violins(std_blink_duration_cols, 'if_antipsychotic',
                   'Std Blink Duration by Antipsychotic Use',
                   'antipsychotic_std_blink_duration.png')
plot_group_violins(mean_blink_latency_norm_cols, 'if_antipsychotic',
                   'Blink Latency (Normalized) by Antipsychotic Use',
                   'antipsychotic_blink_latency.png')

# %% [markdown]
# ## Summary
#
# This notebook provides:
# 1. Descriptive statistics with Shapiro-Wilk normality tests for all blink metric families
# 2. Distributional plots (histograms + KDE) for visual inspection
# 3. Univariate (IQR) and multivariate (Mahalanobis) outlier flagging
# 4. Correlation structure within blink metric families with significance thresholds
# 5. Blink rate plausibility check (blinks/min vs. typical 15-20 range)
# 6. PTSD-group and antipsychotic-group visual previews (descriptive only)
