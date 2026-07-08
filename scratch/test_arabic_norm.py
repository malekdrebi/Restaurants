import unicodedata
import re

def get_base_arabic(char):
    try:
        name = unicodedata.name(char)
        if "ARABIC LETTER" in name or "ARABIC TATWEEL" in name:
            # Special cases for Hamza and other variants
            if "ALEF WITH MADDA ABOVE" in name: return "آ"
            if "ALEF WITH HAMZA ABOVE" in name: return "أ"
            if "WAW WITH HAMZA ABOVE" in name: return "ؤ"
            if "ALEF WITH HAMZA BELOW" in name: return "إ"
            if "YEH WITH HAMZA ABOVE" in name: return "ئ"
            
            # General case: Extract the base letter name
            # Example: "ARABIC LETTER BAA INITIAL" -> "BAA"
            match = re.search(r'ARABIC LETTER ([A-Z ]+)(?: INITIAL| MEDIAL| FINAL| ISOLATED)', name)
            if match:
                base_name = match.group(1).strip()
                # Find the standard version of this letter
                # This is a bit tricky, but NFKC often works for this!
                norm = unicodedata.normalize('NFKC', char)
                if any(0x0600 <= ord(c) <= 0x06FF for c in norm):
                    return norm
        return char
    except:
        return char

def normalize_arabic(text):
    # First, fix misinterpreted UTF-8 bytes if they exist
    try:
        # Check if the text contains patterns like "ط§ظ„"
        if "ط" in text or "ظ" in text:
            # Try to recover from CP1252 mis-encoding
            # This is common in legacy conversions
            b = text.encode('cp1252')
            text = b.decode('utf-8')
    except:
        pass

    # Then, normalize presentation forms
    fixed = ""
    for char in text:
        if 0xFB50 <= ord(char) <= 0xFDFF or 0xFE70 <= ord(char) <= 0xFEFF:
            fixed += get_base_arabic(char)
        else:
            fixed += char
            
    # Final pass: Standard Arabic normalization
    fixed = unicodedata.normalize('NFKC', fixed)
    return fixed

# Test on patterns from the file
test_cases = [
    "ï؛‘ï؛®ظˆï؛³ï»œï»´ï؛کï؛ژ", # Bruschetta
    "ط§ظ„ظ…ظ‚ط¨ظ„ط§طھ", # Appetizers
    "ï؛·ï»®ط±ï؛‘ï؛” ط§ï»ںï»Œï؛ھط³", # Lentil Soup
    "ط¯.ظ„", # LYD price
]

for tc in test_cases:
    print(f"Original: {tc}")
    print(f"Normalized: {normalize_arabic(tc)}")
    print("-" * 20)
