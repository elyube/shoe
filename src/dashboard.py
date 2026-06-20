import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports"
VISUALS_DIR = BASE_DIR / "visuals"
SRC_DIR = BASE_DIR / "src"

# Verileri yükle
site      = pd.read_csv(REPORTS_DIR / "site_bazli_analiz.csv")
avantajli = pd.read_csv(REPORTS_DIR / "kullanici_icin_avantajli_urunler.csv")
tarih     = pd.read_csv(REPORTS_DIR / "tarih_bazli_fiyat_dalgalanmasi.csv")
erkek     = pd.read_csv(REPORTS_DIR / "erkek_avantajli.csv")
kadin     = pd.read_csv(REPORTS_DIR / "kadin_avantajli.csv")

cinsiyet_path = REPORTS_DIR / "cinsiyet_site_analizi.csv"
cinsiyet = pd.read_csv(cinsiyet_path) if cinsiyet_path.exists() else pd.DataFrame()

marka_path = REPORTS_DIR / "marka_site_karsilastirma.csv"
marka = pd.read_csv(marka_path) if marka_path.exists() else pd.DataFrame()

avantajli = avantajli.drop_duplicates(subset=["site", "url"])

# Grafik 1: Ortalama fiyat karşılaştırması
plt.figure(figsize=(9, 5))
renkler = ["#E84C2B", "#2B6CB0", "#16A34A", "#F97316"]
plt.bar(site["site"], site["Ortalama_Fiyat"], color=renkler[:len(site)])
plt.title("Site Bazlı Ortalama Fiyat Karşılaştırması (Spor Ayakkabı)")
plt.xlabel("Site")
plt.ylabel("Ortalama Fiyat (TL)")
plt.xticks(rotation=15)
for i, v in enumerate(site["Ortalama_Fiyat"]):
    plt.text(i, v + 50, f"{v:,.0f} TL", ha="center", fontsize=9, fontweight="bold")
plt.tight_layout()
plt.savefig(VISUALS_DIR / "site_karsilastirma.png", dpi=150)
plt.close()

# Grafik 2: İndirimli ürün sayısı
plt.figure(figsize=(9, 5))
plt.bar(site["site"], site["Indirimli_Urun_Sayisi"], color=renkler[:len(site)])
plt.title("Site Bazlı İndirimli Ürün Sayısı")
plt.xlabel("Site")
plt.ylabel("İndirimli Ürün Sayısı")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(VISUALS_DIR / "indirimli_urun_sayisi.png", dpi=150)
plt.close()

