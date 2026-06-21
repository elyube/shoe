import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"

files = {
    "FLO": DATA_DIR / "flo_prices.csv",
    "Derimod": DATA_DIR / "derimod_prices.csv",
    "InStreet": DATA_DIR / "instreet_prices.csv",
    "Ayakkabı Dünyası": DATA_DIR / "ayakkabidunyasi_prices.csv"
}

all_data = []

for site, path in files.items():
    df = pd.read_csv(path, encoding="utf-8-sig", on_bad_lines="skip")
    df["site"] = site
    df["zaman"] = pd.to_datetime(df["zaman"], errors="coerce")
    df["tarih"] = df["zaman"].dt.date
    
    
    df["fiyat"] = pd.to_numeric(df["fiyat"], errors="coerce")
    if "indirimli_fiyat" in df.columns:
        df["indirimli_fiyat"] = pd.to_numeric(df["indirimli_fiyat"], errors="coerce")
        
    fiyat_kolonu = "indirimli_fiyat" if "indirimli_fiyat" in df.columns else "fiyat"
    df["analiz_fiyati"] = df[fiyat_kolonu].fillna(df["fiyat"])
    df["analiz_fiyati"] = pd.to_numeric(df["analiz_fiyati"], errors="coerce")
    
    # Hatalı fiyatları (scraper hatasıyla gelen 35 Milyon vb. absürt fiyatlar) temizle
    hatali = df["fiyat"] > 50000
    df.loc[hatali, "fiyat"] = df.loc[hatali, "analiz_fiyati"]
    
    # İndirim oranını veri modelindeki alandan okumak yerine fiyatlardan dinamik hesapla
    df["indirim_orani"] = 0.0
    if "indirimli_fiyat" in df.columns:
        gecerli_indirim = (df["fiyat"] > 0) & df["indirimli_fiyat"].notna() & (df["indirimli_fiyat"] < df["fiyat"])
        df.loc[gecerli_indirim, "indirim_orani"] = ((df.loc[gecerli_indirim, "fiyat"] - df.loc[gecerli_indirim, "indirimli_fiyat"]) / df.loc[gecerli_indirim, "fiyat"] * 100).round(2)
    
    all_data.append(df)

df = pd.concat(all_data, ignore_index=True)

def fix_text(text):
    try:
        return str(text).encode("latin1").decode("utf-8")
    except:
        return str(text)

df["ad"] = df["ad"].apply(fix_text)
df["kategori"] = df["kategori"].apply(fix_text)
df["ad"] = df["ad"].astype(str)
df["kategori"] = df["kategori"].astype(str)

df = df.drop_duplicates(subset=["site", "ad", "url", "tarih"])
df = df[df["analiz_fiyati"].notna()]

# FLO için "İndirimli Ürünler" kategorisindeki spor ayakkabıları kurtar
spor_anahtar = ["spor", "sneaker", "koşu", "running", "training", "yürüyüş", "krampon", "basketbol"]
flo_ind_mask = (df["site"] == "FLO") & (df["kategori"] == "İndirimli Ürünler") & (df["ad"].apply(lambda x: any(k in str(x).lower() for k in spor_anahtar)))

# Kurtarılan ürünlerin kategorisini cinsiyetlerine göre "Spor Ayakkabı" olarak düzelt
def flo_kategori_duzelt(ad):
    ad_lower = str(ad).lower()
    if "kadın" in ad_lower or "kadin" in ad_lower:
        return "Kadın Spor Ayakkabı"
    return "Erkek Spor Ayakkabı"

df.loc[flo_ind_mask, "kategori"] = df.loc[flo_ind_mask, "ad"].apply(flo_kategori_duzelt)

# Sadece spor ayakkabı — adil karşılaştırma için
SPOR_KATEGORILER = ["Erkek Spor Ayakkabı", "Kadın Spor Ayakkabı"]
df = df[df["kategori"].isin(SPOR_KATEGORILER)]

# Cinsiyet sütunu ekle
def belirle_cinsiyet(row):
    ad = str(row["ad"]).lower()
    if "erkek" in ad:
        return "Erkek"
    elif "kadın" in ad or "kadin" in ad:
        return "Kadın"
    elif "unisex" in ad:
        return "Unisex"
    
    kat = str(row["kategori"]).lower()
    if "erkek" in kat:
        return "Erkek"
    elif "kadın" in kat or "kadin" in kat:
        return "Kadın"
    return "Unisex"

df["cinsiyet"] = df.apply(belirle_cinsiyet, axis=1)

print("=" * 60)
print("GENEL AYAKKABI FİYAT ANALİZİ — SADECE SPOR AYAKKABI")
print("=" * 60)

# 1) Site bazında genel özet
print("\n1) Site bazında genel fiyat karşılaştırması:")
site_ozet = df.groupby("site").agg(
    Urun_Sayisi=("ad", "count"),
    Ortalama_Fiyat=("analiz_fiyati", "mean"),
    En_Ucuz=("analiz_fiyati", "min"),
    En_Pahali=("analiz_fiyati", "max"),
    Ortalama_Indirim=("indirim_orani", "mean"),
    Indirimli_Urun_Sayisi=("indirim_orani", lambda x: (x > 0).sum())
).round(2)
print(site_ozet)

