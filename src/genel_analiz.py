import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

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

    fiyat_kolonu = "indirimli_fiyat" if "indirimli_fiyat" in df.columns else "fiyat"

    df["analiz_fiyati"] = df[fiyat_kolonu].fillna(df["fiyat"])
    df["analiz_fiyati"] = pd.to_numeric(df["analiz_fiyati"], errors="coerce")
    df["indirim_orani"] = pd.to_numeric(df["indirim_orani"], errors="coerce").fillna(0)

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

print("=" * 60)
print("GENEL AYAKKABI FİYAT ANALİZİ")
print("=" * 60)

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

print("\n2) Kullanıcı için en avantajlı site:")
en_ucuz_site = site_ozet["Ortalama_Fiyat"].idxmin()
print(f"Ortalama fiyata göre en avantajlı site: {en_ucuz_site}")

print("\n3) En yüksek indirimli ürünler:")
top_indirim = df[df["indirim_orani"] > 0].sort_values("indirim_orani", ascending=False)
print(top_indirim[["site", "ad", "fiyat", "indirimli_fiyat", "indirim_orani", "kategori", "tarih"]].head(10).to_string(index=False))

print("\n4) Tarihe göre fiyat dalgalanması:")
tarih_analiz = df.groupby(["tarih", "site"]).agg(
    Ortalama_Fiyat=("analiz_fiyati", "mean"),
    Ortalama_Indirim=("indirim_orani", "mean"),
    Urun_Sayisi=("ad", "count")
).round(2)

print(tarih_analiz)

print("\n5) Kategori bazında en uygun site:")
kategori_site = df.groupby(["kategori", "site"])["analiz_fiyati"].mean().round(2).reset_index()

for kategori in kategori_site["kategori"].dropna().unique():
    temp = kategori_site[kategori_site["kategori"] == kategori]
    en_uygun = temp.loc[temp["analiz_fiyati"].idxmin()]
    print(f"{kategori}: En uygun site → {en_uygun['site']} ({en_uygun['analiz_fiyati']} TL)")

print("\n6) Kullanıcıya avantajlı ürün önerileri:")
avantajli = (
    df.sort_values(
        ["indirim_orani", "analiz_fiyati"],
        ascending=[False, True]
    )
    .drop_duplicates(subset=["site", "url"])
)
avantajli = avantajli.drop_duplicates(subset=["site", "url"])
print(avantajli[["site", "ad", "analiz_fiyati", "indirim_orani", "kategori", "url"]].head(10).to_string(index=False))

site_ozet.to_csv(BASE_DIR / "site_bazli_analiz.csv", encoding="utf-8-sig")
tarih_analiz.to_csv(BASE_DIR / "tarih_bazli_fiyat_dalgalanmasi.csv", encoding="utf-8-sig")
kategori_site.to_csv(BASE_DIR / "kategori_site_fiyat_analizi.csv", encoding="utf-8-sig")
avantajli.head(50).to_csv(BASE_DIR / "kullanici_icin_avantajli_urunler.csv", encoding="utf-8-sig", index=False)

print("\nAnaliz dosyaları oluşturuldu.")