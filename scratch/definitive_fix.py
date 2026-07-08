"""
DEFINITIVE Arabic text restoration for Lavina House Menu.
This script fixes ALL garbled text in both the HTML template and the menuData JSON.
"""
import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

FILE_PATH = r'c:\Users\malek drebi\Desktop\LAVINA\LavinaHouseMenu\index.html'

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# PHASE 1: Fix double-encoded Mojibake in HTML template
# These are Arabic chars that got double-encoded through UTF-8 -> Latin-1 -> UTF-8
# ============================================================

# Complete Mojibake mapping: double-encoded UTF-8 Arabic -> correct Arabic
mojibake_map = {
    'ط§': 'ا', 'ط¨': 'ب', 'طھ': 'ت', 'ط«': 'ث', 'ط¬': 'ج', 'ط­': 'ح',
    'ط®': 'خ', 'ط¯': 'د', 'ط°': 'ذ', 'ط±': 'ر', 'ط²': 'ز', 'ط³': 'س',
    'ط´': 'ش', 'طµ': 'ص', 'ط¶': 'ض', 'ط·': 'ط', 'ط¸': 'ظ', 'ط¹': 'ع',
    'ط؛': 'غ', 'ظپ': 'ف', 'ظ‚': 'ق', 'ظƒ': 'ك', 'ظ„': 'ل', 'ظ…': 'م',
    'ظ†': 'ن', 'ظ‡': 'ه', 'ظˆ': 'و', 'ظٹ': 'ي',
    'ط£': 'أ', 'ط¥': 'إ', 'ط¤': 'ؤ', 'ط¦': 'ئ', 'ط©': 'ة', 'ظ‰': 'ى',
    'ظ‹': '\u064b', 'ظŒ': '\u064c', 'ظŽ': '\u064e', 'ظگ': '\u0650',
    'طŒ': '\u060c', 'طں': '\u061f',
}

# Sort by length (longest first) to avoid partial replacements
sorted_mojibake = sorted(mojibake_map.items(), key=lambda x: len(x[0]), reverse=True)

def fix_mojibake(text):
    """Fix double-encoded Mojibake pattern."""
    for garbled, correct in sorted_mojibake:
        text = text.replace(garbled, correct)
    return text

# Apply mojibake fix to the ENTIRE file
content = fix_mojibake(content)

# ============================================================
# PHASE 2: Fix the menuData JSON with correct Arabic names
# Using the English names as the guide for what each item should be
# ============================================================

match = re.search(r'const menuData = (\[.*?\]);', content, re.DOTALL)
if not match:
    print("ERROR: Could not find menuData!")
    sys.exit(1)

data = json.loads(match.group(1))

