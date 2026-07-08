import json
import re

with open("index_source.html", "r", encoding="utf-8") as f:
    html = f.read()

menu_data = []

category_blocks = re.finditer(r'class="[^"]*menu-category-item menu-category-(\d+)"[^>]*>(.*?)((?=class="[^"]*menu-category-item)|$)', html, re.DOTALL)

cat_names = {}
for match in re.finditer(r'<a href="#" data-catid="(\d+)" class="menu-category">.*?</i>\s*(.*?)</a>', html, re.DOTALL):
    cat_names[match.group(1)] = match.group(2).strip()

def parse_items(html_chunk):
    items = []
    seen = set()
    for m in re.finditer(r'<div class="section-menu" data-id="(\d+)" data-name="(.*?)" data-price="(.*?)" data-amount=".*?" data-description="(.*?)" data-image-url="(.*?)">', html_chunk, re.DOTALL):
        item_id = m.group(1)
        if item_id in seen: continue
        seen.add(item_id)
        items.append({
            "name": m.group(2).strip(),
            "price": m.group(3).strip(),
            "desc": m.group(4).strip(),
            "image": m.group(5).strip() if "default.png" not in m.group(5) else ""
        })
    return items

for block in category_blocks:
    cat_id = block.group(1)
    block_html = block.group(2)
    cat_name = cat_names.get(cat_id, "Unknown Category")
    
    subcategories = []
    
    parts = block_html.split('<div class="card">')
    top_level_html = parts[0]
    
    for part in parts[1:]:
        m_title = re.search(r'<a class="card-title"[^>]*>(.*?)</a>', part)
        if m_title:
            sub_name = m_title.group(1).strip()
            sub_items = parse_items(part)
            if sub_items:
                subcategories.append({
                    "name": sub_name,
                    "items": sub_items
                })
        
    top_items = parse_items(top_level_html)
    
    cat_data = {
        "id": "cat_" + cat_id,
        "name": cat_name,
        "arabic": cat_name
    }
    
    if top_items:
        cat_data["items"] = top_items
    if subcategories:
        cat_data["subcategories"] = subcategories
        
    if top_items or subcategories:
        menu_data.append(cat_data)

with open("scraped_menu.json", "w", encoding="utf-8") as f:
    json.dump(menu_data, f, ensure_ascii=False, indent=4)
print("Saved scraped_menu.json with subcategories")
