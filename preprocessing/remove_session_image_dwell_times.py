# %% [markdown]
# # Remove Session UgMWkyrkRYVZ9cr9thRw from Image Dwell Times
#
# This session was identified as a technical data recording anomaly
# (participant likely sat too far from the screen). Remove it from the
# image dwell times dataset, mirroring the removal already done for
# the eye-tracking metrics dataset.

# %%
import os
from pathlib import Path

os.chdir(Path(__file__).resolve().parent.parent)

import pandas as pd

# %%
SESSION_TO_REMOVE = 'UgMWkyrkRYVZ9cr9thRw'

df = pd.read_csv('data/simplified/dataset_image_dwell_times.csv')
print(f"Rows before removal: {len(df)}")

df_clean = df[df['session_id'] != SESSION_TO_REMOVE].copy()
print(f"Rows after removal:  {len(df_clean)}")
print(f"Removed {len(df) - len(df_clean)} row(s)")

assert SESSION_TO_REMOVE not in df_clean['session_id'].values, "Session still present!"

# %%
df_clean.to_csv('data/simplified/dataset_image_dwell_times_clean.csv', index=False)
print("Saved data/simplified/dataset_image_dwell_times_clean.csv")
