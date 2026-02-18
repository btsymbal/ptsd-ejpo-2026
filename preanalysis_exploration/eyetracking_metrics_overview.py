# %% [markdown]
# # Eye-Tracking Metrics Overview & Outlier Detection
#
# Descriptive overview of all variables in the eye-tracking metrics dataset,
# outlier flagging, distributional checks, and PTSD-group visual preview.
#
# **Input**: `data/simplified/dataset_eyetracking_metrics.csv` (30 sessions × 90 columns)

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

FIG_DIR = 'figures/eyetracking_metrics_overview'
os.makedirs(FIG_DIR, exist_ok=True)

POOR_QUALITY_SESSIONS = [
    'UgMWkyrkRYVZ9cr9thRw',  # 8.0% usable slides
    'xx19J8Xeoc4thStIAtUe',  # 45.3%
    'DTGxc0RwsWrTMRKpenb8',  # 57.3%
]

# %% [markdown]
# ## 1. Data Load & Column Groups

# %%
df = pd.read_csv('data/simplified/dataset_eyetracking_metrics.csv')
print(f"Shape: {df.shape}")
print(f"\nDtypes:\n{df.dtypes.value_counts()}")
print(f"\nNaN counts per column:")
nan_counts = df.isna().sum()
print(nan_counts[nan_counts > 0].to_string() if nan_counts.any() else "  No NaN values")

# %%
# Define column groups
meta_cols = ['session_id', 'if_PTSD', 'ITI_PTSD', 'ITI_cPTSD', 'if_antipsychotic']

mean_dwell_cols = [c for c in df.columns if c.startswith('mean_dwell_pct_')]
std_dwell_cols = [c for c in df.columns if c.startswith('std_dwell_pct_')]
std_delta_dwell_cols = [c for c in df.columns if c.startswith('std_delta_dwell_pct_')]
mean_visits_cols = [c for c in df.columns if c.startswith('mean_visits_')]
blink_count_cols = [c for c in df.columns if c.startswith('blink_count_')]
mean_blink_duration_cat_cols = [c for c in df.columns if c.startswith('mean_blink_duration_') and c != 'mean_blink_duration_ms']
std_blink_duration_cat_cols = [c for c in df.columns if c.startswith('std_blink_duration_')]
mean_blink_latency_cols = [c for c in df.columns if c.startswith('mean_blink_latency_')]
global_blink_cols = ['total_blink_count', 'mean_blink_duration_ms', 'mean_blink_interval_ms', 'std_blink_interval_ms']

numeric_cols = [c for c in df.columns if c not in ['session_id']]

print(f"Column groups:")
print(f"  mean_dwell_pct:         {len(mean_dwell_cols)}")
print(f"  std_dwell_pct:          {len(std_dwell_cols)}")
print(f"  std_delta_dwell_pct:    {len(std_delta_dwell_cols)}")
print(f"  mean_visits:            {len(mean_visits_cols)}")
print(f"  blink_count (per-cat):  {len(blink_count_cols)}")
print(f"  mean_blink_duration:    {len(mean_blink_duration_cat_cols)}")
print(f"  std_blink_duration:     {len(std_blink_duration_cat_cols)}")
print(f"  mean_blink_latency:     {len(mean_blink_latency_cols)}")
print(f"  global_blink:           {len(global_blink_cols)}")

# %% [markdown]
# ### Metadata Variables

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

fig.suptitle('Metadata Overview', fontsize=13, fontweight='bold', y=1.02)
fig.tight_layout()
path = os.path.join(FIG_DIR, 'metadata_overview.png')
fig.savefig(path, dpi=600, bbox_inches='tight')
plt.close(fig)
print(f"Saved {path}")

# %% [markdown]
# ## 2. Descriptive Statistics

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

desc_dwell = descriptive_table(mean_dwell_cols, 'Mean Dwell Percentage by Category')
desc_std_dwell = descriptive_table(std_dwell_cols, 'Std Dwell Percentage by Category')
desc_delta = descriptive_table(std_delta_dwell_cols, 'Std Delta Dwell (Threat Bias Variability)')
desc_visits = descriptive_table(mean_visits_cols, 'Mean Visits by Category')
desc_global_blink = descriptive_table(global_blink_cols, 'Global Blink Metrics')
desc_blink_count = descriptive_table(blink_count_cols, 'Blink Count by Category')
desc_blink_latency = descriptive_table(mean_blink_latency_cols, 'Mean Blink Latency by Category')

