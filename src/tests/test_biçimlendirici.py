import pytest
from .. import biçimlendirici as biç

class Test_Biçimlendirici:

    def test_Virgüllü(self):
        yazılar = (
            " 12.489,99 TRY",
            "12.489,99 ₺",
            "12.489,99 TL",
            " 12489,99 TL ",
            "₺12.489,99",
            "$12.489,99",
            " 12.489,99 USD ",
            "£12.489,99",
            "12.489,99",
            "12.489,99\nTL"
        )

        for yazı in yazılar:
            sayı = biç.FiyatTemizle(yazı)
            assert isinstance(sayı, float)
            assert sayı == 12489.99
    

    def test_Noktalı(self):
        yazılar = (
            " 12,489.99 TRY",
            "12,489.99 ₺",
            "12,489.99 TL",
            " 12489.99 TL ",
            "₺12,489.99",
            "$12,489.99",
            " 12,489.99 USD ",
            "£12,489.99",
            "12,489.99",
            "12,489.99\nTL"
        )

        for yazı in yazılar:
            sayı = biç.FiyatTemizle(yazı, ondalık_ayracı='.')
            assert isinstance(sayı, float)
            assert sayı == 12489.99
    
    
    def test_Ondalıksız(self):
        yazılar = (
            "199",
            "199 TL",
            " 199 TL ",
            "₺199",
            "₺ 199",
            "199 TRY",
            "199TRY",
            "$199",
            "199 USD ",
            " £ 199 ",
            "199\nTL"
        )

        for yazı in yazılar:
            sayı = biç.FiyatTemizle(yazı)
            assert isinstance(sayı, float)
            assert sayı == float(199)
    
    
    def test_SayıDeğil(self):
        yazılar = (
            "aaa",
            "₺",
            "     ",
            "\t\t",
            "\r\n",
            "🧐"
        )

        for yazı in yazılar:
            sayı = biç.FiyatTemizle(yazı)
            assert sayı is None
