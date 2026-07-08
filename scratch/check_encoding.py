import chardet

file_path = r'c:\Users\malek drebi\Desktop\LAVINA\LavinaHouseMenu\index.html'
with open(file_path, 'rb') as f:
    rawdata = f.read()
    result = chardet.detect(rawdata)
    print(f"Detected encoding: {result['encoding']} with confidence {result['confidence']}")
