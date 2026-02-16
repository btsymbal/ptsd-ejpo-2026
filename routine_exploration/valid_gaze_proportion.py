# %% [markdown]
# # Valid Gaze Time Proportion per Slide
#
# Calculate the proportion of each slide's expected duration that has valid
# on-screen gaze data (both RX and RY in [0, 1]).
#
# - Each timestamp diff is attributed to the **earlier** row's gaze validity
# - Expected durations: 1500 ms for slides {8,9,10,17,27,41,45,71}, 2500 ms for all others
# - Output: per-session CSV with `slide_number` and `valid_gaze_proportion`

# %%
import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# Set working directory to project root (works from any location)
os.chdir(Path(__file__).resolve().parent.parent)

# %% [markdown]
# ## Compute Valid Gaze Proportion

# %%
slides_1500 = {8, 9, 10, 17, 27, 41, 45, 71}

raw_dir = 'data/raw_sessions/'
out_dir = 'data/output/valid_gaze_proportion/'
os.makedirs(out_dir, exist_ok=True)
os.makedirs('figures/valid_gaze_proportion', exist_ok=True)

raw_files = sorted(f for f in os.listdir(raw_dir) if f.endswith('.csv'))

low_quality = []

for i, filename in enumerate(raw_files, 1):
    session_id = filename.replace('.csv', '')

    df = pd.read_csv(
        os.path.join(raw_dir, filename),
        usecols=['TIMESTAMP', 'SCENE_INDEX', 'RX', 'RY']
    )

    results = []
    for scene_idx, group in df.groupby('SCENE_INDEX'):
        slide_number = (scene_idx + 1) // 2
        expected_ms = 1500 if slide_number in slides_1500 else 2500

        group = group.sort_values('TIMESTAMP').reset_index(drop=True)
        if len(group) < 2:
            results.append((slide_number, 0.0))
            continue

        ts = group['TIMESTAMP'].values
        diffs = ts[1:] - ts[:-1]

        valid = (
            group['RX'].between(0, 1) & group['RY'].between(0, 1)
        ).values[:-1]  # attribute each diff to the earlier row

        valid_time = diffs[valid].sum()
        proportion = valid_time / expected_ms

        results.append((slide_number, proportion))

    out_df = pd.DataFrame(results, columns=['slide_number', 'valid_gaze_proportion'])
    out_df = out_df.sort_values('slide_number')
    out_df.to_csv(os.path.join(out_dir, f'{session_id}.csv'), index=False)

    poor = out_df[out_df['valid_gaze_proportion'] < 0.5]
    if len(poor) > 0:
        for _, row in poor.iterrows():
            low_quality.append((session_id, int(row['slide_number']), row['valid_gaze_proportion']))

    print(f"[{i:2d}/{len(raw_files)}] {session_id}: {len(out_df)} slides, "
          f"mean valid gaze {out_df['valid_gaze_proportion'].mean():.1%}")

print(f"\nAll {len(raw_files)} sessions processed.")

# %% [markdown]
# ## Slides with < 50% Valid Gaze

# %%
if low_quality:
    lq_df = pd.DataFrame(low_quality, columns=['session_id', 'slide_number', 'valid_gaze_proportion'])

    affected_sessions = lq_df['session_id'].nunique()
    print(f"Sessions with at least one slide <50% valid gaze: {affected_sessions} / {len(raw_files)}")
    print(f"Total session-slide pairs <50%: {len(lq_df)}\n")

    # Group by session, sorted ascending by mean valid gaze proportion
    session_stats = (lq_df.groupby('session_id')['valid_gaze_proportion']
                     .agg(mean_proportion='mean', poor_slide_count='count')
                     .sort_values('mean_proportion'))

    for rank, (session_id, row) in enumerate(session_stats.iterrows(), 1):
        slides = lq_df[lq_df['session_id'] == session_id].sort_values('slide_number')
        print(f"{rank:2d}. {session_id}  "
              f"({int(row['poor_slide_count'])} slides <50%, mean {row['mean_proportion']:.3f})")
        for _, s in slides.iterrows():
            print(f"      slide {int(s['slide_number']):2d}  {s['valid_gaze_proportion']:.3f}")
        print()
