import json
import re

def polish_restoration():
    file_path = r'c:\Users\malek drebi\Desktop\LAVINA\LavinaHouseMenu\index.html'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.search(r'const menuData = (\[.*?\]);', content, re.DOTALL)
    if not match: return

    data = json.loads(match.group(1))

    # Ingredient/Description mapping
    desc_fixes = {
        "’̈ة": "جبنة",
        "أوط2ار": "موزاريللا",
        "شيƒا": "تشيدر",
        "»¤": "طماطم",
        "ب⁄4‍": "بصل",
        "“”:": "فوقها", # or similar
        "—و§ة": "تونة",
        "§€": "خضروات",
        "ط2†": "زيتون",
        "وطμ": "بصوص",
        "ا£¤ر": "الأحمر",
        "ابيس⁄4": "الأبيض",
        "بي̈": "الوردي",
        "ا’ر": "البحر",
        "ا†": "ليمون",
        "£̧": "طبق",
        "£»¢": "حجم",
        "‹ا‹»2": "عائلي",
        "ط3وتي": "سوتي",
        "سلاطط©": "سلطة",
        "سلاطظ‡": "سلطة",
        "وط­": "وملح",
        "ظƒ": "ك",
        "ظٹر": "ير",
        "باظٹ": "باي",
        "طھط ́": "تش",
        "ط ́": "ش",
        "ط ̈": "ب",
        "ط§": "ا",
        "ظ„": "ل",
        "طھ": "ت",
        "ط ̄": "د",
        "ط¬": "ج",
        "ط ̧": "ة", # sometimes ظ‡ is used for ة or similarly garbled
        "ظˆ": "و",
        "ط±": "ر",
        "طμ": "ص",
        "ظ...": "م",
        "ط3": "س",
        "ط­": "ح",
        "ط·": "ط",
        "ط3": "س"
    }

    # Image maps for specific items
    item_image_map = {
        "Coleslaw Salad": "images/سلطة كول سلو.PNG",
        "Arugula Salad": "images/سلطة جرجير.jpg",
        "Grilled Salad": "images/سلطة مشوية.PNG",
        "Baba Ganoush Salad": "images/بابا غنوج.PNG",
        "Fattoush Salad": "images/سلطة فتوش.PNG",
        "Lavina Salad": "images/سلطة لافينا.PNG",
        "Pasta Arrabbiata": "images/باستا اربياتا.PNG",
        "Pesto Fusilli": "images/بظٹستو فوسيلي.PNG",
        "Chicken Alfredo": "images/باستا الفريدو.PNG",
        "Seafood Risotto": "images/ريزوتو فواكه البحر.jpg",
        "Shrimp Soup": "images/شوربة جمبري.PNG",
        "Grilled Chicken Baguette": "images/باجيت دجاج مشوي.PNG",
        "Chicken Strips": "images/تشيكن ستريبس.PNG",
        "Bruschetta": "images/بروسكيتا.PNG",
        "Chicken Pastilla": "images/بسطيلة دجاج.jpg",
        "Beef Fajita Meal": "images/وجبة فاهيتا لحم.PNG",
        "Grilled Fillet": "images/فيلييه مشوي.PNG",
        "Chicken Roll with Spinach and Mozzarella": "images/نجريسكو دجاج.PNG",
        "Chicken Breast": "images/تشيكن بريست.PNG"
    }

    def clean_deep(val, field_name, en_name):
        if not isinstance(val, str) or not val: return val
        
        # Fix images first
        if field_name == "image":
            if en_name in item_image_map:
                return item_image_map[en_name]
            # Manual cleanup of paths
            v = val
            v = v.replace("ط ̈", "ب").replace("ط§", "ا").replace("ظ„", "ل").replace("طھ", "ت").replace("ط ̄", "د").replace("ط¬", "ج").replace("ط ́", "ش").replace("ظˆ", "و").replace("ط±", "ر").replace("طμ", "ص").replace("ظ...", "م").replace("ط3", "س").replace("ط­", "ح").replace("ط·", "ط").replace("ط ̧", "ة").replace("ظ‡", "ة").replace("ظٹر", "ير").replace("ظƒ", "ك")
            return v

        # Fix names by en_name
        # (This was already largely done in v3, but some were missed)
        
        # Generic pattern fixes for descriptions
        v = val
        for old, new in desc_fixes.items():
            v = v.replace(old, new)
        
        # Specific cleanup for names like "ط3وتي"
        if "ط3وتي" in v: v = v.replace("ط3وتي", "سوتي")
        
        # Remove remaining garbage chars
        v = re.sub(r'[ï؛»»°¤¢§€“——ں£†ک1⁄4]', '', v)
        
        return v.strip()

    def process_obj(obj):
        if isinstance(obj, list):
            for i in obj: process_obj(i)
        elif isinstance(obj, dict):
            en_name = obj.get("en_name", "")
            for k in ["name", "desc", "image", "variant_name"]:
                if k in obj:
                    obj[k] = clean_deep(obj[k], k, en_name)
            for k in ["subcategories", "items", "variants"]:
                if k in obj: process_obj(obj[k])

    process_obj(data)

    new_json_str = json.dumps(data, ensure_ascii=False, indent=4)
    new_content = content.replace(match.group(0), f"const menuData = {new_json_str};")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Final polish complete.")

if __name__ == "__main__":
    polish_restoration()
