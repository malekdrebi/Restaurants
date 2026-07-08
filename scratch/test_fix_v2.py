import unicodedata
import json

# Example presentation forms from the file
p_forms = "ï؛‘ï؛®ظˆï؛³ï»œï»´ï؛کï؛ژ" # This looks like raw bytes interpreted as Latin-1

def fix_string(s):
    try:
        # Step 1: Fix corrupted UTF-8
        # Try encoding as CP1252 (commonly misinterpreted as Latin-1/CP1252)
        # then decoding as UTF-8
        b = s.encode('cp1252')
        s = b.decode('utf-8')
    except:
        pass
    
    # Step 2: Normalize Unicode
    # NFKC can help with some presentation forms
    s = unicodedata.normalize('NFKC', s)
    
    return s

examples = [
    "ط§ظ„ظ…ظ‚ط¨ظ„ط§طھ",
    "ï؛‘ï؛®ظˆï؛³ï»œï»´ï؛کï؛ژ",
    "ط§ظ„ط´ظˆط±ط¨ط§طھ",
    "ï؛·ï»®ط±ï؛‘ï؛” ط§ï»ںï»Œï؛ھط³"
]

results = []
for ex in examples:
    fixed = fix_string(ex)
    results.append({
        "original": ex,
        "fixed": fixed
    })

with open(r'c:\Users\malek drebi\Desktop\LAVINA\LavinaHouseMenu\scratch\fix_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)
