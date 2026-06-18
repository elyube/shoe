import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

site = pd.read_csv(BASE_DIR / "site_bazli_analiz.csv")
avantajli = pd.read_csv(BASE_DIR / "kullanici_icin_avantajli_urunler.csv")
tarih = pd.read_csv(BASE_DIR / "tarih_bazli_fiyat_dalgalanmasi.csv")

avantajli = avantajli.drop_duplicates(subset=["site", "url"])

# Grafik 1: Tüm sitelerin ortalama fiyat grafiği
plt.figure(figsize=(9, 5))
plt.bar(site["site"], site["Ortalama_Fiyat"])
plt.title("Site Bazlı Ortalama Fiyat Karşılaştırması")
plt.xlabel("Site")
plt.ylabel("Ortalama Fiyat (TL)")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(BASE_DIR / "site_karsilastirma.png", dpi=150)
plt.close()

# Grafik 2: İndirimli ürün sayısı grafiği
plt.figure(figsize=(9, 5))
plt.bar(site["site"], site["Indirimli_Urun_Sayisi"])
plt.title("Site Bazlı İndirimli Ürün Sayısı")
plt.xlabel("Site")
plt.ylabel("İndirimli Ürün Sayısı")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(BASE_DIR / "indirimli_urun_sayisi.png", dpi=150)
plt.close()

en_ucuz = site.sort_values("Ortalama_Fiyat").iloc[0]
en_indirimli = avantajli.sort_values("indirim_orani", ascending=False).iloc[0]
en_fazla_indirimli_urun = site.sort_values("Indirimli_Urun_Sayisi", ascending=False).iloc[0]

html = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Ayakkabı Fiyat Analizi</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            margin: 0;
            padding: 30px;
        }}
        h1 {{
            text-align: center;
            margin-bottom: 35px;
        }}
        .cards {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px #ccc;
        }}
        .value {{
            font-size: 28px;
            font-weight: bold;
        }}
        .section {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 2px 8px #ccc;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            margin-top: 20px;
            margin-bottom: 35px;
        }}
        th, td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
            text-align: left;
            vertical-align: top;
        }}
        th {{
            background: #222;
            color: white;
        }}
        img {{
            max-width: 100%;
            border-radius: 10px;
        }}
        a {{
            color: #1a73e8;
        }}
    </style>
</head>
<body>

<h1>Ayakkabı Fiyat Karşılaştırma ve Karar Destek Analizi</h1>

<div class="cards">
    <div class="card">
        <h2>🏆 En Ucuz Site</h2>
        <div class="value">{en_ucuz["site"]}</div>
        <p>Ortalama fiyat: {en_ucuz["Ortalama_Fiyat"]:.2f} TL</p>
    </div>

    <div class="card">
        <h2>🔥 En Yüksek İndirim</h2>
        <div class="value">{en_indirimli["indirim_orani"]}%</div>
        <p>{en_indirimli["site"]}</p>
        <p>{en_indirimli["ad"]}</p>
    </div>

    <div class="card">
        <h2>💸 En Çok İndirimli Ürün</h2>
        <div class="value">{en_fazla_indirimli_urun["site"]}</div>
        <p>{int(en_fazla_indirimli_urun["Indirimli_Urun_Sayisi"])} indirimli ürün</p>
    </div>
</div>

<div class="section">
    <h2>📌 Kullanıcı İçin Sonuç</h2>
    <p>
        Ortalama fiyatlara göre en avantajlı site <b>{en_ucuz["site"]}</b>.
        En yüksek indirim oranı ise <b>{en_indirimli["site"]}</b> sitesinde görülmüştür.
        Düşük fiyat arayan kullanıcılar için {en_ucuz["site"]},
        yüksek kampanya arayan kullanıcılar için {en_indirimli["site"]} daha avantajlıdır.
    </p>
</div>

<div class="section">
    <h2>📊 Tüm Sitelerin Ortalama Fiyat Grafiği</h2>
    <img src="site_karsilastirma.png">
</div>

<div class="section">
    <h2>🔥 Site Bazlı İndirimli Ürün Sayısı</h2>
    <img src="indirimli_urun_sayisi.png">
</div>

<h2>Site Bazlı Fiyat Karşılaştırması</h2>
{site.to_html(index=False)}

<h2>Tarihe Göre Fiyat Dalgalanması</h2>
{tarih.to_html(index=False)}

<h2>Kullanıcı İçin Avantajlı Ürünler</h2>
{avantajli[["site", "ad", "analiz_fiyati", "indirim_orani", "kategori", "url"]].head(20).to_html(index=False, render_links=True)}

</body>
</html>
"""

output = BASE_DIR / "analiz_dashboard.html"
output.write_text(html, encoding="utf-8")

print("Arayüz oluşturuldu:", output)