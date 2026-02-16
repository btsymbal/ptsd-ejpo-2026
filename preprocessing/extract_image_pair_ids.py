# %% [markdown]
# # Extract Image Pair IDs to JSON

# %%
import os
import json
from pathlib import Path

import pandas as pd

os.chdir(Path(__file__).resolve().parent.parent)

# %%
df = pd.read_csv('data/simplified/dataset_merged_1_and_2.csv', nrows=0)

# %%
image_cols = df.columns[5:155].tolist()
print(f"Number of image columns: {len(image_cols)}")

# %%
pairs = {}
for i in range(0, len(image_cols), 2):
    pair_num = str(i // 2 + 1)
    pairs[pair_num] = [image_cols[i], image_cols[i + 1]]

print(f"Number of pairs: {len(pairs)}")
print(f"Pair 1: {pairs['1']}")

# %%
with open('materials/image_pair_ids.json', 'w') as f:
    json.dump(pairs, f, indent=2)

print("Written to materials/image_pair_ids.json")
