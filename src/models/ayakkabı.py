from __future__ import annotations
from datetime import datetime

class Ayakkabı:

    def __init__(
        self,
        ad : str,
        marka : str,
        fiyat : float,
        indirimli_fiyat : float | None,
        indirim_oranı : float,
        site : str,
        url : str,
        kategori : str,
        zaman : datetime
    ):
        self.setAd(ad)
        self.setMarka(marka)
        self.setFiyat(fiyat)
        self.setİndirimliFiyat(indirimli_fiyat)
        self.setİndirimOranı(indirim_oranı)
        self.setSite(site)
        self.setURL(url)
        self.setKategori(kategori),
        self.setZaman(zaman)
    

    def toJson(self) -> dict:
        result = {
            "ad" : self.getAd(),
            "marka" : self.getMarka(),
            "fiyat" : self.getFiyat(),
            "indirimli_fiyat" : self.getİndirimliFiyat(),
            "indirim_orani" : self.getİndirimOranı(),
            "site" : self.getSite(),
            "url" : self.getURL(),
            "kategori" : self.getKategori(),
            "zaman" : self.getZaman().isoformat(timespec="seconds")
        }
        return result
    

    def fromJson(jason:dict) -> Ayakkabı | None:
        try:
            result = Ayakkabı(
                ad=jason.get("ad"),
                marka=jason.get("marka"),
                fiyat=jason.get("fiyat"),
                indirimli_fiyat=jason.get("indirimli_fiyat"),
                indirim_oranı=jason.get("indirim_orani"),
                site=jason.get("site"),
                url=jason.get("url"),
                kategori=jason.get("kategori"),
                zaman=datetime.fromisoformat(jason.get("zaman"))
            )
            return result
        except:
            return None

    
    def getAd(self) -> str:
        return self.ad
    
    def setAd(self, ad:str) -> None:
        self.ad = ad
    
    def getMarka(self) -> str:
        return self.marka
    
    def setMarka(self, marka:str) -> None:
        self.marka = marka
    
    def getFiyat(self) -> float:
        return self.fiyat
    
    def setFiyat(self, fiyat:float) -> None:
        self.fiyat = fiyat
    
    def getİndirimliFiyat(self) -> float | None:
        return self.indirimli_fiyat
    
    def setİndirimliFiyat(self, indirimli_fiyat:float|None) -> None:
        self.indirimli_fiyat = indirimli_fiyat
    
    def getİndirimOranı(self) -> float:
        return self.indirim_oranı
    
    def setİndirimOranı(self, indirim_oranı:float) -> None:
        self.indirim_oranı = indirim_oranı
    
    def getSite(self) -> str:
        return self.site
    
    def setSite(self, site:str) -> None:
        self.site = site

    def getURL(self) -> str:
        return self.url
    
    def setURL(self, url:str) -> None:
        self.url = url
    
    def getKategori(self) -> str:
        return self.kategori
    
    def setKategori(self, kategori:str) -> None:
        self.kategori = kategori
    
    def getZaman(self) -> datetime:
        return self.zaman
    
    def setZaman(self, zaman:datetime) -> None:
        self.zaman = zaman