# %% [markdown]
# ## 3. Distributional Plots

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
        short_name = col.replace('mean_dwell_pct_', '').replace('std_dwell_pct_', '') \
                         .replace('std_delta_dwell_pct_', '') \
                         .replace('mean_visits_', '').replace('blink_count_', '') \
                         .replace('mean_blink_latency_', '') \
                         .replace('std_blink_duration_', 'std_blink_dur_') \
                         .replace('mean_blink_duration_ms', 'mean_blink_duration') \
                         .replace('mean_blink_duration_', 'mean_blink_dur_')
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
plot_hist_grid(mean_dwell_cols, 'Mean Dwell % by Category', 'hist_mean_dwell_pct.png', ncols=4)
plot_hist_grid(std_dwell_cols, 'Std Dwell % by Category', 'hist_std_dwell_pct.png', ncols=4)
plot_hist_grid(std_delta_dwell_cols, 'Std Delta Dwell % (Threat Bias Variability)', 'hist_std_delta_dwell.png', ncols=4)
plot_hist_grid(mean_visits_cols, 'Mean Visits by Category', 'hist_mean_visits.png', ncols=4)
plot_hist_grid(global_blink_cols, 'Global Blink Metrics', 'hist_global_blink.png', ncols=4)
plot_hist_grid(blink_count_cols, 'Blink Count by Category', 'hist_blink_count.png', ncols=4)
plot_hist_grid(mean_blink_latency_cols, 'Mean Blink Latency by Category', 'hist_mean_blink_latency.png', ncols=4)

# %% [markdown]
# ## 4. Outlier Detection (Flag Only)

# %% [markdown]
# ### 4a. Univariate Outliers (1.5×IQR)

# %%
analysis_cols = (mean_dwell_cols + std_delta_dwell_cols + mean_visits_cols
                 + global_blink_cols + blink_count_cols + mean_blink_latency_cols)

outlier_flags = pd.DataFrame(index=df['session_id'])
for col in analysis_cols:
    vals = df[col]
    q1, q3 = vals.quantile(0.25), vals.quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    outlier_flags[col] = ((vals.values < lower) | (vals.values > upper))

outlier_flags['total_flags'] = outlier_flags.sum(axis=1)
outlier_flags = outlier_flags.sort_values('total_flags', ascending=False)

print("Univariate outlier flag counts per session:")
print(outlier_flags[['total_flags']].to_string())

# %%
print("\nPoor-quality sessions in outlier ranking:")
for sid in POOR_QUALITY_SESSIONS:
    if sid in outlier_flags.index:
        rank = list(outlier_flags.index).index(sid) + 1
        count = outlier_flags.loc[sid, 'total_flags']
        print(f"  {sid}: {count} flags (rank {rank}/{len(outlier_flags)})")

# %%
# Detailed breakdown of flagged variables per session
print("\nDetailed outlier breakdown (sessions with >= 1 flag):")
flag_cols = [c for c in outlier_flags.columns if c != 'total_flags']
for sid in outlier_flags.index:
    n_flags = outlier_flags.loc[sid, 'total_flags']
    if n_flags == 0:
        continue
    pq = " [POOR QUALITY]" if sid in POOR_QUALITY_SESSIONS else ""
    print(f"\n  {sid} ({n_flags} flags){pq}:")
    for col in flag_cols:
        if outlier_flags.loc[sid, col]:
            val = df.loc[df['session_id'] == sid, col].values[0]
            vals = df[col]
            q1, q3 = vals.quantile(0.25), vals.quantile(0.75)
            iqr = q3 - q1
            direction = "HIGH" if val > q3 + 1.5 * iqr else "LOW"
            print(f"    {col} = {val:.2f} ({direction})")

