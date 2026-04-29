"""
Derimod Ayakkabı Fiyat Takip Scraper - Selenium Versiyonu
Veri Madenciliği Projesi
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import random
from datetime import datetime
import file_operations as fo
import pathlib


THIS_DIR = pathlib.Path(__file__).parent
DATA_FILE = THIS_DIR.parent / "data" / "derimod_prices.json"
CSV_FILE  = THIS_DIR.parent / "data" / "derimod_prices.csv"

KATEGORI_URLS = [
    {
        "ad": "Kadın Spor Ayakkabı",
        "url": "https://derimod.com.tr/collections/kadin-spor-ayakkabi-sneaker?filter.v.availability=1",
    },
    {
        "ad": "Erkek Spor Ayakkabı",
        "url": "https://derimod.com.tr/collections/erkek-spor-ayakkabi-sneaker?filter.v.availability=1",
    },
]

def tarayici_baslat():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def fiyat_temizle(fiyat_str: str) -> float:
    # Derimod İngilizce format: '3,499.99TL' → virgül binlik, nokta ondalık
    if not fiyat_str:
        return None
    temiz = (
        fiyat_str.replace("TL", "").replace("₺", "")
                 .replace("\xa0", "").replace(" ", "")
                 .replace(",", "")   # binlik virgülü sil
                 .strip()
    )
    try:
        return float(temiz)
    except ValueError:
        return None


def veri_kaydet(kayitlar: list) -> None:
    fo.AppendJsonFile(path=DATA_FILE, new_list=kayitlar)
    df = pd.DataFrame(kayitlar)
    df.to_csv(CSV_FILE, mode="a", index=False, header=False)
    print(f"  ✓ {len(kayitlar)} kayıt kaydedildi → {DATA_FILE} & {CSV_FILE}")

def derimod_scrape(driver, kategori_url: str, kategori_adi: str, sayfa_limit: int = 5) -> list:
    urunler = []
    zaman = datetime.now().isoformat(timespec="seconds")

    for sayfa in range(1, sayfa_limit + 1):
        url = f"{kategori_url}&page={sayfa}" if "?" in kategori_url else f"{kategori_url}?page={sayfa}"
        print(f"  → Sayfa {sayfa}: {url}")

        driver.get(url)

        # Ürün kartlarının yüklenmesini bekle
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='product-card'], [class*='ProductCard'], .grid__item"))
            )
        except Exception:
            print(f"    ⚠ Sayfa yüklenemedi, duruluyor.")
            break

        # Lazy load için kaydır
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
        time.sleep(1.5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # CSS sınıflarını tara — hangi seçici en çok eleman döndürüyor?
        kartlar = []
        for sel in [
            "[class*='ProductCard']",
            "[class*='product-card']",
            "li.grid__item",
            "div.grid__item",
            "[class*='product-item']",
        ]:
            sonuc = soup.select(sel)
            if len(sonuc) > len(kartlar):
                kartlar = sonuc

        if not kartlar:
            print(f"    ⚠ Ürün kartı bulunamadı, sayfa sonu.")
            break

        print(f"    ℹ {len(kartlar)} ürün kartı bulundu.")

        for kart in kartlar:
            # Ad
            ad_el = (
                kart.select_one("h2") or
                kart.select_one("h3") or
                kart.select_one("[class*='title']") or
                kart.select_one("[class*='name']")
            )
            ad = ad_el.get_text(strip=True) if ad_el else "Bilinmiyor"

            # Marka
            marka_el = (
                kart.select_one("[class*='vendor']") or
                kart.select_one("[class*='brand']") or
                kart.select_one("[class*='marka']")
            )
            marka = marka_el.get_text(strip=True) if marka_el else "Derimod"

            # Fiyatlar
            fiyat     = None
            indirimli = None

            # Ana fiyat elementi: product-grid-item__price
            fiyat_el  = kart.select_one(".product-grid-item__price, [class*='product-grid-item__price']")
            # Üstü çizili = eski (orijinal) fiyat
            eski_el   = kart.select_one("s, del, [class*='compare'], [class*='original']")
            # İndirimli fiyat
            indirim_el = kart.select_one("[class*='sale-price'], [class*='SalePrice'], ins")

            if eski_el and indirim_el:
                fiyat     = fiyat_temizle(eski_el.get_text(strip=True))
                indirimli = fiyat_temizle(indirim_el.get_text(strip=True))
            elif fiyat_el:
                fiyat     = fiyat_temizle(fiyat_el.get_text(strip=True))
                indirimli = None

            # Yedek: TL geçen tüm metinleri topla
            if not fiyat:
                tl_metinler = [t.strip() for t in kart.find_all(string=True) if "TL" in t or "₺" in t]
                fiyatlar = [fiyat_temizle(t) for t in tl_metinler if fiyat_temizle(t)]
                fiyat     = fiyatlar[0] if fiyatlar else None
                indirimli = fiyatlar[1] if len(fiyatlar) > 1 else None

            # İndirim oranı
            if fiyat and indirimli and fiyat > 0 and indirimli < fiyat:
                indirim_orani = round((1 - indirimli / fiyat) * 100, 1)
            else:
                indirim_orani = 0.0

            # URL
            link_el  = kart.select_one("a[href]")
            href     = link_el["href"] if link_el else ""
            urun_url = "https://derimod.com.tr" + href if href.startswith("/") else href

            urunler.append({
                "ad":              ad,
                "marka":           marka,
                "fiyat":           fiyat,
                "indirimli_fiyat": indirimli,
                "indirim_orani":   indirim_orani,
                "url":             urun_url,
                "kategori":        kategori_adi,
                "site":            "Derimod",
                "zaman":           zaman,
            })

        time.sleep(random.uniform(2.0, 3.0))

    print(f"  ✓ {len(urunler)} ürün çekildi ({kategori_adi})")
    return urunler

def tum_kategorileri_scrape():
    print(f"\n{'='*55}")
    print(f"  Derimod Scraper başladı — {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print(f"{'='*55}")
    print("  ⏳ Tarayıcı başlatılıyor...")

    driver = tarayici_baslat()

    try:
        mevcut = fo.ReadFromJsonFile(DATA_FILE)
        yeni   = []
        for kat in KATEGORI_URLS:
            yeni += derimod_scrape(driver, kat["url"], kat["ad"], sayfa_limit=5)
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