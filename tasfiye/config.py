"""Yollar, veri tarihi ve TEFAS alan sözlükleri."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
CHARTS = ROOT / "output" / "grafikler"

SPK_PDF_ILK = RAW / "spk_bulten_2026-60.pdf"       # ilk duyuru (130 fon)
SPK_PDF = RAW / "spk_bulten_2026-61.pdf"           # güncel liste (131 fon)
TEFAS_GENEL = RAW / "tefas_genel_20260916.txt"
TEFAS_DAGILIM = RAW / "tefas_dagilim_20260916.txt"
KAP_FON_PAYLARI = RAW / "kap_fon_paylari.csv"

FON_LISTESI = PROCESSED / "fon_listesi.csv"
FON_DETAY = PROCESSED / "tasfiye_fonlar_detay.csv"
FON_DAGILIM = PROCESSED / "tasfiye_fonlar_dagilim.csv"

VERI_TARIHI = "16.09.2026"

# portföy dağılımında fon payı kalemleri: yatırım fonu, borsa yatırım fonu, girişim sermayesi fonu
FON_PAYI_ALANLARI = ("yyf", "byf", "gsykb")

# tefas_genel dosyasındaki tur_idx -> TEFAS şemsiye fon türü
SEMSIYE_TURLERI = [
    "Serbest Şemsiye Fonu", "Para Piyasası Şemsiye Fonu", "Hisse Senedi Şemsiye Fonu",
    "Borçlanma Araçları Şemsiye Fonu", "Kıymetli Madenler Şemsiye Fonu", "Değişken Şemsiye Fonu",
    "Katılım Şemsiye Fonu", "Fon Sepeti Şemsiye Fonu",
]

# TEFAS portföy dağılımı alan kodları -> TEFAS "Listeleme Ayarları" sütun etiketleri
VARLIK_ETIKETLERI = {
    "hs": "Hisse Senedi", "dt": "Devlet Tahvili", "hb": "Hazine Bonosu", "fb": "Finansman Bonosu",
    "ost": "Özel Sektör Tahvili", "vdm": "Varlığa Dayalı Menkul Kıymetler", "kba": "Kamu Dış Borçlanma Araçları",
    "osdb": "Özel Sektör Dış Borçlanma Araçları", "kkstl": "Kamu Kira Sertifikaları (TL)",
    "osks": "Özel Sektör Kira Sertifikaları", "tr": "Ters-Repo", "r": "Repo",
    "btas": "BİST Taahhütlü İşlem Pazarı Satım", "tpp": "Takasbank Para Piyasası",
    "bpp": "Borsa İstanbul Para Piyasası", "vmd": "Mevduat (Döviz)", "vmtl": "Mevduat (TL)",
    "khd": "Katılma Hesabı (Döviz)", "khtl": "Katılma Hesabı (TL)", "km": "Kıymetli Madenler",
    "ybyf": "Yabancı Borsa Yatırım Fonları", "yhs": "Yabancı Hisse Senedi",
    "byf": "Borsa Yatırım Fonları Katılma Payları", "yyf": "Yatırım Fonları Katılma Payları",
    "vint": "Vadeli İşlemler Nakit Teminatları", "d": "Diğer",
    "gsykb": "Girişim Sermayesi Yatırım Fonu Katılma Payları",
}
