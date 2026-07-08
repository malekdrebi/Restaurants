"""Phase 4 fix: Final remaining items."""
import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

FILE_PATH = r'c:\Users\malek drebi\Desktop\LAVINA\LavinaHouseMenu\index.html'

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'const menuData = (\[.*?\]);', content, re.DOTALL)
data = json.loads(match.group(1))

# Final remaining fixes by en_name
final_fixes = {
    "Regular Iced Coffee": {"name": "آيس كوفي سادة"},
    "Mint": {"name": "نعناع"},  # Variant
    "Peach": {"name": "خوخ"},
    "Cinnamon": {"name": "قرفة"},
    "Berry": {"name": "توت"},
    "Classic": {"name": "كلاسيك"},
}

# Fix subcategory name "فرابوتشينو" -> "فرابتشينو"
def deep_fix(obj):
    if isinstance(obj, list):
        for item in obj:
            deep_fix(item)
    elif isinstance(obj, dict):
        en = obj.get("en_name", "")
        
        if en in final_fixes:
            for k, v in final_fixes[en].items():
                obj[k] = v
        
        # Fix Frappuccino subcategory name
        if en == "Frappuccino" and obj.get("name") in ["فرابوتشينو", "فرابتشينو"]:
            obj["name"] = "فرابتشينو"
        
        # Fix any remaining variant name issues  
        if "name" in obj and isinstance(obj["name"], str):
            n = obj["name"]
            n = n.replace("نطناط", "نعناع")
            n = n.replace("طادي", "سادة")
            n = n.replace("فرابوتشينو", "فرابتشينو")
            n = n.replace("ههاواي", "هاواي")
            n = n.replace("موخيتو", "موهيتو")
            obj["name"] = n
        
        for key in ["subcategories", "items", "variants"]:
            if key in obj:
                deep_fix(obj[key])

deep_fix(data)

# Rebuild
new_json = json.dumps(data, ensure_ascii=False, indent=4)
new_content = content[:match.start()] + f"const menuData = {new_json};" + content[match.end():]

with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Phase 4 final cleanup complete!")
