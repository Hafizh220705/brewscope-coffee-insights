# Konteks Proyek BrewScope

Dokumen ini adalah konteks kerja aktif per 1 November 2026. Pipeline yang
berlaku telah selesai sampai preprocessing dan leakage-safe data splitting.
Tahap berikutnya adalah modeling oleh anggota tim berikutnya.

Jika terdapat instruksi lama yang mewajibkan human review sebelum modeling,
gunakan keputusan terbaru di dokumen ini: pseudo-label AI telah dibahas dengan
dosen dan disetujui untuk modeling tanpa human verification tambahan. Label
tetap harus dilaporkan sebagai pseudo-label, bukan human gold.

## 1. Tujuan penelitian

BrewScope menggunakan Aspect-Based Sentiment Analysis untuk mengubah ulasan
Google Maps menjadi informasi prioritas bisnis coffee shop di Jatinangor.

Hasil akhir yang dituju:

1. mendeteksi aspek yang disebut pada setiap review;
2. mengklasifikasikan sentimen per aspek;
3. membandingkan SVM, Random Forest, dan Multinomial Naive Bayes;
4. mengidentifikasi kekuatan dan kelemahan setiap coffee shop;
5. menyusun prioritas perbaikan berdasarkan sentimen dan dukungan data.

Judul kerja paper:

> Strategic Prioritization of Jatinangor Coffee Shops Using Comparative
> Machine Learning-Based ABSA

## 2. Status pipeline

| Tahap | Status | Artefak utama |
|---|---|---|
| Akuisisi review Google Maps | Selesai | `data/raw/` |
| Pseudo-labeling ABSA | Selesai | `data/processed/labeling/` |
| Text preprocessing | Selesai dan tervalidasi | `notebooks/01_preprocessing.ipynb` |
| Data splitting | Selesai dan bebas leakage | `notebooks/02_data_splitting.ipynb` |
| Modeling komparatif | Belum | Handoff berikutnya |
| Insight bisnis dan paper | Belum | Setelah evaluasi model |

Kedua notebook terakhir telah dijalankan seluruhnya tanpa error. Hash seluruh
artefak cocok dengan manifest masing-masing.

## 3. Data aktif

### 3.1 Sumber dan labeling

| Data | Nilai |
|---|---:|
| Review awal | 3.538 |
| Coffee shop | 40 |
| Aspek aktif | 6 |
| Pasangan review-aspek canonical | 21.228 |
| Status `draft` pada sumber | 20.905 |
| Status `uncertain` pada sumber | 323 |
| Mixed sentiment pada sumber | 76 |

Sumber yang dipertahankan:

- `data/raw/google_maps_reviews_jatinangor_raw.csv`;
- `data/interim/google_maps_places_jatinangor.csv`;
- `data/interim/reviews_for_annotation.csv`;
- `data/processed/labeling/annotations_full.jsonl`;
- `data/processed/labeling/annotations_flat.csv`;
- `data/processed/labeling/review_level_summary.csv`.

### 3.2 Setelah preprocessing

| Data | Nilai |
|---|---:|
| Review pada master preprocessing | 3.538 |
| Review eligible untuk modeling | 3.537 |
| Review dikeluarkan karena teks unsupported | 1 |
| Task A — aspect detection | 3.424 |
| Task B — aspect sentiment | 5.598 |
| Duplicate group eligible | 3.287 |

Jumlah pasangan Task B per aspek:

| Aspek | Baris |
|---|---:|
| `product_quality` | 1.651 |
| `service` | 937 |
| `price_value` | 464 |
| `ambience` | 2.048 |
| `facilities` | 317 |
| `cleanliness` | 181 |

### 3.3 Fixed split

| Split | Review | Persentase |
|---|---:|---:|
| Train | 2.396 | 70% |
| Validation | 514 | 15% |
| Test | 514 | 15% |
| Total | 3.424 | 100% |

Split mencakup 3.200 duplicate group. Hasil audit:

- review leakage: 0;
- duplicate-group leakage: 0;
- seluruh label positif Task A muncul pada train, validation, dan test;
- seluruh 54 kombinasi `split × aspect × sentiment` Task B memiliki support;
- metadata labeling terlarang tidak terdapat pada dataset model-ready.

## 4. Taksonomi aspek

| ID | Cakupan |
|---|---|
| `product_quality` | Rasa, mutu, porsi, variasi, dan penyajian produk |
| `service` | Interaksi staf, pemesanan, waktu tunggu, dan respons |
| `price_value` | Harga, keterjangkauan, promosi, dan kesepadanan nilai |
| `ambience` | Suasana, interior, kebisingan, dan kenyamanan |
| `facilities` | Wi-Fi, parkir, colokan, toilet, AC, kursi, dan amenitas |
| `cleanliness` | Kebersihan dan higiene ruang, toilet, serta peralatan |

