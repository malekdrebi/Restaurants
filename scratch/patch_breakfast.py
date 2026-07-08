import sys
import json

file_path = r'c:\Users\malek drebi\Desktop\LAVINA\LavinaHouseMenu\index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# We want to replace the items in the Breakfast category.
# Based on previous view_file:
# 1547: "name": "ط§ظ„ط§ظپط·ط§ط± ظ…ظ† (8طµ ط§ظ„ظ‰ 1ظ…)",
# 1549: "items": [
# ends around 1696.

start_line = -1
for i, line in enumerate(lines):
    if '"name": "ط§ظ„ط§ظپط·ط§ط± ظ…ظ† (8طµ ط§ظ„ظ‰ 1ظ…)"' in line:
        start_line = i
        break

if start_line == -1:
    print("Could not find anchor line.")
    sys.exit(1)

# Find the end of the items array
end_line = -1
bracket_count = 0
found_items = False
for i in range(start_line, len(lines)):
    if '"items": [' in lines[i]:
        found_items = True
        bracket_count = 1
        continue
    if found_items:
        bracket_count += lines[i].count('[')
        bracket_count -= lines[i].count(']')
        if bracket_count == 0:
            end_line = i
            break

if end_line == -1:
    print("Could not find end of items array.")
    sys.exit(1)

