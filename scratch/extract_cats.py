import re
import json

file_path = r'c:\Users\malek drebi\Desktop\LAVINA\LavinaHouseMenu\index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'const menuData = (\[.*?\]);', content, re.DOTALL)
if match:
    data = json.loads(match.group(1))
    
    mapping = []
    
    for cat in data:
        mapping.append({
            "type": "category",
            "name": cat.get("name"),
            "en_name": cat.get("en_name")
        })
        for sub in cat.get("subcategories", []):
            mapping.append({
                "type": "subcategory",
                "name": sub.get("name"),
                "en_name": sub.get("en_name")
            })
            for item in sub.get("items", []):
                 # Just categories and subcategories for now
                 pass
        for item in cat.get("items", []):
             pass

    with open(r'c:\Users\malek drebi\Desktop\LAVINA\LavinaHouseMenu\scratch\cat_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=4)
