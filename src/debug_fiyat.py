"""
FLO Fiyat Yapısı Debug Script
Bir ürün kartının tam HTML'ini görmek için
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

URL = "https://www.flo.com.tr/spor-ayakkabi?cinsiyet=erkek&page=1"

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

print("⏳ Tarayıcı başlatılıyor...")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.get(URL)

WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".product-list__item"))
)
time.sleep(3)

soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

kartlar = soup.select(".product-list__item")
print(f"✓ {len(kartlar)} kart bulundu.\n")

# İlk 3 kartın fiyat bölümünü göster
for i, kart in enumerate(kartlar[:3]):
    ad_el = kart.select_one(".product__name-description")
    ad = ad_el.get_text(strip=True) if ad_el else "?"

    print(f"{'='*50}")
    print(f"Ürün {i+1}: {ad}")
    print(f"{'='*50}")

    # Fiyatla ilgili tüm elementleri bul
    fiyat_bolumu = kart.select("[class*='pricing'], [class*='price'], [class*='Price']")
    for el in fiyat_bolumu:
        metin = el.get_text(strip=True)
        if metin:
            print(f"  [{el.get('class')}] → '{metin}'")

    print()