# %% [markdown]
# ### Outlier Box Plots
#
# Box plots with IQR whiskers for each metric group that produced outlier flags.
# Individual sessions are overlaid as points (red = poor gaze quality).

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
        colors = ['red' if s in POOR_QUALITY_SESSIONS else 'steelblue'
                  for s in df.loc[vals.index, 'session_id']]
        ax.scatter(1 + jitter, vals.values, c=colors, s=20, alpha=0.7,
                   edgecolors='black', linewidth=0.3, zorder=5)

        short_name = col.replace('mean_dwell_pct_', '').replace('mean_visits_', '') \
                        .replace('blink_count_', '').replace('mean_blink_latency_', '') \
                        .replace('total_blink_count', 'total') \
                        .replace('mean_blink_interval_ms', 'mean_interval') \
                        .replace('std_blink_interval_ms', 'std_interval')
        ax.set_title(short_name, fontsize=9)
        ax.set_xticks([])
        ax.tick_params(labelsize=8)

    # Hide unused axes
    for j in range(n, nrows * ncols):
        axes[j // ncols, j % ncols].set_visible(False)

    fig.suptitle(f'{title}\n(red = poor gaze quality)', fontsize=12, fontweight='bold')
    fig.tight_layout()
    path = os.path.join(FIG_DIR, filename)
    fig.savefig(path, dpi=600, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved {path}")

plot_outlier_boxplots(
    ['total_blink_count'] + blink_count_cols,
    'Outlier Box Plots: Blink Counts', 'outlier_boxplot_blink_count.png')

plot_outlier_boxplots(
    mean_visits_cols,
    'Outlier Box Plots: Mean Visits', 'outlier_boxplot_mean_visits.png')

plot_outlier_boxplots(
    mean_dwell_cols,
    'Outlier Box Plots: Mean Dwell %', 'outlier_boxplot_mean_dwell_pct.png')

plot_outlier_boxplots(
    ['mean_blink_interval_ms', 'std_blink_interval_ms'],
    'Outlier Box Plots: Blink Interval', 'outlier_boxplot_blink_interval.png')

plot_outlier_boxplots(
    mean_blink_latency_cols,
    'Outlier Box Plots: Blink Latency', 'outlier_boxplot_blink_latency.png')

# %% [markdown]
# ### 4b. Multivariate Outliers (Mahalanobis Distance)

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
        'poor_quality': [s in POOR_QUALITY_SESSIONS for s in df.loc[sub.index, 'session_id'].values],
    }).sort_values('mahalanobis_d', ascending=False)

    print(f"\n{label} (chi2 crit = {chi2_crit:.2f}, p < {p_threshold}):")
    print(result.to_string(index=False, float_format='{:.3f}'.format))
    return result

md_dwell = mahalanobis_outliers(mean_dwell_cols, 'Mean Dwell %')
md_visits = mahalanobis_outliers(mean_visits_cols, 'Mean Visits')
md_blink = mahalanobis_outliers(
    ['total_blink_count'] + blink_count_cols + ['mean_blink_interval_ms', 'mean_blink_duration_ms'],
    'Blink Metrics (counts + interval + duration)'
)

# %% [markdown]
# ## 5. Correlation Structure