else:
    print("All session-slide pairs have >=50% valid gaze.")

# %% [markdown]
# ## Sessions with < 60% of Slides Having Valid Gaze >= 50%
#
# Flag sessions where fewer than 60% of slides meet the 50% valid gaze threshold.

# %%
metadata = pd.read_csv(
    'data/simplified/dataset_merged_1_and_2.csv',
    usecols=['sessions', 'if_PTSD', 'ITI_PTSD']
)

# %%
total_slides = 75
threshold_pct = 0.60

# Count slides with valid gaze >= 50% per session
good_slide_counts = {}
for filename in sorted(os.listdir(out_dir)):
    if not filename.endswith('.csv'):
        continue
    session_id = filename.replace('.csv', '')
    sdf = pd.read_csv(os.path.join(out_dir, filename))
    good = (sdf['valid_gaze_proportion'] >= 0.5).sum()
    good_slide_counts[session_id] = good

session_quality = pd.DataFrame([
    {'session_id': sid, 'good_slides': cnt, 'good_slides_pct': cnt / total_slides}
    for sid, cnt in good_slide_counts.items()
]).sort_values('good_slides_pct')

failing = session_quality[session_quality['good_slides_pct'] < threshold_pct]

print(f"Sessions where <{threshold_pct:.0%} of slides have valid gaze >=50%: "
      f"{len(failing)} / {len(session_quality)}\n")

if len(failing) > 0:
    for _, row in failing.iterrows():
        sid = row['session_id']
        meta_row = metadata[metadata['sessions'] == sid]
        if len(meta_row) > 0:
            ptsd = int(meta_row['if_PTSD'].iloc[0])
            iti = meta_row['ITI_PTSD'].iloc[0]
            ptsd_info = f"  PTSD={ptsd}, ITI={iti}"
        else:
            ptsd_info = "  (no metadata)"
        print(f"  {sid}  "
              f"{int(row['good_slides'])}/{total_slides} good slides "
              f"({row['good_slides_pct']:.1%}){ptsd_info}")
else:
    print("  (none)")

# %% [markdown]
# ### Scatter Plots: Slide-by-Slide Valid Gaze for Failing Sessions

# %%
if len(failing) > 0:
    for _, row in failing.iterrows():
        sid = row['session_id']
        sdf = pd.read_csv(os.path.join(out_dir, f'{sid}.csv'))
        sdf = sdf.sort_values('slide_number')

        meta_row = metadata[metadata['sessions'] == sid]
        if len(meta_row) > 0:
            ptsd = int(meta_row['if_PTSD'].iloc[0])
            iti = meta_row['ITI_PTSD'].iloc[0]
            title_suffix = f' (PTSD={ptsd}, ITI={iti})'
        else:
            title_suffix = ''

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.scatter(sdf['slide_number'], sdf['valid_gaze_proportion'], s=20)
        ax.axhline(0.5, color='red', linestyle='--', linewidth=1, label='50% threshold')
        ax.set_xlabel('Slide number')
        ax.set_ylabel('Valid gaze proportion')
        ax.set_title(f'{sid} — valid gaze proportion per slide{title_suffix}')
        ax.legend()
        fig.tight_layout()
        out_path = f'figures/valid_gaze_proportion/{sid}_slide_dynamics.png'
        fig.savefig(out_path, dpi=600)
        plt.close(fig)
        print(f"Saved {out_path}")

# %% [markdown]
# ## Histogram: Number of Slides with < 50% Valid Gaze per Session

# %%
poor_counts = total_slides - session_quality['good_slides'].values

fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(poor_counts, bins=range(0, max(poor_counts) + 2), edgecolor='black', align='left')
ax.set_xlabel('Number of slides with <50% valid gaze')
ax.set_ylabel('Number of sessions')
ax.set_title('Distribution of Poor-Quality Slides Across Sessions')
ax.set_xticks(range(0, max(poor_counts) + 1, 5))
fig.tight_layout()
fig.savefig('figures/valid_gaze_proportion/poor_slides_histogram.png', dpi=600)
plt.show()
print("Saved to figures/valid_gaze_proportion/poor_slides_histogram.png")
