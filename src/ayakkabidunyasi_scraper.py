"""
Ayakkabı Dünyası Fiyat Takip Scraper — Selenium + JSON Versiyonu
Veri Madenciliği Projesi
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import json
import os
import time
import random
from datetime import datetime
import file_operations as fo
import biçimlendirici as biç
import pathlib
from .models.ayakkabı import Ayakkabı


THIS_DIR = pathlib.Path(__file__).parent
DATA_DIR = THIS_DIR.parent / "data"

DATA_FILE = DATA_DIR / "ayakkabidunyasi_prices.json"
CSV_FILE  = DATA_DIR / "ayakkabidunyasi_prices.csv"

ONDALIK_AYRACI = '.'

KATEGORI_URLS = [
    {
        "ad": "Kadın Spor Ayakkabı",
        "url": "https://www.ayakkabidunyasi.com.tr/kadin-spor-ayakkabi",
    },
    {
        "ad": "Erkek Spor Ayakkabı",
        "url": "https://www.ayakkabidunyasi.com.tr/erkek-spor-ayakkabi",
    },
]

def tarayici_baslat():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def veri_kaydet(kayitlar: list) -> None:
    fo.AppendJsonFile(path=DATA_FILE, new_list=kayitlar)
    df = pd.DataFrame(kayitlar)
    df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
    print(f"  ✓ {len(kayitlar)} kayıt kaydedildi → {DATA_FILE} & {CSV_FILE}")

def ayakkabidunyasi_scrape(driver, kategori_url: str, kategori_adi: str, sayfa_limit: int = 5) -> list:
    urunler = []
    zaman = datetime.now()
    goruldu = set()

    for sayfa in range(1, sayfa_limit + 1):
        url = f"{kategori_url}?pagenumber={sayfa}"
        print(f"  → Sayfa {sayfa}: {url}")

        driver.get(url)

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.item"))
            )
        except:
            print(f"    ⚠ Sayfa yüklenemedi.")
            break

        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        kartlar = soup.select("div.item[data-image-id='0']")

        if not kartlar:
            print(f"    ⚠ Ürün bulunamadı, sayfa sonu.")
            break

        print(f"    ℹ {len(kartlar)} ürün kartı bulundu.")

        yeni_urun = 0
        for kart in kartlar:
            img = kart.select_one("img[data-enhanced-impressions]")
            if not img:
                continue
            try:
                data = json.loads(img["data-enhanced-impressions"])
            except:
                continue

            urun_id = data.get("id", "")
            if urun_id in goruldu:
                continue
            goruldu.add(urun_id)

            ad    = data.get("name", "Bilinmiyor").strip()

            # Marka img alt attribute'unun ilk kelimesinden alınır
            # Örnek: "Skechers Uno Stand On Air..." → "Skechers"
            img_el = kart.select_one("img[alt]")
            if img_el:
                alt = img_el.get("alt", "").strip()
                marka = alt.split()[0] if alt else "Bilinmiyor"
            else:
                marka = "Bilinmiyor"

            ham_fiyat_anlık = str(data.get("price", ""))
            ham_fiyat_asıl = str(data.get("dimension16", ""))

            fiyat_anlık = biç.FiyatTemizle(ham_fiyat_anlık, ONDALIK_AYRACI)
            fiyat_asıl = biç.FiyatTemizle(ham_fiyat_asıl, ONDALIK_AYRACI)
            
            # dimension17 = indirim durumu
            indirim_durumu = data.get("dimension17", "")

            if fiyat_asıl and fiyat_asıl and fiyat_asıl > fiyat_anlık:
                # JSON'da eski ve yeni fiyat farklıysa kullan
                indirimli     = fiyat_anlık
                fiyat         = fiyat_asıl
                indirim_orani = round((1 - indirimli / fiyat) * 100, 1)
            elif indirim_durumu == "İndirimli":
                # İndirimli ama fiyat bilgisi gelmiyor — işaretle
                fiyat = fiyat_anlık
                indirimli     = None
                indirim_orani = -1.0  # -1 = indirimli ama oran bilinmiyor
            else:
                fiyat = fiyat_anlık
                indirimli     = None
                indirim_orani = 0.0

            link_el  = kart.select_one("a[href]")
            href     = link_el["href"] if link_el else ""
            urun_url = "https://www.ayakkabidunyasi.com.tr" + href if href.startswith("/") else href

            bulunan = Ayakkabı(
                ad = ad,
                marka = marka,
                fiyat = fiyat,
                indirimli_fiyat = indirimli,
                indirim_oranı = indirim_orani,
                site = "Ayakkabı Dünyası",
                url = urun_url,
                kategori = kategori_adi,
                zaman = zaman
            )
            urunler.append(bulunan.toJson())
            yeni_urun += 1

        print(f"    ✓ {yeni_urun} yeni ürün eklendi, toplam: {len(goruldu)}")
        time.sleep(random.uniform(2.0, 3.0))

    print(f"  ✓ {len(urunler)} ürün çekildi ({kategori_adi})")
    return urunler

def tum_kategorileri_scrape():
    print(f"\n{'='*55}")
    print(f"  Ayakkabı Dünyası Scraper başladı — {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print(f"{'='*55}")
    print("  ⏳ Tarayıcı başlatılıyor...")

    driver = tarayici_baslat()

    try:
        mevcut = fo.ReadFromJsonFile(DATA_FILE)
        yeni   = []
        for kat in KATEGORI_URLS:
            yeni += ayakkabidunyasi_scrape(driver, kat["url"], kat["ad"], sayfa_limit=5)
    finally:
        driver.quit()
        print("  ✓ Tarayıcı kapatıldı.")

    mevcut += yeni
    veri_kaydet(mevcut)
    print(f"\n  Toplam kayıt: {len(mevcut)}")

    if yeni:
        df = pd.DataFrame(yeni)
        indirimli_df = df[df["indirim_orani"] > 0]
        print(f"\n  📊 Bu tarama özeti:")
        print(f"     Toplam ürün   : {len(df)}")
        print(f"     İndirimli ürün: {len(indirimli_df)}")
        if not indirimli_df.empty:
            en_cok = indirimli_df.loc[indirimli_df["indirim_orani"].idxmax()]
            print(f"     En yüksek indirim: %{en_cok['indirim_orani']} — {en_cok['ad']}")

        fiyat_df = df[df["fiyat"].notna()]
        if not fiyat_df.empty:
            print(f"\n  🏷  Marka bazında ortalama fiyat:")
            ozet = (fiyat_df.groupby("marka")["fiyat"]
                      .agg(["mean","min","max","count"])
                      .rename(columns={"mean":"Ort","min":"Min","max":"Maks","count":"Adet"})
                      .sort_values("Ort", ascending=False).head(10))
            print(ozet.to_string())

            print(f"\n  📦 Kategori bazında ortalama fiyat:")
            print(fiyat_df.groupby("kategori")["fiyat"].mean().sort_values(ascending=False).to_string())

if __name__ == "__main__":
    tum_kategorileri_scrape()