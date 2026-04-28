"""
FLO Debug Script — sayfanın HTML yapısını inceler
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

URL = "https://www.flo.com.tr/spor-ayakkabi?cinsiyet=erkek"

print("⏳ Tarayıcı başlatılıyor...")

options = Options()
# Headless KAPALI — tarayıcı ekranda açılacak, ne yüklendiğini görebilirsin
# options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

print(f"🌐 Sayfa açılıyor: {URL}")
driver.get(URL)

print("⏳ 8 saniye bekleniyor (sayfa yüklensin)...")
time.sleep(8)

# Sayfayı aşağı kaydır
driver.execute_script("window.scrollTo(0, 1000);")
time.sleep(2)
driver.execute_script("window.scrollTo(0, 3000);")
time.sleep(2)

soup = BeautifulSoup(driver.page_source, "html.parser")

print(f"\n📄 Sayfa başlığı: {driver.title}")
print(f"📏 HTML uzunluğu: {len(driver.page_source)} karakter")

# Tüm linkleri tara
tum_linkler = soup.find_all("a", href=True)
print(f"\n🔗 Toplam link sayısı: {len(tum_linkler)}")

# Ürün linki olabilecekleri bul
print("\n🔍 İlk 20 linkin href'leri:")
for i, link in enumerate(tum_linkler[:20]):
    print(f"  {i+1}. {link['href'][:80]}")

# Tüm CSS sınıflarını tara
print("\n📦 'product' veya 'item' içeren tüm CSS sınıfları:")
tum_siniflar = set()
for el in soup.find_all(class_=True):
    for cls in el.get("class", []):
        if any(k in cls.lower() for k in ["product", "item", "card", "urun"]):
            tum_siniflar.add(cls)

for s in sorted(tum_siniflar):
    print(f"  → {s}")

# Fiyat içeren elementler
print("\n💰 Fiyat içeren elementler (TL geçenler):")
fiyat_els = [el for el in soup.find_all(string=True) if "TL" in el and len(el.strip()) < 20]
for f in fiyat_els[:10]:
    print(f"  → '{f.strip()}'")

print("\n✅ Debug tamamlandı. Tarayıcı açık kalıyor — inceleyebilirsin.")
print("   Bitirmek için terminalde Ctrl+C'ye bas.")

input("\nEnter'a basarak tarayıcıyı kapat...")
driver.quit()