# Master mapping: en_name -> correct Arabic name
en_to_ar_name = {
    # === CATEGORIES ===
    "Most Ordered": "الأكثر طلباً",
    "Fastest Ordered": "الأسرع طلباً",
    
    # === MOST ORDERED / FASTEST ===
    "Chicken Alfredo": "الفريدو دجاج",
    "Chicken Fajita Sandwich": "سندوتش فاهيتا دجاج",
    "Chicken Breast": "تشيكن بريست",
    "Pesto Fusilli": "بيستو فوسيلي",
    "Grilled Chicken Baguette": "باجيت دجاج مشوي",
    "Pasta Arrabbiata": "باستا أرابيتا",
    
    # === SAUCE VARIANTS ===
    "White Sauce": "الصوص الأبيض",
    "Rose Sauce": "صوص الروزي",
    
    # === BREAKFAST ===
    "Continental": "كونتيننتال",
    "Moroccan Breakfast": "افطار مغربي",
    "Oriental Breakfast": "شرقي",
    "Lavina": "لافينا",
    "Lavina (Family)": "لافينا (عائلي)",
    "Qallaya Plate": "صحن قلاية",
    "Scrambled Eggs": "سكرامبل بيض",
    
    # === LUNCH - APPETIZERS ===
    "Bruschetta": "بروسكيتا",
    "Meat Bourek": "بوريك لحم",
    "Meat Kibbeh (4 Pieces)": "كبة لحم (4 قطع)",
    "Mozzarella Fingers": "أصابع موزاريلا",
    "Fish Fingers": "أصابع سمك",
    "Potato Fries Plate": "صحن بطاطا",
    "Cheese Sambousek": "سمبوسة بالجبنة",
    "Chicken Strips": "تشيكن ستريبس",
    "Chicken Pastilla": "بسطيلة دجاج",
    "Seafood Saut": "سوتي فواكه البحر",
    "Lavina Mixed Plate": "صحن لافينا مشكل",
    
    # === LUNCH - SALADS ===
    "House Salad": "سلطة المنزل",
    "Coleslaw Salad": "سلطة كول سلو",
    "Arugula Salad": "سلطة جرجير",
    "Grilled Salad": "سلطة مشوية",
    "Baba Ghanouj Salad": "سلطة بابا غنوج",
    "Fattoush Salad": "سلطة فتوش",
    "Fruit Salad": "سلطة فواكه",
    "Lavina Salad": "سلطة لافينا",
    "Greek Salad": "سلطة يونانية",
    "Caesar Salad": "سلطة سيزر",
    "Tuna Salad": "سلطة تونة",
    
    # === LUNCH - SOUPS ===
    "Mushroom Soup": "شوربة فقع",
    "Lentil Soup": "شوربة عدس",
    "Seafood Soup": "شوربة فواكه البحر",
    "Lavina Soup": "شوربة لافينا",
    
    # === LUNCH - PASTA ===
    "Alfredo Pasta": "باستا الفريدو",
    "Arrabbiata Pasta": "باستا أرابيتا",
    "Pesto Pasta": "بيستو فوسيلي",
    "Bolognese Pasta": "باستا بولونيز",
    "Seafood Pasta": "مكرونة فواكه البحر",
    "Shrimp Pasta": "باستا جمبري",
    "Chicken Pesto": "باستا بيستو دجاج",
    
    # === LUNCH - RISOTTO ===
    "Mushroom Risotto": "ريزوتو فقع",
    "Chicken Risotto": "ريزوتو دجاج",
    "Seafood Risotto": "ريزوتو فواكه البحر",
    "Shrimp Risotto": "ريزوتو جمبري",
    
    # === LUNCH - MAIN DISHES ===
    "Chicken Scaloppine": "سكالوبيني دجاج",
    "Cream Cheese Chicken": "كريم تشيز دجاج",
    "Grilled Salmon": "سلمون مشوي",
    "Grilled Shrimp": "جمبري مشوي",
    "Sayadieh Rice": "صيادية",
    
    # === LUNCH - PIZZA ===
    "Margarita Pizza": "بيتزا مارغريتا",
    "Pepperoni Pizza": "بيتزا ببروني",
    "Oriental Pizza": "بيتزا شرقية",
    "Seafood Pizza": "بيتزا فواكه البحر",
    
    # === LUNCH - MANAKISH ===
    "Zaatar Manakish": "مناقيش زعتر",
    "Cheese Manakish": "مناقيش جبنة",
    "Cheese and Zaatar Manakish": "مناقيش جبنة وزعتر",
    "Ground Meat Manakish": "مناقيش لحمة",
    "Halloumi Manakish": "مناقيش حلومي",
    "Pepperoni Manakish": "مناقيش ببروني",
    "Mixed Manakish": "مناقيش مشكلة",
    "Falafel Manakish": "مناقيش فلافل",
    "Labneh Manakish": "مناقيش لبنه",
    "Safiha (6 Pieces)": "صفيحة (6 قطع)",
    
    # === LUNCH - FATAYER ===
    "Meat Fatayer": "فطائر لحم",
    "Cheese Fatayer": "فطائر جبنة",
    "Spinach Fatayer": "فطائر سبانخ",
    
    # === LUNCH - ORIENTAL / GRILL ===
    "Shish Taouk": "شيش طاووق",
    "Veal Shish": "شيش لحم عجل",
    "Lamb Chops": "أرياش خروف",
    "Spicy Adana Kebab": "كباب أضنة حار",
    "Cheese Kebab": "كباب بالجبنة",
    "Grilled Chicken Wings": "أجنحة دجاج مشوية",
    "Grilled Chicken Thigh": "أفخاذ دجاج مشوية",
    "Urfali Kebab": "كباب أورفا",
    "Mixed 2 Skewers": "مشكل 2 اسياخ",
    "Mixed 3 Skewers": "مشكل 3 اسياخ",
    "Mixed 4 Skewers": "مشكل 4 اسياخ",
    "Mixed 5 Skewers": "مشكل 5 اسياخ",
    "Mixed 8 Skewers": "مشكل 8 اسياخ",
    "Lavina Family Grill Mix": "مشكل مشاوي لافينا عائلي",
    
    # === LUNCH - SANDWICHES ===
    "Beef Fajita": "فاهيتا لحم",
    "Mini Beef Burger": "ميني برجر لحم",
    "Club Sandwich": "كلوب سندوتش",
    "Beef Burger": "برجر",
    "Cheese Crepe": "كريب أجبان",
    "Chicken Crepe": "كريب دجاج",
    "Tuna Crepe": "كريب تونة",
    
    # === LUNCH - KIDS ===
    "Chicken Nuggets": "تشيكن ناجتس",
    
    # === DESSERTS ===
    "Sushi Crepe": "كريب سوشي",
    "Fruit Crepe": "كريب فواكه",
    "Ice Cream Crepe": "كريب آيس كريم",
    "Crepe Roll": "كريب رول",
    "Fettuccine Crepe": "كريب فيتوتشيني",
    "Tam Crepe": "كريب تام",
    "Pistachio Crepe": "كريب فستق",
    "Hazelnut Crepe": "كريب بندق",
    "Almond Crepe": "كريب لوز",
    "Nutella Crepe": "كريب نوتيلا",
    "Nutella Croissant": "كرواسون نوتيلا",
    "Cheese Croissant": "كرواسون جبنة",
    "Honey Croissant": "كرواسون عسل",
    "Nutella + Honey + Almond Croissant": "كرواسون نوتيلا + عسل + لوز",
    "Large Oriental Mixed Plate": "طبق حلويات شرقية مشكل كبير",
    "Small Oriental Mixed Plate": "طبق حلويات شرقية مشكل صغير",
    "Moroccan Pie": "فطيرة مغربية",
    "Mixed Fruit Plate": "صحن فواكه مشكل",
    "Large Mixed Fruit Plate": "صحن فواكه مشكل - كبير",
    "Medium Mixed Fruit Plate": "صحن فواكه مشكل - وسط",
    "Lavina Cake": "كيكة لافينا",
    "San Sebastian": "سان سيباستيان",
    "Brownies with Ice Cream": "براونيز مع آيس كريم",
    "Classic Waffle": "وافل كلاسيك",
    "Almond and Honey Waffle": "وافل عسل ولوز",
    "Ice Cream Waffle": "وافل آيس كريم",
    "Fruit Waffle": "وافل فواكه",
    "Pistachio Waffle": "وافل فستق",
    "Hazelnut Waffle": "وافل بندق",
    "Nutella Waffle": "وافل نوتيلا",
    "Mini Almond Pancake": "ميني بان كيك لوز",
    "Mini Red Velvet Pancake": "ميني بان كيك ريد فيلفيت",
    "Mini Fruit Pancake": "ميني بان كيك فواكه",
    "Mini Lotus Pancake": "ميني بان كيك لوتس",
    "Mini Oreo Pancake": "ميني بان كيك أوريو",
    "Mini Pistachio Pancake": "ميني بان كيك فستق",
    "Mini Nutella Pancake": "ميني بان كيك نوتيلا",
    "Classic Pancake": "بان كيك كلاسيك",
    "Red Velvet Pancake": "بان كيك ريد فيلفيت",
    "Fruit Pancake": "بان كيك فواكه",
    "Pistachio Pancake": "بان كيك فستق",
    "Lotus Pancake": "بان كيك لوتس",
    "Nutella Pancake": "بان كيك نوتيلا",
    
    # === BEVERAGES - HOT DRINKS ===
    "Arabic Coffee": "قهوة عربية",
    "Cortado": "كورتادو",
    "Macchiato": "ماكياتو",
    "Flat White": "فلات وايت",
    "Cappuccino": "كابتشينو",
    "Caffe Latte": "كافيه لاتيه",
    "Spanish Latte": "سبانيش لاتيه",
    "Caffe Mocha": "كافيه موكا",
    "Nescafe": "نسكافيه",
    "Tea": "شاي",
    "Medium Tea Pot with Nuts": "براد شاي متوسط مكسرات",
    "Large Tea Pot with Nuts": "براد شاي كبير مكسرات",
    
    # === BEVERAGES - HOT CHOCOLATE ===
    "Hot Chocolate": "شوكولاتة ساخنة",
    
    # === BEVERAGES - JUICE ===
    "Strawberry Juice": "عصير فراولة",
    "Orange Juice": "عصير برتقال",
    "Lemon with Mint Juice": "عصير ليمون ونعناع",
    "Mango Juice": "عصير مانجو",
    "Kiwi Juice": "عصير كيوي",
    "Pomegranate Juice": "عصير رمان",
    "Avocado Juice": "عصير أفوكادو",
    "Froopy": "فروبي",
    "Cocktail": "كوكتيل",
    
    # === BEVERAGES - SMOOTHIES ===
    "Strawberry Smoothie": "سموذي فراولة",
    "Mango Smoothie": "سموذي مانجو",
    "Mixed Berry Smoothie": "سموذي توت مشكل",
    "Blueberry Smoothie": "سموذي بلوبيري",
    "Cherry Smoothie": "سموذي كرز",
    "Banana Smoothie": "سموذي موز",
    
    # === BEVERAGES - MILKSHAKES ===
    "Oreo Milkshake": "ميلك شيك أوريو",
    "Chocolate Milkshake": "ميلك شيك شوكولاتة",
    "Lotus Milkshake": "ميلك شيك لوتس",
    "Nutella Milkshake": "ميلك شيك نوتيلا",
    "Pistachio Milkshake": "ميلك شيك فستق",
    
    # === BEVERAGES - MOJITOS ===
    "Classic Mojito": "موهيتو كلاسيك",
    "Hawaii Mojito": "موهيتو هاواي",
    "Black Moon Mojito": "موهيتو بلاك مون",
    "Strawberry Mojito": "موهيتو فراولة",
    "Montana Mojito": "موهيتو مونتانا",
    "Rose Mojito": "موهيتو روز",
    
    # === BEVERAGES - ICED TEA ===
    "Iced Tea": "آيس تي",
    
    # === BEVERAGES - ICED COFFEE ===
    "Classic Iced Coffee": "آيس كوفي كلاسيك",
    "Flavored Iced Coffee": "آيس كوفي منكه",
    
    # === BEVERAGES - FRAPPUCCINO ===
    "Caramel Frappuccino": "فرابتشينو كراميل",
    "Oreo Frappuccino": "فرابتشينو أوريو",
    "Java Chip Frappuccino": "فرابتشينو جافا تشيب",
    "Mocha Frappuccino": "فرابتشينو موكا",
}