# Grafik 3: Kadın vs Erkek fiyat karşılaştırması
if not cinsiyet.empty and "cinsiyet" in cinsiyet.columns:
    erkek_fiyat = cinsiyet[cinsiyet["cinsiyet"] == "Erkek"].set_index("site")["Ortalama_Fiyat"]
    kadin_fiyat = cinsiyet[cinsiyet["cinsiyet"] == "Kadın"].set_index("site")["Ortalama_Fiyat"]
    siteler = list(set(erkek_fiyat.index) | set(kadin_fiyat.index))
    x = range(len(siteler))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar([i - 0.2 for i in x], [erkek_fiyat.get(s, 0) for s in siteler], 0.4, label="Erkek", color="#2B6CB0")
    ax.bar([i + 0.2 for i in x], [kadin_fiyat.get(s, 0) for s in siteler], 0.4, label="Kadın", color="#E84C2B")
    ax.set_xticks(list(x))
    ax.set_xticklabels(siteler, rotation=15)
    ax.set_title("Cinsiyete Göre Ortalama Fiyat Karşılaştırması")
    ax.set_ylabel("Ortalama Fiyat (TL)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(VISUALS_DIR / "cinsiyet_karsilastirma.png", dpi=150)
    plt.close()

en_ucuz             = site.sort_values("Ortalama_Fiyat").iloc[0]
en_indirimli        = avantajli.sort_values("indirim_orani", ascending=False).iloc[0]
en_fazla_indirimli  = site.sort_values("Indirimli_Urun_Sayisi", ascending=False).iloc[0]

def tablo_html(df, kolonlar, baslik=""):
    if df.empty:
        return f"<p>Veri bulunamadı.</p>"
    satirlar = ""
    for _, r in df[kolonlar].head(10).iterrows():
        hucre = ""
        for k in kolonlar:
            val = r[k]
            if k == "url":
                hucre += f'<td><a href="{val}" target="_blank">Ürüne Git</a></td>'
            elif isinstance(val, float):
                hucre += f"<td>{val:,.2f}</td>"
            else:
                hucre += f"<td>{val}</td>"
        satirlar += f"<tr>{hucre}</tr>"
    basliklar = "".join(f"<th>{k}</th>" for k in kolonlar)
    return f"<table><thead><tr>{basliklar}</tr></thead><tbody>{satirlar}</tbody></table>"

cinsiyet_grafik = '<img src="cinsiyet_karsilastirma.png">' if (VISUALS_DIR / "cinsiyet_karsilastirma.png").exists() else ""

marka_tablo = ""
if not marka.empty:
    marka_tablo = f"<h2>🏷 Marka Bazında Site Fiyat Karşılaştırması</h2>{marka.to_html(index=True)}"

html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Ayakkabı Fiyat Analizi</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background: #f4f6f8; margin: 0; padding: 30px; }}
        h1 {{ text-align: center; margin-bottom: 10px; }}
        .subtitle {{ text-align: center; color: #666; margin-bottom: 35px; font-size: 14px; }}
        .cards {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }}
        .card {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px #ccc; }}
        .value {{ font-size: 28px; font-weight: bold; color: #E84C2B; }}
        .section {{ background: white; padding: 20px; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 2px 8px #ccc; }}
        .cinsiyet-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }}
        .erkek {{ border-left: 5px solid #2B6CB0; }}
        .kadin {{ border-left: 5px solid #E84C2B; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th {{ background: #222; color: white; padding: 10px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; vertical-align: top; }}
        img {{ max-width: 100%; border-radius: 10px; }}
        a {{ color: #1a73e8; }}
        h2 {{ border-bottom: 2px solid #eee; padding-bottom: 8px; }}
    </style>
</head>
<body>

<h1>👟 Ayakkabı Fiyat Karşılaştırma ve Karar Destek Analizi</h1>
<p class="subtitle">FLO · Derimod · Ayakkabı Dünyası · InStreet — Sadece Spor Ayakkabı</p>

<div class="cards">
    <div class="card">
        <h2>🏆 En Ucuz Site</h2>
        <div class="value">{en_ucuz["site"]}</div>
        <p>Ortalama fiyat: <b>{en_ucuz["Ortalama_Fiyat"]:,.2f} TL</b></p>
    </div>
    <div class="card">
        <h2>🔥 En Yüksek İndirim</h2>
        <div class="value">%{en_indirimli["indirim_orani"]}</div>
        <p>{en_indirimli["site"]}</p>
        <p style="font-size:12px">{str(en_indirimli["ad"])[:60]}</p>
    </div>
    <div class="card">
        <h2>💸 En Çok İndirimli Ürün</h2>
        <div class="value">{en_fazla_indirimli["site"]}</div>
        <p>{int(en_fazla_indirimli["Indirimli_Urun_Sayisi"])} indirimli ürün</p>
    </div>
</div>

<div class="section">
    <h2>📌 Kullanıcı İçin Genel Sonuç</h2>
    <p>
        Spor ayakkabı kategorisinde ortalama fiyata göre en avantajlı site <b>{en_ucuz["site"]}</b>'dır.
        En yüksek indirim oranı <b>{en_indirimli["site"]}</b> sitesinde görülmüştür.
        Düşük fiyat arayan kullanıcılar için <b>{en_ucuz["site"]}</b>,
        indirimli ürün arayan kullanıcılar için <b>{en_fazla_indirimli["site"]}</b> daha avantajlıdır.
    </p>
</div>

<div class="cinsiyet-grid">
    <div class="section erkek">
        <h2>👨 Erkek İçin En Avantajlı Ürünler</h2>
        {tablo_html(erkek, ["site", "ad", "analiz_fiyati", "indirim_orani", "url"])}
    </div>
    <div class="section kadin">
        <h2>👩 Kadın İçin En Avantajlı Ürünler</h2>
        {tablo_html(kadin, ["site", "ad", "analiz_fiyati", "indirim_orani", "url"])}
    </div>
</div>

<div class="section">
    <h2>📊 Site Bazlı Ortalama Fiyat</h2>
    <img src="site_karsilastirma.png">
</div>

<div class="section">
    <h2>👥 Cinsiyete Göre Fiyat Karşılaştırması</h2>
    {cinsiyet_grafik}
</div>

<div class="section">
    <h2>🔥 Site Bazlı İndirimli Ürün Sayısı</h2>
    <img src="indirimli_urun_sayisi.png">
</div>

{marka_tablo}

<div class="section">
    <h2>📈 Tarihe Göre Fiyat Dalgalanması</h2>
    {tarih.to_html(index=False)}
</div>

<div class="section">
    <h2>Site Bazlı Özet</h2>
    {site.to_html(index=False)}
</div>

</body>
</html>"""

output = SRC_DIR / "analiz_dashboard.html"
output.write_text(html, encoding="utf-8")
print("Arayüz oluşturuldu:", output)