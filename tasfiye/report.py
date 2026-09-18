"""README'deki "Çıktılar" bölümünü işlenmiş CSV'lerden yeniden üretir."""
from . import config, fonlar_arasi
from .io import load_detay, read_csv

README = config.ROOT / "README.md"
BASLA, BITIS = "<!-- CIKTILAR:BASLA -->", "<!-- CIKTILAR:BITIS -->"


def mlr(x):
    return f"{float(x) / 1e9:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")


def yuzde(pay, toplam):
    """Payı yuvarlanmış CSV değerinden değil tutarlardan hesaplar (grafiklerle aynı yuvarlama)."""
    x = 100 * float(pay) / toplam
    return ("−" if x < 0 else "") + f"%{abs(x):.1f}".replace(".", ",")


def binlik(x):
    return f"{int(x):,}".replace(",", ".")


def tablo(header, rows, align):
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join(":---" if a == "l" else "---:" for a in align) + "|"]
    lines += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(lines)


def grup_tablosu(dosya, baslik):
    rows = read_csv(config.PROCESSED / dosya)
    key = next(iter(rows[0]))
    toplam = sum(float(r["portfoy_buyuklugu_tl"]) for r in rows)
    return tablo([baslik, "Fon", "Büyüklük (mlr TL)", "Pay", "Yatırımcı*"],
                 [[r[key], r["fon_sayisi"], mlr(r["portfoy_buyuklugu_tl"]), yuzde(r["portfoy_buyuklugu_tl"], toplam),
                   binlik(r["yatirimci_sayisi"])] for r in rows], "lrrrr")


def grafik(no, dosya, baslik):
    return f"### {no}. {baslik}\n\n![{baslik}](output/grafikler/{dosya})"


