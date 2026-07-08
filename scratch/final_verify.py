"""Final comprehensive validation scan."""
import re
import json
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')

FILE_PATH = r'c:\Users\malek drebi\Desktop\LAVINA\LavinaHouseMenu\index.html'

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'const menuData = (\[.*?\]);', content, re.DOTALL)
data = json.loads(match.group(1))

# Questionable characters that shouldn't be in proper Arabic text
bad_chars = set('\u0301\u0308\u0327\u200d\u203a\u2039\u06af\u0192\u02c6\u02dc')

issues = []

def scan(obj, path=""):
    if isinstance(obj, list):
        for i, item in enumerate(obj):
            scan(item, f"{path}[{i}]")
    elif isinstance(obj, dict):
        for key in ["name", "desc", "variant_name"]:
            if key in obj and isinstance(obj[key], str) and obj[key]:
                val = obj[key]
                en = obj.get("en_name", obj.get("en_desc", ""))
                
                # Check for bad characters
                bad_found = [ch for ch in val if ch in bad_chars]
                
                # Check for known broken patterns
                broken_found = []
                broken_patterns = [
                    'برجرجر', 'طلباظع', 'الأبيط', 'الروط2', 'وط2', 'ط2',
                    'طسل', '́', 'واكة', 'ع‍', 'باھ', 'كيكو', 'كيكأ',
                    'أاأ', 'ههاواي', 'نطناط', 'طادي', 'فرابوت', 'صوصير',
                    'المخيتو', 'أااس', 'سوك ',
                ]
                for p in broken_patterns:
                    if p in val:
                        broken_found.append(p)
                
                if bad_found or broken_found:
                    issues.append({
                        "path": f"{path}.{key}",
                        "value": val,
                        "en": en,
                        "bad_chars": bad_found,
                        "broken": broken_found,
                    })
        
        for key in ["subcategories", "items", "variants"]:
            if key in obj:
                scan(obj[key], f"{path}.{key}")

scan(data)

if issues:
    print(f"Found {len(issues)} remaining issues:\n")
    for issue in issues:
        print(f"  EN: {issue['en']}")
        print(f"  AR: {issue['value']}")
        print(f"  Path: {issue['path']}")
        if issue['bad_chars']:
            print(f"  Bad chars: {[hex(ord(c)) for c in issue['bad_chars']]}")
        if issue['broken']:
            print(f"  Broken patterns: {issue['broken']}")
        print()
else:
    print("✓ ALL TEXT IS CLEAN! No garbled characters or broken patterns found.")

# Also verify HTML template
print("\n=== HTML Template Check ===")
# Check for mojibake in non-JSON parts
json_start = content.find('const menuData = [')
json_end = content.find('];', json_start) + 2

html_parts = content[:json_start] + content[json_end:]

mojibake_patterns = ['ط§', 'ظ†', 'ظپ', 'ظٹ', 'ط®', 'ظ‡', 'ظ„', 'طھ', 'ظ…', 'ط³',
                     'ط­', 'طµ', 'ط¶', 'ط·', 'ط¸', 'ط¹', 'ط¨', 'ظˆ', 'ط±', 'ط¯',
                     'ط¬', 'ط£', 'ط¥', 'ط¤', 'ط©', 'ظ‰', 'ط؛', 'ظ‚', 'ظƒ', 'طŒ', 'طں']

html_mojibake = 0
for p in mojibake_patterns:
    c = html_parts.count(p)
    if c > 0:
        html_mojibake += c
        print(f"  WARNING: '{p}' found {c} times in HTML template")

if html_mojibake == 0:
    print("  ✓ HTML template is clean - no Mojibake detected")

# Print all category and subcategory names for visual verification
print("\n=== Category Names ===")
def show_structure(obj, indent=0):
    if isinstance(obj, list):
        for item in obj:
            show_structure(item, indent)
    elif isinstance(obj, dict):
        if "name" in obj and ("items" in obj or "subcategories" in obj):
            en = obj.get("en_name", "")
            print(f"{'  ' * indent}• {obj['name']} ({en})")
        if "subcategories" in obj:
            for sub in obj["subcategories"]:
                show_structure(sub, indent + 1)

show_structure(data)
