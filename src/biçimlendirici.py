import re

def FiyatTemizle(fiyat_str : str, ondalık_ayracı : str = ',') -> float | None:
    """
    Farklı formatlardaki fiyat metinlerini standart Python float değerine çevirir.
    
    Kullanım:
        FiyatTemizle("1.299,90 TL", ondalık_ayracı=',')  -> 1299.90 (FLO vb.)
        FiyatTemizle("3,499.99₺", ondalık_ayracı='.') -> 3499.99 (Derimod vb.)
    """
    if not fiyat_str or not isinstance(fiyat_str, str):
        return None
    
    temiz = re.sub(r'[^\d.,]', '', fiyat_str)
    if not temiz:
        return None
    
    if ondalık_ayracı == ',':
        # Float dönüşümü için binlik ayracı silinir.
        temiz = temiz.replace('.', '')
        # Float türü ondalık için nokta kullandığı için
        temiz = temiz.replace(',', '.')

    elif ondalık_ayracı == '.':
        # Float dönüşümü için binlik ayracı silinir.
        temiz = temiz.replace(',', '')
        # Buradaki ondalık ayracı zaten float ile aynı.
    
    try:
        return float(temiz)
    except ValueError:
        return None