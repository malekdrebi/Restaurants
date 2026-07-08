import json
import sys

with open('the_menu_bilingual.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

items = []
for c in data:
    if 'items' in c: items.extend(c['items'])
    if 'subcategories' in c:
        for s in c['subcategories']:
            if 'items' in s: items.extend(s['items'])

search_names = [
    'Chicken Alfredo', 
    'Mixed 3 Skewers', 
    'Fajita chicken sandwich', 
    'Seafood Pasta', 
    'Chicken Breast', 
    'Pasta Arrabbiata', 
    'Pesto', 
    'Baguette'
]

print("RESULTS:")
for search_name in search_names:
    print(f"\n--- {search_name} ---")
    matches = [i for i in items if search_name.lower() in (i.get('en_name') or '').lower()]
    for m in matches:
        print(f"AR: {m['name']} | EN: {m['en_name']}")
