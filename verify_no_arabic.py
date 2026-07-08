import json
import re

def has_arabic(text):
    return bool(re.search(r'[\u0600-\u06FF]', str(text)))

with open('the_menu_bilingual.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def check_recursive(obj, path=""):
    errors = []
    if isinstance(obj, list):
        for i, item in enumerate(obj):
            errors.extend(check_recursive(item, f"{path}[{i}]"))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k in ['en_name', 'en_desc', 'variant_en_name']:
                if has_arabic(v):
                    errors.append(f"{path} -> {k}: {v}")
            errors.extend(check_recursive(v, f"{path}.{k}"))
    return errors

errors = check_recursive(data)
with open('arabic_errors.txt', 'w', encoding='utf-8') as f:
    if errors:
        f.write("Found Arabic in English fields:\n")
        for err in errors:
            f.write(err + "\n")
    else:
        f.write("No Arabic found in English fields!")
