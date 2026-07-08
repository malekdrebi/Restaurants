import json

def find_duplicates():
    with open('the_menu_bilingual.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    all_items = []
    for cat in data:
        # Top level items
        for item in cat.get('items', []):
            all_items.append((cat.get('en_name'), 'none', item))
        # Subcategory items
        for sub in cat.get('subcategories', []):
            for item in sub.get('items', []):
                all_items.append((cat.get('en_name'), sub.get('en_name'), item))

    # Print any items that share the same en_name or have very similar names
    from collections import defaultdict
    by_name = defaultdict(list)
    for cat_name, sub_name, item in all_items:
        by_name[item.get('en_name')].append((cat_name, sub_name, item))

    with open('scratch/duplicates_check.txt', 'w', encoding='utf-8') as f:
        for name, items in by_name.items():
            if len(items) > 1:
                f.write(f"--- {name} ({len(items)} items) ---\n")
                for c, s, i in items:
                    f.write(f"  Cat: {c}, Sub: {s}\n")
                    f.write(f"  Ar Name: {i.get('name')}\n")
                    f.write(f"  Price: {i.get('price')}\n")
                    f.write(f"  Image: {i.get('image')}\n")
                    f.write(f"  Desc: {i.get('desc')}\n\n")

if __name__ == "__main__":
    find_duplicates()