def bolum():
    varlik = read_csv(config.PROCESSED / "ozet_varlik_dagilimi.csv")
    net_toplam = sum(float(r["net_tl"]) for r in varlik)
    en_buyuk = sorted(load_detay(), key=lambda r: -r["portfoy_buyuklugu_tl"])[:10]
    bilinmeyen = fonlar_arasi.bilinmeyen()
    ilk_yayin, son_yayin = fonlar_arasi.yayin_araligi()
    parts = [
        grafik(1, "1_fon_tipine_gore_tasfiye.png", "Fon tipine göre net fon büyüklüğü"),
        grup_tablosu("ozet_fon_tipi.csv", "Fon tipi"),
        "TEFAS şemsiye fon türüne göre:\n\n" + grup_tablosu("ozet_semsiye_fon_turu.csv", "Şemsiye fon türü"),
        grafik(2, "2_varlik_turune_gore_tasfiye.png", "Varlık türüne göre yaklaşık tutarlar"),
        f"Tutarlar, TEFAS'ın {config.VERI_TARIHI} tarihli net fon büyüklüğü × aynı tarihli portföy dağılım oranıyla "
        "hesaplanan yaklaşık TL karşılıklarıdır. Pozitif sütunu varlık sınıflarındaki pozitif kalemleri, negatif sütunu "
        "dağılımdaki repo ve para piyasası borçlarını gösterir. Net toplam fon büyüklüğüne eşittir. "
        "Bu hesap tam bir brüt bilanço, toplam kaldıraç riski veya gerçekleşecek satış tutarı değildir. "
        "Grafikteki paylar pozitif toplam üzerinden, tablodaki net paylar net toplam üzerinden hesaplanır.\n\n"
        + tablo(["Varlık", "Pozitif (mlr TL)", "Negatif (mlr TL)", "Net (mlr TL)", "Net pay"],
                [[r["varlik"], mlr(r["brut_pozitif_tl"]), mlr(r["negatif_tl"]) if float(r["negatif_tl"]) else "",
                  mlr(r["net_tl"]), yuzde(r["net_tl"], net_toplam)] for r in varlik], "lrrrr"),
        grafik(3, "3_portfoy_sirketine_gore_tasfiye.png", "Portföy şirketine göre net fon büyüklüğü"),
        grup_tablosu("ozet_sirket.csv", "Portföy şirketi"),
        "### Fonların listedeki diğer fonlara yatırımı (KAP, yaklaşık)\n\n"
        "Tutarlar, tutan fonun eldeki en güncel KAP raporundaki oran × rapor net varlığı hesabıyla üretilmiştir. "
        f"Ana hesaplamanın kaynağı TEFAS'ın {config.VERI_TARIHI} verisidir; KAP raporları ise eski dönemlere aittir ve "
        f"{ilk_yayin}–{son_yayin} tarihleri arasında yayımlanmıştır. Bu nedenle aşağıdaki tutarlar "
        f"**{config.VERI_TARIHI} için kesin veya bağlayıcı veri değil, fonlar arası yatırımı gösteren yaklaşık bir göstergedir.** "
        "Tutan ve tutulan fonda mükerrer sayılabilecek bu yatırımlar toplamlardan düşülmemiştir. "
        f"KAP raporu bulunamayan ({bilinmeyen['rapor_yok'][0]} fon) veya muafiyet bildirimi olan ({bilinmeyen['muaf'][0]} fon) "
        "fonlar için bu bilgi bulunmamaktadır.\n\n"
        "Tablodaki gün farkı yalnızca TEFAS veri tarihi ile KAP yayın tarihi arasındadır. "
        "**Yayın tarihi portföyün değerleme tarihi değildir; 0 gün fark, pozisyonların aynı güne ait olduğunu göstermez.** "
        "50 mn TL altındaki kalemler için `fonlar_arasi_yatirim.csv` dosyasına bakın.\n\n"
        + tablo(["Tutan fon", "Tutulan fon", "Yaklaşık tutar (mlr TL)", "KAP raporu (yayın tarihi)", "TEFAS tarihi − KAP yayın tarihi"],
                [[r["tutan_fon"], r["tutulan_fon"], f"{float(r['tutar_tl']) / 1e9:,.2f}".replace(".", ","),
                  f"{r['kap_rapor_donemi']} ({r['kap_yayin_tarihi']})", f"{r['tefas_verisiyle_gun_farki']} gün"]
                 for r in read_csv(fonlar_arasi.CIKTI) if float(r["tutar_tl"]) >= 5e7], "llrlr"),
        "### En büyük 10 fon\n\n"
        + tablo(["Kod", "Fon", "Büyüklük (mlr TL)", "Yatırımcı"],
                [[r["fon_kodu"], r["fon_unvani"], mlr(r["portfoy_buyuklugu_tl"]), binlik(r["yatirimci_sayisi"])]
                 for r in en_buyuk], "llrr"),
        "\\* Yatırımcı sayıları fon bazında toplanmıştır; birden fazla fonda payı olan yatırımcı birden çok sayılır.",
        "### Veri dosyaları\n\n"
        + tablo(["Dosya", "İçerik"], [
            ["[`fon_listesi.csv`](data/processed/fon_listesi.csv)", "SPK bülteninden çıkarılan güncel fon listesi"],
            ["[`tasfiye_fonlar_detay.csv`](data/processed/tasfiye_fonlar_detay.csv)",
             "Fon bazında TEFAS kodu, şemsiye türü, fon tipi, büyüklük, yatırımcı, fiyat"],
            ["[`tasfiye_fonlar_dagilim.csv`](data/processed/tasfiye_fonlar_dagilim.csv)",
             "Fon bazında portföy dağılımı (% ve TL), kaldıraç bilgisi"],
            ["[`ozet_fon_tipi.csv`](data/processed/ozet_fon_tipi.csv)", "Fon tipine göre özet"],
            ["[`ozet_semsiye_fon_turu.csv`](data/processed/ozet_semsiye_fon_turu.csv)", "Şemsiye fon türüne göre özet"],
            ["[`ozet_sirket.csv`](data/processed/ozet_sirket.csv)", "Portföy şirketine göre özet"],
            ["[`ozet_varlik_dagilimi.csv`](data/processed/ozet_varlik_dagilimi.csv)", "Varlık türüne göre brüt, borç ve net TL"],
            ["[`fonlar_arasi_yatirim.csv`](data/processed/fonlar_arasi_yatirim.csv)", "Fonların listedeki diğer fonlara yatırımı (eski dönem KAP raporlarından yaklaşık gösterge)"],
            ["[`kap_fon_paylari.csv`](data/raw/kap_fon_paylari.csv)", "KAP raporlarından çıkarılan ham fon payı oranları ve rapor durumu"],
        ], "ll"),
    ]
    return "\n\n".join(parts)


def main():
    text = README.read_text(encoding="utf-8")
    start, end = text.index(BASLA) + len(BASLA), text.index(BITIS)
    README.write_text(text[:start] + "\n" + bolum() + "\n" + text[end:], encoding="utf-8")
    print("güncellendi:", README.relative_to(config.ROOT))


if __name__ == "__main__":
    main()
