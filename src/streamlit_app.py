import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ─── Sayfa Ayarları ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ayakkabı Fiyat Takibi",
    page_icon="👟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stMetric { background: white; padding: 15px; border-radius: 10px; }
    div[data-testid="stMetricValue"] { font-size: 2rem; }
</style>
""", unsafe_allow_html=True)

# ─── Veri Yükle ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

@st.cache_data
def veri_yukle():
    files = {
        "FLO":              BASE_DIR / "data" / "flo_prices.csv",
        "Derimod":          BASE_DIR / "data" / "derimod_prices.csv",
        "InStreet":         BASE_DIR / "data" / "instreet_prices.csv",
        "Ayakkabı Dünyası": BASE_DIR / "data" / "ayakkabidunyasi_prices.csv",
    }

    all_data = []
    for site, path in files.items():
        if not path.exists():
            continue
        df = pd.read_csv(path, encoding="utf-8-sig", on_bad_lines="skip")
        df["site"] = site
        df["zaman"] = pd.to_datetime(df["zaman"], errors="coerce")
        df["tarih"] = df["zaman"].dt.date
        df["analiz_fiyati"] = pd.to_numeric(
            df.get("indirimli_fiyat", df["fiyat"]).fillna(df["fiyat"]),
            errors="coerce"
        )
        df["indirim_orani"] = pd.to_numeric(
            df.get("indirim_orani", 0), errors="coerce"
        ).fillna(0)
        all_data.append(df)

    df = pd.concat(all_data, ignore_index=True)

    def fix_text(t):
        try:
            return str(t).encode("latin1").decode("utf-8")
        except:
            return str(t)

    # Önce encoding düzelt, sonra filtrele
    df["ad"]       = df["ad"].apply(fix_text)
    df["kategori"] = df["kategori"].apply(fix_text)
    df["marka"]    = df["marka"].apply(fix_text) if "marka" in df.columns else "Bilinmiyor"

    # FLO marka düzeltmesi — ürün adının ilk kelimesini marka olarak al
    if site == "FLO":
        df["marka"] = df["ad"].apply(lambda x: str(x).split()[0] if pd.notna(x) else "Bilinmiyor")

    # Derimod marka düzeltmesi
    if site == "Derimod":
        cinsiyet_kelimeleri = {"kadın", "erkek", "unisex", "çocuk"}
        def derimod_marka(ad):
            ilk = str(ad).split()[0].lower() if pd.notna(ad) else ""
            if ilk in cinsiyet_kelimeleri:
                return "Derimod"
            return str(ad).split()[0].capitalize()
        df["marka"] = df["ad"].apply(derimod_marka)

    # InStreet marka düzeltmesi — ürün adının ilk kelimesini marka olarak al
    if site == "InStreet":
        cinsiyet_kelimeleri = {"kadın", "erkek", "unisex", "çocuk"}
        def instreet_marka(ad):
            ilk = str(ad).split()[0].lower() if pd.notna(ad) else ""
            if ilk in cinsiyet_kelimeleri:
                return "InStreet"
            return str(ad).split()[0].capitalize()
        df["marka"] = df["ad"].apply(instreet_marka)

    SPOR = ["Erkek Spor Ayakkabı", "Kadın Spor Ayakkabı"]

    # FLO indirimli sayfasındaki spor ürünlerini de dahil et
    spor_anahtar = ["Spor", "Sneaker", "Koşu", "Running", "Training"]
    flo_ind = df[
        (df["site"] == "FLO") &
        (df["kategori"] == "İndirimli Ürünler") &
        (df["ad"].apply(lambda x: any(k in str(x) for k in spor_anahtar)))
    ].copy()

    # Cinsiyeti ad'dan tahmin et
    def cinsiyet_tahmin(ad):
        ad = str(ad).lower()
        if "erkek" in ad:
            return "Erkek Spor Ayakkabı"
        elif "kadın" in ad or "kadin" in ad:
            return "Kadın Spor Ayakkabı"
        else:
            return "Erkek Spor Ayakkabı"  # varsayılan

    flo_ind["kategori"] = flo_ind["ad"].apply(cinsiyet_tahmin)

    df_spor = df[df["kategori"].isin(SPOR)]
    df = pd.concat([df_spor, flo_ind], ignore_index=True)
    df = df.drop_duplicates(subset=["ad", "url", "zaman"])
    df = df[df["analiz_fiyati"].notna()]
    df = df.drop_duplicates(subset=["site", "ad", "url", "tarih"])

    df["cinsiyet"] = df["kategori"].apply(
        lambda x: "Erkek" if "Erkek" in x else "Kadın"
    )
    return df

df = veri_yukle()

SITE_RENK = {
    "FLO":              "#E84C2B",
    "Derimod":          "#2B6CB0",
    "InStreet":         "#16A34A",
    "Ayakkabı Dünyası": "#F97316",
}

# ─── Sidebar ─────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 👟 Fiyat Takibi")
st.sidebar.divider()
st.sidebar.title("Filtreler")

cinsiyet_sec = st.sidebar.radio("👤 Cinsiyet", ["Tümü", "Erkek", "Kadın"])
site_sec     = st.sidebar.multiselect(
    "🏪 Site",
    options=df["site"].unique().tolist(),
    default=df["site"].unique().tolist()
)

fiyat_min, fiyat_maks = int(df["analiz_fiyati"].min()), int(df["analiz_fiyati"].max())
fiyat_aralik = st.sidebar.slider(
    "💰 Fiyat Aralığı (TL)",
    fiyat_min, fiyat_maks,
    (fiyat_min, fiyat_maks)
)

sadece_indirimli = st.sidebar.checkbox("🔥 Sadece İndirimli Ürünler")

# ─── Filtrele ────────────────────────────────────────────────────────────────
filtre = df[df["site"].isin(site_sec)]
filtre = filtre[
    (filtre["analiz_fiyati"] >= fiyat_aralik[0]) &
    (filtre["analiz_fiyati"] <= fiyat_aralik[1])
]
if cinsiyet_sec != "Tümü":
    filtre = filtre[filtre["cinsiyet"] == cinsiyet_sec]
if sadece_indirimli:
    filtre = filtre[filtre["indirim_orani"] != 0]

# ─── Başlık ──────────────────────────────────────────────────────────────────
st.title("👟 Ayakkabı Fiyat ve İndirim Takibi")
st.caption("FLO · Derimod · InStreet · Ayakkabı Dünyası — Spor Ayakkabı Karşılaştırması")

if filtre.empty:
    st.warning("Seçilen filtrelere uygun ürün bulunamadı.")
    st.stop()

# ─── Metrikler ───────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

en_ucuz_site = filtre.groupby("site")["analiz_fiyati"].mean().idxmin()
en_ucuz_fiyat = filtre.groupby("site")["analiz_fiyati"].mean().min()

c1.metric("🏆 En Ucuz Site", en_ucuz_site, f"{en_ucuz_fiyat:,.0f} TL ort.")
c2.metric("📦 Toplam Ürün", f"{len(filtre):,}")
c3.metric("🔥 İndirimli Ürün", f"{(filtre['indirim_orani'] != 0).sum():,}")
c4.metric("💸 Max İndirim", f"%{filtre[filtre['indirim_orani'] > 0]['indirim_orani'].max():.0f}" if (filtre['indirim_orani'] > 0).any() else "—")

st.divider()

# ─── En İyi Fırsat Önerisi ───────────────────────────────────────────────────
st.subheader("💡 Şu An En İyi Fırsatlar")

col_e, col_k = st.columns(2)

with col_e:
    st.caption("👨 Erkek")
    erkek_firsat = filtre[
        (filtre["cinsiyet"] == "Erkek") & (filtre["indirim_orani"] > 0)
    ].sort_values("indirim_orani", ascending=False).drop_duplicates("url").head(3)
    if not erkek_firsat.empty:
        for _, r in erkek_firsat.iterrows():
            st.markdown(
                f"🔥 **%{r['indirim_orani']:.0f}** — {str(r['ad'])[:45]}  \n"
                f"💰 {r['analiz_fiyati']:,.0f} TL · 🏪 {r['site']}  \n"
                f"[Ürüne Git →]({r['url']})"
            )
            st.divider()
    else:
        st.info("İndirimli erkek ürünü bulunamadı.")

with col_k:
    st.caption("👩 Kadın")
    kadin_firsat = filtre[
        (filtre["cinsiyet"] == "Kadın") & (filtre["indirim_orani"] > 0)
    ].sort_values("indirim_orani", ascending=False).drop_duplicates("url").head(3)
    if not kadin_firsat.empty:
        for _, r in kadin_firsat.iterrows():
            st.markdown(
                f"🔥 **%{r['indirim_orani']:.0f}** — {str(r['ad'])[:45]}  \n"
                f"💰 {r['analiz_fiyati']:,.0f} TL · 🏪 {r['site']}  \n"
                f"[Ürüne Git →]({r['url']})"
            )
            st.divider()
    else:
        st.info("İndirimli kadın ürünü bulunamadı.")

# ─── Marka Fırsat Sorgulayıcı ────────────────────────────────────────────────
st.subheader("🔍 Marka Fiyat Sorgula")
col_m1, col_m2 = st.columns([1, 3])
with col_m1:
    markalar_tum = sorted(filtre["marka"].dropna().unique().tolist())
    sec_sorgula = st.selectbox("Marka seç", markalar_tum)
with col_m2:
    if sec_sorgula:
        m_df = filtre[filtre["marka"] == sec_sorgula]
        site_fiyat = m_df.groupby("site")["analiz_fiyati"].mean().sort_values()
        if not site_fiyat.empty:
            en_ucuz_site_m = site_fiyat.index[0]
            en_ucuz_fiyat_m = site_fiyat.iloc[0]
            st.success(f"**{sec_sorgula}** için en ucuz site: **{en_ucuz_site_m}** — ort. {en_ucuz_fiyat_m:,.0f} TL")
            for site_adi, fiyat in site_fiyat.items():
                fark = fiyat - en_ucuz_fiyat_m
                isaret = "✅" if fiyat == en_ucuz_fiyat_m else f"▲ +{fark:,.0f} TL"
                st.markdown(f"- **{site_adi}**: {fiyat:,.0f} TL {isaret}")

st.divider()

# ─── Tab Yapısı ──────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Site Karşılaştırma",
    "👥 Erkek vs Kadın",
    "🏷 Marka Analizi",
    "🔥 İndirimler",
    "📈 Fiyat Trendi"
])

# ── Tab 1: Site Karşılaştırma ─────────────────────────────────────────────
with tab1:
    site_ort = filtre.groupby("site")["analiz_fiyati"].mean().reset_index()
    site_ort.columns = ["Site", "Ortalama Fiyat (TL)"]
    fig = px.bar(
        site_ort, x="Site", y="Ortalama Fiyat (TL)",
        color="Site", color_discrete_map=SITE_RENK,
        title="Site Bazlı Ortalama Fiyat",
        text_auto=".0f"
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Site Özet Tablosu")

    ozet_rows = []
    for site_adi, grp in filtre.groupby("site"):
        toplam       = len(grp)
        ort_fiyat    = grp["analiz_fiyati"].mean()
        min_fiyat    = grp["analiz_fiyati"].min()
        maks_fiyat   = grp["analiz_fiyati"].max()
        indirimli_n  = (grp["indirim_orani"] != 0).sum()
        indirimli_pct= round(indirimli_n / toplam * 100, 1) if toplam > 0 else 0
        gercek_ind   = grp[grp["indirim_orani"] > 0]["indirim_orani"]
        ort_indirim  = round(gercek_ind.mean(), 1) if len(gercek_ind) >= 5 else None

        ozet_rows.append({
            "Site":                 site_adi,
            "Ürün Sayısı":          toplam,
            "Ort. Fiyat (TL)":      round(ort_fiyat, 2),
            "Min Fiyat (TL)":       round(min_fiyat, 2),
            "Maks Fiyat (TL)":      round(maks_fiyat, 2),
            "İndirimli Ürün":       indirimli_n,
            "İndirimli Oran (%)":   indirimli_pct,
            "Ort. İndirim (%)":     ort_indirim if ort_indirim else "—",
        })

    ozet = pd.DataFrame(ozet_rows)
    st.dataframe(ozet, use_container_width=True, hide_index=True)

# ── Tab 2: Erkek vs Kadın ─────────────────────────────────────────────────
with tab2:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👨 Erkek Spor Ayakkabı")
        erkek_df = filtre[filtre["cinsiyet"] == "Erkek"]
        if not erkek_df.empty:
            erkek_ozet = erkek_df.groupby("site")["analiz_fiyati"].mean().reset_index()
            fig = px.bar(erkek_ozet, x="site", y="analiz_fiyati",
                        color="site", color_discrete_map=SITE_RENK,
                        labels={"analiz_fiyati": "Ort. Fiyat (TL)", "site": "Site"},
                        text_auto=".0f")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

            en_iyi = erkek_df[erkek_df["indirim_orani"] != 0].sort_values(
                ["indirim_orani", "analiz_fiyati"], ascending=[False, True]
            ).head(5)
            st.caption("🔥 En avantajlı erkek ürünleri:")
            for _, r in en_iyi.iterrows():
                st.markdown(f"**{r['site']}** — {str(r['ad'])[:50]}  \n"
                           f"💰 {r['analiz_fiyati']:,.0f} TL &nbsp; 🔥 %{r['indirim_orani']:.0f} indirim")

    with col2:
        st.subheader("👩 Kadın Spor Ayakkabı")
        kadin_df = filtre[filtre["cinsiyet"] == "Kadın"]
        if not kadin_df.empty:
            kadin_ozet = kadin_df.groupby("site")["analiz_fiyati"].mean().reset_index()
            fig = px.bar(kadin_ozet, x="site", y="analiz_fiyati",
                        color="site", color_discrete_map=SITE_RENK,
                        labels={"analiz_fiyati": "Ort. Fiyat (TL)", "site": "Site"},
                        text_auto=".0f")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

            en_iyi = kadin_df[kadin_df["indirim_orani"] != 0].sort_values(
                ["indirim_orani", "analiz_fiyati"], ascending=[False, True]
            ).head(5)
            st.caption("🔥 En avantajlı kadın ürünleri:")
            for _, r in en_iyi.iterrows():
                st.markdown(f"**{r['site']}** — {str(r['ad'])[:50]}  \n"
                           f"💰 {r['analiz_fiyati']:,.0f} TL &nbsp; 🔥 %{r['indirim_orani']:.0f} indirim")

    # Yan yana karşılaştırma
    st.subheader("Erkek vs Kadın — Site Bazında")
    cv = filtre.groupby(["cinsiyet", "site"])["analiz_fiyati"].mean().reset_index()
    fig = px.bar(cv, x="site", y="analiz_fiyati", color="cinsiyet",
                barmode="group", color_discrete_map={"Erkek": "#2B6CB0", "Kadın": "#E84C2B"},
                labels={"analiz_fiyati": "Ort. Fiyat (TL)", "site": "Site"},
                text_auto=".0f")
    st.plotly_chart(fig, use_container_width=True)

# ── Tab 3: Marka Analizi ──────────────────────────────────────────────────
with tab3:
    st.subheader("🏷 Marka Bazında Site Fiyat Karşılaştırması")

    if "marka" in filtre.columns:
        markalar = filtre["marka"].value_counts().head(15).index.tolist()
        sec_marka = st.multiselect(
            "Marka seç", markalar,
            default=markalar[:6]
        )

        if sec_marka:
            marka_df = filtre[filtre["marka"].isin(sec_marka)]
            marka_ozet = marka_df.groupby(["marka", "site"])["analiz_fiyati"].mean().reset_index()
            fig = px.bar(
                marka_ozet, x="marka", y="analiz_fiyati",
                color="site", barmode="group",
                color_discrete_map=SITE_RENK,
                labels={"analiz_fiyati": "Ort. Fiyat (TL)", "marka": "Marka"},
                title="Markaya Göre Site Fiyat Karşılaştırması",
                text_auto=".0f"
            )
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Her Marka İçin En Ucuz Site")
            for marka in sec_marka:
                m_df = filtre[filtre["marka"] == marka]
                if m_df.empty:
                    continue
                en_ucuz = m_df.groupby("site")["analiz_fiyati"].mean()
                st.markdown(
                    f"**{marka}** → En ucuz: **{en_ucuz.idxmin()}** "
                    f"({en_ucuz.min():,.0f} TL)"
                )
    else:
        st.info("Marka verisi bulunamadı.")

# ── Tab 4: İndirimler ─────────────────────────────────────────────────────
with tab4:
    st.subheader("🔥 En Yüksek İndirimli Ürünler")

    cin_filtre = st.radio("Cinsiyet", ["Tümü", "Erkek", "Kadın"], horizontal=True, key="ind_cin")

    ind_df = filtre[filtre["indirim_orani"] != 0].copy()
    if cin_filtre != "Tümü":
        ind_df = ind_df[ind_df["cinsiyet"] == cin_filtre]

    ind_df = ind_df.sort_values("indirim_orani", ascending=False).drop_duplicates(
        subset=["site", "url"]
    ).head(20)

    if not ind_df.empty:
        fig = px.scatter(
            ind_df,
            x="analiz_fiyati", y="indirim_orani",
            color="site", color_discrete_map=SITE_RENK,
            hover_data=["ad", "site"],
            size="indirim_orani",
            labels={"analiz_fiyati": "Fiyat (TL)", "indirim_orani": "İndirim (%)"},
            title="Fiyat vs İndirim Oranı"
        )
        st.plotly_chart(fig, use_container_width=True)

        for _, r in ind_df.head(10).iterrows():
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.markdown(f"**{str(r['ad'])[:60]}**  \n🏪 {r['site']} · {r['cinsiyet']}")
            col2.metric("Fiyat", f"{r['analiz_fiyati']:,.0f} TL")
            col3.metric("İndirim", f"%{r['indirim_orani']:.0f}" if r['indirim_orani'] > 0 else "İndirimli")
            st.divider()
    else:
        st.info("İndirimli ürün bulunamadı.")

# ── Tab 5: Fiyat Trendi ───────────────────────────────────────────────────
with tab5:
    st.subheader("📈 Zamana Göre Ortalama Fiyat Trendi")

    tarih_df = filtre.groupby(["tarih", "site"])["analiz_fiyati"].mean().reset_index()
    tarih_df["tarih"] = pd.to_datetime(tarih_df["tarih"])
    tarih_df = tarih_df.sort_values("tarih")

    if tarih_df["tarih"].nunique() > 1:
        fig = px.line(
            tarih_df, x="tarih", y="analiz_fiyati",
            color="site", color_discrete_map=SITE_RENK,
            markers=True,
            labels={"analiz_fiyati": "Ort. Fiyat (TL)", "tarih": "Tarih"},
            title="Günlük Ortalama Fiyat Değişimi"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Fiyat trendi için en az 2 farklı tarihte veri gereklidir. "
                "Scraper'ı birkaç gün çalıştırdıktan sonra burada grafik görünecek.")

    st.subheader("Ham Veri")
    goster = filtre[["site", "cinsiyet", "ad", "marka", "analiz_fiyati",
                      "indirim_orani", "kategori", "tarih", "url"]].sort_values(
        "analiz_fiyati"
    ).reset_index(drop=True)
    st.dataframe(goster, use_container_width=True, height=400)