# 2) En avantajlı site
print("\n2) Kullanıcı için en avantajlı site:")
en_ucuz_site = site_ozet["Ortalama_Fiyat"].idxmin()
print(f"Ortalama fiyata göre en avantajlı site: {en_ucuz_site}")

# 3) Cinsiyete göre site karşılaştırması
print("\n3) Cinsiyete göre site karşılaştırması:")
cinsiyet_site = df.groupby(["cinsiyet", "site"]).agg(
    Ortalama_Fiyat=("analiz_fiyati", "mean"),
    Indirimli_Urun=("indirim_orani", lambda x: (x > 0).sum()),
    Urun_Sayisi=("ad", "count")
).round(2)
print(cinsiyet_site)

print("\n  Erkek spor ayakkabıda en ucuz site:")
erkek_df = df[df["cinsiyet"] == "Erkek"]
erkek_ozet = erkek_df.groupby("site")["analiz_fiyati"].mean().round(2)
print(f"  → {erkek_ozet.idxmin()} ({erkek_ozet.min()} TL)")

print("\n  Kadın spor ayakkabıda en ucuz site:")
kadin_df = df[df["cinsiyet"] == "Kadın"]
kadin_ozet = kadin_df.groupby("site")["analiz_fiyati"].mean().round(2)
print(f"  → {kadin_ozet.idxmin()} ({kadin_ozet.min()} TL)")

# 4) Marka bazında site karşılaştırması
print("\n4) Marka bazında site karşılaştırması (Nike, Adidas, Puma, Skechers):")
hedef_markalar = ["Nike", "Adidas", "Puma", "Skechers", "New", "Reebok", "Fila"]
marka_df = df[df["marka"].isin(hedef_markalar)]
if not marka_df.empty:
    marka_site = marka_df.groupby(["marka", "site"])["analiz_fiyati"].mean().round(2).unstack()
    print(marka_site.to_string())
else:
    print("  Marka verisi bulunamadı.")

# 5) En indirimli ürünler
print("\n5) En yüksek indirimli ürünler:")
top_indirim = df[df["indirim_orani"] > 0].sort_values("indirim_orani", ascending=False)
print(top_indirim[["site", "cinsiyet", "ad", "fiyat", "indirimli_fiyat", "indirim_orani"]].head(10).to_string(index=False))

# 6) Tarihe göre fiyat dalgalanması
print("\n6) Tarihe göre fiyat dalgalanması:")
tarih_analiz = df.groupby(["tarih", "site"]).agg(
    Ortalama_Fiyat=("analiz_fiyati", "mean"),
    Ortalama_Indirim=("indirim_orani", "mean"),
    Urun_Sayisi=("ad", "count")
).round(2)
print(tarih_analiz)

# 7) Kullanıcıya avantajlı ürün önerileri — cinsiyete göre ayrı
print("\n7) Erkek için en avantajlı 5 ürün:")
erkek_avantajli = (
    erkek_df[erkek_df["indirim_orani"] > 0]
    .sort_values(["indirim_orani", "analiz_fiyati"], ascending=[False, True])
    .drop_duplicates(subset=["site", "url"])
    .head(5)
)
print(erkek_avantajli[["site", "ad", "analiz_fiyati", "indirim_orani", "url"]].to_string(index=False))

print("\n8) Kadın için en avantajlı 5 ürün:")
kadin_avantajli = (
    kadin_df[kadin_df["indirim_orani"] > 0]
    .sort_values(["indirim_orani", "analiz_fiyati"], ascending=[False, True])
    .drop_duplicates(subset=["site", "url"])
    .head(5)
)
print(kadin_avantajli[["site", "ad", "analiz_fiyati", "indirim_orani", "url"]].to_string(index=False))

# CSV çıktıları
avantajli = (
    df.sort_values(["indirim_orani", "analiz_fiyati"], ascending=[False, True])
    .drop_duplicates(subset=["site", "url"])
)

site_ozet.to_csv(REPORTS_DIR / "site_bazli_analiz.csv", encoding="utf-8-sig")
tarih_analiz.to_csv(REPORTS_DIR / "tarih_bazli_fiyat_dalgalanmasi.csv", encoding="utf-8-sig")
cinsiyet_site.to_csv(REPORTS_DIR / "cinsiyet_site_analizi.csv", encoding="utf-8-sig")
avantajli.head(50).to_csv(REPORTS_DIR / "kullanici_icin_avantajli_urunler.csv", encoding="utf-8-sig", index=False)
erkek_avantajli.to_csv(REPORTS_DIR / "erkek_avantajli.csv", encoding="utf-8-sig", index=False)
kadin_avantajli.to_csv(REPORTS_DIR / "kadin_avantajli.csv", encoding="utf-8-sig", index=False)

if not marka_df.empty:
    marka_site.to_csv(REPORTS_DIR / "marka_site_karsilastirma.csv", encoding="utf-8-sig")

print("\nAnaliz dosyaları oluşturuldu.")