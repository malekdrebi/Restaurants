import json

def update_hot_drinks_structure():
    with open("the_menu_bilingual.json", "r", encoding="utf-8") as f:
        menu = json.load(f)

    # Find "Hot Drinks" category
    hot_drinks = None
    for cat in menu:
        if cat["name"] == "مشروبات ساخنه" or cat["en_name"] == "Hot Drinks":
            hot_drinks = cat
            break
    
    if not hot_drinks:
        print("Hot Drinks category not found")
        return

    # Items to move
    target_names = ["ﺑﺴﺘﺎﺷﻴﻮ", "ﻟﻮﺗﺲ", "ﺷﻮﻛﻠﺖ", "مارشميلو"]
    items_to_move = []
    remaining_items = []

    for item in hot_drinks.get("items", []):
        if item["name"] in target_names:
            # Also fix Pistachio en_name while we are at it
            if item["name"] == "ﺑﺴﺘﺎﺷﻴﻮ":
                item["en_name"] = "Pistachio"
            items_to_move.append(item)
        else:
            remaining_items.append(item)

    # Create new subcategory
    hot_chocolate_sub = {
        "name": "شوكولاتة ساخنة",
        "en_name": "Hot Chocolate",
        "items": items_to_move
    }

    # Add to subcategories
    if "subcategories" not in hot_drinks:
        hot_drinks["subcategories"] = []
    
    # Prepend or append? Usually subcategories appear before direct items in my layout or they are handled separately.
    # In my index.html, categories render subcategories first then local items.
    hot_drinks["subcategories"].append(hot_chocolate_sub)
    hot_drinks["items"] = remaining_items

    with open("the_menu_bilingual.json", "w", encoding="utf-8") as f:
        json.dump(menu, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    update_hot_drinks_structure()
    print("Updated Hot Drinks structure: Moved Hot Chocolate items to sub-category.")
