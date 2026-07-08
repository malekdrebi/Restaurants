import json
import sys
import io

# Force stdout to be utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    with open('the_menu_bilingual.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for i, c in enumerate(data):
        en_name = c.get('en_name', 'No EN')
        ar_name = c.get('name', 'No AR')
        print(f"{i}: {en_name} ({ar_name})")
except Exception as e:
    print(f"Error: {e}")
