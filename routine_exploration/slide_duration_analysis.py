# %% [markdown]
# # Raw Session Slide Duration Analysis
#
# Verify raw eye-tracking session data integrity against the merged dataset
# and calculate per-slide durations for each session.
#
# - Raw sessions in `data/raw_sessions/` contain timestamped gaze data with `SCENE_INDEX` values
# - SCENE_INDEX: odd numbers 1–149, representing 75 slides
# - Remap: `slide_number = (SCENE_INDEX + 1) / 2` → slides 1–75
# - Duration = last TIMESTAMP − first TIMESTAMP per SCENE_INDEX group (ms)

# %%
import os
from pathlib import Path

import pandas as pd

# Set working directory to project root (works from any location)
os.chdir(Path(__file__).resolve().parent.parent)

# %% [markdown]
# ## Section 1: File-Session Validation
#
# Check that the 30 raw session files match the 30 session IDs in the merged dataset.

# %%
merged = pd.read_csv('data/simplified/dataset_merged_1_and_2.csv')
session_ids = set(merged['sessions'].tolist())

raw_files = os.listdir('data/raw_sessions/')
raw_files = [f for f in raw_files if f.endswith('.csv')]
file_ids = set(f.replace('.csv', '') for f in raw_files)

print(f"Merged dataset sessions: {len(session_ids)}")
print(f"Raw session files:       {len(file_ids)}")

assert len(session_ids) == len(file_ids), f"Count mismatch: {len(session_ids)} vs {len(file_ids)}"
assert session_ids == file_ids, f"ID mismatch. Only in merged: {session_ids - file_ids}. Only in files: {file_ids - session_ids}"

print("Validation passed: all 30 session IDs match.")

# %% [markdown]
# ## Section 2: Slide Duration Calculation
#
# For each raw session, compute the duration (ms) per slide and save results.

# %%
os.makedirs('data/output/slides_duration', exist_ok=True)

# %%
raw_dir = 'data/raw_sessions/'
out_dir = 'data/output/slides_duration/'

for i, filename in enumerate(sorted(raw_files), 1):
    session_id = filename.replace('.csv', '')

    df = pd.read_csv(
        os.path.join(raw_dir, filename),
        usecols=['TIMESTAMP', 'SCENE_INDEX']
    )

    grouped = df.groupby('SCENE_INDEX')['TIMESTAMP']
    durations = (grouped.last() - grouped.first()).reset_index()
    durations.columns = ['SCENE_INDEX', 'duration_ms']

    durations['slide_number'] = (durations['SCENE_INDEX'] + 1) // 2
    durations = durations[['slide_number', 'duration_ms']].sort_values('slide_number')

    durations.to_csv(os.path.join(out_dir, f'{session_id}.csv'), index=False)

    print(f"[{i:2d}/30] {session_id}: {len(durations)} slides, "
          f"mean duration {durations['duration_ms'].mean():.0f} ms")

print("\nAll sessions processed.")

# %% [markdown]
# ## Section 3: Expected Duration Outlier Detection
#
# Slides are designed to display for either 2500 ms or 1500 ms.
# Flag individual session-slide pairs where the measured duration
# deviates by more than 10% from the expected value.

# %%
all_durations = []
for filename in sorted(os.listdir(out_dir)):
    if not filename.endswith('.csv'):
        continue
    session_id = filename.replace('.csv', '')
    df = pd.read_csv(os.path.join(out_dir, filename))
    df['session_id'] = session_id
    all_durations.append(df)

combined = pd.concat(all_durations, ignore_index=True)
print(f"Combined records: {len(combined)} ({combined['session_id'].nunique()} sessions × {combined['slide_number'].nunique()} slides)")

# Define expected durations per slide
slides_1500 = {8, 9, 10, 17, 27, 41, 45, 71}
slides_2500 = set(range(1, 76)) - slides_1500

combined['expected_ms'] = combined['slide_number'].apply(
    lambda s: 1500 if s in slides_1500 else 2500
)

print(f"Slide duration groups:")
print(f"  1500 ms slides ({len(slides_1500)}): {sorted(slides_1500)}")
print(f"  2500 ms slides ({len(slides_2500)}): {sorted(slides_2500)}")

# %%
# Find session-slide pairs deviating >10% from expected duration
combined['pct_deviation'] = (
    (combined['duration_ms'] - combined['expected_ms']) / combined['expected_ms'] * 100
)

threshold = 10
outliers = combined[combined['pct_deviation'].abs() > threshold].sort_values(
    ['slide_number', 'session_id']
)

print(f"\nSession-slide pairs with >{threshold}% deviation from expected duration: "
      f"{len(outliers)} / {len(combined)} records")
if len(outliers) > 0:
    print(outliers[['session_id', 'slide_number', 'duration_ms', 'expected_ms', 'pct_deviation']]
          .to_string(index=False, float_format='%.1f'))
else:
    print("  (none)")

# %% [markdown]
# ## Section 4: Export Correct Slide Durations
#
# Save the expected duration for each slide (1–75) to a reusable CSV.

# %%
slide_durations = pd.DataFrame({
    'slide_number': range(1, 76),
    'expected_duration_ms': [1500 if s in slides_1500 else 2500 for s in range(1, 76)]
})

slide_durations.to_csv('materials/slide_durations.csv', index=False)
print(f"Exported {len(slide_durations)} slide durations to materials/slide_durations.csv")