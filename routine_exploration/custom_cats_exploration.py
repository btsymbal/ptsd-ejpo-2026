# %% [markdown]
# # Custom Categories Mapping — Exploration & Reverse Mapping

# %%
import os
import json
from pathlib import Path
from collections import Counter

# Set working directory to project root (works from any location)
os.chdir(Path(__file__).resolve().parent.parent)

# %% [markdown]
# ## Load mapping

# %%
with open('materials/custom_cats_mapping.json', 'r') as f:
    mapping = json.load(f)

print(f"Number of categories: {len(mapping)}")
print(f"Categories: {list(mapping.keys())}")

# %% [markdown]
# ## Count unique IDs

# %%
all_ids = [id_ for ids in mapping.values() for id_ in ids]
unique_ids = set(all_ids)

print("Per-category counts:")
for cat, ids in mapping.items():
    print(f"  {cat}: {len(ids)}")

print(f"\nTotal IDs (with possible duplicates): {len(all_ids)}")
print(f"Unique IDs: {len(unique_ids)}")

# %% [markdown]
# ## Check for duplicate IDs

# %%
id_counts = Counter(all_ids)
duplicates = {id_: count for id_, count in id_counts.items() if count > 1}

if duplicates:
    print(f"Found {len(duplicates)} duplicate ID(s):\n")
    for dup_id, count in duplicates.items():
        cats = [cat for cat, ids in mapping.items() if dup_id in ids]
        print(f"  {dup_id} (appears {count}x) — in categories: {cats}")
else:
    print("No duplicates found — every ID appears in exactly one category.")

# %% [markdown]
# ## Create reverse mapping (ID → category)

# %%
id_to_category = {id_: cat for cat, ids in mapping.items() for id_ in ids}

print(f"Reverse mapping length: {len(id_to_category)}")
print(f"Matches unique count: {len(id_to_category) == len(unique_ids)}")

# %% [markdown]
# ## Export reverse mapping

# %%
with open('materials/id_to_category_mapping.json', 'w') as f:
    json.dump(id_to_category, f, indent=2)

print("Saved reverse mapping to materials/id_to_category_mapping.json")