`location_accessibility` tidak menjadi aspek ketujuh. Kasus terkait tetap
ditangani sebagai `out_of_taxonomy` pada sumber labeling.

Konfigurasi aktif:

- `configs/labeling/aspect_taxonomy.yaml`;
- `configs/labeling/annotation_schema.json`;
- `docs/annotation/annotation_guidelines.md`.

## 5. Kebijakan pseudo-label

Label dibuat offline dan deterministik oleh `scripts/label_brewscope.py` dengan
provenance:

```text
auto:lexical_preannotation_v1
```

Labeler menggunakan target/aspect lexicon, pemisahan klausa, polaritas,
negasi, overlap rule, mixed sentiment, dan evidence span. Rating tidak digunakan
sebagai label aspek atau sentimen.

Keputusan aktif:

- pseudo-label disetujui tim dan dosen untuk training serta evaluasi proyek;
- human verification tambahan tidak menjadi bagian pipeline aktif;
- sumber canonical tidak ditimpa atau dipalsukan sebagai human gold;
- metadata `draft`, annotator, taxonomy version, evidence, dan status lain
  disimpan pada sumber/manifest tetapi dihapus dari CSV model-ready;
- hasil eksperimen harus disebut evaluasi terhadap pseudo-label atau silver
  labels, bukan akurasi terhadap ground truth manusia.

## 6. Preprocessing aktif

Notebook: `notebooks/01_preprocessing.ipynb`.

Transformasi utama:

1. Unicode NFKC, HTML unescape, dan case folding;
2. pembersihan HTML serta placeholder URL, email, dan telepon;
3. varian angka `numtoken` dan angka dipertahankan;
4. emoji dan emoticon menjadi token semantik;
5. normalisasi karakter berulang secara konservatif;
6. normalisasi slang lokal yang reproducible;
7. negation binding, termasuk pola seperti `tidak_terlalu_cepat`;
8. stopword removal dengan negasi/intensifier yang dilindungi;
9. stemming Bahasa Indonesia dengan cache;
10. duplicate grouping untuk pencegahan leakage;
11. preprocessing contract tests dan final validation;
12. tabel, grafik, dan Word Cloud 300 DPI.

Varian eksperimen:

| Kolom | Fungsi |
|---|---|
| `text_clean` | Baseline, angka menjadi `numtoken` |
| `text_numbers_preserved` | Angka asli dipertahankan |
| `text_negation` | Negasi diikat ke kata/frasa berikutnya |
| `text_no_stopwords` | Stopword removal tanpa stemming |
| `text_stemmed` | Stemming tanpa stopword removal |
| `text_no_stopwords_stemmed` | Stopword removal + stemming |
| `text_model` | Alias baseline aktif |

`duplicate_group_id` dibentuk dari `text_no_stopwords_stemmed` dengan fallback ke
`text_clean`. Kebijakan ini lebih konservatif agar eksperimen varian teks tidak
menghasilkan near-duplicate leakage.

Output preprocessing:

- `data/processed/modeling/reviews_preprocessed.csv`;
- `data/processed/modeling/aspect_detection_dataset.csv`;
- `data/processed/modeling/aspect_sentiment_dataset.csv`;
- `data/processed/modeling/aspect_sentiment_by_aspect/*.csv`;
- `data/processed/modeling/preprocessing_manifest.json`;
- `reports/figures/preprocessing/`;
- `reports/tables/preprocessing/`.

## 7. Data splitting aktif

Notebook: `notebooks/02_data_splitting.ipynb`.

Konfigurasi:

- rasio 70% train, 15% validation, dan 15% test;
- `random_state=42`;
- 50 greedy multi-start assignment;
- unit assignment adalah `duplicate_group_id`;
- objective menyeimbangkan ukuran split, enam target Task A, eligibility Task A,
  serta 18 kombinasi aspek-sentimen Task B;
- satu assignment dipakai bersama oleh Task A dan Task B.

Output splitting:

- `data/processed/modeling/splits/split_assignments.csv`;
- `data/processed/modeling/splits/aspect_detection_with_split.csv`;
- `data/processed/modeling/splits/aspect_sentiment_with_split.csv`;
- `data/processed/modeling/splits/split_manifest.json`;
- `reports/figures/splitting/`;
- `reports/tables/splitting/`.

Jangan membuat ulang split pada notebook modeling. Gunakan kolom `split` yang
sudah tersedia.

