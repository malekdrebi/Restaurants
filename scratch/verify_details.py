import json
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

start_marker = "const menuData = "
start_idx = html.find(start_marker)
if start_idx != -1:
    end_idx = html.find("];", start_idx)
    if end_idx != -1:
        json_str = html[start_idx + len(start_marker):end_idx + 1]
        data = json.loads(json_str)
        
        main_courses = data[6] # Index 6 based on previous output
        print(f"\nMain Courses ({main_courses.get('en_name')}):")
        for sub in main_courses.get('subcategories', []):
            print(f" - {sub.get('en_name')} ({sub.get('name')})")

        beverages = data[8] # Index 8
        print(f"\nBeverages ({beverages.get('en_name')}):")
        for sub in beverages.get('subcategories', []):
            print(f" - {sub.get('en_name')} ({sub.get('name')})")
    else:
        print("End marker not found")
else:
    print("Start marker not found")
