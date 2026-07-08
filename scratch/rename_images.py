import os
import json
import re

def slugify(s):
    # Keep only alphanumeric and spaces, then replace spaces with underscores, and lowercase
    s = s.encode('ascii', 'ignore').decode('ascii')
    s = re.sub(r'[^\w\s-]', '', s).strip()
    s = re.sub(r'[-\s]+', '_', s)
    return s.lower()

def clean_json(s):
    # Remove trailing commas
    s = re.sub(r',\s*([\]}])', r'\1', s)
    return s

def main():
    html_path = 'index.html'
    image_folder = 'Images' # Currently capital I on disk
    
    if not os.path.isdir(image_folder):
        print(f"Folder {image_folder} not found")
        return

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find menuData
    match = re.search(r'const menuData = (\[.*?\]);', content, re.DOTALL)
    if not match: return
    
    json_str = clean_json(match.group(1))
    data = json.loads(json_str)

    files_on_disk = os.listdir(image_folder)
    
    mapping = {} # old_path_in_json -> new_filename

    def process_node(node):
        if isinstance(node, list):
            for i in node: process_node(i)
        elif isinstance(node, dict):
            if 'image' in node and node['image'] and node['image'].startswith('images/'):
                old_path = node['image']
                old_filename = old_path.replace('images/', '')
                
                # If file exists on disk
                if old_filename in files_on_disk:
                    en_name = node.get('en_name', '')
                    if not en_name:
                        en_name = node.get('name', 'image') # Fallback
                    
                    new_filename_base = slugify(en_name)
                    ext = os.path.splitext(old_filename)[1].lower()
                    if not ext: ext = '.png'
                    
                    new_filename = f"{new_filename_base}{ext}"
                    
                    # Store mapping
                    mapping[old_path] = f"images/{new_filename}"
                    
                    # Do the physical rename
                    old_disk_path = os.path.join(image_folder, old_filename)
                    new_disk_path = os.path.join(image_folder, new_filename)
                    if old_disk_path != new_disk_path:
                        try:
                            # If destination exists, add a suffix
                            counter = 1
                            while os.path.exists(new_disk_path) and old_disk_path.lower() != new_disk_path.lower():
                                new_disk_path = os.path.join(image_folder, f"{new_filename_base}_{counter}{ext}")
                                counter += 1
                                
                            os.rename(old_disk_path, new_disk_path)
                            print(f"Renamed: {old_filename} -> {os.path.basename(new_disk_path)}")
                        except Exception as e:
                            print(f"Failed to rename {old_filename}: {e}")

            for key in ['items', 'subcategories', 'variants']:
                if key in node: process_node(node[key])

    process_node(data)

    # Update index.html content
    new_content = content
    # Sort mapping by length desc to avoid partial replacements
    for old_path, new_path in sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True):
        # Escape for regex because of parens in Arabic names
        safe_old = re.escape(old_path)
        new_content = re.sub(f'"{safe_old}"', f'"{new_path}"', new_content)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Updated index.html")

if __name__ == "__main__":
    main()
