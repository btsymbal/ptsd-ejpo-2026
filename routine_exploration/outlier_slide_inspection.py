# %% [markdown]
# # Outlier Slide Inspection
#
# Inspect raw gaze data for session-slide pairs flagged as duration outliers
# in `slide_duration_analysis.py`.

# %%
import os
from pathlib import Path

import pandas as pd

os.chdir(Path(__file__).resolve().parent.parent)

# %% [markdown]
# ## Section 1: DAccofkFpBK00oVonRAi — Slide 35
#
# Duration: 1437 ms (expected 2500 ms, -42.5% deviation).
# SCENE_INDEX = 69.

# %%
df1 = pd.read_csv('data/raw_sessions/DAccofkFpBK00oVonRAi.csv')
slide35 = df1[df1['SCENE_INDEX'] == 69].copy()
print(f"Rows for slide 35 (SCENE_INDEX 69): {len(slide35)}")
print(slide35.to_string())

# %%
slide35['time_delta'] = slide35['TIMESTAMP'].diff()
print("Time deltas between consecutive rows:")
print(slide35[['TIMESTAMP', 'time_delta']].to_string(index=False))

# %% [markdown]
# ### Slide-boundary timing
#
# Compare gaps before and after slide 35 to typical inter-slide gaps
# to determine whether data was lost at the beginning or end.

# %%
slide34 = df1[df1['SCENE_INDEX'] == 67]
slide36 = df1[df1['SCENE_INDEX'] == 71]

gap_before = slide35['TIMESTAMP'].iloc[0] - slide34['TIMESTAMP'].iloc[-1]
gap_after = slide36['TIMESTAMP'].iloc[0] - slide35['TIMESTAMP'].iloc[-1]

# Typical gap from nearby slides (30-40, excluding 35)
gaps = []
for sn in range(30, 41):
    if sn == 35:
        continue
    sa = df1[df1['SCENE_INDEX'] == sn * 2 - 1]
    sb = df1[df1['SCENE_INDEX'] == (sn + 1) * 2 - 1]
    if len(sa) > 0 and len(sb) > 0:
        gaps.append(sb['TIMESTAMP'].iloc[0] - sa['TIMESTAMP'].iloc[-1])

typical_gap = sum(gaps) / len(gaps)

print(f"Gap before slide 35 (slide 34 last → slide 35 first): {gap_before:.2f} ms")
print(f"Gap after  slide 35 (slide 35 last → slide 36 first): {gap_after:.2f} ms")
print(f"Typical inter-slide gap (slides 30-40 excl. 35):      {typical_gap:.2f} ms")
print()
print(f"Excess gap before: {gap_before - typical_gap:+.2f} ms")
print(f"Excess gap after:  {gap_after - typical_gap:+.2f} ms")
print()
print("→ Data was lost at the END of slide 35 (trailing gap is ~1070 ms too long)")

# %% [markdown]
# ## Section 2: Y20f3G9ulPHmbLwFS3JL — Slide 37
#
# Duration: 6868 ms (expected 2500 ms, +174.7% deviation).
# SCENE_INDEX = 73.

# %%
df2 = pd.read_csv('data/raw_sessions/Y20f3G9ulPHmbLwFS3JL.csv')
slide37 = df2[df2['SCENE_INDEX'] == 73].copy()
print(f"Rows for slide 37 (SCENE_INDEX 73): {len(slide37)}")
print(slide37.to_string())

# %%
slide37['time_delta'] = slide37['TIMESTAMP'].diff()
print("Time deltas between consecutive rows:")
print(slide37[['TIMESTAMP', 'time_delta']].to_string(index=False))
