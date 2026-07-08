import json
import re

def fix_text_v3(text):
    if not isinstance(text, str) or not text:
        return text
    
    # 1. Broad pattern replacements for known Mojibake
    replacements = {
        "ط ̈": "ب", "ظ...": "م", "ظ‚": "ق", "طھ": "ت", "ط§": "ا", "ظ„": "ل",
        "ط ̄": "د", "ط¬": "ج", "ط ́": "ش", "ظˆ": "و", "ط±": "ر", "ط­": "ح",
        "ط¹": "ع", "ط©": "ة", "ط§": "ا", "ط²": "ز", "ط·": "ط", "ط«": "ث",
        "ط®": "خ", "ط°": "ذ", "ط¹": "ع", "ط؛": "غ", "ظپ": "ف", "ظƒ": "ك",
        "ظ†": "ن", "ظ‡": "ه", "ظٹ": "ي", "ط¦": "ئ", "ط£": "أ", "ط¤": "ؤ",
        "ط¥": "إ", "آ": "آ", "ï؛3": "س", "ï»1⁄4": "لا", "ï» ́": "ي",
        "ï؛»ï؛¤ï»¦": "صحن", "ï»ںï؛¤ï»¢": "لحم", "ï»›ï؛’ة": "كبة", "ط¯.ظ„": "د.ل", "طμ": "ص",
        "ظ€": "", "طŒ": "،", "ظ...ط ́ظƒظ„": "مشكل", "ط§ظ„": "ال", "ط§": "ا",
        "»": "", "ï": "", "؛": "", "°": "ز", "£": "أ", "†": "ن", "¤": "د", "¢": "ت",
        "§": "ا", "€": "خ", "“": "ش", "—": "ت", "”": "ف", "ں": "ن", "ظ": "م",
        "ک": "ك", "ا": "ا", "ب": "ب", "ت": "ت", "ث": "ث", "ج": "ج", "ح": "ح",
        "خ": "خ", "د": "د", "ذ": "ذ", "ر": "ر", "ز": "ز", "س": "س", "ش": "ش",
        "ص": "ص", "ض": "ض", "ط": "ط", "ظ": "ظ", "ع": "ع", "غ": "غ", "ف": "ف",
        "ق": "ق", "ك": "ك", "ل": "ل", "م": "م", "ن": "ن", "ه": "ه", "و": "و",
        "ي": "ي", "ة": "ة", "ى": "ى", "أ": "أ", "إ": "إ", "آ": "آ", "ؤ": "ؤ", "ئ": "ئ"
    }
    
    # Actually, a better approach for Mojibake is decoding again if it fits
    # But since the file is already a mix of fixed and garbled, pattern matching is safer.
    
    # 2. Hard mapping for common items to ensure 100% accuracy
    hard_mapping = {
        "Appetizers": "المقبلات",
        "Soups": "الشوربات",
        "Salads": "السلطات",
        "Pasta": "المكرونة",
        "Risotto": "الريزوتو",
        "Pizza": "البيتزا",
        "Safiha": "الصفائح",
        "Fajita Meals": "وجبات فاهيتا",
        "Meat Selection": "غربي اللحوم",
        "Chicken Selection": "غربي الدجاج",
        "Seafood": "المأكولات البحرية",
        "Oriental Kitchen": "المطبخ الشرقي",
        "Desserts": "الحلويات",
        "Beverages": "المشروبات",
        "Breakfast (8 AM to 1 PM)": "الافطار من (8ص الى 1م)",
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
        "Caesar Salad": "سلطة سيزر",
        "Tuna Salad": "سلطة تونة",
        "Greek Salad": "سلطة يونانية",
        "Lavina Special Salad": "سلطة لافينا الخاصة",
        "Seafood Pasta": "مكرونة فواكه البحر",
        "Shrimp Linguine": "لينجويني جمبري",
        "Bolognese Lasagna": "لازانيا بولونيز",
        "Chicken Bchamel": "بشاميل دجاج",
        "Mushroom Risotto": "ريزوتو فقع",
        "Seafood Risotto": "ريزوتو فواكه البحر",
        "Margherita": "مارغريتا",
        "Vegetable": "خضروات",
        "Mushroom": "فقع",
        "Tuna": "تونة",
        "Regina Pizza": "بيتزا ريجينا",
        "Pesto Pizza": "بيتزا بيستو",
        "Quattro Formaggi Pizza": "بيتزا كواترو فورماجي",
        "Chicken Pizza": "بيتزا دجاج",
        "Bianca Pizza": "بيتزا بيانكا",
        "Lavina Pizza": "بيتزا لافينا",
        "Meat Safiha": "صفيحة لحم",
        "Cheese Safiha": "صفيحة جبنة",
        "Cheese and Meat Safiha": "صفيحة بجبنة ولحم",
        "Zaatar Safiha": "صفيحة زعتر",
        "Zaatar and Cheese Safiha": "صفيحة زعتر وجبنة",
        "Meat Safiha with Cheese and Zaatar": "صفيحة لحم بجبنة وزعتر",
        "Family Size Safiha": "صفيحة عائلية",
        "Chicken Fajita Meal": "وجبة فاهيتا دجاج",
        "Beef Fajita Meal": "وجبة فاهيتا لحم",
        "Mixed Fajita Meal": "وجبة فاهيتا ميكس",
        "Fillet with Mushroom Sauce": "فيلييه صوص ماشروم",
        "Fillet with Lemon Sauce": "فيلييه صوص ليمون",
        "Fillet with Black Pepper Sauce": "فيلييه بصلصة الفلفل الأسود",
        "T-Bone Steak": "تي بون",
        "Filet Mignon": "فيلييه المينيون",
        "Lamb Chops with Lemon Sauce": "أرياش خروف بصوص ليمون",
        "Fillet with Gravy Sauce": "فيلييه صوص جريفى",
        "Fillet with Tomato and Cheese Sauce": "فيلييه صوص طماطم وجبن",
        "Grilled Fillet": "فيلييه مشوي",
        "Chicken Breast with Mushroom Sauce": "تشيكن بريست بصوص ماشروم",
        "Chicken Breast Pane": "تشيكن بريست بانية",
        "Chicken Breast with Lemon Sauce": "تشيكن بريست بصوص ليمون",
        "Chicken Roll with Spinach and Mozzarella": "رول دجاج بالسبانخ والموزاريلا",
        "Cordon Bleu": "كوردون بلو",
        "Chicken Breast": "تشيكن بريست",
        "Grilled Sea Bass": "قاروص مشوي",
        "Sea Bass Fillet": "فيلييه قاروص",
        "Grilled Shrimp": "جمبري مشوي",
        "Bream Slices with Lemon Sauce": "شرائح وراثة بصوص ليمون",
        "Paella": "باييلا",
        "Lavina Seafood Mix": "لوحة لافينا أسماك",
        "Shish Taouk": "شيش طاووق",
        "Chicken Kebab": "كباب دجاج",
        "Half Grilled Chicken": "نصف دجاجة مشوية",
        "Meat Kebab": "كباب لحم",
        "Lamb Shish": "شيش لحم خروف",
        "Lamb Chops": "أرياش خروف",
        "Mixed Grill": "مشويات مشكلة",
        "Grilled Liver": "كبدة مشوية",
        "Lamb Meat with Rice (Kabsa)": "لحم خروف مع الأرز (كبسة)",
        "Shish Bark": "شيشبرك",
        "Meat with Dough (Kibe)": "كبة بالصينية",
        "Hummus with Meat": "حمص باللحمة",
        "Chicken Wings": "أجنحة دجاج",
        "Chicken Liver": "كبدة دجاج",
        "Chicken Escalope": "إسكالوب دجاج",
        "Chicken Burger": "تشيكن برجر",
        "Meat Burger": "ميت برجر",
        "Fajita Sandwich": "سندوتش فاهيتا",
        "Steak Sandwich": "سندوتش ستيك",
        "Zinger Sandwich": "سندوتش زينجر",
        "Chicken Escalope Sandwich": "سندوتش إسكالوب دجاج",
        "Spicy Potato": "بطاطا حارة",
        "Cheese Cake": "تشيز كيك",
        "Tiramisu": "تيراميسو",
        "Fruit Salad": "سلطة فواكه",
        "Pancakes": "بان كيك",
        "Waffles": "وافل",
        "Fondue": "فوندو",
        "San Sebastian": "سان سيباستيان",
        "Kunafa": "كنافة",
        "Pistachio Kunafa": "كنافة بستاشيو",
        "Cream Kunafa": "كنافة قشطة",
        "Cheese Kunafa": "كنافة جبنة",
        "Turkish Tea": "شاي تركي",
        "Arabic Coffee": "قهوة عربية",
        "Fresh Orange Juice": "عصير برتقال فريش",
        "Lemon with Mint": "ليمون ونعناع",
        "Strawberry Juice": "عصير فراولة",
        "Mango Juice": "عصير مانجو",
        "Mixed Fruits Juice": "عصير فواكه",
        "Avocado with Honey and Nuts": "أفوكادو بالعسل والمكسرات",
        "Mojito": "موهيتو",
        "Classic Mojito": "موهيتو كلاسيك",
        "Strawberry Mojito": "موهيتو فراولة",
        "Blue Lagoon Mojito": "موهيتو بلو لاغون",
        "Red Bull Mojito": "موهيتو ريد بول",
        "Milkshake": "ميلك شيك",
        "Vanilla Milkshake": "ميلك شيك فانيلا",
        "Chocolate Milkshake": "ميلك شيك شوكولاتة",
        "Strawberry Milkshake": "ميلك شيك فراولة",
        "Oreo Milkshake": "ميلك شيك أوريو",
        "Iced Tea": "آيس تي",
        "Peach Iced Tea": "آيس تي خوخ",
        "Lemon Iced Tea": "آيس تي ليمون",
        "Iced Coffee": "آيس كوفي",
        "Frappuccino": "فرابوتشينو",
        "Hot Drinks": "مشروبات ساخنة",
        "Cold Drinks": "مشروبات باردة",
        "Juices": "عصائر",
        "Smoothies": "سموثي",
        "Dessert (Available from 1 PM)": "الحلويات (متوفرة من الساعه 1م)"
    }
    
    return text

