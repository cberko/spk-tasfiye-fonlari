# SPK 2026/60: Tasfiye Edilecek Fonlar

SPK'nın 17.09.2026 tarihli 2026/60 sayılı bülteninde tasfiyesine karar verilen yatırım fonlarının analizi.
Karar Tera, Pusula, Hedef, Atlas, A1 Capital, Pardus ve Bulls portföy şirketlerinin 130 fonunu kapsıyor.
Fon büyüklükleri ve portföy dağılımları TEFAS'ın **16.09.2026** verisinden alındı.

## Sonuçlar

| | |
|---|---|
| Tasfiye edilecek fon | 130 (128'i TEFAS verisiyle) |
| Toplam fon büyüklüğü (net varlık) | **842,7 milyar TL** |
| Brüt varlık | 883,0 milyar TL |
| Kaldıraç borcu (32 fon) | 40,3 milyar TL |
| Hisse senedi | 480,5 milyar TL |

![Fon tipine göre](output/grafikler/1_fon_tipine_gore_tasfiye.png)
![Varlık türüne göre](output/grafikler/2_varlik_turune_gore_tasfiye.png)
![Portföy şirketine göre](output/grafikler/3_portfoy_sirketine_gore_tasfiye.png)

## Kurulum ve çalıştırma

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m tasfiye          # tüm akış
.venv/bin/python -m tasfiye.plots    # yalnızca grafikler
```

PDF'ten fon listesini çıkarmak için `pdftotext` gerekir (`brew install poppler`).

## Akış

| Adım | Modül | Girdi | Çıktı |
|---|---|---|---|
| 1 | `tasfiye.extract` | `data/raw/spk_bulten_2026-60.pdf` | `fon_listesi.csv` |
| 2 | `tasfiye.dataset` | fon listesi + `tefas_genel_20260916.txt` | `tasfiye_fonlar_detay.csv`, `ozet_fon_tipi.csv`, `ozet_semsiye_fon_turu.csv`, `ozet_sirket_grubu.csv` |
| 3 | `tasfiye.allocation` | detay + `tefas_dagilim_20260916.txt` | `tasfiye_fonlar_dagilim.csv`, `ozet_varlik_dagilimi.csv` |
| 4 | `tasfiye.plots` | işlenmiş veriler | `output/grafikler/*.png` |

## Veri kaynakları ve notlar

- **TEFAS verisi ham snapshot olarak repoda duruyor.** TEFAS bot koruması arkasında olduğu için veri tarayıcı üzerinden
  `api/funds/fonGnlBlgSiraliGetir` (genel bilgiler) ve `api/funds/dagilimSiraliGetirT` (portföy dağılımı) uç noktalarından çekildi.
  Kod bu dosyaları okur, TEFAS'a bağlanmaz.
- **Fon eşleştirme:** SPK listesindeki unvanlar TEFAS unvanlarıyla eşleştirildi. `tefas_genel` dosyası SPK listesindeki sıra numarasıyla bağlanır.
- **TEFAS'ta olmayan fonlar:** Hedef Portföy İnci Hisse Senedi Serbest Özel Fon (HIN) ve Hedef Portföy İkinci Para Piyasası (TL) Fon (HPP)
  16.09 listesinde yok; 15.09'da büyüklükleri 0 TL.
- **Şemsiye fon türü**, fonun bağlı olduğu şemsiye fonun TEFAS kategorisidir. **Fon tipi** ise grafikler için şemsiye türü ve unvandan türetilen sınıflamadır.
- **Kaldıraç:** Portföy dağılımında repo ve para piyasası borçları negatif yüzde olarak gelir.
  Varlık grafiği brüt tutarı gösterir; borç düşülünce toplam, fon büyüklüğüne (842,7 mlr TL) eşitlenir.
- A1 Capital ve Pardus portföy şirketleri raporlamada tek grup olarak ele alındı.
- `gsykb` alanının TEFAS arayüzünde etiketi yok; "Girişim Sermayesi Yatırım Fonu Katılma Payları" olarak yorumlandı (0,5 mlr TL).
