import json
import io
import sys

with open('the_menu_bilingual.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Output summary to a text file
with open('scratch/menu_summary.txt', 'w', encoding='utf-8') as f:
    for i, cat in enumerate(data):
        f.write(f"{i}: {cat.get('en_name')} ({cat.get('name')})\n")
        if 'subcategories' in cat:
            for j, sub in enumerate(cat['subcategories']):
                f.write(f"  - Sub {j}: {sub.get('en_name')} ({sub.get('name')})\n")
                if 'subcategories' in sub:
                     for k, ssub in enumerate(sub['subcategories']):
                         f.write(f"    -- SubSub {k}: {ssub.get('en_name')} ({ssub.get('name')})\n")
