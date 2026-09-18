"""KAP portföy dağılım raporlarından, fon payı tutan fonların listedeki diğer fonlara yatırımlarını çıkarır.

Ağ erişimi gerektirir, ana akışta çalışmaz: python -m tasfiye.kap
Çıktı: data/raw/kap_fon_paylari.csv (her satır: tutan fon, rapor bilgisi ve net varlığı, tutulan listedeki fon, oran).
İndirilen raporlar data/raw/kap_cache/ altında önbelleğe alınır (repoya girmez).
"""
import datetime as dt
import json
import re
import subprocess
import time
import urllib.error
import urllib.request

from . import config
from .io import load_detay, load_tefas_dagilim, write_csv

API = "https://www.kap.org.tr/tr/api"
CACHE = config.RAW / "kap_cache"
PORTFOY_DAGILIM_RAPORU = "8aca490d502e34b801502e380044002b"  # KAP konu (subject) kimliği
ARAMA_BITIS, ARAMA_BASLANGIC = dt.date(2026, 9, 17), dt.date(2026, 1, 1)


def _request(url, body=None):
    headers = {"User-Agent": "Mozilla/5.0", "Accept-Language": "tr", "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(6):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, data, headers), timeout=120).read()
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(60 * (attempt + 1))  # KAP istek sınırı
    raise RuntimeError(f"KAP istek sınırı aşılamadı: {url}")


def fon_payi_tutanlar():
    return sorted(k for k, a in load_tefas_dagilim().items() if any(f in a for f in config.FON_PAYI_ALANLARI))


def son_raporlar(fonlar):
    """Her fon için ARAMA_BITIS'ten geriye en güncel portföy dağılım raporu bildirimi (önbellekli)."""
    path = CACHE / "son_raporlar.json"
    found = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    aranan = fonlar - set(found)  # önbellekte olmayan fonlar için KAP'a sorulur
    if not aranan:
        return found
    end = ARAMA_BITIS
    while end >= ARAMA_BASLANGIC and not aranan <= set(found):
        start = end - dt.timedelta(days=6)
        body = {"fromDate": start.isoformat(), "toDate": end.isoformat(), "fundTypeList": ["YF"],
                "mkkMemberOidList": [], "fundOidList": [], "passiveFundOidList": [], "disclosureClass": "DG",
                "isLate": "", "subjectList": [PORTFOY_DAGILIM_RAPORU], "discIndex": [], "fromSrc": False, "srcCategory": ""}
        for x in sorted(json.loads(_request(f"{API}/disclosure/funds/byCriteria", body)), key=lambda x: -x["disclosureIndex"]):
            if x["fundCode"] in aranan and x["fundCode"] not in found:
                found[x["fundCode"]] = {k: x[k] for k in ("disclosureIndex", "publishDate", "ruleType")}
        end = start - dt.timedelta(days=1)
        time.sleep(8)
    CACHE.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(found, ensure_ascii=False, indent=1), encoding="utf-8")
    return found


def rapor_metni(kod, bildirim_no):
    pdf, txt = CACHE / f"{kod}.pdf", CACHE / f"{kod}.txt"
    if not txt.exists():
        if not pdf.exists():
            detail = json.loads(_request(f"{API}/notification/attachment-detail/{bildirim_no}"))
            ekler = detail[0].get("attachments") or []
            url = f"{API}/file/download/{ekler[0]['objId']}" if ekler else f"{API}/BildirimPdf/{bildirim_no}"
            pdf.write_bytes(_request(url))
            time.sleep(3)
        subprocess.run(["pdftotext", "-layout", str(pdf), str(txt)], check=True, capture_output=True)
    return txt.read_text(encoding="utf-8", errors="ignore")


def _sayi(s):
    """'1.234,56' (TR) veya '1,234.56' (US) biçimindeki sayıyı çevirir."""
    if re.fullmatch(r"-?\d{1,3}(\.\d{3})*,\d+", s):
        return float(s.replace(".", "").replace(",", "."))
    return float(s.replace(",", ""))


def net_varlik(metin):
    for pat in (r"Net Varl[ıi]k De[ğg]eri\s*:\s*([\d.,]+)", r"FON TOPLAM DE[ĞG]ER[İI]\s+([\d.,]+)"):
        if m := re.search(pat, metin, re.I):
            return _sayi(m.group(1))
    raise ValueError("net varlık değeri bulunamadı")


def listedeki_fon_paylari(kod, metin, nav, listedeki):
    """Tutulan listedeki fon kodu -> fon toplam değerine oranı (0-1)."""
    oranlar = {}
    for line in metin.splitlines():
        m = re.match(r"^\s*([A-Z0-9]{3})\s+(.*\S)\s*$", line)
        if not m or m.group(1) not in listedeki or m.group(1) == kod:
            continue
        if atlas := re.search(r"([\d,]+\.\d+)\s+-?[\d.]+%$", m.group(2)):  # ... rayiç değer  %FPD
            oran = _sayi(atlas.group(1)) / nav
        elif tera := re.search(r"(-?[\d.]+,\d+)\s+(-?[\d.]+,\d+)\s+(-?[\d.]+,\d+)$", m.group(2)):  # ... grup% FPD% FTD%
            oran = _sayi(tera.group(3)) / 100
        else:
            raise ValueError(f"{kod}: satır ayrıştırılamadı: {line.strip()[:100]}")
        oranlar[m.group(1)] = oranlar.get(m.group(1), 0) + oran
    return oranlar


def main():
    listedeki = {r["fon_kodu"] for r in load_detay()}
    fonlar = fon_payi_tutanlar()
    raporlar = son_raporlar(set(fonlar))
    rows = []
    for kod in fonlar:
        r = raporlar.get(kod)
        if not r:
            rows.append([kod, "rapor_yok", "", "", "", "", "", ""])
            continue
        metin = rapor_metni(kod, r["disclosureIndex"])
        bilgi = [r["ruleType"], r["publishDate"][:10], r["disclosureIndex"]]
        if "muaftır" in metin:  # II-14.2 md.19/2: nitelikli yatırımcı fonları rapor yayımlamaz
            rows.append([kod, "muaf", *bilgi, "", "", ""])
            continue
        nav = net_varlik(metin)
        paylar = listedeki_fon_paylari(kod, metin, nav, listedeki)
        bilgi.append(round(nav, 2))
        rows += [[kod, "rapor", *bilgi, c, round(o, 6)] for c, o in sorted(paylar.items())] or [[kod, "rapor", *bilgi, "", 0]]
    write_csv(config.KAP_FON_PAYLARI, ["fon_kodu", "durum", "rapor_donemi", "yayin_tarihi", "kap_bildirim_no",
                                       "rapor_net_varlik_tl", "tutulan_fon_kodu", "oran"], rows)
    print(f"{len(fonlar)} fon payı tutan fon -> {config.KAP_FON_PAYLARI.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
