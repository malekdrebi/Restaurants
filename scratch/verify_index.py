import re
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find the navContainer section or just all nav-item links
# The renderer generates: <a href="#cat_${index}" class="nav-item ...">
# But the apply_menu.py just replaces menuData.
# The actual nav items are rendered at runtime by JS.
# So I should check the menuData array in index.html.

start_marker = "const menuData = "
start_idx = html.find(start_marker)
if start_idx != -1:
    end_idx = html.find("];", start_idx)
    if end_idx != -1:
        json_str = html[start_idx + len(start_marker):end_idx + 1]
        import json
        data = json.loads(json_str)
        print("Categories in index.html:")
        for i, c in enumerate(data):
            print(f"{i}: {c.get('en_name')} ({c.get('name')})")
    else:
        print("End marker not found")
else:
    print("Start marker not found")
