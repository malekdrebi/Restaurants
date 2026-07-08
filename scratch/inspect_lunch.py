import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('the_menu_bilingual.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

lunch = data[3]
print(f"Name: {lunch.get('en_name')} ({lunch.get('name')})")

if 'subcategories' in lunch:
    for i, sub in enumerate(lunch['subcategories']):
        print(f"Sub {i}: {sub.get('en_name')} ({sub.get('name')})")

if 'items' in lunch and lunch['items']:
    print(f"Total top-level lunch items: {len(lunch['items'])}")
