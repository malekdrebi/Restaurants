"""Phase 5 fix: Fix all remaining garbled pizza descriptions and other stray items."""
import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

FILE_PATH = r'c:\Users\malek drebi\Desktop\LAVINA\LavinaHouseMenu\index.html'

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'const menuData = (\[.*?\]);', content, re.DOTALL)
data = json.loads(match.group(1))

# Fix all remaining descs by en_name using the en_desc as guide
desc_fixes = {
    # Pizza descs
    "Mushroom": "جبنة، فقع، طماطم و بصل.",
    "Regina Pizza": "صوص، جبنة، فقع، سلامي وريحان.",
    "Quattro Formaggi Pizza": "أربعة أنواع من الجبنة",
    "Chicken Pizza": "صوص، جبنة، دجاج",
    "Bianca Pizza": "صوص أبيض، جبنة وجمبري.",
    "Margherita": "جبنة موزاريلا، جبنة شيدر وطماطم",
}

def deep_fix_descs(obj):
    if isinstance(obj, list):
        for item in obj:
            deep_fix_descs(item)
    elif isinstance(obj, dict):
        en = obj.get("en_name", "")
        
        if en in desc_fixes:
            obj["desc"] = desc_fixes[en]
        
        # Generic cleanup for any remaining one-off garbled chars
        if "desc" in obj and isinstance(obj["desc"], str):
            d = obj["desc"]
            # Remove stray combining/control characters
            cleaned = []
            for ch in d:
                if ch in '\u0301\u0308\u0327\u200d\u203a\u2039\u06af':
                    continue
                cleaned.append(ch)
            d = ''.join(cleaned)
            # Clean double spaces  
            while '  ' in d:
                d = d.replace('  ', ' ')
            obj["desc"] = d.strip()
        
        for key in ["subcategories", "items", "variants"]:
            if key in obj:
                deep_fix_descs(obj[key])

deep_fix_descs(data)

# Rebuild
new_json = json.dumps(data, ensure_ascii=False, indent=4)
new_content = content[:match.start()] + f"const menuData = {new_json};" + content[match.end():]

with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Phase 5 pizza desc fix complete!")
