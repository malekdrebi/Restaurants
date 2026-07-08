import os
import json
import re

def slugify(s):
    if not s: return ""
    s = s.encode('ascii', 'ignore').decode('ascii')
    s = re.sub(r'[^\w\s-]', '', s).strip()
    s = re.sub(r'[-\s]+', '_', s)
    return s.lower()

def clean_json(s):
    s = re.sub(r',\s*([\]}])', r'\1', s)
    return s

def main():
    html_path = 'index.html'
    image_folder = 'images'
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.search(r'const menuData = (\[.*?\]);', content, re.DOTALL)
    if not match: return
    
    json_str = clean_json(match.group(1))
    data = json.loads(json_str)

    files_on_disk = os.listdir(image_folder)
    
    replacements = {} # old_path -> new_path

    def process_node(node):
        if isinstance(node, list):
            for i in node: process_node(i)
        elif isinstance(node, dict):
            if 'image' in node and node['image']:
                old_path = node['image']
                filename = old_path.replace('images/', '')
                
                if not os.path.exists(os.path.join(image_folder, filename)):
                    # Try to find a match
                    en_name = node.get('en_name', '')
                    if not en_name: en_name = node.get('name', 'image')
                    
                    slug = slugify(en_name)
                    # Try to find a file starting with slug
                    best_match = None
                    for f in files_on_disk:
                        if f.startswith(slug) and f.lower().endswith(('.png', '.jpg', '.jpeg')):
                            best_match = f
                            break
                    
                    if not best_match:
                        # Fallback for known tricky ones
                        if "Mixed 3 Skewers" in en_name: best_match = "mixed_3_skewers.png"
                        elif "Seafood Pasta" in en_name: best_match = "rose_sauce.png"
                        elif "Chicken Alfredo" in en_name: best_match = "chicken_alfredo.png"
                        elif "Half Grilled Chicken" in en_name: best_match = "half_grilled_chicken.png"
                        elif "Grilled Bream Meal" in en_name: best_match = "grilled_bream_meal.png"

                    if best_match:
                        replacements[old_path] = f"images/{best_match}"

            for key in ['items', 'subcategories', 'variants']:
                if key in node: process_node(node[key])

    process_node(data)

    # Apply replacements
    new_content = content
    for old, new in sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True):
        new_content = new_content.replace(f'"{old}"', f'"{new}"')

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Applied {len(replacements)} final replacements.")

if __name__ == "__main__":
    main()
