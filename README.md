# Ayakkabı İndirim ve Fiyat Takibi

Alışveriş sitelerinden web scraping yöntemi ile düzenli
aralıklarla ayakkabı modelleri ve fiyatları çekilerek
fiyat ve indirim takibi sağlayan bir program.

> Veri çekmek için Selenium kullanılmaktadır.

## Siteler
- FLO
- Derimod
- Ayakkabı Dünyası
- InStreet

## Kurulum
```bash
pip install -r requirements.txt
```

## Kullanım
```bash
python src/flo_scraper.py
python src/derimod_scraper.py
python src/ayakkabidunyasi_scraper.py
python src/instreet_scraper.py
python src/genel_analiz.py
python src/dashboard.py
streamlit run src/streamlit_app.py
```

---
*Copyright © 2026 Elmas Güneş, Yusuf Kozan, Betül Turan*