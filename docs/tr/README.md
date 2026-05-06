# Bluearf Nova API, CLI ve Codex Plugin Kullanım Rehberi

Bu doküman Bluearf Nova Public API, Python SDK, `bluearf` CLI ve Codex plugin
kullanımı için müşteri odaklı Türkçe rehberdir.

## 1. Kurulum

Python SDK:

```bash
pip install bluearf-nova
```

Bu repodan lokal çalıştırma:

```bash
cd python
python3 -m pip install -e .
```

API anahtarını ortam değişkeni olarak verin:

```bash
export BLUEARF_NOVA_API_KEY="..."
export BLUEARF_NOVA_LANGUAGE="tr"
```

Varsayılan API adresi `https://api.bluearf.com/v1` olur. Farklı ortam için
yalnızca gerekirse `BLUEARF_NOVA_API_URL` kullanın.

`BLUEARF_NOVA_API_TOKEN` eski uyumluluk için kabul edilir. Yeni kurulumlarda
`BLUEARF_NOVA_API_KEY` kullanın.

## 2. Hızlı Kontrol

```bash
bluearf credits get
bluearf usage list --days 7 --limit 25
bluearf companies list
```

Yanıtlar varsayılan olarak Türkçe döner. İngilizce için:

```bash
bluearf --language en credits get
```

## 3. Erişilebilir Verileri Sorgulama

Şirketler:

```bash
bluearf companies list
```

Araçlar:

```bash
bluearf vehicles list --company-id COMPANY_ID --source binek_ticari_araclar --limit 25
```

Araç marka/model referansları:

```bash
bluearf vehicle-models search --brand Toyota --model Corolla --limit 10
```

Karbon kayıtları:

```bash
bluearf carbon-records list --company-id COMPANY_ID --year 2024 --source "Binek ve Ticari Araçlar"
```

Uniform karbon kayıtları:

```bash
bluearf carbon-uniform list --company-id COMPANY_ID --coid COID --year 2024
```

API ham Firestore dokümanı döndürmez; dış kullanıcıya güvenli ve sınırlandırılmış
alanlar döner. Erişim `readAccessIds` ve API anahtar scope'u ile sınırlıdır.

## 4. Kayıt Yapmadan Binek ve Ticari Araç Hesaplama

`calculations passenger-commercial-vehicles` kayıt oluşturmaz. Sadece emisyon
önizlemesi döndürür.

```bash
bluearf calculations passenger-commercial-vehicles \
  --company-id COMPANY_ID \
  --coid COID \
  --year 2024 \
  --input examples/passenger_commercial_rows.tr.json
```

Örnek JSON:

```json
{
  "rows": [
    {
      "vehicleName": "Servis-01",
      "ownershipType": "Şirket Aracı",
      "vehicleType": "Otomobil",
      "fuelTypeName": "Dizel",
      "fuelConsumption": 120,
      "fuelUnit": "Litre",
      "invoiceDate": "2024-03-15"
    }
  ]
}
```

Sonuç `carbonDataPreview` benzeri hesaplama çıktısı döndürür; `carbonData`,
`vehicleData` veya `CarbonDataUniform` yazmaz.

## 5. Nova Runs ile Dosya Pipeline'ı

Nova Runs dosya yükleme, sütun eşleştirme, değer eşleştirme, akıllı sorular ve
güvenliyse kayıt adımlarını backend-first çalıştırır.

1. Upload URL oluşturun:

```bash
bluearf uploads create \
  --company-id COMPANY_ID \
  --source binek_ticari_araclar \
  --year 2024 \
  --filename fleet.xlsx \
  --content-type application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
```

2. Dönen signed upload URL'ye dosyayı yükleyin:

```bash
curl -X PUT \
  -H "Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" \
  --upload-file fleet.xlsx \
  "SIGNED_UPLOAD_URL"
```

3. Run başlatın:

```bash
bluearf nova-runs create \
  --company-id COMPANY_ID \
  --source binek_ticari_araclar \
  --coid FACILITY_ID \
  --year 2024 \
  --file-id FILE_ID \
  --auto-column-match \
  --auto-enrich \
  --auto-safe-save
```

Otomasyon seçenekleri:

- `--auto-column-match`: Güvenliyse sütun eşleştirme adımını otomatik geçer.
- `--auto-enrich`: Nova Assist ile eksik değerleri yüksek güvenle tamamlar, düşük güveni kullanıcıya bırakır.
- `--auto-safe-save`: Blocker yoksa kayıt adımını da otomatik tamamlar. Bu seçenek `--auto-enrich` açık kabul edilir.

Run durumunu takip edin:

```bash
bluearf nova-runs get --run-id RUN_ID
bluearf nova-runs export --run-id RUN_ID --limit 100
```

## 6. Akıllı Sorular

Run güvenli ilerleyemediğinde Nova kullanıcıya kısa sorular üretebilir. Soruları
listeleyin:

```bash
bluearf nova-runs questions --run-id RUN_ID --status pending
```

Bir soruyu yanıtlayın:

```bash
bluearf nova-runs answer-question \
  --run-id RUN_ID \
  --question-id QUESTION_ID \
  --answer "Şirket Aracı"
```

Bir soruyu atlayın:

```bash
bluearf nova-runs skip-question --run-id RUN_ID --question-id QUESTION_ID
```

Kalan tüm soruları atlayın:

```bash
bluearf nova-runs skip-question --run-id RUN_ID --remaining
```

Cevaplanan sorular run verisine uygulanır. Atlanan sorular veri yazmaz.

## 7. Python SDK

```python
import os
from bluearf_nova import BluearfNova

client = BluearfNova(api_key=os.environ["BLUEARF_NOVA_API_KEY"], language="tr")

credits = client.credits.get()
companies = client.companies.list()
vehicles = client.vehicles.list(company_id="COMPANY_ID", limit=25)

preview = client.calculations.passenger_commercial_vehicles(
    company_id="COMPANY_ID",
    coid="COID",
    year=2024,
    rows=[
        {
            "vehicleName": "Servis-01",
            "ownershipType": "Şirket Aracı",
            "vehicleType": "Otomobil",
            "fuelTypeName": "Dizel",
            "fuelConsumption": 120,
            "fuelUnit": "Litre",
            "invoiceDate": "2024-03-15",
        }
    ],
)
```

## 8. Codex Plugin

Plugin klasörü:

```text
plugins/bluearf-nova
```

Codex içinde kullanılmadan önce API key ortamda olmalı:

```bash
export BLUEARF_NOVA_API_KEY="..."
```

Kontrol:

```bash
plugins/bluearf-nova/scripts/check-bluearf-nova
plugins/bluearf-nova/scripts/bluearf-nova credits get
```

Codex plugin API anahtarını saklamaz; sadece ortam değişkeninden okur.

## 9. Kredi Mantığı

Krediler endpoint ve iş yüküne göre hesaplanır. Liste endpointleri sayfa
büyüklüğü ve dönen satır sayısına göre, hesaplama endpointleri input/output
satır birimlerine göre ücretlenir. Backend hatalarında harcama iade edilir.

Kredi ve kullanım kontrolü:

```bash
bluearf credits get
bluearf usage list --days 30 --limit 100
```

## 10. Hata Formatı

Hatalar standart JSON formatında döner:

```json
{
  "error": {
    "type": "authentication_error",
    "code": "authentication_failed",
    "message": "Invalid or missing Bluearf API token"
  },
  "request_id": "..."
}
```

Token veya yetki hatasında API anahtarını loglamayın veya paylaşmayın.
