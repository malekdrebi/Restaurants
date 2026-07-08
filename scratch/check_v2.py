import codecs

file_path = r'c:\Users\malek drebi\Desktop\LAVINA\LavinaHouseMenu\index.html'
encodings = ['utf-8', 'cp1256', 'iso-8859-6', 'utf-16', 'windows-1252', 'latin-1']

for enc in encodings:
    try:
        with codecs.open(file_path, 'r', encoding=enc) as f:
            f.read()
        print(f"Success with {enc}")
    except Exception as e:
        print(f"Failed with {enc}: {e}")
