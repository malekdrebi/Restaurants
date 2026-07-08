"""Phase 3 fix: Final cleanup of remaining beverage/smoothie name issues."""
import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

FILE_PATH = r'c:\Users\malek drebi\Desktop\LAVINA\LavinaHouseMenu\index.html'

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'const menuData = (\[.*?\]);', content, re.DOTALL)
data = json.loads(match.group(1))

# Comprehensive mapping using en_name for ALL remaining items
remaining_fixes = {
    # Subcategory names
    "Juice": {"cat_name": "عصائر"},
    "Mojitos": {"cat_name": "موهيتو"},
    
    # Juice items
    "Pineapple Juice": {"name": "عصير أناناس"},
    "Pomegranate Juice": {"name": "عصير رمان"},
    
    # Smoothies
    "Passion Fruit Smoothie": {"name": "سموذي باشن فروت"},
    "Mixed Berry Smoothie": {"name": "سموذي توت مشكل"},
    
    # Mojitos
    "Hawaii Mojito": {"name": "موهيتو هاواي"},
    "Fruit Mojito": {"name": "موهيتو فواكه", "desc": "فراولة، مانجو، أناناس، بطيخ"},
    "Pina Colada Mojito": {"name": "موهيتو بينا كولادا"},
    "Passion Fruit Mojito": {"name": "موهيتو باشن فروت"},
    "Classic Mojito": {"name": "موهيتو كلاسيك"},
    "Strawberry Mojito": {"name": "موهيتو فراولة"},
    
    # Vanilla Milkshake (just to be sure)
    "Vanilla Milkshake": {"name": "ميلك شيك فانيلا"},
    "Oreo Milkshake": {"name": "ميلك شيك أوريو"},
}

def deep_apply(obj):
    if isinstance(obj, list):
        for item in obj:
            deep_apply(item)
    elif isinstance(obj, dict):
        en = obj.get("en_name", "")
        
        # Fix subcategory/category names
        if en in remaining_fixes:
            fix = remaining_fixes[en]
            if "cat_name" in fix:
                obj["name"] = fix["cat_name"]
            if "name" in fix:
                obj["name"] = fix["name"]
            if "desc" in fix:
                obj["desc"] = fix["desc"]
        
        # Recurse
        for key in ["subcategories", "items", "variants"]:
            if key in obj:
                deep_apply(obj[key])

deep_apply(data)

# Rebuild
new_json = json.dumps(data, ensure_ascii=False, indent=4)
new_content = content[:match.start()] + f"const menuData = {new_json};" + content[match.end():]

with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Phase 3 cleanup complete!")
