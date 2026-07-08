import json
import os

def apply():
    with open("the_menu_bilingual.json", "r", encoding="utf-8") as f:
        menu_json = f.read()
    
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Inject CSS for Bilingual Toggle
    bilingual_css = """
        /* Language Toggle and Text */
        .lang-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 2000;
            background: var(--bg-secondary);
            border: 1px solid var(--accent-gold);
            border-radius: 30px;
            padding: 5px;
            display: flex;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }

        .lang-btn {
            padding: 8px 15px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--text-secondary);
            transition: all 0.3s ease;
            text-transform: uppercase;
            border: none;
            background: transparent;
        }

        .lang-btn.active {
            background: var(--accent-gold);
            color: var(--bg-color);
        }

        /* Hide logic */
        [lang="en"] .ar-text { display: none !important; }
        [lang="ar"] .en-text { display: none !important; }
        
        [lang="ar"] { direction: rtl; }
        [lang="en"] { direction: ltr; }

        .ar-text { font-family: 'Cairo', sans-serif; }
        .en-text { font-family: 'Montserrat', sans-serif; }
    """
    if ".lang-toggle {" not in html:
        html = html.replace("</style>", bilingual_css + "\n    </style>")

    # 2. Add Language Toggle HTML
    toggle_html = """
    <div class="lang-toggle">
        <button class="lang-btn active" onclick="setLang('ar')">AR</button>
        <button class="lang-btn" onclick="setLang('en')">EN</button>
    </div>
    """
    if '<div class="lang-toggle">' not in html:
        html = html.replace("<body>", "<body>\n" + toggle_html)

    # 3. Inject Updated menuData
    start_marker = "// JSON_DATA_START"
    end_marker = "// JSON_DATA_END"
    
    start_idx = html.find(start_marker)
    end_idx = html.find(end_marker)
    
    if start_idx != -1 and end_idx != -1:
        # Keep the markers and replace everything between them
        # We assume menu_json is the full data, so we need to wrap it in the variable declaration
        new_data_section = f"{start_marker}\n        const menuData = {menu_json};\n        {end_marker}"
        
        # Determine the full range to replace
        # We'll replace from start_marker to end_marker
        html = html[:start_idx] + new_data_section + html[end_idx + len(end_marker):]

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Successfully injected menu data into index.html")

if __name__ == "__main__":
    apply()
