"""
Ayakkabı Dünyası Debug Script
"""
import requests
from bs4 import BeautifulSoup

URL = "https://www.ayakkabidunyasi.com.tr/kadin-spor-ayakkabi"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9",
}

print("⏳ Sayfa indiriliyor...")
r = requests.get(URL, headers=HEADERS, timeout=15)
print(f"✓ HTTP {r.status_code} — {len(r.text)} karakter\n")

soup = BeautifulSoup(r.text, "html.parser")

# Ürün kartı seçicilerini dene
print("🔍 Ürün kartı seçicileri:")
for sel in [
    "div.product-item", "li.product-item", "[class*='product-item']",
    "[class*='product-card']", "[class*='ProductCard']",
    "div.item", "li.item", "[class*='p-card']",
    "[class*='product_item']", "article"
]:
    sonuc = soup.select(sel)
    if sonuc:
        print(f"  ✓ '{sel}' → {len(sonuc)} eleman")

print("\n💰 Fiyat içeren elementler:")
fiyat_els = [t.strip() for t in soup.find_all(string=True) if "TL" in t and len(t.strip()) < 25]
for f in fiyat_els[:8]:
    print(f"  → '{f}'")

print("\n📦 'product' veya 'item' içeren CSS sınıfları:")
siniflar = set()
for el in soup.find_all(class_=True):
    for cls in el.get("class", []):
        if any(k in cls.lower() for k in ["product", "item", "card", "price"]):
            siniflar.add(cls)
for s in sorted(siniflar)[:30]:
    print(f"  → {s}")