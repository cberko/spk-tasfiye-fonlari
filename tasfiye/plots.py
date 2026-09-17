"""Üç donut grafik: fon tipi, varlık türü ve portföy şirketine göre tasfiye tutarı."""
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch

from . import config
from .allocation import varlik_tutarlari
from .io import load_detay, load_tefas_dagilim

# dataviz referans paleti, açık tema, sabit slot sırası (6 slot renk körlüğü testinden geçti)
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0"

KAYNAK = f"Kaynak: SPK Bülteni 2026/60 (17.09.2026), TEFAS {config.VERI_TARIHI} fon büyüklükleri."
IMZA = "linkedin.com/in/ceylanberk-tola"

VARLIK_GRUPLARI = {
    "Hisse Senedi": ["hs"],
    "Ters-Repo": ["tr"],
    "Borçlanma Araçları ve Kira Sert.": ["dt", "hb", "fb", "ost", "vdm", "osks", "kkstl"],
    "Para Piyasası İşlemleri": ["bpp", "tpp"],
    "Yatırım Fonu Katılma Payları": ["yyf", "byf", "gsykb"],
    "Mevduat, Katılma Hesabı ve Diğer": ["vmtl", "khtl", "vint", "btas", "d"],
}
VARLIK_ACIKLAMALARI = {
    "Borçlanma Araçları ve Kira Sert.": "DT, finansman bonosu, özel sektör tahvil/kira sert., VDMK",
    "Para Piyasası İşlemleri": "BİST ve Takasbank para piyasası (alacak)",
    "Mevduat, Katılma Hesabı ve Diğer": "TL mevduat, katılma hesabı, VİOP teminatı, diğer",
}


def mlr(x):
    """Türkçe biçimde milyar TL: 842706253086 -> '842,7'."""
    return f"{x / 1e9:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")


def setup_fonts():
    available = {f.name for f in font_manager.fontManager.ttflist}
    plt.rcParams["font.family"] = next(f for f in ("Helvetica Neue", "Arial", "DejaVu Sans") if f in available)
    plt.rcParams["text.color"] = INK


def donut(slices, title, subtitle, fname, footnote=None, source=KAYNAK):
    """slices: (etiket, tutar_tl, açıklama) listesi, büyükten küçüğe."""
    fig = plt.figure(figsize=(16, 9), dpi=100, facecolor=SURFACE)
    fig.text(0.05, 0.925, title, fontsize=26, fontweight="bold")
    fig.text(0.05, 0.875, subtitle, fontsize=15, color=INK2)
    if footnote:
        fig.text(0.05, 0.075, footnote, fontsize=12, color=INK2)
    fig.text(0.05, 0.04, source, fontsize=10.5, color=MUTED)
    fig.text(0.95, 0.04, IMZA, fontsize=10.5, color=MUTED, ha="right")

    total = sum(v for _, v, _ in slices)
    ax = fig.add_axes([0.03, 0.10, 0.48, 0.72])
    ax.pie([v for _, v, _ in slices], colors=SERIES[: len(slices)], startangle=90, counterclock=False,
           wedgeprops=dict(width=0.34, edgecolor=SURFACE, linewidth=2.5))
    ax.text(0, 0.10, mlr(total), ha="center", va="center", fontsize=40, fontweight="bold")
    ax.text(0, -0.13, "milyar TL", ha="center", va="center", fontsize=16, color=INK2)
    ax.set(aspect="equal")

    # etiket tablosu: düşük kontrastlı renkler için değerler doğrudan yazılır
    x0, y, row_h, col_tl, col_pay = 0.55, 0.76, 0.098, 0.86, 0.95
    fig.text(x0 + 0.03, y + 0.045, "Kalem", fontsize=12, color=MUTED)
    fig.text(col_tl, y + 0.045, "mlr TL", fontsize=12, color=MUTED, ha="right")
    fig.text(col_pay, y + 0.045, "Pay", fontsize=12, color=MUTED, ha="right")
    for i, (label, value, detail) in enumerate(slices):
        yy = y - i * row_h
        fig.patches.append(FancyBboxPatch((x0, yy - 0.012), 0.016, 0.028, boxstyle="round,pad=0,rounding_size=0.003",
                                          transform=fig.transFigure, facecolor=SERIES[i], edgecolor="none"))
        fig.text(x0 + 0.03, yy + 0.002, label, fontsize=16, va="center")
        if detail:
            fig.text(x0 + 0.03, yy - 0.034, detail, fontsize=11.5, color=INK2, va="center")
        fig.text(col_tl, yy + 0.002, mlr(value), fontsize=16, va="center", ha="right", fontweight="bold")
        fig.text(col_pay, yy + 0.002, f"%{100 * value / total:.1f}".replace(".", ","),
                 fontsize=16, color=INK2, va="center", ha="right")
        fig.add_artist(plt.Line2D([x0, col_pay], [yy - 0.058] * 2, transform=fig.transFigure, color=GRID, linewidth=1))

    config.CHARTS.mkdir(parents=True, exist_ok=True)
    fig.savefig(config.CHARTS / fname, facecolor=SURFACE)
    plt.close(fig)
    print("yazıldı:", (config.CHARTS / fname).relative_to(config.ROOT))


def grupla(detay, key):
    groups = defaultdict(lambda: [0.0, 0])
    for r in detay:
        groups[r[key]][0] += r["portfoy_buyuklugu_tl"]
        groups[r[key]][1] += 1
    return sorted(groups.items(), key=lambda kv: -kv[1][0])


def main():
    setup_fonts()
    detay = load_detay()

    donut([(k, v, f"{n} fon") for k, (v, n) in grupla(detay, "fon_tipi")],
          f"Tasfiye edilecek fonlar: {mlr(sum(r['portfoy_buyuklugu_tl'] for r in detay))} milyar TL",
          f"SPK listesindeki {len(detay)} fonun büyüklüğü, fon tipine göre",
          "1_fon_tipine_gore_tasfiye.png")

    pos, neg, kaldiracli = varlik_tutarlari(detay, load_tefas_dagilim())
    brut, borc = sum(pos.values()), sum(neg.values())
    varliklar = [(g, sum(pos[k] for k in kodlar), VARLIK_ACIKLAMALARI.get(g, "")) for g, kodlar in VARLIK_GRUPLARI.items()]
    donut(sorted(varliklar, key=lambda t: -t[1]),
          "Tasfiye edilecek varlıklar: türe göre",
          f"Fon büyüklüğü × TEFAS portföy dağılım oranı, brüt {mlr(brut)} mlr TL varlık*",
          "2_varlik_turune_gore_tasfiye.png",
          footnote=f"* Brüt tutardır: kaldıraçlı {len(kaldiracli)} fonun {mlr(-borc)} mlr TL repo ve para piyasası borcu "
                   f"düşülmemiştir. Borç düşüldüğünde net varlık {mlr(brut + borc)} mlr TL (toplam fon büyüklüğü).",
          source=f"Kaynak: SPK Bülteni 2026/60, TEFAS {config.VERI_TARIHI}. "
                 "Hesaplama: fon büyüklüğü × TEFAS portföy dağılım oranı.")

    donut([(f"{k} Portföy", v, f"{n} fon") for k, (v, n) in grupla(detay, "sirket_grubu")],
          "Tasfiye tutarı: portföy şirketine göre",
          "SPK listesindeki fonların büyüklüğü, kurucu portföy yönetim şirketine göre",
          "3_portfoy_sirketine_gore_tasfiye.png")


if __name__ == "__main__":
    main()
