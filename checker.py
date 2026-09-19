import requests
from bs4 import BeautifulSoup

URL = "https://mangaplus.shueisha.co.jp/titles/200116"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140.0 Safari/537.36"
}

response = requests.get(
    URL,
    headers=headers,
    timeout=30
)

print("HTTP status:", response.status_code)
print("URL:", response.url)

response.raise_for_status()

print("\n--- PRIMEROS 5000 CARACTERES ---\n")
print(response.text[:5000])

print("\n--- BUSCANDO CAPÍTULOS ---\n")

soup = BeautifulSoup(response.text, "html.parser")

text = soup.get_text(" ", strip=True)

for word in ["Chapter", "Capítulo", "chapter", "capítulo"]:
    if word in text:
        print("Encontrado:", word)

print("\n--- TEXTO DE LA PÁGINA ---\n")
print(text[:10000])
