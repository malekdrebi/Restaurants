import json
import re

def fix_mojibake(text):
    if not isinstance(text, str) or not text:
        return text
    
    # Common artifacts after the first pass
    replacements = {
        "ط ̈": "ب",
        "ط§": "ا",
        "ظ„": "ل",
        "ظ...": "م",
        "ظ‚": "ق",
        "طھ": "ت",
        "ط ̄": "د",
        "ط¬": "ج",
        "ط ́": "ش",
        "ظˆ": "و",
        "ط±": "ر",
        "ï؛3": "س",
        "ï»1⁄4": "لا",
        "ï» ́": "ي",
        "ï؛»ï؛¤ï»¦": "صحن",
        "ï»ںï؛¤ï»¢": "لحم",
        "ï»›ï؛’ة": "كبة",
        "ï»£وط2ط§ط±ï»3ï»1⁄4": "موزاريلا",
        "ï»“ï» ́ï» ̈ï»کر": "فينجر",
        "ï؛—ï؛ ̧كï» ́ï»¦": "تسكين", # Might need review
        "ï؛3ترï»3ï؛’ï؛2": "ستريبس",
        "ط ̈ط±ظˆط3ظƒظٹطھط§": "بروسكيتا",
        "ط ̈ط3ط·ظٹظ„ط§": "بسطيلة",
        "ط ̄ط¬ط§ط¬": "دجاج",
        "ط3ظˆطھظٹ": "سوتي",
        "طμط­ظ†": "صحن",
        "ظ„ط§ع¤ظٹظ†ط§": "لافينا",
        "ظ...ط ́ظƒظ„": "مشكل",
        "ط ́ظˆط±ط ̈ط§طھ": "شوربات",
        "ط ́ظˆط±ط ̈ظ‡": "شوربة",
        "ط¬ظ...ط ̈ط±ظٹ": "جمبري",
        "ط3ظ„ط§ط·ط§طھ": "سلطات",
        "ï؛£ï»¤ï؛؛": "حمص",
        "ï»›وظ„": "كول",
        "ط ̄.ظ„": "د.ل"
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Handle the "ال" pattern more safely
    text = re.sub(r'ط§ظ„', 'ال', text)
    
    # Cleanup any remaining stray marks
    text = re.sub(r'ï[؛»][\w\s]*', '', text) # Dangerous? maybe keep as fallback
    
    return text.strip()

def clean_by_en_name(item):
    """If en_name exists, try to set a correct Arabic name for common items."""
    mapping = {
        "Bruschetta": "بروسكيتا",
        "Meat Bourek": "بوريك لحم",
        "Meat Kibbeh (4 Pieces)": "كبة لحم (4 قطع)",
        "Mozzarella Fingers": "أصابع موزاريلا",
        "Fish Fingers": "أصابع سمك",
        "Potato Fries Plate": "صحن بطاطا",
        "Cheese Sambousek": "سمبوسة بالجبنة",
        "Chicken Strips": "تشيكن ستريبس",
        "Chicken Pastilla": "بسطيلة دجاج",
        "Seafood Saut\u00e9": "سوتي فواكه البحر",
        "Lavina Mixed Plate": "صحن لافينا مشكل",
        "Lentil Soup": "شوربة العدس",
        "Chicken Mushroom Soup": "شوربة الدجاج بالفقع",
        "Shrimp Soup": "شوربة الجمبري",
        "Arabic Salad": "سلطة عربية",
        "Hummus Salad": "سلطة حمص",
        "Cole Slaw": "كول سلو",
        "Appetizers": "المقبلات",
        "Soups": "الشوربات",
        "Salads": "السلطات",
        "Main Courses": "الأطباق الرئيسية",
        "Pizza & Pasta": "بيتزا ومكرونة",
        "Sandwiches": "سندوتشات",
        "Desserts": "الحلويات",
        "Lunch (From 1 PM)": "الغداء (من الساعه 1م)"
    }
    
    en_name = item.get("en_name")
    if en_name in mapping:
        item["name"] = mapping[en_name]

def run_v2_restoration():
    file_path = r'c:\Users\malek drebi\Desktop\LAVINA\LavinaHouseMenu\index.html'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.search(r'const menuData = (\[.*?\]);', content, re.DOTALL)
    if not match:
        return

    data = json.loads(match.group(1))

    for cat in data:
        clean_by_en_name(cat)
        cat["name"] = fix_mojibake(cat.get("name"))
        cat["en_desc"] = re.sub(r'[^\x00-\x7F]+', '', cat.get("en_desc", "")) # Strip non-English
        
        for sub in cat.get("subcategories", []):
            clean_by_en_name(sub)
            sub["name"] = fix_mojibake(sub.get("name"))
            
            for item in sub.get("items", []):
                clean_by_en_name(item)
                item["name"] = fix_mojibake(item.get("name"))
                item["desc"] = fix_mojibake(item.get("desc"))
                item["price"] = fix_mojibake(item.get("price"))
                # Clean English fields from any stray Arabic
                item["en_name"] = re.sub(r'[^\x00-\x7F\s\(\)/,.-]+', '', item.get("en_name", ""))
                item["en_desc"] = re.sub(r'[^\x00-\x7F\s\(\)/,.-]+', '', item.get("en_desc", ""))
        
        for item in cat.get("items", []):
            clean_by_en_name(item)
            item["name"] = fix_mojibake(item.get("name"))
            item["desc"] = fix_mojibake(item.get("desc"))
            item["price"] = fix_mojibake(item.get("price"))
            item["en_name"] = re.sub(r'[^\x00-\x7F\s\(\)/,.-]+', '', item.get("en_name", ""))
            item["en_desc"] = re.sub(r'[^\x00-\x7F\s\(\)/,.-]+', '', item.get("en_desc", ""))

    new_json_str = json.dumps(data, ensure_ascii=False, indent=4)
    new_content = content.replace(match.group(0), f"const menuData = {new_json_str};")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Success! index.html text has been cleaned (v2).")

if __name__ == "__main__":
    run_v2_restoration()
