"""
Ayakkabı Dünyası Selenium Debug
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

URL = "https://www.ayakkabidunyasi.com.tr/kadin-spor-ayakkabi"

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36")

print("⏳ Tarayıcı başlatılıyor...")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(URL)

try:
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.item"))
    )
except:
    pass

time.sleep(3)
driver.execute_script("window.scrollTo(0, 1500);")
time.sleep(2)

soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

kartlar = soup.select("div.item")
print(f"✓ {len(kartlar)} kart bulundu\n")

# İlk 2 kartı göster
for i, kart in enumerate(kartlar[:2]):
    print(f"{'='*50}")
    print(f"Kart {i+1} HTML:")
    print(kart.prettify()[:1500])
    print()