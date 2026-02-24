# %% [markdown]
# # Remove Blink-Outlier Sessions
#
# Three sessions are significant blink-metric outliers that will distort
# upcoming blink-related hypothesis tests:
#
# - **DTGxc0RwsWrTMRKpenb8**: 217 total blinks (72.5 blinks/min) — extreme
#   high blink count, 12 IQR outlier flags all blink-related.
# - **RBRGZzWIzDitollqkpzW**: 7 total blinks — very low count, flagged on
#   blink interval metrics (HIGH).
# - **xn3yMJ8STzchnQPg94lH**: 4 total blinks — very low count, flagged on
#   blink interval metrics (HIGH).
#
# Evidence documented in
# `reports/preanalysis_overview/eyetracking_metrics_overview_report.md`
# (sections 4 and 6).

# %%
import os
from pathlib import Path

os.chdir(Path(__file__).resolve().parent.parent)

import pandas as pd

# %%
SESSIONS_TO_REMOVE = [
    'DTGxc0RwsWrTMRKpenb8',
    'RBRGZzWIzDitollqkpzW',
    'xn3yMJ8STzchnQPg94lH',
]

df = pd.read_csv('data/simplified/dataset_eyetracking_metrics_clean.csv')
print(f"Rows before removal: {len(df)}")

df_clean = df[~df['session_id'].isin(SESSIONS_TO_REMOVE)].copy()
print(f"Rows after removal:  {len(df_clean)}")
print(f"Removed {len(df) - len(df_clean)} row(s)")

for sid in SESSIONS_TO_REMOVE:
    assert sid not in df_clean['session_id'].values, f"Session {sid} still present!"

# %%
df_clean.to_csv('data/simplified/dataset_eyetracking_metrics_blink_clean.csv', index=False)
print("Saved data/simplified/dataset_eyetracking_metrics_blink_clean.csv")