new_breakfast_content = """                "name": "الافطار من (8ص الى 1م)",
                "subcategories": [],
                "items": [
                    {
                        "name": "كونتيننتال",
                        "price": "45 د.ل",
                        "desc": "بريوش , انجليش كيك, بشماط قريسينى, مربى , عسل, زبدة, صحن سلاطة, فواكة مجففة, كوب عصير, قهوة وحليب",
                        "image": "",
                        "en_name": "Continental",
                        "en_desc": "Brioche, English Cake, Grissini, Jam, Honey, Butter, Salad Plate, Dried Fruits, Juice Cup, Coffee and Milk"
                    },
                    {
                        "name": "افطار مغربي",
                        "price": "35 د.ل",
                        "desc": "فطيرة مغربية, عسل, مربى, زبدة, بيض مسلوق, جبنة , سلة خبز, شاي (أخضر أو أحمر )",
                        "image": "",
                        "en_name": "Moroccan Breakfast",
                        "en_desc": "Moroccan Pie, Honey, Jam, Butter, Boiled Egg, Cheese, Bread Basket, Tea (Green or Red)"
                    },
                    {
                        "name": "شرقي",
                        "price": "45 د.ل",
                        "desc": "فول فلافل, بابافنوح, سلاطة حمض, مخللل, لبنة , سلة خبز ,شاي (أخضر أو أحمر)",
                        "image": "images/افطار شرقي.PNG",
                        "en_name": "Oriental Breakfast",
                        "en_desc": "Foul, Falafel, Baba Ganoush, Hummus Salad, Pickles, Labneh, Bread Basket, Tea (Green or Red)"
                    },
                    {
                        "name": "لافينا",
                        "price": "40 د.ل",
                        "desc": "بريوش, أومليت, عسل, مربى, جبنة, فواكه, نوتيلا, زيتون متبل, هريسة, سلة خبز, شاي (أخضر أو أحمر)",
                        "image": "",
                        "en_name": "Lavina",
                        "en_desc": "Brioche, Omelette, Honey, Jam, Cheese, Fruits, Nutella, Seasoned Olives, Harissa, Bread Basket, Tea (Green or Red)"
                    },
                    {
                        "name": "لافينا (عائلي)",
                        "price": "195 د.ل",
                        "desc": "شكشوكة, أومليت, قلاية, مناقيش, أجبان مشكلة, سلاطة مخلل, زيتون متبل, هريسة, بريوش, بن كيك, مربى, فطيرة مغربية, نوتيلا, عسل, ياغورت، زبدة, سلة خبز, براد شاهي (أخضر أو أحمر) (يكفي 3 أشخاص)",
                        "image": "",
                        "en_name": "Lavina (Family)",
                        "en_desc": "Shakshouka, Omelette, Qallaya, Manakish, Assorted Cheeses, Pickled Salad, Seasoned Olives, Harissa, Brioche, Pancake, Jam, Moroccan Pie, Nutella, Honey, Yogurt, Butter, Bread Basket, Large Tea Pot (Green or Red) (Serves 3 Persons)"
                    },
                    {
                        "name": "صحن قلايه",
                        "price": "38 د.ل",
                        "desc": "لحم بقر, صحن سلاطة مشكل, هريسة, زيتون, سلة خبز",
                        "image": "",
                        "en_name": "Qallaya Plate",
                        "en_desc": "Beef, Mixed Salad Plate, Harissa, Olives, Bread Basket"
                    },
                    {
                        "name": "شكشوكة",
                        "en_name": "Shakshouka",
                        "price": "28 د.ل",
                        "desc": "( تركية / مرقاز / قديد )",
                        "image": "",
                        "variants": [
                            {
                                "name": "شكشوكة تركية",
                                "en_name": "Turkish Shakshouka",
                                "price": "28 د.ل",
                                "desc": "شكشوكة مع جبنة موزاريللا وجبنة تشيدر, خيار وجرجير, زيتون متبل, سلة خبز, شاي (أخضر أو أحمر)"
                            },
                            {
                                "name": "شكشوكة مرقاز",
                                "en_name": "Merguez Shakshouka",
                                "price": "32 د.ل",
                                "desc": "شكشوكة مع مرقاز, جبنة, خضروات, زيتون متبل, سلة خبز و شاي (أخضر أو أحمر)"
                            },
                            {
                                "name": "شكشوكة قديد",
                                "en_name": "Qadeed Shakshouka",
                                "price": "35 د.ل",
                                "desc": "شكشوكة بقديد, جبنة, خضروات, زيتون متبل, سلة خبز, شاي (أخضر أو أحمر)"
                            }
                        ]
                    },
                    {
                        "name": "أومليت",
                        "en_name": "Omelette",
                        "price": "15 د.ل",
                        "desc": "( كلاسيك / جبنة / خضروات / فقع )",
                        "image": "",
                        "variants": [
                            {
                                "name": "أومليت كلاسيك",
                                "en_name": "Classic Omelette",
                                "price": "15 د.ل",
                                "desc": "بيض مع هريسة, زيتون, طماطم، خيار، جرجير و سلة خبز."
                            },
                            {
                                "name": "أومليت بالجبنة",
                                "en_name": "Cheese Omelette",
                                "price": "18 د.ل",
                                "desc": "بيض وجبنة مع هريسة, زيتون, طماطم، خيار، جرجير و سلة"
                            },
                            {
                                "name": "أومليت خضروات",
                                "en_name": "Veggie Omelette",
                                "price": "20 د.ل",
                                "desc": "بيض, فلفل حلو, بصل, جبنة, جرجير, طماطم، خيار , زيتون و سلة خبز."
                            },
                            {
                                "name": "أومليت فقع",
                                "en_name": "Mushroom Omelette",
                                "price": "22 د.ل",
                                "desc": "بيض, فلفل حلو, فقع, جبنة، زيتون, طماطم, خيار, هريسة, و سلة خبز."
                            }
                        ]
                    },
                    {
                        "name": "توست",
                        "en_name": "Toast",
                        "price": "18 د.ل",
                        "desc": "( جبنة / تونة / بيض / ببروني )",
                        "image": "",
                        "variants": [
                            {
                                "name": "توست جبنة",
                                "en_name": "Cheese Toast",
                                "price": "18 د.ل",
                                "desc": "توست مع جبنة كريم,موزاريللا و جبنة زعتر."
                            },
                            {
                                "name": "توست تونة",
                                "en_name": "Tuna Toast",
                                "price": "15 د.ل",
                                "desc": "توست تونة, جبنة, طماطم, جرجير, زيتون أسود, زيتون متبل و هريسة."
                            },
                            {
                                "name": "توست بيض",
                                "en_name": "Egg Toast",
                                "price": "15 د.ل",
                                "desc": "توست بيض مقلي, جبنة, طماطم, جرجير, زيتون أسود, زيتون متبل وهريسة."
                            },
                            {
                                "name": "توست ببروني",
                                "en_name": "Pepperoni Toast",
                                "price": "18 د.ل",
                                "desc": "توست سلامي, جبنة, طماطم, جرجير ،زيتون شرائح أسود, زيتون متبل وهريسة."
                            }
                        ]
                    },
"""

# We replace lines from start_line to end_line (inclusive)
new_lines = lines[:start_line] + [new_breakfast_content] + lines[end_line+1:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Success!")
