"""README'deki "Çıktılar" bölümünü işlenmiş CSV'lerden yeniden üretir."""
from . import config
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
    parts = [
        grafik(1, "1_fon_tipine_gore_tasfiye.png", "Fon tipine göre tasfiye tutarı"),
        grup_tablosu("ozet_fon_tipi.csv", "Fon tipi"),
        "TEFAS şemsiye fon türüne göre:\n\n" + grup_tablosu("ozet_semsiye_fon_turu.csv", "Şemsiye fon türü"),
        grafik(2, "2_varlik_turune_gore_tasfiye.png", "Varlık türüne göre tasfiye tutarı"),
        "Fon büyüklüğü × TEFAS portföy dağılım oranı. Negatif tutarlar kaldıraçlı fonların repo ve para piyasası borçlarıdır; "
        "net toplam fon büyüklüğüne eşittir.\n\n"
        + tablo(["Varlık", "Brüt (mlr TL)", "Borç (mlr TL)", "Net (mlr TL)", "Net pay"],
                [[r["varlik"], mlr(r["brut_pozitif_tl"]), mlr(r["negatif_tl"]) if float(r["negatif_tl"]) else "",
                  mlr(r["net_tl"]), yuzde(r["net_tl"], net_toplam)] for r in varlik], "lrrrr"),
        grafik(3, "3_portfoy_sirketine_gore_tasfiye.png", "Portföy şirketine göre tasfiye tutarı"),
        grup_tablosu("ozet_sirket_grubu.csv", "Portföy şirketi"),
        "### En büyük 10 fon\n\n"
        + tablo(["Kod", "Fon", "Büyüklük (mlr TL)", "Yatırımcı"],
                [[r["fon_kodu"], r["fon_unvani"], mlr(r["portfoy_buyuklugu_tl"]), binlik(r["yatirimci_sayisi"])]
                 for r in en_buyuk], "llrr"),
        "\\* Yatırımcı sayıları fon bazında toplanmıştır; birden fazla fonda payı olan yatırımcı birden çok sayılır.",
        "### Veri dosyaları\n\n"
        + tablo(["Dosya", "İçerik"], [
            ["[`fon_listesi.csv`](data/processed/fon_listesi.csv)", "SPK bülteninden çıkarılan 130 fon"],
            ["[`tasfiye_fonlar_detay.csv`](data/processed/tasfiye_fonlar_detay.csv)",
             "Fon bazında TEFAS kodu, şemsiye türü, fon tipi, büyüklük, yatırımcı, fiyat"],
            ["[`tasfiye_fonlar_dagilim.csv`](data/processed/tasfiye_fonlar_dagilim.csv)",
             "Fon bazında portföy dağılımı (% ve TL), kaldıraç bilgisi"],
            ["[`ozet_fon_tipi.csv`](data/processed/ozet_fon_tipi.csv)", "Fon tipine göre özet"],
            ["[`ozet_semsiye_fon_turu.csv`](data/processed/ozet_semsiye_fon_turu.csv)", "Şemsiye fon türüne göre özet"],
            ["[`ozet_sirket_grubu.csv`](data/processed/ozet_sirket_grubu.csv)", "Portföy şirketine göre özet"],
            ["[`ozet_varlik_dagilimi.csv`](data/processed/ozet_varlik_dagilimi.csv)", "Varlık türüne göre brüt, borç ve net TL"],
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
