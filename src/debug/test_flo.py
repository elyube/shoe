import pandas as pd
df=pd.read_csv('data/flo_prices.csv', on_bad_lines='skip')
df['fiyat']=pd.to_numeric(df['fiyat'], errors='coerce')
df['indirimli_fiyat']=pd.to_numeric(df['indirimli_fiyat'], errors='coerce')
df = df[(df['fiyat'] < 50000) & (df['indirimli_fiyat'].notna()) & (df['indirimli_fiyat'] < df['fiyat'])]
print("Before drop_duplicates:", len(df))
df = df.drop_duplicates(subset=["ad", "url"])
print("After drop_duplicates:", len(df))
SPOR = ["Erkek Spor Ayakkabı", "Kadın Spor Ayakkabı"]
df_spor = df[df["kategori"].isin(SPOR)]
print("After SPOR filter:", len(df_spor))
print("Categories in remaining discounted FLO items:", df["kategori"].value_counts().head(10))
