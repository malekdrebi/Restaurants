import os
import json
import re

def clean_json(s):
    # Remove trailing commas
    s = re.sub(r',\s*([\]}])', r'\1', s)
    return s

def main():
    html_path = 'index.html'
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.search(r'const menuData = (\[.*?\]);', content, re.DOTALL)
    if not match: return
    
    json_str = clean_json(match.group(1))
    data = json.loads(json_str)

    referenced_images = []
    def collect_images(node):
        if isinstance(node, list):
            for i in node: collect_images(i)
        elif isinstance(node, dict):
            if 'image' in node and node['image']:
                referenced_images.append(node['image'])
            for key in ['items', 'subcategories', 'variants']:
                if key in node: collect_images(node[key])

    collect_images(data)
    referenced_images = sorted(list(set(referenced_images)))

    folders = ['Images', 'images']
    for folder in folders:
        if not os.path.isdir(folder): continue
        files = os.listdir(folder)
        found = []
        missing = []
        for img in referenced_images:
            fname = img.replace('images/', '')
            if fname in files: found.append(fname)
            else: missing.append(fname)
        print(f"Folder '{folder}': Found {len(found)}, Missing {len(missing)}")
        if missing:
            print(f"First 5 missing: {missing[:5]}")

if __name__ == "__main__":
    main()