## 8. Kontrak modeling untuk handoff

### 8.1 Task A — Aspect Detection

- Unit: satu review.
- Target: enam kolom biner `aspect_*`.
- Masalah: multi-label classification.
- Data: `aspect_detection_with_split.csv`.
- Evaluasi: macro-F1, micro-F1, precision/recall/F1 dan support per aspek.

### 8.2 Task B — Aspect Sentiment Classification

- Unit: satu pasangan review-aspek yang resolved dan bukan mixed sentiment.
- Target: `negative`, `neutral`, atau `positive`.
- Data: `aspect_sentiment_with_split.csv`.
- Baseline utama: classifier terpisah untuk setiap `aspect_category`.
- Pembanding: satu classifier gabungan menggunakan `aspect_text_model`.
- Evaluasi: macro-F1, weighted-F1, recall negatif, confusion matrix, dan metrik
  per aspek.

### 8.3 Model wajib

1. Support Vector Machine;
2. Random Forest;
3. Multinomial Naive Bayes.

Semua model wajib memakai split dan preprocessing input yang sama untuk
perbandingan yang adil.

### 8.4 Pencegahan leakage

- Fit TF-IDF/CountVectorizer hanya pada train.
- Transform validation dan test menggunakan vectorizer train.
- Hyperparameter selection hanya menggunakan validation atau cross-validation
  di dalam train.
- Test hanya digunakan untuk evaluasi final.
- Class weighting, oversampling, undersampling, dan feature selection hanya
  diterapkan pada train.
- Jangan memakai `review_id`, `annotation_id`, `coffee_shop_id`, rating,
  nama kedai, atau metadata labeling sebagai fitur prediksi.

### 8.5 Class imbalance

Task B memiliki 4.217 positive, 1.099 neutral, dan 282 negative pada keseluruhan
dataset. Accuracy saja akan menyesatkan. Prioritaskan macro-F1 dan recall
negative. Laporkan support agar hasil pada aspek dengan data sedikit tidak
ditafsirkan berlebihan.

Task A juga tidak seimbang, khususnya `cleanliness` dan `facilities`. Gunakan
metrik per label dan pertimbangkan class weight pada model yang mendukungnya.

## 9. Insight bisnis setelah modeling

Insight dihitung dari prediksi model terpilih dan diagregasi per coffee shop:

- jumlah mention setiap aspek;
- distribusi positive/neutral/negative;
- support dan confidence yang tersedia;
- kekuatan utama;
- keluhan utama;
- prioritas perbaikan dengan minimum support agar satu review tidak
  mendominasi keputusan.

Rating tidak digunakan sebagai target sentimen. Rating hanya boleh dipakai
sebagai analisis eksternal atau sanity check yang dijelaskan terpisah.

## 10. Batasan yang wajib dilaporkan

- Label merupakan pseudo-label berbasis aturan leksikal, bukan human gold.
- Evaluasi mengukur kemampuan model mereproduksi pseudo-label.
- Distribusi sentimen sangat tidak seimbang menuju kelas positif.
- Beberapa aspek memiliki support negative yang rendah.
- Satu review non-Latin dikeluarkan dari modeling tetapi tetap disimpan untuk
  audit.
- Teks dapat mengandung code-switching Indonesia-Inggris.
- Identitas geografis dan privasi sumber tetap mengikuti keterbatasan scraping
  awal.

## 11. Checklist rekan modeling

1. Aktifkan environment dan install `.[preprocessing,modeling]`.
2. Jangan menjalankan ulang scraping atau labeling tanpa kebutuhan baru.
3. Gunakan dua file `*_with_split.csv`.
4. Pisahkan `X_train`, `X_validation`, dan `X_test` dari kolom `split`.
5. Fit vectorizer hanya pada train.
6. Mulai dari `text_clean`, lalu bandingkan varian preprocessing lain.
7. Latih Task B per aspek sebagai baseline utama.
8. Tangani imbalance hanya pada train.
9. Simpan metrik, confusion matrix, prediksi, dan konfigurasi eksperimen.
10. Dokumentasikan bahwa label merupakan pseudo-label.

## 12. Urutan sumber kebenaran

Jika terdapat informasi yang bertentangan, gunakan urutan berikut:

1. `data/processed/modeling/splits/split_manifest.json`;
2. `data/processed/modeling/preprocessing_manifest.json`;
3. `data/processed/labeling/annotations_full.jsonl`;
4. `reports/labeling/qa_report.json`;
5. `configs/labeling/annotation_schema.json`;
6. `configs/labeling/aspect_taxonomy.yaml`;
7. dokumen konteks ini;
8. `README.md`.
