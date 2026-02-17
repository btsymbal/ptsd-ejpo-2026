# %%
import os
import json
from pathlib import Path

# Set working directory to project root (works from any location)
os.chdir(Path(__file__).resolve().parent.parent)

# %%
with open('materials/image_pair_ids.json') as f:
    slide_to_ids = json.load(f)

with open('materials/id_to_category_mapping.json') as f:
    id_to_category = json.load(f)

# %%
slide_categories = {}
for slide, image_ids in slide_to_ids.items():
    slide_categories[slide] = [id_to_category[img_id] for img_id in image_ids]

with open('materials/slide_categories.json', 'w') as f:
    json.dump(slide_categories, f, indent=2)

print(f"Wrote {len(slide_categories)} slides to materials/slide_categories.json")

# %%
unique_pairs = sorted({tuple(sorted(cats)) for cats in slide_categories.values()})
print(f"\nUnique category pairs ({len(unique_pairs)}):")
for pair in unique_pairs:
    print(f"  {pair[0]} / {pair[1]}")
