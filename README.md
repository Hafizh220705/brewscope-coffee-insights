# BrewScope

BrewScope adalah proyek *Aspect-Based Sentiment Analysis* (ABSA) untuk
memetakan prioritas strategis coffee shop di Jatinangor berdasarkan ulasan
pelanggan.

Artefak baseline labeling ditempatkan menurut fungsinya di `configs/`, `data/`,
`docs/`, `reports/`, dan `scripts/`. Dataset label tetap tidak boleh diubah tanpa
keputusan metodologi baru.

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
|-- configs/
|   `-- labeling/               # Schema dan taksonomi aspek
|-- data/
|   |-- raw/
|   |   `-- google_maps_reviews_jatinangor_raw.csv
|   |-- interim/
|   |   |-- google_maps_places_jatinangor.csv
|   |   |-- reviews_for_annotation.csv
|   |   `-- labeling_review/    # Paket dan antrean human review
|   `-- processed/
|       `-- labeling/           # Anotasi kanonis dan proyeksi tabular
|-- docs/
|   `-- annotation/             # Pedoman dan dokumentasi labeling
|-- reports/
|   `-- labeling/               # QA, coverage, diagnostic, checksum
|-- scripts/
|   |-- scrape_google_maps.py   # Akuisisi review melalui Apify
|   |-- label_brewscope.py      # Generator pre-anotasi leksikal
|   `-- validate_annotations.py # Validator labeling
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

- `data/processed/labeling/annotations_full.jsonl`: satu record kanonis untuk
  setiap kombinasi review, aspek, dan annotator otomatis.
- `data/processed/labeling/annotations_flat.csv`: representasi tabular 21.228 record.
- `data/processed/labeling/review_level_summary.csv`: satu baris per review.
- `data/interim/labeling_review/manual_review_queue.csv`: 1.891 review yang diprioritaskan
  untuk pemeriksaan manusia.
- `data/interim/labeling_review/blind_human_review_pack.csv`: formulir human review tanpa
  rating, label otomatis, atau flag.
- `reports/labeling/SHA256SUMS.txt`: checksum artefak labeling.

## Validasi

Siapkan environment lalu jalankan validator read-only:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python scripts/validate_annotations.py
```

Hasil baseline saat ini: 21.228 record, 3.538 review, dan 0 error schema,
keunikan aspek, maupun evidence offset.

`scripts/label_brewscope.py` menggunakan path proyek secara otomatis dan berjalan
dalam preview mode secara default:

```powershell
python scripts/label_brewscope.py
```

Gunakan `--execute` untuk menulis hasil dan `--overwrite` hanya jika memang ingin
mengganti baseline yang sudah ada. `data/processed/labeling/annotations_full.jsonl`
tetap menjadi sumber kebenaran labeling saat ini.

## Tahap berikutnya

Human review dilakukan dari prioritas HIGH, MEDIUM, LOW, lalu audit acak pada
record di luar antrean. Hanya label yang telah direview dan disepakati yang
boleh dipromosikan menjadi dataset training. Modeling akan membandingkan SVM,
Random Forest, dan Multinomial Naive Bayes untuk deteksi aspek, klasifikasi
sentimen, dan penyusunan insight bisnis per coffee shop.
