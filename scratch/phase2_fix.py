"""Phase 2 fix: Clean up remaining 12 issues after the definitive fix."""
import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

FILE_PATH = r'c:\Users\malek drebi\Desktop\LAVINA\LavinaHouseMenu\index.html'

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# Fix 1: Remaining hardcoded strings in HTML
# ============================================================
# Fix "بقراط،ة" -> "بقراءة" 
content = content.replace('بقراط،ة', 'بقراءة')

# Fix double-جاج issue: "دجاججاج" -> "دجاج"
content = content.replace('دجاججاج', 'دجاج')

# Fix "شاهي" (shahii) -> "شاي" for Tea Pot
content = content.replace('شاهي', 'شاي')

# ============================================================  
# Fix 2: JSON data remaining issues
# ============================================================
match = re.search(r'const menuData = (\[.*?\]);', content, re.DOTALL)
if not match:
    print("ERROR: Could not find menuData!")
    sys.exit(1)

data = json.loads(match.group(1))

def deep_fix(obj):
    if isinstance(obj, list):
        for item in obj:
            deep_fix(item)
    elif isinstance(obj, dict):
        # Fix ALL string fields
        for key in list(obj.keys()):
            if isinstance(obj[key], str):
                val = obj[key]
                # Fix variant_name fields
                val = val.replace('الأبيط', 'الأبيض')
                val = val.replace('الروط2', 'الروزي')
                val = val.replace('صوص الروط2', 'صوص الروزي')
                val = val.replace('بشماط', 'بشمات')
                val = val.replace('ففواكه', 'فواكه')
                val = val.replace('كريب سوشيي', 'كريب سوشي')
                val = val.replace('قهوة عربية', 'قهوة عربية')  # Already clean
                
                # Fix the pizza descs with garbled text
                if 'روات' in val and 'جبنة' in val:
                    if obj.get('en_name') == 'Vegetable' or obj.get('en_desc', '').startswith('Veg'):
                        val = 'خضروات، جبنة، فلفل أخضر، طماطم، زيتون و بصل'
                if 'وة، ا و بصل' in val:
                    val = 'جبنة، تونة، طماطم و بصل.'
                if 'ة راط' in val or 'ا ̈' in val:
                    if obj.get('en_name') == 'Pesto Pizza':
                        val = 'صوص بيستو، جبنة، طماطم مجففة'
                
                # Clean leftover garbled chars
                val = val.replace('̈', '')
                val = val.replace('́', '')
                val = val.replace('‍', '')
                val = val.replace('̧', '')
                
                # Clean double spaces
                while '  ' in val:
                    val = val.replace('  ', ' ')
                
                obj[key] = val.strip()
        
        # Recurse into nested structures
        for key in ['subcategories', 'items', 'variants']:
            if key in obj:
                deep_fix(obj[key])

deep_fix(data)

# ============================================================
# Fix 3: Fix the isFeatured check in JS to match new category names
# ============================================================
new_json = json.dumps(data, ensure_ascii=False, indent=4)
new_content = content[:match.start()] + f"const menuData = {new_json};" + content[match.end():]

# Fix the featured category name matching in JS
new_content = new_content.replace(
    "category.name === 'الأكثر طلبا' || category.name === 'الأسرع طلبا'",
    "category.name === 'الأكثر طلباً' || category.name === 'الأسرع طلباً'"
)

# Also check for a different version of the check
new_content = new_content.replace(
    "category.name === 'الأكثر طلبا'",
    "category.name === 'الأكثر طلباً'"
)
new_content = new_content.replace(
    "category.name === 'الأسرع طلبا'",  
    "category.name === 'الأسرع طلباً'"
)

with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Phase 2 cleanup complete!")
