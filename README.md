# BrewScope

BrewScope adalah proyek *Aspect-Based Sentiment Analysis* (ABSA) untuk
memetakan prioritas strategis coffee shop di Jatinangor berdasarkan ulasan
pelanggan.

Baseline labeling yang berlaku berada di [`labeling/`](labeling/).
Folder tersebut merupakan snapshot tetap dan tidak boleh diubah tanpa keputusan
metodologi baru.

## Status proyek

- 3.538 review dari 40 coffee shop tercakup.
- Setiap review memiliki keputusan untuk enam aspek aktif.
- Total 21.228 pasangan review-aspek telah dibuat.
- Label merupakan pre-anotasi leksikal offline, bukan human gold.
- Seluruh record masih `draft` atau `uncertain` dan
  `training_eligible=false` sampai selesai human review.

## Struktur repository

```text
.
|-- data/
|   |-- raw/
|   |   `-- google_maps_reviews_jatinangor_raw.csv
|   `-- interim/
|       |-- google_maps_places_jatinangor.csv
|       `-- reviews_for_annotation.csv
|-- scripts/
|   `-- scrape_google_maps.py    # Akuisisi review melalui Apify
|-- labeling/                   # Baseline labeling tetap
|   |-- config/                 # Schema dan taksonomi
|   |-- docs/                   # Pedoman anotasi
|   |-- scripts/                # Labeler dan validator
|   |-- data/
|   |   |-- canonical/          # Sumber anotasi kanonis
|   |   |-- tabular/            # Proyeksi CSV dan lookup
|   |   `-- review/             # Paket dan antrean human review
|   |-- reports/                # QA, coverage, diagnostic, checksum
|   `-- README.md
|-- PROJECT_CONTEXT.md
|-- .env.example
|-- pyproject.toml
`-- README.md
```

## Scraping Google Maps

Salin `.env.example` menjadi `.env`, lalu isi `APIFY_TOKEN` milik Anda. Jangan
memasukkan `.env` ke Git. Daftar URL coffee shop berada di
`data/interim/google_maps_places_jatinangor.csv`.

Periksa konfigurasi tanpa menjalankan Actor atau memakai kredit:

```powershell
python scripts/scrape_google_maps.py
```

Jalankan scraping nyata:

```powershell
python scripts/scrape_google_maps.py --run
```

Program meminta konfirmasi `JALANKAN` sebelum menghubungi Apify. Hasilnya ditulis
ke `data/raw/google_maps_reviews_jatinangor_raw.csv`. Scraping nyata memakai
kuota/kredit akun Apify.

## Artefak utama

- `labeling/data/canonical/annotations_full.jsonl`: satu record kanonis untuk setiap
  kombinasi review, aspek, dan annotator otomatis.
- `labeling/data/tabular/annotations_flat.csv`: representasi tabular 21.228 record.
- `labeling/data/tabular/review_level_summary.csv`: satu baris per review.
- `labeling/data/review/manual_review_queue.csv`: 1.891 review yang diprioritaskan
  untuk pemeriksaan manusia.
- `labeling/data/review/blind_human_review_pack.csv`: formulir human review tanpa
  rating, label otomatis, atau flag.
- `labeling/reports/SHA256SUMS.txt`: checksum artefak labeling.

## Validasi

Siapkan environment lalu jalankan validator read-only:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python labeling/scripts/validate_annotations.py `
  --input labeling/data/canonical/annotations_full.jsonl `
  --schema labeling/config/annotation_schema.json
```

Hasil baseline saat ini: 21.228 record, 3.538 review, dan 0 error schema,
keunikan aspek, maupun evidence offset.

`labeling/scripts/label_brewscope.py` dipertahankan apa adanya sebagai provenance
snapshot dari environment pembentukan pre-anotasi. Gunakan
`labeling/data/canonical/annotations_full.jsonl` sebagai
sumber kebenaran labeling saat ini.

## Tahap berikutnya

Human review dilakukan dari prioritas HIGH, MEDIUM, LOW, lalu audit acak pada
record di luar antrean. Hanya label yang telah direview dan disepakati yang
boleh dipromosikan menjadi dataset training. Modeling akan membandingkan SVM,
Random Forest, dan Multinomial Naive Bayes untuk deteksi aspek, klasifikasi
sentimen, dan penyusunan insight bisnis per coffee shop.
