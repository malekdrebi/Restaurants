import urllib.request
import re

url = "https://talabiety.net/LAVINA-HOUSE"
req = urllib.request.Request(
    url, 
    data=None, 
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
)

with urllib.request.urlopen(req) as response:
    html = response.read().decode('utf-8')

with open("index_source.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Saved HTML")
