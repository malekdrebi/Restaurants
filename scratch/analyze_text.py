import re
import sys

file_path = r'c:\Users\malek drebi\Desktop\LAVINA\LavinaHouseMenu\index.html'

def is_garbled(s):
    # Standard Arabic characters are in U+0600 - U+06FF
    # Presentation forms are in U+FB50 - U+FDFF and U+FE70 - U+FEFF
    # Garbled characters (Latin-1 misinterpreted as CP1256) often have extended ASCII
    if any(ord(c) > 0x7FF for c in s): # Simplistic check for non-standard/garbled
        return True
    if any(0xFB50 <= ord(c) <= 0xFEFF for c in s):
        return True
    return False

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all strings in quotes that might be names or descriptions
matches = re.findall(r'\"(?:name|desc)\":\s*\"([^\"]+)\"', content)

unique_garbled = set()
for m in matches:
    if is_garbled(m):
        unique_garbled.add(m)

print(f"Found {len(unique_garbled)} unique potentially garbled strings.")
for s in sorted(list(unique_garbled))[:100]:
    print(s)
