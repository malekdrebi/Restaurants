import re
import json
import sys

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\malek drebi\Desktop\LAVINA\LavinaHouseMenu\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract menuData JSON
match = re.search(r'const menuData = (\[.*?\]);', content, re.DOTALL)
if not match:
    print("ERROR: Could not find menuData!")
    sys.exit(1)

data = json.loads(match.group(1))

# Collect ALL name/desc fields recursively
def collect_fields(obj, path=""):
    results = []
    if isinstance(obj, list):
        for i, item in enumerate(obj):
            results.extend(collect_fields(item, f"{path}[{i}]"))
    elif isinstance(obj, dict):
        for key in ["name", "desc", "variant_name"]:
            if key in obj and isinstance(obj[key], str) and obj[key]:
                val = obj[key]
                # Check for garbled characters
                garbled_chars = set()
                for ch in val:
                    if ch in '\u0301\u0308\u0327\u200d\u203a\u2039\u2013\u2014\u201c\u201d\u201a\u201e\u0192\u02c6\u02dc\u06af':
                        garbled_chars.add(ch)
                # Also check for known broken patterns
                broken = any(p in val for p in [
                    'برجرجر', 'طلباظع', 'باھ', 'وط2', 'الروط2',
                    'واكة', 'كيكو', 'كيك́', 'كيكن', 'كيكر', 'كيكأ',
                    'ط2', 'أ̧', '́', 'الأبيط', 'اخطر', 'طسل',
                    'وة', ' د\n', 'سوش', 'كيلافينا', 'لوحة شر',
                    'سبانيش\n', 'فاهيتا د\n', 'ببرجر', 'أي̈ر',
                ])
                if garbled_chars or broken:
                    results.append({
                        "path": f"{path}.{key}",
                        "value": val,
                        "en_name": obj.get("en_name", ""),
                        "garbled_chars": list(garbled_chars),
                    })
        for key in ["subcategories", "items", "variants"]:
            if key in obj:
                results.extend(collect_fields(obj[key], f"{path}.{key}"))
    return results

issues = collect_fields(data)
print(f"Found {len(issues)} garbled text fields:\n")
for issue in issues:
    en = issue['en_name'] 
    print(f"  EN: {en}")
    print(f"  AR: {issue['value']}")
    print(f"  Path: {issue['path']}")
    print()

# Also scan HTML template for Mojibake
print("\n=== HTML TEMPLATE MOJIBAKE ===")
mojibake_pattern = re.compile(r'[ظطؤ][§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ„†‡ˆ‰Š‹ŒŽ''""•–—˜™š›œžŸ]')
# Find lines with mojibake in HTML (not in JSON)  
json_start = content.find('const menuData = [')
html_before = content[:json_start]
html_after = content[content.find('];', json_start):]

for section_name, section in [("HTML Before Menu", html_before), ("HTML After Menu", html_after)]:
    lines = section.split('\n')
    for i, line in enumerate(lines):
        if mojibake_pattern.search(line):
            # Skip image paths  
            if '"image"' in line: continue
            stripped = line.strip()
            if stripped and not stripped.startswith('//'):
                print(f"  [{section_name}] {stripped[:120]}")
