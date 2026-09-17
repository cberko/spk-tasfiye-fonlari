"""SPK fon listesini TEFAS verisiyle birleştirir; fon tipi, şemsiye türü ve şirket özetlerini yazar."""
from collections import defaultdict

from . import config
from .io import load_tefas_genel, read_csv, write_csv

# PDF'teki büyük harfli kısa ad -> raporlarda kullanılan ad
SIRKET_ADLARI = {"TERA": "Tera", "PUSULA": "Pusula", "HEDEF": "Hedef", "ATLAS": "Atlas",
                 "A1 CAPİTAL": "A1 Capital", "PARDUS": "Pardus", "BULLS": "Bulls"}

DETAY_ALANLARI = ["sira", "portfoy_sirketi", "sirket", "fon_unvani", "fon_kodu", "semsiye_fon_turu",
                  "fon_tipi", "portfoy_buyuklugu_tl", "yatirimci_sayisi", "fiyat", "tedavuldeki_pay"]


def fon_tipi(unvan, semsiye):
    """Grafiklerde kullanılan sınıflama: şemsiye türü + unvandaki ifadeler."""
    if semsiye == "Para Piyasası Şemsiye Fonu":
        return "Para Piyasası Fonu (PPF)"
    if semsiye == "Katılım Şemsiye Fonu":
        return "Katılım (Para Piyasası) Fonu"
    if semsiye == "Hisse Senedi Şemsiye Fonu":
        return "Hisse Senedi Fonu"
    if "PARA PİYASASI" in unvan or "KISA VADELİ" in unvan:
        return "Para Piyasası / Kısa Vadeli Serbest"
    if "YOĞUN" in unvan:
        return "Hisse Senedi Yoğun Serbest"
    return "Diğer Serbest Fon"


def build_rows():
    tefas = load_tefas_genel()
    rows = []
    for f in read_csv(config.FON_LISTESI):
        t = tefas[f["sira"]]
        rows.append({**f, **t, "sirket": SIRKET_ADLARI[f["portfoy_sirketi"]],
                     "fon_tipi": fon_tipi(f["fon_unvani"], t["semsiye_fon_turu"])})
    return rows


def summarize(rows, key, total):
    groups = defaultdict(lambda: [0, 0.0, 0])
    for r in rows:
        g = groups[r[key]]
        g[0] += 1
        g[1] += r["portfoy_buyuklugu_tl"]
        g[2] += r["yatirimci_sayisi"]
    return [[k, n, round(s, 2), round(100 * s / total, 2), p]
            for k, (n, s, p) in sorted(groups.items(), key=lambda kv: -kv[1][1])]


def main():
    rows = build_rows()
    write_csv(config.FON_DETAY, DETAY_ALANLARI, [[r[k] for k in DETAY_ALANLARI] for r in rows])

    total = sum(r["portfoy_buyuklugu_tl"] for r in rows)
    for key in ("fon_tipi", "semsiye_fon_turu", "sirket"):
        write_csv(config.PROCESSED / f"ozet_{key}.csv",
                  [key, "fon_sayisi", "portfoy_buyuklugu_tl", "pay_yuzde", "yatirimci_sayisi"],
                  summarize(rows, key, total))

    print(f"{len(rows)} fon, toplam tasfiye büyüklüğü: {total / 1e9:,.2f} mlr TL")


if __name__ == "__main__":
    main()
