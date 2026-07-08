import json

def research():
    with open('the_menu_bilingual.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = {}
    
    # Categorized scan
    target_keywords = [
        'اﻷﻓﻄﺎر اﻟﺼﺤﻲ', 'Healthy Breakfast',
        'ﺳﺒﺎﻗﻴﺘﻲ', 'Spaghetti',
        'لانجويني', 'Linguine',
        'ﺻﺤﻦ ﻓﻮاﻛﺔ', 'Fruit Plate',
        'مخيتو', 'Mojito',
        'ﺳﻤﻮﺛﻲ', 'Smoothie',
        'ميلك شيك', 'Milkshake',
        'ايس كافي', 'Iced Coffee'
    ]

    found_items = []
    
    for cat in data:
        for item in cat.get('items', []):
            if any(kw.lower() in item.get('en_name', '').lower() or kw in item.get('name', '') for kw in target_keywords):
                found_items.append({'cat': cat['en_name'], 'sub': 'none', 'item': item})
        for sub in cat.get('subcategories', []):
            for item in sub.get('items', []):
                if any(kw.lower() in item.get('en_name', '').lower() or kw in item.get('name', '') for kw in target_keywords):
                    found_items.append({'cat': cat['en_name'], 'sub': sub['en_name'], 'item': item})

    with open('scratch/research_findings.json', 'w', encoding='utf-8') as f:
        json.dump(found_items, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    research()
