import os
import json
import re

def main():
    html_path = 'index.html'
    if not os.path.exists(html_path):
        print("index.html not found")
        return

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find menuData
    match = re.search(r'const menuData = (\[.*?\]);', content, re.DOTALL)
    if not match:
        print("menuData not found")
        return

    try:
        data = json.loads(match.group(1))
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        # Try a more lenient approach if it fails
        return

    referenced_images = []
    def collect_images(node):
        if isinstance(node, list):
            for i in node: collect_images(i)
        elif isinstance(node, dict):
            if 'image' in node and node['image']:
                referenced_images.append(node['image'])
            for key in ['items', 'subcategories', 'variants']:
                if key in node:
                    collect_images(node[key])

    collect_images(data)
    referenced_images = sorted(list(set(referenced_images)))

    print(f"Total referenced images: {len(referenced_images)}")
    
    # Check physical folders
    folders = ['Images', 'images']
    
    for folder in folders:
        print(f"\nChecking folder: {folder}")
        if not os.path.isdir(folder):
            print(f"Folder '{folder}' does not exist")
            continue
        
        existing_files = os.listdir(folder)
        found = 0
        missing = []
        for img in referenced_images:
            # Expected relative path in JSON is "images/filename.ext"
            if img.startswith('images/'):
                filename = img[7:] # remove "images/"
                if filename in existing_files:
                    found += 1
                else:
                    missing.append(filename)
            else:
                print(f"Unknown image path format: {img}")

        print(f"Found: {found}/{len(referenced_images)}")
        if missing:
            print("Missing files (partial list):")
            for m in missing[:10]:
                print(f" - {m}")

if __name__ == "__main__":
    main()
