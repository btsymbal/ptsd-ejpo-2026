import os
import json
from pathlib import Path

# Set working directory to project root (works from any location)
os.chdir(Path(__file__).resolve().parent.parent)

from pdf2image import convert_from_path
from PIL import Image

pdf_path = 'materials/PTSD_final_without_42.pdf'
ids_path = 'materials/image_pair_ids.json'
output_dir = 'materials/stimuli'

os.makedirs(output_dir, exist_ok=True)

with open(ids_path) as f:
    image_pair_ids = json.load(f)

pages = convert_from_path(pdf_path, dpi=150)
print(f"Loaded {len(pages)} pages from PDF")

for i, page in enumerate(pages):
    page_num = str(i + 1)
    left_id, right_id = image_pair_ids[page_num]

    width, height = page.size
    mid = width // 2

    left_half = page.crop((0, 0, mid, height))
    right_half = page.crop((mid, 0, width, height))

    left_half.save(f'{output_dir}/{left_id}.png')
    right_half.save(f'{output_dir}/{right_id}.png')

saved = len(list(Path(output_dir).glob('*.png')))
print(f"Done. {saved} images saved to {output_dir}/")
