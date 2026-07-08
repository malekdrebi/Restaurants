import os
import json
import re
import sys

# Ensure UTF-8 output even if the terminal is problematic
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')

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
    image_folder = 'Images' 
    
    # Check if images folder exists (case-sensitive check is hard on Windows, but let's see)
    if not os.path.exists(image_folder):
        if os.path.exists('images'):
            image_folder = 'images'
        else:
            print("No image folder found")
            return

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find menuData
    match = re.search(r'const menuData = (\[.*?\]);', content, re.DOTALL)
    if not match: 
        print("Menu data not found in HTML")
        return
    
    json_str = clean_json(match.group(1))
    try:
        data = json.loads(json_str)
    except Exception as e:
        print(f"JSON Parse error: {e}")
        return

    files_on_disk = os.listdir(image_folder)
    print(f"Files found on disk: {len(files_on_disk)}")
    
    mapping = {} 

    def process_node(node):
        if isinstance(node, list):
            for i in node: process_node(i)
        elif isinstance(node, dict):
            if 'image' in node and node['image'] and node['image'].startswith('images/'):
                old_path = node['image']
                old_filename = old_path.replace('images/', '')
                
                # Check if it exists (case-insensitive find because disk might be different)
                found_actual_name = None
                for fname in files_on_disk:
                    if fname.lower() == old_filename.lower():
                        found_actual_name = fname
                        break
                
                if found_actual_name:
                    en_name = node.get('en_name', '')
                    if not en_name:
                        en_name = node.get('name', 'image')
                    
                    new_filename_base = slugify(en_name)
                    ext = os.path.splitext(found_actual_name)[1].lower()
                    if not ext: ext = '.png'
                    
                    new_filename = f"{new_filename_base}{ext}"
                    
                    # Store mapping
                    mapping[old_path] = f"images/{new_filename}"
                    
                    # Do the physical rename
                    old_disk_path = os.path.join(image_folder, found_actual_name)
                    new_disk_path = os.path.join(image_folder, new_filename)
                    if old_disk_path != new_disk_path:
                        try:
                            # If destination exists, add a suffix
                            counter = 1
                            final_new_filename = new_filename
                            while os.path.exists(os.path.join(image_folder, final_new_filename)) and old_disk_path.lower() != os.path.join(image_folder, final_new_filename).lower():
                                final_new_filename = f"{new_filename_base}_{counter}{ext}"
                                counter += 1
                            
                            final_new_path = os.path.join(image_folder, final_new_filename)
                            os.rename(old_disk_path, final_new_path)
                            mapping[old_path] = f"images/{final_new_filename}"
                            print(f"Renamed: {found_actual_name} -> {final_new_filename}")
                        except Exception as e:
                            print(f"Failed to rename: {e}")

            for key in ['items', 'subcategories', 'variants']:
                if key in node: process_node(node[key])

    process_node(data)

    # Update index.html content
    new_content = content
    # Sort mapping by length desc to avoid partial replacements
    for old_path, new_path in sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True):
        safe_old = re.escape(old_path)
        new_content = re.sub(f'"{safe_old}"', f'"{new_path}"', new_content)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Updated index.html")
    
    # Final step: If folder is Images, try to rename to images
    if image_folder == 'Images':
        try:
            # Use os.rename with tmp to handle case switch on Windows
            os.rename('Images', 'images_tmp')
            os.rename('images_tmp', 'images')
            print("Renamed folder Images -> images")
        except Exception as e:
            print(f"Note: Folder rename failed (might already be lowercase or in use): {e}")

if __name__ == "__main__":
    main()
