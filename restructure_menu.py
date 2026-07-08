import json
import os
import copy

def restructure():
    # Load from the source
    with open('the_menu_bilingual.json', 'r', encoding='utf-8') as f:
        data_raw = json.load(f)

    # Filter out any existing featured categories to prevent duplication if re-run
    featured_names = ['Most Ordered', 'Fastest Ordered', 'الأكثر طلباً', 'الأسرع طلباً']
    data = [c for c in data_raw if c.get('en_name') not in featured_names and c.get('name') not in featured_names]

    # Helper to find category by English name
    def find_cat(en_name):
        for c in data:
            if c.get('en_name') == en_name:
                return c
        return None

    # 1. Consolidate Beverages (Hot Drinks + Fresh Juices -> Beverages)
    fresh_juices = find_cat('Fresh Juices')
    hot_drinks = find_cat('Hot Drinks')
    
    # Create or find Beverages category
    bev_cat = find_cat('Beverages')
    if not bev_cat:
        # Check if we can rename Fresh Juices or create new
        if fresh_juices:
            bev_cat = fresh_juices
            bev_cat['en_name'] = 'Beverages'
            bev_cat['name'] = 'المشروبات'
        else:
            bev_cat = {'name': 'المشروبات', 'en_name': 'Beverages', 'subcategories': [], 'items': []}
            data.append(bev_cat)

    if hot_drinks and hot_drinks != bev_cat:
        # Move hot drinks into bev subcategories
        hot_sub = {
            'name': hot_drinks['name'],
            'en_name': hot_drinks['en_name'],
            'items': hot_drinks['items']
        }
        if 'subcategories' not in bev_cat: bev_cat['subcategories'] = []
        # Check if hot drinks already moved
        if not any(s['en_name'] == 'Hot Drinks' for s in bev_cat['subcategories']):
            bev_cat['subcategories'].append(hot_sub)
        # Remove top-level Hot Drinks
        data = [c for c in data if c['en_name'] != 'Hot Drinks' or c == bev_cat]

    # 2. Sort Beverages subcategories
    # USER: "start with cold drinks then hot drinks then keep the canned to the last"
    bev_priority = {
        'Juices': 0,
        'Mojitos': 1,
        'Smoothies': 2,
        'Milkshakes': 3,
        'Fresh Juices': 4,
        'Iced Coffee': 5,
        'Iced Tea': 6,
        'Frappuccino': 7,
        'Iced Coffee & Tea': 8,
        'Hot Drinks': 20,
        'Hot Chocolate': 21,
        'Canned Drinks': 50
    }
    
    if bev_cat.get('subcategories'):
        bev_cat['subcategories'].sort(key=lambda x: bev_priority.get(x.get('en_name'), 99))
        
    # 3. Sort Lunch (Main Courses) subcategories
    # The category is named "Lunch (From 1 PM)"
    lunch = find_cat('Lunch (From 1 PM)')
    if lunch and lunch.get('subcategories'):
        # Move Salty Crepe items to Sandwiches before sorting
        salty_crepe = next((s for s in lunch['subcategories'] if s.get('en_name') == 'Salty Crepe' or s.get('name') == 'كريب حار'), None)
        sandwiches = next((s for s in lunch['subcategories'] if s.get('en_name') == 'Sandwiches' or s.get('name') == 'سندوتشات'), None)
        
        if salty_crepe and sandwiches:
            # Add a small note to items if needed, or just append
            sandwiches['items'].extend(salty_crepe['items'])
            # Remove Salty Crepe from subcategories
            lunch['subcategories'] = [s for s in lunch['subcategories'] if s != salty_crepe]

        # USER REQUEST: Specific ranking for Lunch subcategories
        priority = {
            'Appetizers': 0, 'المقبلات': 0,
            'Salads': 1, 'السلاطات': 1,
            'Soups': 2, 'الشوربات': 2,
            'Pasta': 3, 'باستا': 3,
            'Risotto': 4, 'ريزوتو': 4,
            'Pizza': 5, 'بيتزا': 5,
            'Safiha': 6, 'صفايح': 6,
            'Chicken Selection': 7, 'غربي الدجاج': 7,
            'Meat Selection': 8, 'غربي اللحوم': 8,
            'Seafood': 9, 'غربي اسماك وبحريات': 9,
            'Oriental Cuisine': 10, 'المطبخ الشرقي': 10,
            'Fajita Meals': 11, 'وجبات فاهيتا': 11,
            'Sandwiches': 12, 'سندوتشات': 12,
            "Kids' Meals": 13, 'وجبات اطفال': 13
        }
        
        def get_priority(sub):
            en = sub.get('en_name')
            ar = sub.get('name')
            return priority.get(en, priority.get(ar, 99))
            
        lunch['subcategories'].sort(key=get_priority)

    # --- ASSET MAPPING ---
    images_dir = "images"
    image_files = []
    if os.path.exists(images_dir):
        image_files = os.listdir(images_dir)
    
    def find_image(name_ar, name_en=None, desc_ar=""):
        # 1. Try exact Arabic match
        if name_ar:
            clean_ar = name_ar.strip()
            for f in image_files:
                if clean_ar in f: return os.path.join(images_dir, f).replace("\\", "/")
        
        # 2. Try exact English match (lowercased)
        if name_en:
            clean_en = name_en.lower().strip()
            # Basic mapping for common English names to known files
            mapping = {
                "chicken alfredo": "باستا الفريدو.PNG",
                "pasta arrabbiata": "باستا اربياتا.PNG",
                "bruschetta": "بروسكيتا.PNG",
                "club sandwich": "كلوب سندوتش.PNG",
                "mixed 3 skewers": "مشكل 3 اسياخ.PNG",
                "mixed 2 skewers": "مشكل 2 اسياخ.PNG",
                "mixed 4 skewers": "مشكل 4 اسياخ.PNG",
                "nutella croissant": "كرواسون نوتيلا.jpg",
                "eggs bagels": "بيجلز بيض.jpg",
                "shrimp soup": "شوربه جمبري.PNG",
                "potato plate": "صحن بطاطا.PNG",
                "chicken strips": "تشكن ستريبس.PNG",
                "grilled fillet": "فيليه مشوي.PNG",
                "lavina breakfast": "افطار لافينا.jpg",
                "oriental breakfast": "افطار شرقي.PNG",
                "continental breakfast": "كونتيننتال افطار.jpg",
                "fajita chicken sandwich": "سندوتش فاهيتا دجاج.PNG",
                "fajita meat sandwich": "سندوتش فاهيتا لحم.PNG",
                "fattoush salad": "سلطة فتوش.PNG",
                "arugula salad": "سلطة جرجير.jpg",
                "negresco chicken": "نجريسكو دجاج.PNG",
                "chicken roll with spinach and mozzarella": "نجريسكو دجاج.PNG", # Assuming based on visual similarity if appropriate
                "seafood risotto": "ريزوتو فواكه البحر.jpg",
                "lavina salad": "سلاطه لافينا.PNG",
                "baba ganoush salad": "سلاطه بابا غنوج.PNG",
                "grilled salad": "سلاطه مشويه.PNG",
                "coleslaw salad": "سلاطة كول سلو.PNG",
                "chicken breast": "تشيكن بريست.PNG",
                "chicken fajita sandwich": "سندوتش فاهيتا دجاج.PNG",
                "beef fajita sandwich": "سندوتش فاهيتا لحم.PNG",
                "pesto fusilli": "بيستو فوزيلى.PNG",
                "grilled chicken baguette": "باجيت دجاج مشوي.PNG"
            }
            if clean_en in mapping:
                return os.path.join(images_dir, mapping[clean_en]).replace("\\", "/")
        
        return None

    def group_items(items, sub_name=None):
        if not items: return []
        
        # 0. Clean items from any existing variants to start fresh
        processed_items = []
        for i in items:
            clean_item = copy.deepcopy(i)
            if 'variants' in clean_item: del clean_item['variants']
            
            # ASSIGN IMAGE
            img = find_image(clean_item.get('name'), clean_item.get('en_name'), clean_item.get('desc', ''))
            if img: clean_item['image'] = img
            
            processed_items.append(clean_item)
        items = processed_items

        # 1. Healthy Breakfast (اﻷﻓﻄﺎر اﻟﺼﺤﻲ)
        # USER: "yes for اﻷﻓﻄﺎر اﻟﺼﺤﻲ make them one"
        healthy = [i for i in items if "Healthy Breakfast" in i.get('en_name', '') or "إﻓﻄﺎر ﻟﺬﻳﺬ" in i.get('name', '')]
        if len(healthy) > 1:
            indices = [items.index(i) for i in healthy]
            primary = copy.deepcopy(healthy[0])
            primary['en_name'] = "Healthy Breakfast"
            primary['name'] = "اﻷﻓﻄﺎر اﻟﺼﺤﻲ"
            primary['variants'] = []
            for h in healthy:
                v = copy.deepcopy(h)
                v['variant_name'] = h['name']
                v['variant_en_name'] = h['en_name']
                v['variants'] = []
                primary['variants'].append(v)
            first_idx = min(indices)
            for i in sorted(indices, reverse=True): items.pop(i)
            items.insert(first_idx, primary)

        # 2. Fruit Plate (ﺻﺤﻦ ﻓﻮاﻛﺔ)
        fruit = [i for i in items if "Fruit Plate" in i.get('en_name', '') or "ﺻﺤﻦ ﻓﻮاﻛﺔ" in i.get('name', '')]
        if len(fruit) > 1:
            indices = [items.index(i) for i in fruit]
            primary = copy.deepcopy(fruit[0])
            primary['en_name'] = "Mixed Fruit Plate"
            primary['name'] = "ﺻﺤﻦ ﻓﻮاﻛﺔ ﻣﺸﻜﻠﺔ"
            primary['variants'] = []
            for f in fruit:
                v = copy.deepcopy(f)
                v['variant_name'] = f['name'].split('-')[-1].strip() if '-' in f['name'] else f['name']
                v['variant_en_name'] = f['en_name'].split(' ')[0] if ' ' in f['en_name'] else f['en_name']
                # Specific image for large fruit plate if available
                v['variants'] = []
                primary['variants'].append(v)
            first_idx = min(indices)
            for i in sorted(indices, reverse=True): items.pop(i)
            items.insert(first_idx, primary)

        # 3. Pasta Specific (Seafood Pasta & Shrimp Linguine)
        for i in range(len(items)):
            item = items[i]
            is_seafood_pasta = ("Seafood" in item.get('en_name', '') and ("Spaghetti" in item.get('en_name', '') or "Pasta" in item.get('en_name', '')))
            is_shrimp_linguine = ("Shrimp" in item.get('en_name', '') and ("Linguine" in item.get('en_name', '') or "Fettuccine" in item.get('en_name', '')))
            
            if is_seafood_pasta or is_shrimp_linguine:
                if is_seafood_pasta:
                    item['en_name'] = "Seafood Pasta"
                    item['name'] = "باستا فواكه البحر"
                elif is_shrimp_linguine:
                    item['en_name'] = "Shrimp Linguine"
                    item['name'] = "لانجويني قمبري"
                
                # Logic: White Sauce 55, Others 50
                item['variants'] = []
                for v_en, v_ar, v_price in [
                    ("White Sauce", "الصوص الأبيض", "55 د.ل"),
                    ("Red Sauce", "الصوص الأحمر", "50 د.ل"),
                    ("Pink Sauce", "الصوص الوردي", "50 د.ل"),
                    ("Rose Sauce", "صوص الروز", "50 د.ل")
                ]:
                    v = {
                        "variant_en_name": v_en,
                        "variant_name": v_ar,
                        "price": v_price,
                        "variants": []
                    }
                    
                    # Assign image only if it matches the specific item + sauce
                    v_img = None
                    if is_seafood_pasta:
                        if v_en == "Rose Sauce": v_img = "images/باستا فواكه البجر صوص روزي.PNG"
                    elif is_shrimp_linguine:
                        if v_en == "Rose Sauce": v_img = "images/باستا جمبري صوص  روزي.PNG"
                        if v_en == "Pink Sauce": v_img = "images/باستا جمبري صوص وردي.PNG"
                    
                    if v_img and os.path.exists(v_img):
                        v['image'] = v_img
                    
                    item['variants'].append(v)

        # 4. Drinks Specific (Iced Tea & Frappuccino)
        # Ensure these exist even if parser skipped them due to name collision with subcategory
        found_iced_tea = any("ايس تي" in it.get('name', '') for it in items)
        found_frappuccino = any("فرابتشينو" in it.get('name', '') for it in items)
        
        sub_name_lower = sub_name.lower() if sub_name else ""
        if not found_iced_tea and ("iced tea" in sub_name_lower or "ايس تي" in sub_name_lower):
            items.append({"name": "ايس تي", "en_name": "Iced Tea", "price": "14 د.ل", "desc": "( ﺧﻮخ / ﻧﻌﻨﺎع / قرفة / ﺗﻮت )"})
        if not found_frappuccino and ("frappuccino" in sub_name_lower or "فرابتشينو" in sub_name_lower):
            items.append({"name": "فرابتشينو", "en_name": "Frappuccino", "price": "20 د.ل", "desc": "( كلاسيك / كراميل / فانيليا )"})
            
        for i in range(len(items)):
            item = items[i]
            is_iced_tea = ("Iced Tea" in item.get('en_name', '') or "ايس تي" in item.get('name', ''))
            is_frappuccino = ("Frappuccino" in item.get('en_name', '') or "فرابتشينو" in item.get('name', ''))
            
            if is_iced_tea or is_frappuccino:
                if is_iced_tea:
                    item['en_name'] = "Iced Tea"
                    item['name'] = "ايس تي"
                    variants_list = [
                        ("Peach", "خوخ", "14 د.ل"),
                        ("Mint", "نعناع", "14 د.ل"),
                        ("Cinnamon", "قرفة", "14 د.ل"),
                        ("Berry", "توت", "14 د.ل")
                    ]
                    price = "14 د.ل"
                else: # Frappuccino
                    item['en_name'] = "Frappuccino"
                    item['name'] = "فرابتشينو"
                    variants_list = [
                        ("Classic", "كلاسيك", "20 د.ل"),
                        ("Caramel", "كراميل", "20 د.ل"),
                        ("Vanilla", "فانيليا", "20 د.ل")
                    ]
                    price = "20 د.ل"
                
                item['price'] = price
                item['variants'] = []
                for en, ar, p in variants_list:
                    item['variants'].append({
                        "variant_en_name": en,
                        "variant_name": ar,
                        "price": p,
                        "variants": []
                    })

        # 4. Standard same-name grouping (Bagels, etc)
        name_map = {}
        for idx, item in enumerate(items):
            if "variants" in item and item['variants']: continue
            name = item.get('en_name', '')
            if name not in name_map: name_map[name] = []
            name_map[name].append(idx)
        
        final_items = []
        skip_indices = set()
        for i in range(len(items)):
            if i in skip_indices: continue
            item = items[i]
            if "variants" in item and item['variants']:
                final_items.append(item)
                continue
            
            name = item.get('en_name', '')
            cluster_indices = name_map.get(name, [])
            if len(cluster_indices) > 1:
                primary = copy.deepcopy(item)
                primary['variants'] = []
                for idx in cluster_indices:
                    orig_v = items[idx]
                    v = {
                        "price": orig_v.get('price'),
                        "variants": []
                    }
                    
                    if 'Bagel' in name:
                        desc = orig_v.get('desc', '')
                        if 'ﺳﻼﻣﻲ' in desc: 
                            v['variant_name'], v['variant_en_name'] = 'ﺳﻼﻣﻲ', 'Salami'
                        elif 'بيض' in desc or 'Eggs' in orig_v.get('en_name', ''): 
                            v['variant_name'], v['variant_en_name'] = 'ﺑﻴﺾ', 'Eggs'
                            v['image'] = "images/بيجلز بيض.jpg"
                        elif 'ﺗﻮﻧﺔ' in desc: 
                            v['variant_name'], v['variant_en_name'] = 'ﺗﻮﻧﺔ', 'Tuna'
                        elif 'أجبان' in desc: 
                            v['variant_name'], v['variant_en_name'] = 'أجبان', 'Cheese'
                    else:
                        v['variant_name'] = orig_v.get('name')
                        v['variant_en_name'] = orig_v.get('en_name')
                    
                    # If variant has a specific image, keep it
                    if orig_v.get('image') and orig_v.get('image') != primary.get('image'):
                        v['image'] = orig_v.get('image')
                    
                    primary['variants'].append(v)
                    skip_indices.add(idx)
                final_items.append(primary)
            else:
                final_items.append(item)
        
        # 5. Beverage Flavor Splitting - RESTRICTED TO SMOOTHIES only
        if sub_name == "Smoothies":
            for i in range(len(final_items)):
                item = final_items[i]
                if "variants" in item and len(item['variants']) > 0: continue
                
                desc = item.get('desc', '')
                en_desc = item.get('en_desc', '')
                
                if '(' in desc and '/' in desc:
                    base_desc = desc.split('(')[0].strip()
                    base_en_desc = en_desc.split('(')[0].strip()
                    
                    try:
                        ar_opts = desc.split('(')[1].split(')')[0].split('/')
                        en_opts = en_desc.split('(')[1].split(')')[0].split('/')
                        
                        if len(ar_opts) == len(en_opts):
                            item['variants'] = []
                            clean_base = copy.deepcopy(item)
                            if 'variants' in clean_base: del clean_base['variants']
                            
                            for ar, en in zip(ar_opts, en_opts):
                                v = {
                                    "variant_name": ar.strip(),
                                    "variant_en_name": en.strip(),
                                    "price": item.get('price'),
                                    "variants": []
                                }
                                # Image mapping for flavored variants could go here if needed
                                item['variants'].append(v)
                    except: pass
                        
        return final_items

    # Process all sections
    new_data = [] # rebuild to handle top-level removals
    for cat in data:
        sub_items = cat.get('items', [])
        if sub_items:
            cat['items'] = group_items(sub_items)
            
        if cat.get('subcategories'):
            for sub in cat['subcategories']:
                s_items = sub.get('items', [])
                s_en_name = sub.get('en_name', '').lower()
                if not s_items:
                    if "iced tea" in s_en_name:
                        s_items = [{"name": "ايس تي", "en_name": "Iced Tea", "price": "14 د.ل", "desc": "( ﺧﻮخ / ﻧﻌﻨﺎع / قرفة / ﺗﻮت )"}]
                    elif "frappuccino" in s_en_name:
                        s_items = [{"name": "فرابتشينو", "en_name": "Frappuccino", "price": "20 د.ل", "desc": "( كلاسيك / كراميل / فانيليا )"}]
                sub['items'] = group_items(s_items, sub_name=sub.get('en_name'))
        new_data.append(cat)
    
    # --- FEATURED CATEGORIES ---
    # Pick unique items for Most Ordered and Fastest Ordered
    all_items_list = []
    for cat in new_data:
        if cat.get('items'): 
            all_items_list.extend(cat['items'])
        if cat.get('subcategories'):
            for sub in cat['subcategories']:
                if sub.get('items'):
                    all_items_list.extend(sub['items'])
    
    def clean_price(p):
        if not p: return ""
        return p.replace(".000", "").replace(",000", "")

    def find_item_by_en_name(en_name):
        for item in all_items_list:
            if item.get('en_name') and item.get('en_name').lower() == en_name.lower():
                return item
        return None

    # Most Ordered
    most_ordered_en_names = [
        "Chicken Alfredo", 
        "Mixed 3 Skewers", 
        "Chicken Fajita Sandwich", 
        "Seafood Pasta", 
        "Chicken Breast"
    ]
    most_ordered_items = []
    for en_name in most_ordered_en_names:
        item = find_item_by_en_name(en_name)
        if item:
            item_copy = copy.deepcopy(item)
            # Special case for Seafood Pasta: force Rose Sauce as default for featured highlight
            if en_name == "Seafood Pasta" and item_copy.get('variants'):
                rose_v = next((v for v in item_copy['variants'] if "Rose" in v.get('variant_en_name', '')), None)
                if rose_v:
                    item_copy['price'] = rose_v['price']
                    item_copy['image'] = rose_v.get('image', item_copy.get('image'))
                    item_copy['selected_variant_idx'] = item_copy['variants'].index(rose_v)
            most_ordered_items.append(item_copy)
    
    # Fastest Ordered
    fastest_ordered_en_names = [
        "Chicken Alfredo", 
        "Chicken Fajita Sandwich", 
        "Pasta Arrabbiata", 
        "Pesto Fusilli", 
        "Grilled Chicken Baguette"
    ]
    fastest_ordered_items = []
    for en_name in fastest_ordered_en_names:
        item = find_item_by_en_name(en_name)
        if item:
            fastest_ordered_items.append(copy.deepcopy(item))

    featured = []
    if most_ordered_items:
        featured.append({
            "name": "الأكثر طلباً",
            "en_name": "Most Ordered",
            "items": most_ordered_items
        })
    if fastest_ordered_items:
        featured.append({
            "name": "الأسرع طلباً",
            "en_name": "Fastest Ordered",
            "items": fastest_ordered_items
        })

    # Final price cleaning pass on the entire nested structure
    def final_clean(data_obj):
        if isinstance(data_obj, list):
            for item in data_obj:
                final_clean(item)
        elif isinstance(data_obj, dict):
            if 'price' in data_obj:
                data_obj['price'] = clean_price(data_obj['price'])
            for key in data_obj:
                if key != 'price':
                    final_clean(data_obj[key])

    cat_order = {
        'Most Ordered': 0,
        'Fastest Ordered': 1,
        'Breakfast (8 AM to 1 PM)': 10,
        'Lunch (From 1 PM)': 11,
        'Desserts': 12,
        'Beverages': 13
    }
    
    final_data = featured + new_data
    final_data.sort(key=lambda x: cat_order.get(x.get('en_name'), 99))
    final_clean(final_data)

    with open('the_menu_bilingual.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)

    print("Restructuring, grouping and asset mapping complete.")

if __name__ == "__main__":
    restructure()
