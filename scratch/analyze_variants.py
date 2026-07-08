import json
import os
from collections import Counter

def analyze_menu():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            data = f.read()
        
        start = data.find('const menuData = [')
        end = data.find('];', start)
        if start == -1 or end == -1:
            print("Could not find menuData in index.html")
            return
            
        json_str = data[start + 17 : end + 1]
        menu_data = json.loads(json_str)
        
        all_items = []
        def collect(cats, category_name=""):
            for cat in cats:
                name = cat.get('name', category_name)
                if 'items' in cat:
                    for item in cat['items']:
                        item['_cat'] = name
                        all_items.append(item)
                if 'subcategories' in cat:
                    collect(cat['subcategories'], name)
                    
        collect(menu_data)
        
        # Find duplicates by name/en_name within the same category
        # (excluding 'Most Ordered' / 'Fastest Ordered' as those are duplicates by design)
        
        filtered_items = [i for i in all_items if i['_cat'] not in ['الأكثر طلباً', 'Most Ordered', 'الأسرع طلباً', 'Fastest Ordered']]
        
        # Group by name + category
        groups = {}
        for item in filtered_items:
            key = (item.get('name'), item['_cat'])
            if key not in groups:
                groups[key] = []
            groups[key].append(item)
            
        candidates = {k: v for k, v in groups.items() if len(v) > 1}
        
        print(f"Total items analyzed (excluding design duplicates): {len(filtered_items)}")
        print(f"Found {len(candidates)} groups of items with same name in same category:")
        
        for (name, cat), items in candidates.items():
            print(f"\nGroup: {name} (Category: {cat})")
            for i, item in enumerate(items):
                print(f"  {i+1}. Price: {item.get('price')}, Desc: {item.get('desc')}, en_name: {item.get('en_name')}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_menu()
