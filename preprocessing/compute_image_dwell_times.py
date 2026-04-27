# %% [markdown]
# # Compute Per-Image Dwell Times
#
# Compute dwell time at the **individual image** level — one value per
# image per session — to enable fine-grained image-level analysis.
# Output: long-format CSV with 30 sessions × 150 images = 4,500 rows.

# %%
import os
from pathlib import Path

os.chdir(Path(__file__).resolve().parent.parent)

import json
import numpy as np
import pandas as pd
from collections import defaultdict

# %%  Load materials
# -------------------------------------------------------------------
slide_dur_df = pd.read_csv('materials/slide_durations.csv')
slide_duration = dict(zip(slide_dur_df['slide_number'], slide_dur_df['expected_duration_ms']))

with open('materials/id_to_category_mapping.json') as f:
    id_to_category = json.load(f)

with open('materials/image_pair_ids.json') as f:
    slide_to_image_ids = {int(k): v for k, v in json.load(f).items()}

# %%  Build ordered image list
# -------------------------------------------------------------------
# 150 entries: (slide_num, image_position, image_id)
ordered_images = []
for slide_num in range(1, 76):
    img1, img2 = slide_to_image_ids[slide_num]
    ordered_images.append((slide_num, 1, img1))
    ordered_images.append((slide_num, 2, img2))

assert len(ordered_images) == 150, f"Expected 150 images, got {len(ordered_images)}"

# %%  Session loop
# -------------------------------------------------------------------
raw_dir = Path('data/raw_sessions')
session_files = sorted(raw_dir.glob('*.csv'))
assert len(session_files) == 30, f"Expected 30 session files, got {len(session_files)}"

rows = []

for fpath in session_files:
    session_id = fpath.stem
    print(f"Processing {session_id} ...")

    df = pd.read_csv(fpath, usecols=['TIMESTAMP', 'SCENE_INDEX', 'IMAGE'])
    df = df.sort_values('TIMESTAMP').reset_index(drop=True)

    for slide_num in range(1, 76):
        scene_idx = slide_num * 2 - 1
        slide_df = df[df['SCENE_INDEX'] == float(scene_idx)]
        expected_ms = slide_duration[slide_num]
        img1, img2 = slide_to_image_ids[slide_num]

        # Compute dwell_pct per image (same algorithm as compute_slide_dwell_pct)
        if len(slide_df) == 0 or expected_ms <= 0:
            dwell = {img1: 0.0, img2: 0.0}
        else:
            timestamps = slide_df['TIMESTAMP'].values
            images = slide_df['IMAGE'].values

            durations = np.empty(len(timestamps))
            durations[:-1] = np.diff(timestamps)
            durations[-1] = 0.0

            time_per_img = defaultdict(float)
            for dur, img in zip(durations, images):
                if img != 'no_image':
                    time_per_img[img] += dur

            dwell = {
                img1: (time_per_img.get(img1, 0.0) / expected_ms) * 100,
                img2: (time_per_img.get(img2, 0.0) / expected_ms) * 100,
            }

        # Emit one row per image (2 per slide)
        for position, img_id in [(1, img1), (2, img2)]:
            rows.append({
                'session_id': session_id,
                'slide_num': slide_num,
                'image_position': position,
                'image_id': img_id,
                'category': id_to_category.get(img_id, 'unknown'),
                'dwell_pct': dwell[img_id],
            })

# %%  Create DataFrame and merge metadata
# -------------------------------------------------------------------
result_df = pd.DataFrame(rows)

meta_df = pd.read_csv('data/simplified/dataset_merged_1_and_2.csv',
                       usecols=['sessions', 'if_PTSD', 'ITI_PTSD', 'ITI_cPTSD', 'if_antipsychotic'])
meta_df = meta_df.rename(columns={'sessions': 'session_id'})

result_df = result_df.merge(meta_df, on='session_id', how='left')

print(f"\nShape: {result_df.shape}")

# %%  Validation
# -------------------------------------------------------------------
assert len(result_df) == 4500, f"Expected 4500 rows, got {len(result_df)}"
assert result_df['session_id'].nunique() == 30, "Expected 30 unique sessions"

# Each session should have exactly 150 images
imgs_per_session = result_df.groupby('session_id').size()
assert (imgs_per_session == 150).all(), f"Not all sessions have 150 images: {imgs_per_session.value_counts()}"

# dwell_pct in [0, 100]
assert result_df['dwell_pct'].min() >= -0.01, f"dwell_pct has negative values: {result_df['dwell_pct'].min()}"
assert result_df['dwell_pct'].max() <= 101, f"dwell_pct > 100: {result_df['dwell_pct'].max()}"

# No missing metadata
for col in ['if_PTSD', 'ITI_PTSD', 'ITI_cPTSD', 'if_antipsychotic']:
    assert result_df[col].notna().all(), f"Missing metadata in {col}"

print("All validations passed!")
print(f"dwell_pct range: [{result_df['dwell_pct'].min():.2f}, {result_df['dwell_pct'].max():.2f}]")
print(f"Categories: {sorted(result_df['category'].unique())}")

# %%  Export
# -------------------------------------------------------------------
os.makedirs('data/simplified', exist_ok=True)
result_df.to_csv('data/simplified/dataset_image_dwell_times.csv', index=False)
print(f"\nExported to data/simplified/dataset_image_dwell_times.csv")
print(f"Shape: {result_df.shape[0]} rows x {result_df.shape[1]} columns")