# Descriptions that need fixing (en_name -> correct Arabic desc)
en_to_ar_desc = {
    "Chicken Nuggets": "يقدم مع أرز, بطاطا مقلية, خضار سوتيه",
    "Mixed Fruit Plate": "(حسب الموسم)",
    "Large Mixed Fruit Plate": "(حسب الموسم)",
    "Medium Mixed Fruit Plate": "(حسب الموسم)",
    "Classic Waffle": "عسل",
    "Moroccan Pie": "(يقدم مع عسل وزيتون مغربي)",
    "Fettuccine Crepe": "( نوتيلا / فستق / عسل ولوز / لوتس / عسل / أوريو / فواكه )",
    "Tea": "( أحمر / أخضر )",
    "Caffe Mocha": "(وايت / دارك)",
    "Froopy": "(فراولة, مانجو, موز)",
    "Chocolate Milkshake": "( مارس / كندر / سنيكرز )",
    "Iced Tea": "( خوخ / نعناع / قرفة / توت )",
    "Flavored Iced Coffee": "( كراميل / فانيلا / بندق )",
}

# Variant name fixes
variant_name_fixes = {
    "Caramel": "كراميل",
    "Hazelnut": "بندق",
    "Vanilla": "فانيلا",
    "Plain": "سادة",
    "Red": "أحمر",
    "Green": "أخضر",
    "Chocolate": "شوكولاتة",
    "Lotus": "لوتس",
    "Pistachio": "فستق",
    "Large": "كبير",
    "Medium": "وسط",
}

