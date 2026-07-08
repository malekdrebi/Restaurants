import re

def fix_content(content):
    # Mapping of specific strings to fix
    fixes = {
        # Smoothies
        'سموذي': 'سموثي',
        # Margarita
        'مارغريتا': 'مارجاريتا',
        # Pepperoni typos (the user said correct is ببيروني)
        'بببروني': 'ببيروني',
        'ببروني': 'ببيروني',
        # Fix specific multi-word issues if needed
    }
    
    new_content = content
    for old, new in fixes.items():
        # Using word boundaries for Arabic is tricky with re, but since these are specialized words in quotes, 
        # simple replace inside the JSON structure is relatively safe if we check context.
        # We will use simple replace for these specific unique menu words.
        new_content = new_content.replace(old, new)
        
    return new_content

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

fixed = fix_content(content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(fixed)

print("Applied final consistency fixes.")
