# BrewScope

BrewScope adalah proyek *Aspect-Based Sentiment Analysis* (ABSA) berbasis
Traditional Machine Learning untuk mengidentifikasi prioritas strategis coffee
shop di Jatinangor dari ulasan pelanggan Google Maps.

## Status proyek

Pipeline telah selesai sampai tahap insight bisnis:

| Tahap | Status |
|---|---|
| Akuisisi Google Maps | Selesai |
| Pseudo-labeling enam aspek | Selesai |
| Text preprocessing | Selesai dan tervalidasi |
| Train/validation/test splitting | Selesai dan bebas group leakage |
| Modeling SVM, Random Forest, dan Multinomial Naive Bayes | Selesai |
| Penyusunan insight bisnis | Selesai |

Model terpilih: SVM untuk Task A (macro-F1 test 0.8775) dan Random Forest
per-aspek untuk Task B (pooled macro-F1 test 0.7013). Ringkasan hasil lengkap:
`RESULTS.md`.

Ringkasan data aktif:

- 3.538 review dari 40 coffee shop;
- 21.228 pasangan review-aspek pada sumber labeling;
- 3.537 review memiliki teks yang eligible untuk modeling;
- 3.424 baris Task A — aspect detection;
- 5.598 baris Task B — aspect sentiment classification;
- split review: 2.396 train, 514 validation, dan 514 test;
- tidak ada review atau duplicate group yang bocor antar-split;
- seluruh label positif Task A dan seluruh kombinasi aspek-sentimen Task B
  terwakili pada ketiga split.

Label merupakan pseudo-label AI berbasis aturan leksikal yang telah disetujui
tim dan dosen untuk digunakan pada modeling. Label tersebut bukan human gold.
Provenance tetap disimpan pada manifest, sedangkan metadata labeling tidak
menjadi kolom dataset model-ready.

## Persiapan environment

Gunakan virtual environment proyek:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[preprocessing,modeling]"
```

Salin `.env.example` menjadi `.env` dan isi `APIFY_TOKEN` hanya jika scraping
akan dijalankan ulang. Jangan memasukkan `.env` ke Git.

## Urutan pipeline

```text
Google Maps place URLs
        |
        v
scripts/scrape_google_maps.py
        |
        v
google_maps_reviews_jatinangor_raw.csv
        |
        v
reviews_for_annotation.csv
        |
        v
scripts/label_brewscope.py
        |
        v
canonical pseudo-labeling
        |
        v
notebooks/01_preprocessing.ipynb
        |
        v
model-ready Task A dan Task B
        |
        v
notebooks/02_data_splitting.ipynb
        |
        v
fixed train / validation / test split
        |
        v
notebooks/03_modeling_all_models.ipynb
        |
        v
artefak model MNB, SVM, dan Random Forest
        |
        v
notebooks/04_business_insights.ipynb
        |
        v
