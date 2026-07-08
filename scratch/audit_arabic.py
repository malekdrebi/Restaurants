import re
import sys

def extract_arabic(content):
    pattern = r'\"(name|desc|variant_name)\":\s*\"([^\"]*)\"'
    matches = re.finditer(pattern, content)
    results = []
    for m in matches:
        key, val = m.groups()
        if any('\u0600' <= c <= '\u06FF' for c in val) or any(ord(c) > 127 for c in val):
            results.append((key, val))
    return results

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

arabic_data = extract_arabic(content)
with open('scratch/audit_results.txt', 'w', encoding='utf-8') as out:
    for key, val in arabic_data:
        out.write(f"{key}: {val}\n")
