import json

with open("scraped_menu.json", encoding="utf-8") as f:
    data = json.load(f)

with open("hierarchy.txt", "w", encoding="utf-8") as out:
    for cat in data:
        out.write(f"Category: {cat['name']}\n")
        if "subcategories" in cat:
            for sub in cat["subcategories"]:
                out.write(f"  - Subcategory: {sub['name']} ({len(sub['items'])} items)\n")
        elif "items" in cat:
            out.write(f"  - (Direct Items: {len(cat['items'])})\n")
