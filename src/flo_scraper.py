"""
FLO Ayakkabı Fiyat Takip Scraper'ı — Selenium Versiyonu
Veri Madenciliği Projesi

Kullanım:
    pip install selenium webdriver-manager pandas schedule beautifulsoup4
    python flo_scraper.py
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
import schedule
from datetime import datetime
import random
import file_operations as fo
import pathlib

# ─── Ayarlar ────────────────────────────────────────────────────────────────
THIS_DIR = pathlib.Path(__file__).parent
DATA_FILE = THIS_DIR.parent / "data" / "flo_prices.json"
CSV_FILE  = THIS_DIR.parent / "data" / "flo_prices.csv"

KATEGORI_URLS = [
    {
        "ad": "Erkek Spor Ayakkabı",
        "url": "https://www.flo.com.tr/spor-ayakkabi?cinsiyet=erkek",
    },
    {
        "ad": "Kadın Spor Ayakkabı",
        "url": "https://www.flo.com.tr/spor-ayakkabi?cinsiyet=kadin",
    },
    {
        "ad": "Erkek Günlük Ayakkabı",
        "url": "https://www.flo.com.tr/gunluk-ayakkabi?cinsiyet=erkek",
    },
    {
        "ad": "Kadın Günlük Ayakkabı",
        "url": "https://www.flo.com.tr/gunluk-ayakkabi?cinsiyet=kadin",
    },
    {
        "ad": "İndirimli Ürünler",
        "url": "https://www.flo.com.tr/indirim?cinsiyet=erkek,kadin,unisex",
    },
]

# ─── Tarayıcı ────────────────────────────────────────────────────────────────

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
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# ─── Yardımcılar ─────────────────────────────────────────────────────────────

def fiyat_temizle(fiyat_str: str) -> float:
    """'1.299,90 TL' → 1299.90"""
    if not fiyat_str:
        return None
    temiz = (
        fiyat_str.replace("TL", "")
                 .replace("\xa0", "")
                 .replace(" ", "")
                 .replace(".", "")
                 .replace(",", ".")
                 .strip()
    )
    try:
        return float(temiz)
    except ValueError:
        return None



def veri_kaydet(kayitlar: list) -> None:
    fo.AppendJsonFile(path=DATA_FILE, new_list=kayitlar)
    df = pd.DataFrame(kayitlar)
    df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
    print(f"  ✓ {len(kayitlar)} kayıt kaydedildi → {DATA_FILE} & {CSV_FILE}")

# ─── Scraping ────────────────────────────────────────────────────────────────

def flo_scrape(driver, kategori_url: str, kategori_adi: str, sayfa_limit: int = 3) -> list:
    urunler = []
    zaman = datetime.now().isoformat(timespec="seconds")

    for sayfa in range(1, sayfa_limit + 1):

        url = f"{kategori_url}&page={sayfa}" if "?" in kategori_url else f"{kategori_url}?page={sayfa}"
        print(f"  → Sayfa {sayfa}: {url}")

        driver.get(url)

        # Ürün kartlarının yüklenmesini bekle
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".product-list__item"))
            )
        except Exception:
            print(f"    ⚠ Ürün kartları yüklenemedi, sayfa atlanıyor.")
            break

        # Sayfayı aşağı kaydır (lazy load için)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
        time.sleep(1.5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        kartlar = soup.select(".product-list__item")

        if not kartlar:
            print(f"    ⚠ Kart bulunamadı.")
            break

        print(f"    ℹ {len(kartlar)} ürün kartı bulundu.")

        for kart in kartlar:

            # Ad
            ad_el = kart.select_one(".product__name-description")
            ad = ad_el.get_text(strip=True) if ad_el else "Bilinmiyor"

            # Marka
            marka_el = kart.select_one(".product__name-brand")
            marka = marka_el.get_text(strip=True) if marka_el else "Bilinmiyor"

            # Fiyatlar
            fiyat     = None
            indirimli = None
            pricing   = kart.select_one(".product-pricing")

            if pricing:
                # Üstü çizili = eski (orijinal) fiyat
                eski_el = pricing.select_one("s, del, [class*='old'], [class*='before'], [class*='two']")
                yeni_el = pricing.select_one(".product-pricing-one__price")

                if eski_el:
                    fiyat     = fiyat_temizle(eski_el.get_text(strip=True))
                    indirimli = fiyat_temizle(yeni_el.get_text(strip=True)) if yeni_el else None
                elif yeni_el:
                    fiyat     = fiyat_temizle(yeni_el.get_text(strip=True))
                    indirimli = None

                # Hâlâ bulunamadıysa TL geçen tüm metinleri sırala
                if not fiyat:
                    tl_metinler = [t for t in pricing.find_all(string=True) if "TL" in t]
                    fiyatlar    = [fiyat_temizle(t) for t in tl_metinler if fiyat_temizle(t)]
                    fiyat       = fiyatlar[0] if fiyatlar else None
                    indirimli   = fiyatlar[1] if len(fiyatlar) > 1 else None

            # URL
            link_el = kart.select_one("a[href]")
            href = link_el["href"] if link_el else ""
            urun_url = "https://www.flo.com.tr" + href if href.startswith("/") else href

            # İndirim oranı
            if fiyat and indirimli and fiyat > 0 and indirimli < fiyat:
                indirim_orani = round((1 - indirimli / fiyat) * 100, 1)
            else:
                indirim_orani = 0.0

            urunler.append({
                "ad":              ad,
                "marka":           marka,
                "fiyat":           fiyat,
                "indirimli_fiyat": indirimli,
                "indirim_orani":   indirim_orani,
                "url":             urun_url,
                "kategori":        kategori_adi,
                "zaman":           zaman,
            })

        time.sleep(random.uniform(2.0, 3.5))

    print(f"  ✓ {len(urunler)} ürün çekildi ({kategori_adi})")
    return urunler

# ─── Ana Fonksiyon ───────────────────────────────────────────────────────────

def tum_kategorileri_scrape():
    print(f"\n{'='*55}")
    print(f"  FLO Scraper başladı — {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print(f"{'='*55}")
    print("  ⏳ Tarayıcı başlatılıyor...")

    driver = tarayici_baslat()

    try:
        mevcut = fo.ReadFromJsonFile(DATA_FILE)
        yeni = []
        for kat in KATEGORI_URLS:
            yeni += flo_scrape(driver, kat["url"], kat["ad"], sayfa_limit=3)
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

# ─── Analiz ──────────────────────────────────────────────────────────────────

def fiyat_analizi():
    if not os.path.exists(CSV_FILE):
        print("Henüz veri yok. Önce scraper'ı çalıştırın.")
        return

    df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")

    if df.empty or len(df.columns) == 0:
        print("CSV dosyası boş. Önce veri çekilmesi gerekiyor.")
        return

    df["zaman"] = pd.to_datetime(df["zaman"])

    print("\n📈 FLO Fiyat Analizi")
    print("=" * 40)

    print("\n🏷  Marka bazında ortalama fiyat (TL):")
    ozet = (df.groupby("marka")["fiyat"]
              .agg(["mean", "min", "max", "count"])
              .rename(columns={"mean":"Ort", "min":"Min", "max":"Maks", "count":"Adet"})
              .sort_values("Ort", ascending=False)
              .head(10))
    print(ozet.to_string())

    print("\n📦 Kategori bazında ortalama fiyat (TL):")
    kat_ozet = df.groupby("kategori")["fiyat"].mean().sort_values(ascending=False)
    print(kat_ozet.to_string())

    print("\n🔥 En yüksek indirimli 10 ürün:")
    top_indirim = (df[df["indirim_orani"] > 0]
                   .sort_values("indirim_orani", ascending=False)
                   .head(10)[["ad", "marka", "fiyat", "indirimli_fiyat", "indirim_orani"]])
    if top_indirim.empty:
        print("     İndirimli ürün bulunamadı.")
    else:
        print(top_indirim.to_string(index=False))

# ─── Giriş ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "analiz":
        fiyat_analizi()
    elif len(sys.argv) > 1 and sys.argv[1] == "zamanlama":
        schedule.every().day.at("09:00").do(tum_kategorileri_scrape)
        schedule.every().day.at("21:00").do(tum_kategorileri_scrape)
        print("⏰ Zamanlama aktif: 09:00 ve 21:00'de scraping yapılacak.")
        tum_kategorileri_scrape()
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        tum_kategorileri_scrape()
        fiyat_analizi()