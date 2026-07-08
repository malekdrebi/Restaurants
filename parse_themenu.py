import json

with open("TheMenu.txt", "r", encoding="utf-8") as f:
    raw_lines = f.read().splitlines()

lines = [l.strip() for l in raw_lines if l.strip() and l.strip() != ""]

def is_price(txt):
    return "د.ل" in txt

subcats = [
    "المقبلات", "السلاطات", "الشوربات", "باستا", "ريزوتو", "صفايح", "بيتزا",
    "سندوتشات", "غربي اسماك وبحريات", "وجبات اطفال", "المطبخ الشرقي", "كريب حار",
    "غربي اللحوم", "غربي الدجاج", "وجبات فاهيتا",
    "المخيتو", "ميلك شيك", "سموثي", "مشروبات معلبه", "ايس كافي", "ايس تي", "فرابتشينو"
]

categories = []
current_cat = None
current_subcat = None
current_items_list = None 

i = 0
while i < len(lines):
    line = lines[i]
    if line == "**":
        if i + 1 < len(lines) and lines[i+1] != "**":
            # New category
            cat_name = lines[i+1]
            current_cat = {"name": cat_name, "subcategories": [], "items": []}
            categories.append(current_cat)
            current_subcat = None
            current_items_list = current_cat["items"]
            i += 2
            continue
        i += 1
        continue
    
    if current_cat is None:
        i += 1
        continue

    # Skip exact duplicate item names
    if i + 1 < len(lines) and line == lines[i+1] and not is_price(line):
        i += 1
        continue

    # New subcategory
    if line in subcats:
        current_subcat = {"name": line, "items": []}
        current_cat["subcategories"].append(current_subcat)
        current_items_list = current_subcat["items"]
        i += 1
        continue

    # New Item
    if i + 1 < len(lines) and is_price(lines[i+1]):
        item_name = line
        price = lines[i+1]
        desc_lines = []
        i += 2
        
        while i < len(lines) and lines[i] != "**":
            if lines[i] in subcats:
                break
            if i + 1 < len(lines) and is_price(lines[i+1]):
                break
            if i + 2 < len(lines) and is_price(lines[i+2]) and lines[i] == lines[i+1]:
                break
            
            desc_lines.append(lines[i])
            i += 1
            
        current_items_list.append({
            "name": item_name,
            "price": price,
            "desc": " ".join(desc_lines),
            "image": ""
        })
        continue

    # If we get here, it's a stray line, but our logic should cover everything
    i += 1

with open("the_menu.json", "w", encoding="utf-8") as f:
    json.dump(categories, f, ensure_ascii=False, indent=4)

with open("counts_new.txt", "w", encoding="utf-8") as out:
    out.write(f"Categories parsed: {len(categories)}\n")
    for c in categories:
        sc = len(c['subcategories'])
        items = sum(len(s['items']) for s in c['subcategories']) + len(c['items'])
        out.write(f"- {c['name']} (Subcats: {sc}, Total Items: {items})\n")