# Mixed skewer descriptions
skewer_descs = {
    "Mixed 2 Skewers": "كباب لحم + شيش طاووق",
    "Mixed 3 Skewers": "كباب لحم + شيش طاووق + شيش لحم عجل",
    "Mixed 4 Skewers": "كباب لحم + شيش طاووق + شيش لحم + كباب دجاج",
    "Mixed 5 Skewers": "كباب لحم + كباب دجاج + شيش طاووق + شيش لحم عجل + كباب أورفا",
    "Mixed 8 Skewers": "كباب لحم + كباب دجاج + شيش طاووق + شيش لحم عجل + كباب أورفا + كباب حار + أجنحة + صفيحة + صحن سلطة",
    "Lavina Family Grill Mix": "2 كباب لحم + 2 كباب دجاج + 2 شيش طاووق + 2 شيش لحم عجل + 2 أرياش خروف + 2 أجنحة + 2 أفخاذ دجاج + صفيحة حسب الطلب + صحن سلطة",
}

# Toast desc fix
toast_descs = {
    "Pepperoni Toast": "توست سلامي, جبنة, طماطم, جرجير, زيتون شرائح أسود, زيتون متبل وهريسة.",
}

# Breakfast descriptions that contain "برجرجر" (should be "بريوش")
breakfast_brioche_fix = "بريوش"

