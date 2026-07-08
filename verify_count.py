import json
import re

with open("index_source.html", encoding="utf-8") as f:
    html = f.read()

# Find all menu items in HTML by their unique node
html_items = re.findall(r'<div class="section-menu" data-id="(\d+)"', html)
unique_html_items = set(html_items)

print(f"Total HTML section-menu nodes: {len(html_items)}")
print(f"Unique section-menu data-ids: {len(unique_html_items)}")

with open("scraped_menu.json", encoding="utf-8") as f:
    data = json.load(f)

json_count = 0
for cat in data:
    if "items" in cat:
        json_count += len(cat["items"])
    if "subcategories" in cat:
        for sub in cat["subcategories"]:
            json_count += len(sub["items"])

print(f"Items extracted into JSON: {json_count}")
