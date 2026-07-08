import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('the_menu_bilingual.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

juices = data[6]
print(f"Name: {juices.get('en_name')} ({juices.get('name')})")

if 'subcategories' in juices:
    for i, sub in enumerate(juices['subcategories']):
        print(f"Sub {i}: {sub.get('en_name')} ({sub.get('name')})")

if 'items' in juices and juices['items']:
    print(f"Total top-level juice items: {len(juices['items'])}")
