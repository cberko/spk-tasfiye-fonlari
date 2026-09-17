"""TEFAS portföy dağılımı × fon büyüklüğü: tasfiye edilecek varlıkların TL karşılığı."""
from collections import defaultdict

from . import config
from .io import load_detay, load_tefas_dagilim, write_csv


def varlik_tutarlari(detay, dagilim):
    """Varlık kodu başına (brüt pozitif TL, negatif TL) ve kaldıraçlı fon kodları."""
    pos, neg, kaldiracli = defaultdict(float), defaultdict(float), set()
    size = {r["fon_kodu"]: r["portfoy_buyuklugu_tl"] for r in detay}
    for kod, alanlar in dagilim.items():
        for k, yuzde in alanlar.items():
            tl = yuzde / 100 * size[kod]
            if tl < 0:
                neg[k] += tl
                kaldiracli.add(kod)
            else:
                pos[k] += tl
    return pos, neg, kaldiracli


def main():
    detay, dagilim = load_detay(), load_tefas_dagilim()
    keys = [k for k in config.VARLIK_ETIKETLERI if any(k in a for a in dagilim.values())]
    etiket = config.VARLIK_ETIKETLERI

    rows = []
    for r in detay:
        a, size = dagilim.get(r["fon_kodu"], {}), r["portfoy_buyuklugu_tl"]
        kaldirac = "evet" if any(v < 0 for v in a.values()) else ("" if a else "veri yok")
        rows.append([r["fon_kodu"], r["fon_unvani"], r["sirket_grubu"], r["semsiye_fon_turu"], round(size, 2), kaldirac]
                    + [a.get(k, "") for k in keys]
                    + [round(a[k] / 100 * size, 2) if k in a else "" for k in keys])
    write_csv(config.FON_DAGILIM,
              ["fon_kodu", "fon_unvani", "sirket_grubu", "semsiye_fon_turu", "portfoy_buyuklugu_tl", "kaldirac_var"]
              + [f"{etiket[k]} (%)" for k in keys] + [f"{etiket[k]} (TL)" for k in keys], rows)

    pos, neg, kaldiracli = varlik_tutarlari(detay, dagilim)
    net_toplam = sum(pos.values()) + sum(neg.values())
    ozet = sorted(keys, key=lambda k: -(pos[k] + neg[k]))
    write_csv(config.PROCESSED / "ozet_varlik_dagilimi.csv",
              ["varlik", "brut_pozitif_tl", "negatif_tl", "net_tl", "net_pay_yuzde"],
              [[etiket[k], round(pos[k], 2), round(neg[k], 2), round(pos[k] + neg[k], 2),
                round(100 * (pos[k] + neg[k]) / net_toplam, 2)] for k in ozet])

    print(f"Dağılım verisi olan fon: {len(dagilim)} / {len(detay)}")
    print(f"Brüt varlık: {sum(pos.values()) / 1e9:,.2f} mlr TL, borç: {sum(neg.values()) / 1e9:,.2f} mlr TL "
          f"({len(kaldiracli)} kaldıraçlı fon), net: {net_toplam / 1e9:,.2f} mlr TL")


if __name__ == "__main__":
    main()
