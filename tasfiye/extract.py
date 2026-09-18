"""SPK bülteni PDF'inden tasfiye edilecek güncel fon listesini çıkarır (pdftotext gerekir).

Liste, 2026/61 sayılı bültende güncellenmiş haliyle numaralandırılmış olarak yer alır.
"""
import re
import subprocess

from . import config
from .io import write_csv

BASLANGIC = "güncellenmiştir"
ATLANACAK = ("___", "MERKEZ", "İSTANBUL TEMSİLCİLİĞİ", "B. DİĞER", "İhraç ettiği", "https://")


def pdf_text(path):
    return subprocess.run(["pdftotext", "-raw", str(path), "-"], capture_output=True, text=True, check=True).stdout


def parse_funds(text):
    """Numaralı liste; uzun unvanlar birden fazla satıra bölünmüş olabilir."""
    lines = text.splitlines()
    start = next(i for i, l in enumerate(lines) if BASLANGIC in l) + 1
    funds, cur = [], ""
    for line in lines[start:]:
        s = line.strip()
        if not s or s.startswith(ATLANACAK):
            continue
        m = re.match(r"^(\d{1,3})\s*(.*)$", s)
        if m and (not m.group(2) or "PORTFÖY" in m.group(2)):  # yeni sıra numarası
            if cur:
                funds.append(re.sub(r"\s+", " ", cur).strip())
            cur = m.group(2)
        else:
            cur += " " + s
    if cur:
        funds.append(re.sub(r"\s+", " ", cur).strip())
    return funds


def main():
    funds = parse_funds(pdf_text(config.SPK_PDF))
    write_csv(config.FON_LISTESI, ["sira", "portfoy_sirketi", "fon_unvani"],
              [[i, name.split(" PORTFÖY")[0], name] for i, name in enumerate(funds, 1)])
    print(f"{len(funds)} fon -> {config.FON_LISTESI.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
