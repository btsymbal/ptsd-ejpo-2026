---
name: stimuli-browser
description: >
  Use when the user asks to find, show, or list visual stimulus images by
  category, slide number, or image ID (e.g. "show me all neutral images",
  "what's on slide 5", "find all warfare stimuli").
---

## Purpose
Look up stimulus images by category, slide number, or image ID, returning
file paths and slide placement metadata.

## Key Files (all relative to project root)
- `materials/custom_cats_mapping.json` — category → [image IDs]
- `materials/id_to_category_mapping.json` — image ID → category
- `materials/image_pair_ids.json` — slide number (string) → [left_id, right_id]
- `materials/stimuli/{ID}.png` — actual image files

## Categories Available
`sad_face`, `happy_face`, `angry_face`, `neutral_face`, `happy_event`,
`combat_vehicles`, `soldiers`, `warfare`, `anxiety_inducing`, `sleep_related`, `neutral`

## Slide Position Convention
In `image_pair_ids.json`, each slide has exactly 2 IDs:
- Index 0 → **position 1 (left)**
- Index 1 → **position 2 (right)**

## Lookup Procedure

### By category (e.g., "show me neutral images")
1. Read `materials/custom_cats_mapping.json`
2. Get the ID list for the requested category (partial name matching is fine, e.g. "neutral" matches "neutral_face" and "neutral")
3. Read `materials/image_pair_ids.json` and build a reverse index: for each image ID, record which slides it appears on and at what position
4. Output each image with its path and slide placements

### By slide (e.g., "what's on slide 12?")
1. Read `materials/image_pair_ids.json`, get the two IDs for that slide
2. Read `materials/id_to_category_mapping.json` for their categories
3. Output both images with paths, categories, and positions

### By image ID (e.g., "what category is 68123405?")
1. Read `materials/id_to_category_mapping.json` for the category
2. Read `materials/image_pair_ids.json` to find all slides it appears on
3. Output path, category, and slide placements

### Combined queries (e.g., "show sad_face images from slides 1–10")
Read all necessary files, filter by both criteria, and output matching images.

## Output Format

For each image:
```
**ID:** 68123405
**Path:** `materials/stimuli/68123405.png`
**Category:** sad_face
**Slides:** Slide 2 (position 1, left), Slide 14 (position 2, right)
```

If the result set has more than 10 images, start with a count summary (e.g., "Found 51 images in category `neutral`:"), then list all — do not truncate.
