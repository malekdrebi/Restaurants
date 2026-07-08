import json
import re

def get_themenu_prices():
    with open("TheMenu.txt", "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    
    prices = {}
    for i in range(len(lines)):
        if "د.ل" in lines[i]:
            # The line before this is usually the item name
            # But wait, some items are duplicated in the text file before the price
            # Logic from parse_themenu.py:
            # if i + 1 < len(lines) and is_price(lines[i+1]):
            #     item_name = line
            #     price = lines[i+1]
            if i > 0:
                item_name = lines[i-1]
                # If there's a double line name, handle it?
                # Actually let's just use the same logic as parse_themenu.py
                pass
    
    # Let's just use the logic from parse_themenu.py to be consistent
    subcats = [
        "المقبلات", "السلاطات", "الشوربات", "باستا", "ريزوتو", "صفايح", "بيتزا",
        "سندوتشات", "غربي اسماك وبحريات", "وجبات اطفال", "المطبخ الشرقي", "كريب حار",
        "غربي اللحوم", "غربي الدجاج", "وجبات فاهيتا",
        "المخيتو", "ميلك شيك", "سموثي", "مشروبات معلبه", "ايس كافي", "ايس تي", "فرابتشينو"
    ]
    
    parsed_items = []
    current_items_list = parsed_items
    i = 0
    while i < len(lines):
        line = lines[i]
        if line == "**":
            i += 1
            continue
        if line in subcats:
            i += 1
            continue
        if i + 1 < len(lines) and "د.ل" in lines[i+1]:
            item_name = line
            price = lines[i+1]
            parsed_items.append({"name": item_name, "price": price})
            i += 2
            continue
        i += 1
    return parsed_items

def get_index_prices():
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
    
    start_marker = "// JSON_DATA_START"
    end_marker = "// JSON_DATA_END"
    
    start = content.find(start_marker)
    end = content.find(end_marker)
    
    if start == -1 or end == -1:
        return []
    
    data_str = content[start:end]
    # Extract the JSON part
    json_match = re.search(r"const menuData = (\[.*\]);", data_str, re.DOTALL)
    if not json_match:
        return []
    
    data = json.loads(json_match.group(1))
    
    index_items = []
    def extract_items(obj):
        if isinstance(obj, list):
            for item in obj:
                extract_items(item)
        elif isinstance(obj, dict):
            if "items" in obj:
                extract_items(obj["items"])
            if "subcategories" in obj:
                extract_items(obj["subcategories"])
            if "name" in obj and "price" in obj:
                # Add the main item
                index_items.append({"name": obj["name"], "price": obj["price"]})
                # Check for variants
                if "variants" in obj and obj["variants"]:
                    for v in obj["variants"]:
                        # Variants often have their own name or variant_name
                        v_name = v.get("variant_name") or v.get("name")
                        index_items.append({"name": v_name, "price": v.get("price")})
    
    extract_items(data)
    return index_items

def main():
    menu_txt_items = get_themenu_prices()
    index_items = get_index_prices()
    
    print(f"Items in TheMenu.txt: {len(menu_txt_items)}")
    print(f"Items in index.html: {len(index_items)}")
    
    # Create lookup for index items
    index_lookup = {}
    for item in index_items:
        name = item['name'].strip()
        price = item['price'].strip()
        index_lookup[name] = price

    mismatches = []
    missing_in_index = []
    
    for item in menu_txt_items:
        name = item['name'].strip()
        price = item['price'].strip()
        
        if name not in index_lookup:
            missing_in_index.append(name)
        elif index_lookup[name] != price:
            mismatches.append({"name": name, "txt_price": price, "index_price": index_lookup[name]})
            
    if missing_in_index:
        print("\nMissing in index.html:")
        for m in missing_in_index:
            print(f"- {m}")
            
    if mismatches:
        print("\nPrice mismatches:")
        for m in mismatches:
            print(f"- {m['name']}: TXT={m['txt_price']}, INDEX={m['index_price']}")
    else:
        print("\nNo price mismatches found among matched items!")

if __name__ == "__main__":
    main()
