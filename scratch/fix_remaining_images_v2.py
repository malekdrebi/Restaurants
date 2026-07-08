import os
import re

def main():
    html_path = 'index.html'
    image_folder = 'images'
    
    # Mapping of current filename -> new filename
    manual_renames = {
        'بيجلز بيض.jpg': 'egg_bagels.jpg',
        'صفيحة جبنة.PNG': 'cheese_sfihah.png',
        'كافي لاتيه.jpg': 'caffe_latte.jpg',
        '.png': 'fruit_pancake.png',
        'Grilled Bream Meal.PNG': 'grilled_bream_meal.png',
        'Half Grilled Chicken.PNG': 'half_grilled_chicken.png',
        'IMG_5382.PNG': 'lavina_house_special.png'
    }
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old_file, new_file in manual_renames.items():
        old_path = os.path.join(image_folder, old_file)
        new_path = os.path.join(image_folder, new_file)
        
        if os.path.exists(old_path):
            try:
                os.rename(old_path, new_path)
                print(f"Renamed a file to {new_file}")
            except Exception as e:
                print(f"Rename failed: {e}")
            
            # Update index.html
            if old_file == '.png':
                content = content.replace('"images/.png"', f'"images/{new_file}"')
            else:
                content = content.replace(f'images/{old_file}', f'images/{new_file}')
        else:
            # Maybe it was already renamed in the JSON but not on disk? 
            # Or vice versa. Let's ensure the JSON is updated even if disk was already done.
            content = content.replace(f'images/{old_file}', f'images/{new_file}')

    # Final check for any remaining Arabic image paths in index.html
    arabic_pattern = re.compile(r'"images/[^"]*[\u0600-\u06FF][^"]*"')
    matches = arabic_pattern.findall(content)
    if matches:
        print(f"Found {len(matches)} remaining Arabic image paths.")
        for match in matches:
            old_fullpath = match.strip('"')
            old_filename = old_fullpath.replace('images/', '')
            found = False
            for f in os.listdir(image_folder):
                if f.lower() == old_filename.lower():
                    new_filename = f"item_{abs(hash(old_filename)) % 1000}.png"
                    try:
                        os.rename(os.path.join(image_folder, f), os.path.join(image_folder, new_filename))
                        content = content.replace(match, f'"images/{new_filename}"')
                        print(f"Auto-fixed an Arabic path to {new_filename}")
                    except:
                        pass
                    found = True
                    break
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated index.html")

if __name__ == "__main__":
    main()