# %%
def plot_corr_heatmap(columns, title, filename):
    """Plot and save a correlation heatmap."""
    sub = df[columns].dropna()
    corr = sub.corr()
    short_labels = [c.replace('mean_dwell_pct_', '').replace('std_dwell_pct_', '')
                      .replace('std_delta_dwell_pct_', '')
                      .replace('mean_visits_', '').replace('blink_count_', '')
                      .replace('mean_blink_latency_', '')
                      .replace('std_blink_duration_', 'std_blink_dur_')
                      .replace('mean_blink_duration_ms', 'mean_blink_duration')
                      .replace('mean_blink_duration_', 'mean_blink_dur_')
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
plot_corr_heatmap(mean_dwell_cols, 'Correlation: Mean Dwell %', 'corr_mean_dwell_pct.png')
plot_corr_heatmap(mean_visits_cols, 'Correlation: Mean Visits', 'corr_mean_visits.png')
plot_corr_heatmap(blink_count_cols, 'Correlation: Blink Count by Category', 'corr_blink_count.png')

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
for cols, label in [(mean_dwell_cols, 'Mean Dwell %'),
                    (mean_visits_cols, 'Mean Visits'),
                    (blink_count_cols, 'Blink Count')]:
    corr = df[cols].corr()
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
                short1 = c1.replace('mean_dwell_pct_', '').replace('mean_visits_', '').replace('blink_count_', '')
                short2 = c2.replace('mean_dwell_pct_', '').replace('mean_visits_', '').replace('blink_count_', '')
                print(f"  p<0.05 only: {short1}–{short2} (r = {val:.3f})")

# %%
# Cross-family scatter matrix: dwell vs visits for a few key categories
key_cats = ['angry_face', 'warfare', 'neutral', 'happy_face']
scatter_pairs = []
for cat in key_cats:
    dwell_col = f'mean_dwell_pct_{cat}'
    visits_col = f'mean_visits_{cat}'
    if dwell_col in df.columns and visits_col in df.columns:
        scatter_pairs.append((dwell_col, visits_col, cat))

fig, axes = plt.subplots(1, len(scatter_pairs), figsize=(5 * len(scatter_pairs), 4))
if len(scatter_pairs) == 1:
    axes = [axes]
for ax, (dc, vc, cat) in zip(axes, scatter_pairs):
    colors = ['red' if s in POOR_QUALITY_SESSIONS else 'steelblue' for s in df['session_id']]
    ax.scatter(df[dc], df[vc], c=colors, alpha=0.7, edgecolors='black', linewidth=0.5)
    ax.set_xlabel(f'Dwell % ({cat})')
    ax.set_ylabel(f'Visits ({cat})')
    ax.set_title(cat)
fig.suptitle('Dwell % vs Visits (red = poor gaze quality)', fontsize=12, fontweight='bold')
fig.tight_layout()
path = os.path.join(FIG_DIR, 'scatter_dwell_vs_visits.png')
fig.savefig(path, dpi=600, bbox_inches='tight')
plt.close(fig)
print(f"Saved {path}")

# %% [markdown]
# ## 6. Domain-Specific Sanity Checks

# %% [markdown]
# ### 6a. Blink Rate Plausibility

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
        pq = " [POOR QUALITY]" if row['session_id'] in POOR_QUALITY_SESSIONS else ""
        print(f"  {row['session_id']}: {row['blinks_per_min']:.1f} /min "
              f"(total={int(row['total_blink_count'])}){pq}")

# %% [markdown]
# ### 6b. Dwell Percentage Range Check

# %%
print("Dwell % range check (flag if any value < 1% or > 90%):")
for col in mean_dwell_cols:
    low = df[df[col] < 1]
    high = df[df[col] > 90]
    if len(low) > 0 or len(high) > 0:
        cat = col.replace('mean_dwell_pct_', '')
        if len(low) > 0:
            for _, row in low.iterrows():
                pq = " [POOR QUALITY]" if row['session_id'] in POOR_QUALITY_SESSIONS else ""
                print(f"  {cat}: {row['session_id']} = {row[col]:.2f}% (very low){pq}")
        if len(high) > 0:
            for _, row in high.iterrows():
                pq = " [POOR QUALITY]" if row['session_id'] in POOR_QUALITY_SESSIONS else ""
                print(f"  {cat}: {row['session_id']} = {row[col]:.2f}% (very high){pq}")

if not any((df[col] < 1).any() or (df[col] > 90).any() for col in mean_dwell_cols):
    print("  All values in plausible range (1%–90%)")

# %% [markdown]
# ### 6c. Delta Dwell Std Near Zero

# %%
print("Std delta dwell near zero (< 5, suspiciously uniform bias):")
for col in std_delta_dwell_cols:
    low = df[df[col] < 5]
    if len(low) > 0:
        cat = col.replace('std_delta_dwell_pct_', '')
        for _, row in low.iterrows():
            pq = " [POOR QUALITY]" if row['session_id'] in POOR_QUALITY_SESSIONS else ""
            print(f"  {cat}: {row['session_id']} = {row[col]:.2f}{pq}")

if not any((df[col] < 5).any() for col in std_delta_dwell_cols):
    print("  No suspiciously low values found")

# %% [markdown]
# ## 7. PTSD-Group Visual Preview

# %%
def plot_group_boxplots(columns, group_col, title, filename, ncols=4):
    """Side-by-side boxplots split by a binary group variable."""
    n = len(columns)
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.5 * ncols, 4 * nrows))
    axes = np.atleast_2d(axes)

    for i, col in enumerate(columns):
        ax = axes[i // ncols, i % ncols]
        data_plot = df[[col, group_col]].dropna()
        groups = sorted(data_plot[group_col].unique())
        group_data = [data_plot[data_plot[group_col] == g][col].values for g in groups]

        parts = ax.violinplot(group_data, positions=range(len(groups)), showmedians=True, showextrema=True)
        for pc in parts['bodies']:
            pc.set_alpha(0.6)

        # Overlay individual points
        for j, g in enumerate(groups):
            vals = data_plot[data_plot[group_col] == g]
            jitter = np.random.normal(0, 0.04, size=len(vals))
            colors = ['red' if s in POOR_QUALITY_SESSIONS else 'black' for s in df.loc[vals.index, 'session_id']]
            ax.scatter(j + jitter, vals[col].values, c=colors, s=15, alpha=0.7, zorder=5)

        ax.set_xticks(range(len(groups)))
        group_labels = [str(int(g)) if g == g else str(g) for g in groups]
        if group_col == 'if_PTSD':
            group_labels = ['No PTSD' if g == '0' else 'PTSD' for g in group_labels]
        elif group_col == 'if_antipsychotic':
            group_labels = ['No' if g == '0' else 'Yes' for g in group_labels]
        ax.set_xticklabels(group_labels, fontsize=9)

        short_name = col.replace('mean_dwell_pct_', '').replace('std_dwell_pct_', '') \
                         .replace('std_delta_dwell_pct_', '') \
                         .replace('mean_visits_', '').replace('blink_count_', '') \
                         .replace('mean_blink_latency_', '').replace('total_blink_count', 'total_blinks') \
                         .replace('mean_blink_interval_ms', 'blink_interval') \
                         .replace('mean_blink_duration_ms', 'blink_duration')
        ax.set_title(short_name, fontsize=10)
        ax.tick_params(labelsize=8)

    for i in range(n, nrows * ncols):
        axes[i // ncols, i % ncols].set_visible(False)

    fig.suptitle(f'{title}\n(red dots = poor gaze quality sessions)', fontsize=13, fontweight='bold', y=1.02)
    fig.tight_layout()
    path = os.path.join(FIG_DIR, filename)
    fig.savefig(path, dpi=600, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved {path}")

# %% [markdown]
# ### By PTSD Status

# %%
plot_group_boxplots(mean_dwell_cols, 'if_PTSD',
                    'Mean Dwell % by PTSD Status', 'ptsd_mean_dwell_pct.png')
plot_group_boxplots(std_delta_dwell_cols, 'if_PTSD',
                    'Std Delta Dwell % by PTSD Status', 'ptsd_std_delta_dwell.png')
plot_group_boxplots(global_blink_cols[:3], 'if_PTSD',
                    'Global Blink Metrics by PTSD Status', 'ptsd_global_blink.png', ncols=3)
plot_group_boxplots(mean_visits_cols, 'if_PTSD',
                    'Mean Visits by PTSD Status', 'ptsd_mean_visits.png')
plot_group_boxplots(std_dwell_cols, 'if_PTSD',
                    'Std Dwell % by PTSD Status', 'ptsd_std_dwell_pct.png')

# %% [markdown]
# ### By Antipsychotic Use (Confound Check)

# %%
plot_group_boxplots(mean_dwell_cols, 'if_antipsychotic',
                    'Mean Dwell % by Antipsychotic Use', 'antipsychotic_mean_dwell_pct.png')
plot_group_boxplots(std_delta_dwell_cols, 'if_antipsychotic',
                    'Std Delta Dwell % by Antipsychotic Use', 'antipsychotic_std_delta_dwell.png')
plot_group_boxplots(global_blink_cols[:3], 'if_antipsychotic',
                    'Global Blink Metrics by Antipsychotic Use', 'antipsychotic_global_blink.png', ncols=3)
plot_group_boxplots(mean_visits_cols, 'if_antipsychotic',
                    'Mean Visits by Antipsychotic Use', 'antipsychotic_mean_visits.png')
plot_group_boxplots(std_dwell_cols, 'if_antipsychotic',
                    'Std Dwell % by Antipsychotic Use', 'antipsychotic_std_dwell_pct.png')

# %% [markdown]
# ## Summary
#
# This notebook provides:
# 1. Descriptive statistics with Shapiro-Wilk normality tests for all metric families
# 2. Distributional plots (histograms + KDE) for visual inspection
# 3. Univariate (IQR) and multivariate (Mahalanobis) outlier flagging
# 4. Cross-reference of outliers with the 3 poor gaze quality sessions
# 5. Correlation structure within metric families
# 6. Domain-specific sanity checks (blink rate, dwell range, delta dwell uniformity)
# 7. PTSD-group and antipsychotic-group visual previews (descriptive only)