def fix_item(item):
    """Fix a single item's Arabic text using its en_name as guide."""
    en = item.get("en_name", "")
    
    # Fix name
    if en in en_to_ar_name:
        item["name"] = en_to_ar_name[en]
    
    # Fix desc
    if en in en_to_ar_desc:
        item["desc"] = en_to_ar_desc[en]
    if en in skewer_descs:
        item["desc"] = skewer_descs[en]
    if en in toast_descs:
        item["desc"] = toast_descs[en]
    
    # Fix generic broken patterns in name
    if "name" in item:
        item["name"] = item["name"].replace("برجرجر", "بر")
        # But re-check - some things shouldn't have "بر"
        # These are specific post-fix cleanups
    
    # Fix generic broken patterns in desc  
    if "desc" in item and item["desc"]:
        item["desc"] = item["desc"].replace("برجرجر", "بريوش")
        item["desc"] = item["desc"].replace("طسل", "عسل")
        item["desc"] = item["desc"].replace("وط2", "وز")
        item["desc"] = item["desc"].replace("ط2", "ز")
        item["desc"] = item["desc"].replace("أ́وس", "الموسم")
        item["desc"] = item["desc"].replace("́", "")
        item["desc"] = item["desc"].replace("ع‍", "عجل")
        item["desc"] = item["desc"].replace("اخطر", "أخضر")
    
    # Fix variants
    if "variants" in item and item["variants"]:
        for v in item["variants"]:
            v_en = v.get("en_name", "")
            # Fix variant name from en_name
            if v_en in variant_name_fixes:
                v["name"] = variant_name_fixes[v_en]
            # Also check if this variant has its own en_name match  
            if v_en in en_to_ar_name:
                v["name"] = en_to_ar_name[v_en]
            # Fix variant_name field too
            if "variant_name" in v and v_en in variant_name_fixes:
                v["variant_name"] = variant_name_fixes[v_en]
            # Recurse
            fix_item(v)

def fix_category(cat):
    """Fix a category and all its subcategories/items."""
    en = cat.get("en_name", "")
    if en in en_to_ar_name:
        cat["name"] = en_to_ar_name[en]
    
    # Fix category-level broken patterns
    if "name" in cat:
        cat["name"] = cat["name"].replace("طلباظع", "طلباً")
        cat["name"] = cat["name"].replace("الأسرط", "الأسرع")
        cat["name"] = cat["name"].replace("الأبيط", "الأبيض")
    
    if "items" in cat:
        for item in cat["items"]:
            fix_item(item)
    
    if "subcategories" in cat:
        for sub in cat["subcategories"]:
            fix_category(sub)

# Apply fixes
for category in data:
    fix_category(category)

# ============================================================  
# PHASE 3: Fix specific remaining hardcoded issues
# ============================================================

