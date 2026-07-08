import json

with open('scraped_menu.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open('cats.txt', 'w', encoding='utf-8') as f:
    for c in data:
        f.write(f"{c['id']} {c['name']}\n")
