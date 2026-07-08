import json
import re
import unicodedata

# Mapping common presentation form blocks characters to baseline Arabic
# Range A: U+FB50 - U+FDFF
# Range B: U+FE70 - U+FEFF
def get_base_arabic(char):
    try:
        # Standard normalization works for many of these if they are correctly decoded
        norm = unicodedata.normalize('NFKC', char)
        if any(0x0600 <= ord(c) <= 0x06FF for c in norm):
            return norm
        
        # Manually handling some persistent variants or non-NFKC mapping
        name = unicodedata.name(char)
        # BAA, TAA, etc. - if NFKC failed search for the base
        if "ARABIC LETTER" in name:
            # This is a fallback but NFKC is usually enough
            pass
        return char
    except:
        return char

def fix_all_issues(text):
    if not isinstance(text, str) or not text:
        return text

    # PHASE 1: Fix Misinterpreted UTF-8 (Mojibake)
    # Common pattern: "ط§ظ„" (AL-)
    if ("ط§ظ„" in text or "ط¯.ظ„" in text or "ط°" in text):
        try:
            # Try to recover from cp1252/latin-1 to utf-8 conversion failure
            # This handles the "ط§ظ„" -> "ال" case
            b = text.encode('cp1252')
            text = b.decode('utf-8')
        except:
            pass

    # PHASE 2: Fix Presentation Forms (e.g. ï؛‘ï؛®ظˆ)
    # Some strings are mixed. We iterate character by character.
    fixed = ""
    for char in text:
        # Check if in presentation blocks or potentially mis-encoded versions of them
        if 0xFB50 <= ord(char) <= 0xFEFF:
            fixed += get_base_arabic(char)
        else:
            fixed += char
    
    # PHASE 3: Standardize and Cleanup
    # NFKC normalizes things like Hamza-Alef combinations
    fixed = unicodedata.normalize('NFKC', fixed)
    
    # Specific common fixes for this specific file patterns
    replacements = {
        "ط¯.ظ„": "د.ل", # Fix price label if still garbled
        "ط§ظ„": "ال",    # Legacy catch-all
        "ï؛‘": "ب",
        "ï؛®": "ر",
        "ï»®": "و",
        "ï؛³": "س",
        "ï»œ": "ك",
        "ï»´": "ي",
        "ï؛ک": "ت",
        "ï؛ژ": "ا",
        "ï؛·": "ش",
        "ï؛”": "ة"
    }
    for old, new in replacements.items():
        fixed = fixed.replace(old, new)
        
    return fixed

def clean_json_recursive(obj):
    if isinstance(obj, dict):
        return {k: clean_json_recursive(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_json_recursive(i) for i in obj]
    elif isinstance(obj, str):
        return fix_all_issues(obj)
    else:
        return obj

def run_restoration():
    file_path = r'c:\Users\malek drebi\Desktop\LAVINA\LavinaHouseMenu\index.html'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the menuData constant
    match = re.search(r'const menuData = (\[.*?\]);', content, re.DOTALL)
    if not match:
        print("Could not find menuData in index.html")
        return

    json_str = match.group(1)
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")
        # Try to clean common trailing commas or issues before giving up
        fixed_json_str = re.sub(r',\s*\]', ']', json_str)
        fixed_json_str = re.sub(r',\s*\}', '}', fixed_json_str)
        try:
            data = json.loads(fixed_json_str)
        except:
             print("Critical: Could not parse JSON even after structural fix.")
             return

    print("Restoring text contents...")
    cleaned_data = clean_json_recursive(data)

    # Convert back to JSON string with proper indentation
    new_json_str = json.dumps(cleaned_data, ensure_ascii=False, indent=4)
    
    # Inject back into the content
    new_content = content.replace(match.group(0), f"const menuData = {new_json_str};")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Success! index.html has been restored.")

if __name__ == "__main__":
    run_restoration()
