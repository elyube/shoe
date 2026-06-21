"""
Derimod Debug Script
"""
import requests
from bs4 import BeautifulSoup

URL = "https://derimod.com.tr/collections/kadin-spor-ayakkabi-sneaker?filter.v.availability=1"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9",
}

print("⏳ Sayfa indiriliyor...")
r = requests.get(URL, headers=HEADERS, timeout=15)
print(f"✓ HTTP {r.status_code} — {len(r.text)} karakter\n")

soup = BeautifulSoup(r.text, "html.parser")

# Kaç ürün var?
for selectors in [
    "li.grid__item", "div.grid__item",
    "[class*='product-item']", "[class*='ProductItem']",
    "li[class*='item']", ".product-card", "[class*='product-card']"
]:
    sonuc = soup.select(selectors)
    if sonuc:
        print(f"✓ '{selectors}' → {len(sonuc)} eleman bulundu")

print("\n--- İlk ürün kartının HTML'i ---")
# En fazla eleman döndüren seçiciyi bul
kartlar = soup.select("li.grid__item") or soup.select("[class*='product']")
if kartlar:
    print(kartlar[0].prettify()[:2000])
else:
    print("Kart bulunamadı!")
    # Tüm li elementlerini göster
    lis = soup.find_all("li", class_=True)
    print(f"\nSayfadaki li elementleri ({len(lis)} adet), ilk 5'i:")
    for li in lis[:5]:
        print(f"  class={li.get('class')} → {li.get_text(strip=True)[:60]}")