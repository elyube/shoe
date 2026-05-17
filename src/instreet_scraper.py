"""
InStreet Ayakkabı Fiyat Takip Scraper - Selenium Versiyonu
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
import json
import os
import time
import random
from datetime import datetime

DATA_FILE = "instreet_prices.json"
CSV_FILE = "instreet_prices.csv"

KATEGORI_URLS = [
    {
        "ad": "Kadın Spor Ayakkabı",
        "url": "https://www.instreet.com.tr/kadin-spor-ayakkabi",
    },
    {
        "ad": "Erkek Spor Ayakkabı",
        "url": "https://www.instreet.com.tr/erkek-spor-ayakkabi",
    },
]


def tarayici_baslat():
    options = Options()

    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")

    options.add_experimental_option(
        "excludeSwitches",
        ["enable-automation"]
    )

    options.add_argument(
        "user-agent=Mozilla/5.0 "
        "(Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    service = Service(ChromeDriverManager().install())

    return webdriver.Chrome(service=service, options=options)


def fiyat_temizle(fiyat_str: str) -> float:
    if not fiyat_str:
        return None

    temiz = (
        fiyat_str.replace("TL", "")
        .replace("₺", "")
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


def veri_yukle() -> list:
    if os.path.exists(DATA_FILE):

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    return []


def veri_kaydet(kayitlar: list) -> None:

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            kayitlar,
            f,
            ensure_ascii=False,
            indent=2
        )

    df = pd.DataFrame(kayitlar)

    df.to_csv(
        CSV_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"✓ {len(kayitlar)} kayıt kaydedildi")


def instreet_scrape(
    driver,
    kategori_url: str,
    kategori_adi: str,
    sayfa_limit: int = 3
) -> list:

    urunler = []

    zaman = datetime.now().isoformat(timespec="seconds")

    for sayfa in range(1, sayfa_limit + 1):

        url = f"{kategori_url}?page={sayfa}"

        print(f"→ Sayfa {sayfa}: {url}")

        driver.get(url)

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "[class*='product']"
                    )
                )
            )

        except Exception:
            print("⚠ Sayfa yüklenemedi")
            break

        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight / 2);"
        )

        time.sleep(1.5)

        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )

        time.sleep(2)

        soup = BeautifulSoup(
            driver.page_source,
            "html.parser"
        )

        kartlar = []

        for sel in [
            ".product-item",
            ".product-card",
            "[class*='product-card']",
            "[class*='ProductCard']",
            "[class*='product-item']",
            "[class*='ProductItem']",
            "[class*='product']",
        ]:

            sonuc = soup.select(sel)

            if len(sonuc) > len(kartlar):
                kartlar = sonuc

        gercek_kartlar = []

        for kart in kartlar:
            metin = kart.get_text(" ", strip=True)

            if "TL" not in metin and "₺" not in metin:
                continue

            link_el = kart.select_one("a[href]")
            href = link_el["href"] if link_el else ""

            if not href:
                continue

            gercek_kartlar.append(kart)

        print(f"    ℹ {len(gercek_kartlar)} ürün kartı bulundu.")

        if not gercek_kartlar:
            print("    ⚠ Ürün kartı bulunamadı, sayfa sonu.")
            break

        gorulen_url = set()

        for kart in gercek_kartlar:

            metin = kart.get_text(" ", strip=True)

            if "TL" not in metin and "₺" not in metin:
                continue

            link_el = kart.select_one("a[href]")

            href = link_el["href"] if link_el else ""

            if not href:
                continue

            if href.startswith("/"):
                urun_url = (
                    "https://www.instreet.com.tr"
                    + href
                )

            else:
                urun_url = href

            if urun_url in gorulen_url:
                continue

            gorulen_url.add(urun_url)

            fiyat_metinleri = [
                t.strip()
                for t in kart.find_all(string=True)
                if "TL" in t or "₺" in t
            ]

            fiyatlar = []

            for f in fiyat_metinleri:

                temiz = fiyat_temizle(f)

                if temiz is not None:
                    fiyatlar.append(temiz)

            if not fiyatlar:
                continue

            fiyat = fiyatlar[0]

            indirimli = (
                fiyatlar[1]
                if len(fiyatlar) > 1
                else None
            )

            if (
                fiyat
                and indirimli
                and fiyat > indirimli
            ):

                indirim_orani = round(
                    (1 - indirimli / fiyat) * 100,
                    1
                )

            else:
                indirim_orani = 0.0

            ad_el = (
                kart.select_one("h2")
                or kart.select_one("h3")
                or kart.select_one("[class*='title']")
                or kart.select_one("[class*='name']")
            )

            ad = (
                ad_el.get_text(strip=True)
                if ad_el
                else "Bilinmiyor"
            )

            if ad == "Bilinmiyor":
                continue

            urunler.append({
                "ad": ad,
                "marka": "InStreet",
                "fiyat": fiyat,
                "indirimli_fiyat": indirimli,
                "indirim_orani": indirim_orani,
                "url": urun_url,
                "kategori": kategori_adi,
                "site": "InStreet",
                "zaman": zaman,
            })

        time.sleep(random.uniform(2.0, 3.0))

    print(f"✓ {len(urunler)} ürün çekildi")

    return urunler


def tum_kategorileri_scrape():

    print("=" * 50)
    print("InStreet Scraper Başladı")
    print("=" * 50)

    driver = tarayici_baslat()

    try:

        mevcut = veri_yukle()

        yeni = []

        for kat in KATEGORI_URLS:

            yeni += instreet_scrape(
                driver,
                kat["url"],
                kat["ad"],
                sayfa_limit=3
            )

    finally:

        driver.quit()

        print("✓ Tarayıcı kapatıldı")

    mevcut += yeni

    veri_kaydet(mevcut)

    print(f"Toplam kayıt: {len(mevcut)}")


if __name__ == "__main__":
    tum_kategorileri_scrape()