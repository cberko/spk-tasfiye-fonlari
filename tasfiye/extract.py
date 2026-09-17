"""SPK bülteni PDF'inden tasfiye edilecek fon listesini çıkarır (pdftotext gerekir)."""
import subprocess

from . import config
from .io import write_csv

BASLANGIC = "tasfiye ettirilmesine"
BITIS = "karar verilmiştir"
SAYFA_ALTLIGI = ("___", "MERKEZ", "İSTANBUL TEMSİLCİLİĞİ")


def pdf_text(path):
    return subprocess.run(["pdftotext", "-layout", str(path), "-"],
                          capture_output=True, text=True, check=True).stdout


def parse_funds(text):
    lines = text.splitlines()
    start = next(i for i, l in enumerate(lines) if BASLANGIC in l) + 1
    end = next(i for i, l in enumerate(lines) if BITIS in l)
    funds = []
    for line in lines[start:end]:
        s = line.strip()
        if not s or s.isdigit() or s.startswith(SAYFA_ALTLIGI):
            continue
        if "PORTFÖY" in s:
            funds.append(s)
        else:  # alt satıra taşan unvan devamı, ör. "FON)"
            funds[-1] += " " + s
    return funds


def main():
    funds = parse_funds(pdf_text(config.SPK_PDF))
    write_csv(config.FON_LISTESI, ["sira", "portfoy_sirketi", "fon_unvani"],
              [[i, name.split(" PORTFÖY")[0], name] for i, name in enumerate(funds, 1)])
    print(f"{len(funds)} fon -> {config.FON_LISTESI.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
