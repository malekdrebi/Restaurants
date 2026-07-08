import json
import re

def final_word_fix():
    file_path = r'c:\Users\malek drebi\Desktop\LAVINA\LavinaHouseMenu\index.html'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.search(r'const menuData = (\[.*?\]);', content, re.DOTALL)
    if not match: return

    data = json.loads(match.group(1))

    # Comprehensive word-level garbled mapping
    word_map = {
        "›رگ": "كريب",
        "أ̈ن ›ي": "ميني بان كيك",
        "بان ›ي": "بان كيك",
        "ويلا": "نوتيلا",
        "‹́‍": "عسل",
        "أ̈اد": "أفخاذ",
        "أرروف": "أرياش خروف",
        "شي¶": "شيش",
        "›’اب": "كباب",
        "‹ير": "عصير",
        "واي̈ا": "لافينيا",
        "ا’ر": "البحر",
        "طص": "صوص",
        "ا£¤ر": "الأحمر",
        "ابيس⁄4": "الأبيض",
        "بي̈": "الوردي",
        "›ورادو": "كورتادو",
        "أكياو": "ماكياتو",
        "لات وا–": "فلات وايت",
        "›ابت̧ي̈و": "كابتشينو",
        "›ا‡": "كافيه لاتيه",
        "س’ا": "سبانيش لاتيه",
        "›اأو›ا": "كافيه موكا",
        "́كاية": "نسكافيه",
        "أ̧ك‍": "مشكل",
        "”ي¤ة": "صفيحة",
        "ايتا": "فاهيتا",
        "أترد": "لوحة",
        "سلا›ول س": "سلطة كول سلو",
        "سلار": "سلطة جرجير",
        "سلاأ̧و": "سلطة مشوية",
        "سلاڈ̈وش": "سلطة بابا غنوج",
        "سلاتوش": "سلطة فتوش",
        "سلاوا›ة": "سلطة فواكه",
        "سلاي̈ا": "سلطة لافينا",
        "أ̈ن": "بان",
        "ور2": "أورفا",
        "ادا": "أضنة",
        "أار": "حار",
        "أير": "ميني",
        "› ̈": "كلوب",
        "بر": "برجر",
        "باي–": "باجيت",
        "›رواسون": "كرواسون",
        "„يرة": "فطيرة",
        "وا‍": "وافل",
        "براوي": "براونيز",
        "أ ́": "فواكه",
        "المط·بط®": "المطبخ",
        "̧كي ا–": "تشيكن ناجتس",
        "دأ̧وي": "أجنحة دجاج",
        "̈ دأ̧وي": "أفخاذ دجاج",
        "3ييو": "ريد فيلفيت",
        "3و": "أوريو",
        "ا2 كر": "آيس كريم",
        "أخطر": "أخضر",
        "أ ́وس": "الموسم",
        "أ ́گ الموس": "فاكهة الموسم",
        "أرأروف": "أرياش خروف",
        "بي́تو": "بيستو",
        "باستا أربياا": "باستا أرابيتا",
        "ارھو": "الفريدو",
        "بوي": "بولونيز",
        "روط2و—و": "ريزوتو",
        "و—و": "وتو",
        "قمبرظي": "جمبري",
        "طصير": "عصير",
        "ون و ̈اط": "ليمون ونعناع",
        "—̧كي": "تشيكن",
        "س’ا": "سبانيش",
        "ي̈ا": "لافينا"
    }

    # Character-level messy mappings for strings that are still slightly broken
    char_map = {
        "أ̧ك‍": "مشكل",
        "أ̈": "ب",
        "›": "ك",
        "‹": "ع",
        "–": "و",
        "¶": "ش",
        "”": "ص",
        "¤": "ة",
        "£": "أ",
        "†": "ن",
        "ک": "ك",
        "ا": "ا",
        "ب": "ب",
        "ت": "ت",
        "ج": "ج",
        "ح": "ح",
        "خ": "خ",
        "د": "د",
        "ر": "ر",
        "ز": "ز",
        "س": "س",
        "ش": "ش",
        "ص": "ص",
        "ط": "ط",
        "ع": "ع",
        "ف": "ف",
        "ق": "ق",
        "ك": "ك",
        "ل": "ل",
        "م": "م",
        "ن": "ن",
        "ه": "ه",
        "و": "و",
        "ي": "ي"
    }

    def deep_replace(obj):
        if isinstance(obj, list):
            for i in obj: deep_replace(i)
        elif isinstance(obj, dict):
            for k in ["name", "desc", "variant_name", "price"]:
                if k in obj and isinstance(obj[k], str):
                    # Word replace
                    for old, new in word_map.items():
                        obj[k] = obj[k].replace(old, new)
                    # Clean up any leftover single garbled chars if they are sticking out
                    # (only if the string still looks garbled)
                    if any(c in obj[k] for c in "›‹–¶”¤£†ک"):
                         obj[k] = "".join([char_map.get(c, c) for c in obj[k]])
                         # Final cleanup of common artifacts
                         obj[k] = obj[k].replace("ـ", "").replace("  ", " ").strip()
            for k in ["subcategories", "items", "variants"]:
                if k in obj: deep_replace(obj[k])

    deep_replace(data)
    
    # Final check: any price containing 'ط' should be 'د.ل'
    def fix_prices(obj):
        if isinstance(obj, list):
            for i in obj: fix_prices(i)
        elif isinstance(obj, dict):
            if "price" in obj and isinstance(obj["price"], str):
                if "د.ل" not in obj["price"] and any(c in obj["price"] for c in "طظ"):
                    obj["price"] = re.sub(r'[^\d.]+', '', obj["price"]) + " د.ل"
            for k in ["items", "variants", "subcategories"]:
                if k in obj: fix_prices(obj[k])
    
    fix_prices(data)

    new_json_str = json.dumps(data, ensure_ascii=False, indent=4)
    new_content = content.replace(match.group(0), f"const menuData = {new_json_str};")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Word-level fix complete.")

if __name__ == "__main__":
    final_word_fix()