def normalize_all_fields(obj):
    hard_mapping = {
        "Appetizers": "المقبلات", "Soups": "الشوربات", "Salads": "السلطات",
        "Pasta": "المكرونة", "Risotto": "الريزوتو", "Pizza": "البيتزا",
        "Safiha": "الصفائح", "Fajita Meals": "وجبات فاهيتا", "Meat Selection": "غربي اللحوم",
        "Chicken Selection": "غربي الدجاج", "Seafood": "المأكولات البحرية",
        "Oriental Kitchen": "المطبخ الشرقي", "Desserts": "الحلويات",
        "Beverages": "المشروبات", "Breakfast (8 AM to 1 PM)": "الافطار من (8ص الى 1م)",
        "Bruschetta": "بروسكيتا", "Meat Bourek": "بوريك لحم", "Meat Kibbeh (4 Pieces)": "كبة لحم (4 قطع)",
        "Mozzarella Fingers": "أصابع موزاريلا", "Fish Fingers": "أصابع سمك",
        "Potato Fries Plate": "صحن بطاطا", "Cheese Sambousek": "سمبوسة بالجبنة",
        "Chicken Strips": "تشيكن ستريبس", "Chicken Pastilla": "بسطيلة دجاج",
        "Seafood Saut\u00e9": "سوتي فواكه البحر", "Lavina Mixed Plate": "صحن لافينا مشكل",
        "Lentil Soup": "شوربة العدس", "Chicken Mushroom Soup": "شوربة الدجاج بالفقع",
        "Shrimp Soup": "شوربة الجمبري", "Arabic Salad": "سلطة عربية", "Hummus Salad": "سلطة حمص",
        "Cole Slaw": "كول سلو", "Caesar Salad": "سلطة سيزر", "Tuna Salad": "سلطة تونة",
        "Greek Salad": "سلطة يونانية", "Lavina Special Salad": "سلطة لافينا الخاصة",
        "Seafood Pasta": "مكرونة فواكه البحر", "Shrimp Linguine": "لينجويني جمبري",
        "Bolognese Lasagna": "لازانيا بولونيز", "Chicken Bchamel": "بشاميل دجاج",
        "Mushroom Risotto": "ريزوتو فقع", "Seafood Risotto": "ريزوتو فواكه البحر",
        "Margherita": "مارغريتا", "Vegetable": "خضروات", "Mushroom": "فقع",
        "Tuna": "تونة", "Regina Pizza": "بيتزا ريجينا", "Pesto Pizza": "بيتزا بيستو",
        "Quattro Formaggi Pizza": "بيتزا كواترو فورماجي", "Chicken Pizza": "بيتزا دجاج",
        "Bianca Pizza": "بيتزا بيانكا", "Lavina Pizza": "بيتزا لافينا",
        "Meat Safiha": "صفيحة لحم", "Cheese Safiha": "صفيحة جبنة",
        "Cheese and Meat Safiha": "صفيحة بجبنة ولحم", "Zaatar Safiha": "صفيحة زعتر",
        "Zaatar and Cheese Safiha": "صفيحة زعتر وجبنة", "Meat Safiha with Cheese and Zaatar": "صفيحة لحم بجبنة وزعتر",
        "Family Size Safiha": "صفيحة عائلية", "Chicken Fajita Meal": "وجبة فاهيتا دجاج",
        "Beef Fajita Meal": "وجبة فاهيتا لحم", "Mixed Fajita Meal": "وجبة فاهيتا ميكس",
        "Fillet with Mushroom Sauce": "فيلييه صوص ماشروم", "Fillet with Lemon Sauce": "فيلييه صوص ليمون",
        "Fillet with Black Pepper Sauce": "فيلييه بصلصة الفلفل الأسود", "T-Bone Steak": "تي بون",
        "Filet Mignon": "فيلييه المينيون", "Lamb Chops with Lemon Sauce": "أرياش خروف بصوص ليمون",
        "Fillet with Gravy Sauce": "فيلييه صوص جريفى", "Fillet with Tomato and Cheese Sauce": "فيلييه صوص طماطم وجبن",
        "Grilled Fillet": "فيلييه مشوي", "Chicken Breast with Mushroom Sauce": "تشيكن بريست بصوص ماشروم",
        "Chicken Breast Pane": "تشيكن بريست بانية", "Chicken Breast with Lemon Sauce": "تشيكن بريست بصوص ليمون",
        "Chicken Roll with Spinach and Mozzarella": "رول دجاج بالسبانخ والموزاريلا", "Cordon Bleu": "كوردون بلو",
        "Chicken Breast": "تشيكن بريست", "Grilled Sea Bass": "قاروص مشوي",
        "Sea Bass Fillet": "فيلييه قاروص", "Grilled Shrimp": "جمبري مشوي",
        "Bream Slices with Lemon Sauce": "شرائح وراثة بصوص ليمون", "Paella": "باييلا",
        "Lavina Seafood Mix": "لوحة لافينا أسماك", "Shish Taouk": "شيش طاووق",
        "Chicken Kebab": "كباب دجاج", "Half Grilled Chicken": "نصف دجاجة مشوية",
        "Meat Kebab": "كباب لحم", "Lamb Shish": "شيش لحم خروف", "Lamb Chops": "أرياش خروف",
        "Mixed Grill": "مشويات مشكلة", "Grilled Liver": "كبدة مشوية",
        "Lamb Meat with Rice (Kabsa)": "لحم خروف مع الأرز (كبسة)", "Shish Bark": "شيشبرك",
        "Meat with Dough (Kibe)": "كبة بالصينية", "Hummus with Meat": "حمص باللحمة",
        "Chicken Wings": "أجنحة دجاج", "Chicken Liver": "كبدة دجاج", "Chicken Escalope": "إسكالوب دجاج",
        "Chicken Burger": "تشيكن برجر", "Meat Burger": "ميت برجر", "Fajita Sandwich": "سندوتش فاهيتا",
        "Steak Sandwich": "سندوتش ستيك", "Zinger Sandwich": "سندوتش زينجر", "Chicken Escalope Sandwich": "سندوتش إسكالوب دجاج",
        "Spicy Potato": "بطاطا حارة", "Cheese Cake": "تشيز كيك", "Tiramisu": "تيراميسو",
        "Fruit Salad": "سلطة فواكه", "Pancakes": "بان كيك", "Waffles": "وافل", "Fondue": "فوندو",
        "San Sebastian": "سان سيباستيان", "Kunafa": "كنافة", "Pistachio Kunafa": "كنافة بستاشيو",
        "Cream Kunafa": "كنافة قشطة", "Cheese Kunafa": "كنافة جبنة", "Turkish Tea": "شاي تركي",
        "Arabic Coffee": "قهوة عربية", "Fresh Orange Juice": "عصير برتقال فريش", "Lemon with Mint": "ليمون ونعناع",
        "Strawberry Juice": "عصير فراولة", "Mango Juice": "عصير مانجو", "Mixed Fruits Juice": "عصير فواكه",
        "Avocado with Honey and Nuts": "أفوكادو بالعسل والمكسرات", "Mojito": "موهيتو",
        "Classic Mojito": "موهيتو كلاسيك", "Strawberry Mojito": "موهيتو فراولة",
        "Blue Lagoon Mojito": "موهيتو بلو لاغون", "Red Bull Mojito": "موهيتو ريد بول",
        "Milkshake": "ميلك شيك", "Vanilla Milkshake": "ميلك شيك فانيلا",
        "Chocolate Milkshake": "ميلك شيك شوكولاتة", "Strawberry Milkshake": "ميلك شيك فراولة",
        "Oreo Milkshake": "ميلك شيك أوريو", "Iced Tea": "آيس تي", "Peach Iced Tea": "آيس تي خوخ",
        "Lemon Iced Tea": "آيس تي ليمون", "Iced Coffee": "آيس كوفي", "Frappuccino": "فرابوتشينو",
        "Hot Drinks": "مشروبات ساخنة", "Cold Drinks": "مشروبات باردة", "Juices": "عصائر",
        "Smoothies": "سموثي", "Dessert (Available from 1 PM)": "الحلويات (متوفرة من الساعه 1م)"
    }
    
    # Also image mapping to fix garbled paths
    image_mapping = {
        "ط ̈ط±ظˆط3ظƒظٹطھط§.PNG": "بروسكيتا.PNG",
        "طھط ́ظƒظ† ط3طھط±ظٹط ̈ط3.PNG": "تشيكن ستريبس.PNG",
        "ط ̈ط3ط·ظٹظ„ط§ ط ̄ط¬ط§ط¬.jpg": "بسطيلة دجاج.jpg",
        "ط±ظٹط2ظˆطھظˆ ظپظˆط§ظƒظ‡ الط ̈ط­ط±.jpg": "ريزوتو فواكه البحر.jpg",
        "ظˆط¬ط ̈ط© ظپط§ظ‡ظٹطھط§ ظ„ط­ظ....PNG": "وجبة فاهيتا لحم.PNG",
        "ظپظٹظ„ظٹظ‡ ظ...ط ́ظˆظٹ.PNG": "فيلييه مشوي.PNG",
        "ظ†ط¬ط±ظٹط3ظƒظˆ ط ̄ط¬ط§ط¬.PNG": "نجريسكو دجاج.PNG",
        "طھط ́ظٹظƒظ† ط ̈ط±ظٹط3طھ.PNG": "تشيكن بريست.PNG",
        "ط ̈ط§ط¬ظٹطھ ط ̄ط¬ط§ط¬ ظ...ط ́ظˆظٹ.PNG": "باجيت دجاج مشوي.PNG",
        "ط ̈ط§ط3طھط§ ظپظˆط§ظƒظ‡ الط ̈ط¬ط± طμظˆطμ ط±ظˆط2ظٹ.PNG": "مكرونة فواكه البحر صوص روزي.PNG",
        "ط ̈ط§ط3طھط§ ط¬ظ...ط ̈ط±ظٹ طμظˆطμ ظˆط±ط ̄ظٹ.PNG": "مكرونة جمبري صوص وردي.PNG",
        "ط ̈ط§ط3طھط§ ط¬ظ...ط ̈ط±ظٹ طμظˆطμ  ط±ظˆط2ظٹ.PNG": "مكرونة جمبري صوص روزي.PNG"
    }

    def clean_val(val, field_name, item_en_name):
        if not isinstance(val, str) or not val: return val
        
        # Priority 1: Image Mapping
        if field_name == "image":
            for old, new in image_mapping.items():
                if old in val: return val.replace(old, new)
            # If not in mapping, apply basic mojibake fix to path
            path_parts = val.split('/')
            if len(path_parts) > 1:
                filename = path_parts[-1]
                # Applying a very restricted fix for filenames to avoid breaking extensions
                filename = filename.replace("ط ̈", "ب").replace("ط§", "ا").replace("ظ„", "ل").replace("طھ", "ت").replace("ط ̄", "د").replace("ط¬", "ج").replace("ط ́", "ش").replace("ظˆ", "و").replace("ط±", "ر").replace("طμ", "ص").replace("ظ...", "م").replace("ط3", "س").replace("ط­", "ح").replace("ط·", "ط")
                return "/".join(path_parts[:-1] + [filename])
            return val
            
        # Priority 2: Hard-mapping by en_name
        if field_name == "name" and item_en_name in hard_mapping:
            return hard_mapping[item_en_name]
            
        # Priority 3: General Mojibake Clean
        v = val
        v = v.replace("ط ̈", "ب").replace("ط§", "ا").replace("ظ„", "ل").replace("ظ...", "م").replace("ظ‚", "ق").replace("طھ", "ت").replace("ط ̄", "د").replace("ط¬", "ج").replace("ط ́", "ش").replace("ظˆ", "و").replace("ط±", "ر").replace("ط­", "ح").replace("ط¹", "ع").replace("ط©", "ة").replace("ط²", "ز").replace("ط·", "ط").replace("ط«", "ث").replace("ط®", "خ").replace("ط°", "ذ").replace("ط؛", "غ").replace("ظپ", "ف").replace("ظƒ", "ك").replace("ظ†", "ن").replace("ظ‡", "ه").replace("ظٹ", "ي").replace("ط¦", "ئ").replace("ط£", "أ").replace("ط¤", "ؤ").replace("ط¥", "إ").replace("آ", "آ").replace("طμ", "ص")
        v = v.replace("ï؛3", "س").replace("ï»1⁄4", "لا").replace("ï» ́", "ي").replace("ï؛»", "ص").replace("ï؛¤", "ح").replace("ï»¦", "ن").replace("ï»ں", "ل").replace("ï؛¤", "ح").replace("ï»¤", "م").replace("ï؛’", "ب").replace("ï؛®", "ر").replace("ï»®", "و").replace("ï»œ", "ك").replace("ï؛ک", "ت").replace("ï؛ژ", "ا").replace("ï؛·", "ش").replace("ï؛”", "ة").replace("ï؛ھ", "د").replace("ï»Œ", "ع")
        v = re.sub(r'ط§ظ„', 'ال', v)
        v = re.sub(r'ط§', 'ا', v)
        v = v.replace("ط ̄.ظ„", "د.ل").replace("ط ̄.ظ", "د.ل")
        
        # Cleanup strange separators
        v = v.replace("»", "").replace("ï", "").replace("؛", "").replace("°", "").replace("¤", "").replace("¢", "").replace("§", "").replace("€", "").replace("“", "").replace("—", "").replace("”", "").replace("ں", "").replace("£", "أ").replace("†", "ن").replace("ک", "ك")
        
        # Strip remaining non-arabic/non-standard chars if they are single artifacts
        if len(v) > 1:
            v = re.sub(r'[\u0080-\u00FF]', '', v)
            
        return v.strip()

    if isinstance(obj, list):
        for item in obj: normalize_all_fields(item)
    elif isinstance(obj, dict):
        en_name = obj.get("en_name", "")
        # First pass: Clean names and descs
        for k in ["name", "desc", "price", "image", "variant_name"]:
            if k in obj:
                obj[k] = clean_val(obj[k], k, en_name)
        
        # English cleaning
        for k in ["en_name", "en_desc", "variant_en_name"]:
            if k in obj and isinstance(obj[k], str):
                obj[k] = re.sub(r'[^\x00-\x7F\s\(\)/,.-]+', '', obj[k]).strip()
        
        # Recurse
        for k in ["subcategories", "items", "variants"]:
            if k in obj:
                normalize_all_fields(obj[k])

def run_v3_restoration():
    file_path = r'c:\Users\malek drebi\Desktop\LAVINA\LavinaHouseMenu\index.html'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.search(r'const menuData = (\[.*?\]);', content, re.DOTALL)
    if not match: return

    data = json.loads(match.group(1))
    normalize_all_fields(data)

    new_json_str = json.dumps(data, ensure_ascii=False, indent=4)
    new_content = content.replace(match.group(0), f"const menuData = {new_json_str};")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Success! index.html text has been cleaned (v3).")

if __name__ == "__main__":
    run_v3_restoration()
