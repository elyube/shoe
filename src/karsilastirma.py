"""
FLO vs Derimod Fiyat Karşılaştırma Analizi
Veri Madenciliği Projesi
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
import warnings
warnings.filterwarnings("ignore")

# ─── Veri Yükle ──────────────────────────────────────────────────────────────

flo = pd.read_csv("flo_prices.csv", encoding="utf-8-sig")
flo["site"] = "FLO"

derimod = pd.read_csv("derimod_prices.csv", encoding="utf-8-sig")
derimod["site"] = "Derimod"

# Ortak kategorileri eşleştir
flo_spor = flo[flo["kategori"].isin(["Erkek Spor Ayakkabı", "Kadın Spor Ayakkabı"])].copy()
derimod_spor = derimod[derimod["kategori"].isin(["Erkek Spor Ayakkabı", "Kadın Spor Ayakkabı"])].copy()

df = pd.concat([flo_spor, derimod_spor], ignore_index=True)
df = df[df["fiyat"].notna()]

print("=" * 55)
print("  FLO vs Derimod — Spor Ayakkabı Karşılaştırması")
print("=" * 55)

# ─── 1. Genel Özet ───────────────────────────────────────────────────────────
print("\n📊 Genel Özet:")
ozet = df.groupby("site").agg(
    Urun_Sayisi=("fiyat", "count"),
    Ort_Fiyat=("fiyat", "mean"),
    Min_Fiyat=("fiyat", "min"),
    Maks_Fiyat=("fiyat", "max"),
    Indirimli_Urun=("indirim_orani", lambda x: (x > 0).sum()),
    Ort_Indirim=("indirim_orani", lambda x: x[x > 0].mean() if (x > 0).any() else 0),
).round(2)
print(ozet.to_string())

# ─── 2. Kategori Bazında ─────────────────────────────────────────────────────
print("\n📦 Kategori bazında ortalama fiyat (TL):")
kat = df.groupby(["kategori", "site"])["fiyat"].mean().round(2).unstack()
print(kat.to_string())

# ─── 3. En İndirimli Ürünler ─────────────────────────────────────────────────
print("\n🔥 Her siteden en çok indirimli 5 ürün:")
for site in ["FLO", "Derimod"]:
    print(f"\n  {site}:")
    top = (df[(df["site"] == site) & (df["indirim_orani"] > 0)]
           .sort_values("indirim_orani", ascending=False)
           .head(5)[["ad", "fiyat", "indirimli_fiyat", "indirim_orani"]])
    if top.empty:
        print("    İndirimli ürün bulunamadı.")
    else:
        for _, r in top.iterrows():
            print(f"    %{r['indirim_orani']:.0f} — {r['ad'][:50]} ({r['fiyat']:.0f} → {r['indirimli_fiyat']:.0f} TL)")

# ─── 4. Grafikler ────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("FLO vs Derimod — Spor Ayakkabı Fiyat Analizi", fontsize=14, fontweight="bold", y=1.01)

renkler = {"FLO": "#E84C2B", "Derimod": "#2B6CB0"}

# Grafik 1: Ortalama fiyat karşılaştırması
ax1 = axes[0, 0]
site_ort = df.groupby("site")["fiyat"].mean()
bars = ax1.bar(site_ort.index, site_ort.values,
               color=[renkler[s] for s in site_ort.index], width=0.5)
ax1.set_title("Ortalama Fiyat Karşılaştırması")
ax1.set_ylabel("Fiyat (TL)")
ax1.set_ylim(0, site_ort.max() * 1.25)
for bar, val in zip(bars, site_ort.values):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
             f"{val:,.0f} TL", ha="center", fontsize=10, fontweight="bold")
ax1.grid(axis="y", alpha=0.3)
ax1.spines[["top","right"]].set_visible(False)

# Grafik 2: Kategori bazında yan yana bar
ax2 = axes[0, 1]
kategoriler = ["Erkek Spor Ayakkabı", "Kadın Spor Ayakkabı"]
x = range(len(kategoriler))
width = 0.35
for i, site in enumerate(["FLO", "Derimod"]):
    degerler = [df[(df["kategori"]==k) & (df["site"]==site)]["fiyat"].mean() for k in kategoriler]
    bars2 = ax2.bar([xi + i*width for xi in x], degerler,
                    width=width, label=site, color=renkler[site])
ax2.set_title("Kategori Bazında Ortalama Fiyat")
ax2.set_ylabel("Fiyat (TL)")
ax2.set_xticks([xi + width/2 for xi in x])
ax2.set_xticklabels(["Erkek Spor", "Kadın Spor"], fontsize=9)
ax2.legend()
ax2.grid(axis="y", alpha=0.3)
ax2.spines[["top","right"]].set_visible(False)

# Grafik 3: İndirim oranı dağılımı
ax3 = axes[1, 0]
for site in ["FLO", "Derimod"]:
    ind = df[(df["site"]==site) & (df["indirim_orani"] > 0)]["indirim_orani"]
    if not ind.empty:
        ax3.hist(ind, bins=15, alpha=0.6, label=site, color=renkler[site])
ax3.set_title("İndirim Oranı Dağılımı")
ax3.set_xlabel("İndirim Oranı (%)")
ax3.set_ylabel("Ürün Sayısı")
ax3.legend()
ax3.grid(axis="y", alpha=0.3)
ax3.spines[["top","right"]].set_visible(False)

# Grafik 4: İndirimli vs İndirimsiz pasta
ax4 = axes[1, 1]
veriler, etiketler, patlar = [], [], []
for site in ["FLO", "Derimod"]:
    ind = (df[df["site"]==site]["indirim_orani"] > 0).sum()
    toplam = len(df[df["site"]==site])
    veriler += [ind, toplam - ind]
    etiketler += [f"{site} İndirimli", f"{site} Normal"]
    patlar += [0.05, 0]

renkler_pasta = ["#E84C2B", "#FFAA99", "#2B6CB0", "#99BBDD"]
wedges, texts, autotexts = ax4.pie(veriler, labels=etiketler, autopct="%1.0f%%",
                                    colors=renkler_pasta, explode=patlar,
                                    textprops={"fontsize": 8})
ax4.set_title("İndirimli Ürün Oranı")

plt.tight_layout()
plt.savefig("karsilastirma_grafik.png", dpi=150, bbox_inches="tight")
plt.close()
print("\n✅ Grafik kaydedildi → karsilastirma_grafik.png")
print("\n🏁 Analiz tamamlandı!")