# Fix breakfast descriptions that mention "بريوش"
def deep_fix_desc(obj):
    if isinstance(obj, list):
        for item in obj:
            deep_fix_desc(item)
    elif isinstance(obj, dict):
        if "desc" in obj and isinstance(obj["desc"], str):
            d = obj["desc"]
            d = d.replace("برجرجريوش", "بريوش")
            d = d.replace("برجرجروني", "ببروني")
            d = d.replace("ببرجرجروني", "ببروني")  
            d = d.replace("ببرجروني", "ببروني")
            d = d.replace("بريوشيوش", "بريوش")
            d = d.replace("بريوشوني", "ببروني")
            d = d.replace("بررجراد", "براد")
            d = d.replace("بررجريوش", "بريوش")
            d = d.replace("واكة", "فواكه")
            d = d.replace("اأورفا", "أورفا")
            d = d.replace("́„گ", "حسب الطلب")
            d = d.replace(",", "، ")
            d = d.replace("،  ", "، ")
            obj["desc"] = d
        if "name" in obj and isinstance(obj["name"], str):
            n = obj["name"]
            n = n.replace("برجرجريست", "بريست")
            n = n.replace("برجرجروسكيتا", "بروسكيتا")
            n = n.replace("برجرجراوي", "براونيز")
            n = n.replace("برجرجراد", "براد")
            n = n.replace("برجرجري", "بلوبيري")
            n = n.replace("برجرجر", "برتقال")
            n = n.replace("سوكوت", "سموذي")
            n = n.replace("سوككرط2", "سموذي كرز")  
            n = n.replace("سوكأوط2", "سموذي موز")
            n = n.replace("أو̈يتو", "موهيتو")
            n = n.replace("أيڑ شي́تو", "ميلك شيك فستق")
            n = n.replace("كوكتي‍", "كوكتيل")
            n = n.replace("كراأي‍", "كراميل")
            n = n.replace("ب ̈دق", "بندق")
            n = n.replace("̈يتو", "هيتو")
            n = n.replace("أوتاا", "مونتانا")
            n = n.replace("اواي", "هاواي")
            n = n.replace("بلاك أون", "بلاك مون")
            n = n.replace("روط2", "روز")
            n = n.replace("ب̈", "بندق")
            n = n.replace("́تو", "فستق")
            n = n.replace("واكة", "فواكه")
            n = n.replace("اخطر", "أخضر")
            n = n.replace("الأبيط", "الأبيض")
            n = n.replace("الروط2", "الروزي")
            n = n.replace("وط2", "وز")
            n = n.replace("ط2", "ز")
            n = n.replace("سوش", "سوشي")
            n = n.replace("فاهيتا د", "فاهيتا دجاج")
            n = n.replace("كريب د", "كريب دجاج")
            n = n.replace("كريب وة", "كريب تونة")
            n = n.replace("كريب ب̈", "كريب بندق")
            n = n.replace("باھ", "دجاج")
            n = n.replace("اأورفا", "أورفا")
            n = n.replace("كبة لحم ( قطع)", "كبة لحم (4 قطع)")
            # Clean up double spaces
            while "  " in n:
                n = n.replace("  ", " ")
            obj["name"] = n.strip()
        for key in ["subcategories", "items", "variants"]:
            if key in obj:
                deep_fix_desc(obj[key])

deep_fix_desc(data)

# ============================================================
# PHASE 4: Rebuild the file
# ============================================================

new_json = json.dumps(data, ensure_ascii=False, indent=4)
new_content = content[:match.start()] + f"const menuData = {new_json};" + content[match.end():]

# ============================================================
# PHASE 5: Fix remaining hardcoded strings in HTML/JS
# ============================================================

# Fix "د.ل" replacements in JavaScript
new_content = new_content.replace("price.replace('د.ل', 'LYD')", "price.replace('د.ل', 'LYD')")

# Fix specific JS strings
new_content = new_content.replace("category.name === 'الأكثر طلبا' || category.name === 'الأسرع طلبا'",
                                   "category.name === 'الأكثر طلباً' || category.name === 'الأسرع طلباً'")

# Make sure the "cleanName" check works
# Fix the mn suffix check  
new_content = new_content.replace("cleanName.endsWith(' من')", "cleanName.endsWith(' من')")

with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("=== DEFINITIVE RESTORATION COMPLETE ===")
print(f"File saved: {FILE_PATH}")

# Quick verify
with open(FILE_PATH, 'r', encoding='utf-8') as f:
    verify = f.read()

# Check no mojibake patterns remain
mojibake_count = 0
for pattern in ['ط§', 'ظ†', 'ظپ', 'ظٹ', 'ط®', 'ظ‡', 'ظ„', 'طھ', 'ظ…', 'ط³']:
    c = verify.count(pattern)
    if c > 0:
        mojibake_count += c
        print(f"  WARNING: '{pattern}' still found {c} times")

if mojibake_count == 0:
    print("  ✓ No Mojibake patterns detected")
else:
    print(f"  ✗ {mojibake_count} Mojibake patterns remain")
