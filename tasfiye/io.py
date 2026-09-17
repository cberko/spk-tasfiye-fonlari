"""Ham ve işlenmiş verilerin okunup yazılması."""
import csv

from . import config


def read_csv(path, encoding="utf-8-sig"):
    with open(path, encoding=encoding, newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def _data_lines(path):
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip() and not line.startswith("#"):
                yield line.strip()


def load_tefas_genel():
    """SPK listesindeki sıra no -> TEFAS genel bilgileri."""
    out = {}
    for line in _data_lines(config.TEFAS_GENEL):
        sira, kod, tur, buyukluk, kisi, fiyat, pay = line.split(";")
        out[sira] = {
            "fon_kodu": kod,
            "semsiye_fon_turu": config.SEMSIYE_TURLERI[int(tur)],
            "portfoy_buyuklugu_tl": float(buyukluk),
            "yatirimci_sayisi": int(kisi),
            "fiyat": float(fiyat),
            "tedavuldeki_pay": int(pay),
        }
    return out


def load_tefas_dagilim():
    """Fon kodu -> {alan kodu: yüzde}. Her fonun toplamı %100; borçlar negatif."""
    out = {}
    for line in _data_lines(config.TEFAS_DAGILIM):
        kod, rest = line.split(":")
        out[kod] = {k: float(v) for k, v in (kv.split("=") for kv in rest.split(","))}
    return out


def load_detay():
    """TEFAS'ta bulunan fonlar (büyüklük float olarak)."""
    rows = [r for r in read_csv(config.FON_DETAY) if r["fon_kodu"]]
    for r in rows:
        r["portfoy_buyuklugu_tl"] = float(r["portfoy_buyuklugu_tl"])
    return rows
