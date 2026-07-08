import json

data = json.load(open("scraped_menu.json", encoding="utf-8"))
with open("counts.txt", "w", encoding="utf-8") as f:
    for cat in data:
        if cat['id'] == 'cat_1063':
            for sub in cat.get('subcategories', []):
                f.write(f"{sub['name']}: {len(sub['items'])}\n")
