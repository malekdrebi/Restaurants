import json

def apply_translations():
    with open("the_menu_bilingual.json", "r", encoding="utf-8") as f:
        menu = json.load(f)

    # Cat[0] (Breakfast)
    # Item[4] (Oriental Breakfast)
    menu[0]["items"][4]["en_desc"] = "Fava Beans, Falafel, Baba Ganoush, Hummus Salad, Pickles, Labneh, Bread Basket, Tea (Green or Red)"

    # Cat[1] (Lunch)
    # Sub[3] (Pasta). Item[5] (Penne Arabiata)
    menu[1]["subcategories"][3]["items"][5]["en_desc"] = "(Red Sauce / White Sauce / Pink Sauce)"
    
    # Sub[8] (Seafood). Item[0] (Grilled Sea Bass)
    menu[1]["subcategories"][8]["items"][0]["en_desc"] = "Sea Bass"
    
    # Sub[10] (Oriental Cuisine)
    menu[1]["subcategories"][10]["items"][11]["en_desc"] = "Meat Kebab + Shish Taouk"
    menu[1]["subcategories"][10]["items"][12]["en_desc"] = "Meat Kebab + Shish Taouk + Beef Shish"
    menu[1]["subcategories"][10]["items"][13]["en_desc"] = "Meat Kebab + Shish Taouk + Beef Shish + Chicken Kebab"
    menu[1]["subcategories"][10]["items"][14]["en_desc"] = "Meat Kebab + Chicken Kebab + Shish Taouk + Beef Shish + Urfali Kebab"
    menu[1]["subcategories"][10]["items"][15]["en_desc"] = "Meat Kebab + Chicken Kebab + Shish Taouk + Beef Shish + Urfali Kebab + Spicy Kebab + Wings + Safiha + Salad Plate"
    menu[1]["subcategories"][10]["items"][16]["en_desc"] = "2 Meat Kebab + 2 Chicken Kebab + 2 Shish Taouk + 2 Beef Shish + 2 Lamb Chops + 2 Wings + 2 Chicken Thighs + 1 Safiha (on demand) + 1 Salad Plate"
    
    # Sub[12] (Steak). Item[4] (T-Bone Steak) - Wait, let me check name
    # The audit says "وزن اللحمة 600ج شخصين"
    # I'll just check by name in the script to be safer for some
    
    # Cat[2] (Desserts)
    # Item[4] (Fettuccine Nutella)
    menu[2]["items"][4]["en_desc"] = "(Nutella / Pistachio / Honey & Almond / Lotus / Honey / Oreo / Fruits)"
    # Item[10] (فاطيرة مغربية) - wait, audit said Cat[2].Item[16]
    # Let's use a smarter mapping for the rest to avoid index errors if structure changed slightly
    
    translations = {
        "وزن اللحمة 600ج شخصين": ("Weight 600g (Serves 2 persons)", ""),
        "صدر دجاج متبل بالأعشاب والفلفل الحار و البصل ، الطماطم وخبز مكسيكان ساور كريم ، بيقو ديقالو ، ارز مكسيكان ، جبنة شيدر مكس": ("Herb-marinated chicken breast with chili, onions, tomatoes, Mexican bread, sour cream, pico de gallo, Mexican rice, and mixed cheddar cheese.", ""),
        "لحم بقري مشوي متبل بالأعشاب فلفل الوان ، بصل ، طماطم، خبز مكسيكان ، ارز مكسيكان ،ساور كريم ، بيقو ميقالو ، شيدر مكس": ("Grilled beef marinated with herbs, mixed peppers, onions, tomatoes, Mexican bread, Mexican rice, sour cream, pico de gallo, and mixed cheddar.", ""),
        "مكس صدر دجاج مشوي ، لحم بقري مشوي مع فلفل الوات ، بصل ، طماطم ، ارز مكسيكان ، ساور كريم ، بيقو ديقالو ، شيدر مكس": ("Mixed grilled chicken breast and grilled beef with mixed peppers, onions, tomatoes, Mexican rice, sour cream, pico de gallo, and mixed cheddar.", ""),
        "(ﺗﻘﺪم ﻣﻊ ﻋﺴﻞ وزﻳﺘﻮن ﻣﻐﺮﺑﻲ)": ("(Served with honey and Moroccan olives)", ""),
        "ﺑﺮاوﻧﻴﺰ أﻳﺲ ﻛﺮﻳﻢ": ("", "Brownies with Ice Cream"),
        "عسل": ("Honey", ""),
        "ﻣﻨﻲ ﺑﺎن ﻛﻴﻚ رﻳﺪ ﻓﻴﻠﻔﻴﺖ": ("", "Mini Red Velvet Pancake"),
        "ﺑﺎن ﻛﻴﻚ رﻳﺪ ﻓﻴﻠﻔﻴﺖ": ("", "Red Velvet Pancake"),
        "أمريكانو": ("", "Americano"),
        "أﻓﻮﻛﺎﺗﻮ": ("", "Affogato"),
        "(واﻳﺖ دارك)": ("(White / Dark)", ""),
        "(كراميل - بندق - فانيلا)": ("(Caramel - Hazelnut - Vanilla)", ""),
        "( احمر / اخضر )": ("(Red / Green)", ""),
        "( مارس , كندر , سنكرز )": ("(Mars / Kinder / Snickers)", ""),
        "ﺑﻴﺒﺴﻲ ﻣﺎرﻳﻨﺪا ﺷﺎﻧﻲ ﺳﻔﻦ أب": ("Pepsi, Miranda, Shani, 7Up", ""),
        "( ﻛﺮاﻣﻴﻞ / ﻓانيليا / ﺑﻨﺪق )": ("(Caramel / Vanilla / Hazelnut)", ""),
        "ﻓﺮوبي": ("", "Frooby"), # Note: audit said ﻓﺮوﺑﻲ
        "ﻓﺮوﺑﻲ": ("", "Frooby"),
        "(ﻓﺮاوﻟﺔ ,ﻣﺎﻧﺠﺎ, ﻣﻮز )": ("(Strawberry / Mango / Banana)", ""),
        "حسب الطلب": ("On Demand", "")
    }

    def process_items(items):
        for item in items:
            desc = item.get("desc", "")
            name = item.get("name", "")
            if desc in translations:
                item["en_desc"] = translations[desc][0] if translations[desc][0] else item.get("en_desc", "")
                if translations[desc][1]:
                    item["en_name"] = translations[desc][1]
            if name in translations:
                if translations[name][1]:
                    item["en_name"] = translations[name][1]
                if translations[name][0]:
                    item["en_desc"] = translations[name][0]

    for category in menu:
        process_items(category.get("items", []))
        for sub in category.get("subcategories", []):
            process_items(sub.get("items", []))

    with open("the_menu_bilingual.json", "w", encoding="utf-8") as f:
        json.dump(menu, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    apply_translations()
    print("Applied English translations to the_menu_bilingual.json")