insight bisnis per coffee shop dan RESULTS.md
```

Jika artefak sumber tidak berubah, rekan yang melanjutkan modeling tidak perlu
menjalankan scraping atau labeling ulang. Gunakan hasil splitting yang sudah
tersedia.

## Notebook aktif

### 1. Text preprocessing

Jalankan `notebooks/01_preprocessing.ipynb` terlebih dahulu. Notebook ini:

- mempertahankan teks mentah;
- membersihkan Unicode, HTML, URL, email, telepon, emoji, emoticon, slang, dan
  karakter berulang;
- mempertahankan negasi dan intensifier;
- menyediakan varian angka asli dan `numtoken`;
- memisahkan stemming-only dari stopword-removal + stemming;
- membuat duplicate group konservatif untuk pencegahan leakage;
- menjalankan preprocessing contract tests;
- membuat tabel, grafik, dan Word Cloud 300 DPI;
- mengekspor dataset gabungan serta enam dataset sentimen per aspek.

Varian teks yang tersedia:

- `text_clean` — baseline dengan `numtoken`;
- `text_numbers_preserved`;
- `text_negation`;
- `text_no_stopwords`;
- `text_stemmed` — stemming tanpa stopword removal;
- `text_no_stopwords_stemmed`;
- `text_model` — alias baseline aktif.

### 2. Data splitting

Setelah preprocessing berhasil, jalankan `notebooks/02_data_splitting.ipynb`.
Notebook ini membuat split 70%/15%/15% menggunakan greedy multi-start
group-aware stratification dengan `random_state=42` dan 50 percobaan.

Assignment yang dihasilkan wajib digunakan oleh seluruh algoritma. Jangan
membuat split baru untuk setiap model.

### 3. Modeling

`notebooks/03_modeling_all_models.ipynb` melatih dan mengevaluasi Multinomial
Naive Bayes, SVM, dan Random Forest untuk Task A dan Task B pada split yang
sama. Artefak (model, vectorizer, metrik, prediksi, manifest) tersimpan di
`data/processed/modeling/{mnb,svm,rf}/` dan `reports/{tables,figures}/modeling/`.

### 4. Insight bisnis

`notebooks/04_business_insights.ipynb` memuat model terpilih dan menghitung
agregasi per coffee shop: mention aspek, distribusi sentimen, kekuatan,
keluhan, dan prioritas perbaikan (minimum support 3 mention). Notebook ini
juga menulis `RESULTS.md` - dokumen hasil lengkap untuk penulisan paper.
Output lain: `data/processed/insights/` dan `reports/{tables,figures}/insights/`.

## Artefak utama

### Labeling canonical

- `data/processed/labeling/annotations_full.jsonl`
- `data/processed/labeling/annotations_flat.csv`
- `data/processed/labeling/review_level_summary.csv`
- `reports/labeling/qa_report.json`

### Preprocessing dan model-ready data

- `data/processed/modeling/reviews_preprocessed.csv` — master audit teks;
- `data/processed/modeling/aspect_detection_dataset.csv` — Task A;
- `data/processed/modeling/aspect_sentiment_dataset.csv` — Task B gabungan;
- `data/processed/modeling/aspect_sentiment_by_aspect/*.csv` — enam dataset
  Task B untuk classifier terpisah per aspek;
- `data/processed/modeling/preprocessing_manifest.json`.

### Fixed split

- `data/processed/modeling/splits/split_assignments.csv`;
- `data/processed/modeling/splits/aspect_detection_with_split.csv`;
- `data/processed/modeling/splits/aspect_sentiment_with_split.csv`;
- `data/processed/modeling/splits/split_manifest.json`.

File yang langsung digunakan untuk modeling adalah dua file `*_with_split.csv`.

### Insight bisnis

- `data/processed/insights/task_a_predictions_all.csv`;
- `data/processed/insights/task_b_predictions_all.csv`;
- `data/processed/insights/insights_manifest.json`;
- `reports/tables/insights/*.csv` - mention, sentimen, kekuatan/keluhan, prioritas;
- `reports/figures/insights/*.png`;
- `RESULTS.md` - dokumen hasil lengkap untuk penulisan paper.

## Kontrak modeling

Task A adalah klasifikasi multi-label enam aspek pada tingkat review. Task B
adalah klasifikasi sentimen `negative`, `neutral`, atau `positive` pada pasangan
review-aspek.

Aturan yang wajib dipertahankan:

1. gunakan kolom `split` yang sudah tersedia;
2. fit TF-IDF atau CountVectorizer hanya pada train;
3. terapkan class weighting atau resampling hanya pada train;
4. gunakan classifier terpisah per aspek sebagai baseline utama Task B;
5. gunakan `aspect_text_model` untuk baseline model gabungan pembanding;
6. jangan menggunakan ID, nama coffee shop, rating, atau metadata labeling
   sebagai fitur teks;
7. bandingkan SVM, Random Forest, dan Multinomial Naive Bayes pada split yang
   sama;
8. simpan konfigurasi, seed, vectorizer, model, metrik, dan prediksi setiap
   eksperimen.

Metrik minimum:

- Task A: macro-F1, micro-F1, precision/recall/F1 per aspek, dan support;
- Task B: macro-F1, weighted-F1, recall kelas negatif, confusion matrix, dan
  metrik per aspek;
- accuracy boleh dilaporkan, tetapi tidak boleh menjadi satu-satunya metrik.

## Scraping ulang

Periksa konfigurasi tanpa menggunakan kredit Apify:

```powershell
python scripts/scrape_google_maps.py
```

Jalankan scraping nyata:

```powershell
python scripts/scrape_google_maps.py --run
```

Program meminta konfirmasi `JALANKAN`. Output ditulis ke
`data/raw/google_maps_reviews_jatinangor_raw.csv`.

## Struktur ringkas repository

```text
configs/labeling/                   # Schema dan taksonomi aspek
data/raw/                           # Hasil scraping mentah
data/interim/                       # Input anotasi dan audit labeling
data/processed/labeling/            # Sumber canonical pseudo-label
data/processed/modeling/            # Preprocessing, Task A, dan Task B
data/processed/modeling/splits/     # Fixed split untuk seluruh model
data/processed/insights/            # Prediksi dan manifest insight
docs/annotation/                    # Pedoman labeling
notebooks/01_preprocessing.ipynb    # Text preprocessing
notebooks/02_data_splitting.ipynb   # Leakage-safe splitting
notebooks/03_modeling_all_models.ipynb  # MNB, SVM, dan Random Forest
notebooks/04_business_insights.ipynb    # Insight bisnis dan RESULTS.md
reports/labeling/                   # QA labeling
reports/figures/                    # Visual paper-ready
reports/tables/                     # Tabel paper-ready
scripts/                            # Scraping, labeling, dan validator
PROJECT_CONTEXT.md                  # Keputusan metodologis aktif
RESULTS.md                          # Hasil analisis lengkap
pyproject.toml                      # Dependency proyek
```

Detail keputusan metodologis dan handoff terdapat di `PROJECT_CONTEXT.md`.
