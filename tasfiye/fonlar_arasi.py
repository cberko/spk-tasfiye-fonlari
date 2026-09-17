"""Listedeki fonların birbirine yatırımı (bilgi amaçlı; toplamlardan düşülmez).

Bir fon (ör. TLY) listedeki başka bir fonun (HMV) payını tutuyorsa o tutar iki fonun büyüklüğünde de yer alır.
Tutarlar, tutan fonun KAP'taki en güncel portföy dağılım raporundaki değerlerdir (oran × rapor net varlığı).
"""
from collections import defaultdict

from . import config
from .io import load_detay, load_tefas_dagilim, read_csv, write_csv

CIKTI = config.PROCESSED / "fonlar_arasi_yatirim.csv"


def yatirimlar():
    """Rapor yayımlayan fonların listedeki fonlara yatırımları, rapordaki TL tutarıyla, büyükten küçüğe."""
    return sorted(({**r, "tutar_tl": float(r["oran"]) * float(r["rapor_net_varlik_tl"])}
                   for r in read_csv(config.KAP_FON_PAYLARI) if r["durum"] == "rapor" and r["tutulan_fon_kodu"]),
                  key=lambda r: -r["tutar_tl"])


def toplam():
    return sum(r["tutar_tl"] for r in yatirimlar())


def bilinmeyen():
    """Portföy içeriği bilinmeyen fonlar: KAP durumu -> (fon sayısı, 16.09 fon payı TL)."""
    buyukluk = {r["fon_kodu"]: r["portfoy_buyuklugu_tl"] for r in load_detay()}
    dagilim = load_tefas_dagilim()
    out = defaultdict(lambda: [0, 0.0])
    for r in read_csv(config.KAP_FON_PAYLARI):  # muaf / rapor_yok fonlar tek satır
        kod = r["fon_kodu"]
        if r["durum"] != "rapor":
            out[r["durum"]][0] += 1
            out[r["durum"]][1] += sum(dagilim[kod].get(f, 0) for f in config.FON_PAYI_ALANLARI) / 100 * buyukluk[kod]
    return dict(out)


def main():
    rows = yatirimlar()
    write_csv(CIKTI, ["tutan_fon", "tutulan_fon", "tutar_tl", "tutan_fon_rapor_net_varlik_tl", "oran",
                      "kap_rapor_donemi", "kap_yayin_tarihi", "kap_bildirim_no"],
              [[r["fon_kodu"], r["tutulan_fon_kodu"], round(r["tutar_tl"], 2), r["rapor_net_varlik_tl"], r["oran"],
                r["rapor_donemi"], r["yayin_tarihi"], r["kap_bildirim_no"]] for r in rows])
    print(f"Listedeki fonlara yatırım (son KAP raporları): {toplam() / 1e9:,.2f} mlr TL, {len(rows)} çift")
    for durum, (adet, tl) in bilinmeyen().items():
        print(f"  içeriği bilinmeyen ({durum}): {adet} fon, {tl / 1e9:,.2f} mlr TL fon payı")


if __name__ == "__main__":
    main()
