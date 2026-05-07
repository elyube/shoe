"""
Derimod Fiyat Yapısı Debug
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

URL = "https://derimod.com.tr/collections/kadin-spor-ayakkabi-sneaker?filter.v.availability=1"

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(URL)

# Daha geniş seçici ile bekle
try:
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".grid__item"))
    )
except:
    pass

time.sleep(4)
driver.execute_script("window.scrollTo(0, 1500);")
time.sleep(2)

soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

# En çok eleman döndüren seçiciyi bul
en_iyi = []
en_iyi_sel = ""
for sel in ["[class*='product-card']", "[class*='ProductCard']", ".grid__item", "li.grid__item", "div.grid__item", "[class*='product-item']"]:
    sonuc = soup.select(sel)
    print(f"  '{sel}' → {len(sonuc)} eleman")
    if len(sonuc) > len(en_iyi):
        en_iyi = sonuc
        en_iyi_sel = sel

print(f"\n✓ En iyi seçici: '{en_iyi_sel}' → {len(en_iyi)} eleman\n")

# İlk 2 kartın fiyat kısmını göster
for i, kart in enumerate(en_iyi[:2]):
    ad_el = kart.select_one("h2, h3, [class*='title'], [class*='name']")
    print(f"{'='*50}")
    print(f"Ürün {i+1}: {ad_el.get_text(strip=True) if ad_el else '?'}")
    print(f"{'='*50}")
    for el in kart.find_all(True):
        metin = el.get_text(strip=True)
        if metin and len(metin) < 40 and any(c.isdigit() for c in metin):
            print(f"  <{el.name} class='{el.get('class')}'> → '{metin}'")
    print()