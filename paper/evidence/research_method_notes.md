# Informasi untuk Research Method

## Akuisisi data

- Sumber: ulasan Google Maps melalui Apify actor `compass/google-maps-reviews-scraper`.
- Script: `scripts/scrape_google_maps.py`.
- Cakupan konfigurasi: maksimal 40 lokasi dan 170 review per lokasi; bahasa `id`; `personalData=False`.
- Review tanpa teks dibuang dan data dideduplikasi berdasarkan `review_id`.
- Kolom mentah: `review_id`, `nama_tempat`, `rating`, `tanggal_review`, `teks_review`, `url_tempat`.
- Rating tidak dipakai sebagai fitur atau target model.

## Pelabelan

- Pseudo-label deterministik berbasis leksikal, provenance `auto:lexical_preannotation_v1`.
- Script: `scripts/label_brewscope.py`.
- Komponen: leksikon target/aspek, pemisahan klausa, leksikon polaritas, negasi, aturan overlap, mixed sentiment, dan evidence span.
- Rating tidak digunakan untuk menentukan aspek atau sentimen.

## Preprocessing

1. Normalisasi Unicode NFKC, HTML unescape, dan case folding.
2. Pembersihan HTML.
3. Penggantian URL, email, dan telepon dengan placeholder.
4. Konversi emoji/emoticon menjadi token semantik.
5. Normalisasi karakter berulang.
6. Normalisasi 92 entri slang lokal.
7. Negation binding.
8. Stopword removal dengan negasi dan intensifier terlindungi.
9. Stemming Bahasa Indonesia menggunakan Sastrawi dan cache.
10. Pembentukan `duplicate_group_id`.
11. Contract test dan validasi akhir.

Eksperimen final memakai `text_clean` untuk Task A dan Task B per aspek. Model gabungan Task B memakai `aspect_text_model`.

## Pembentukan task

### Task A

- Unit analisis: review.
- Masalah: klasifikasi multi-label.
- Target: enam indikator aspek biner.
- Implementasi model: `OneVsRestClassifier`.
- Jumlah: 3.424 review.

### Task B

- Unit analisis: pasangan review-aspek.
- Masalah: klasifikasi multiclass negative, neutral, positive.
- Strategi utama: enam classifier terpisah.
- Pembanding: satu classifier gabungan dengan teks berkondisi aspek.
- Jumlah: 5.598 pasangan.

## Split data

- Rasio 70/15/15.
- Train: 2.396 review dan 3.313 pasangan Task B.
- Validation: 514 review dan 1.143 pasangan.
- Test: 514 review dan 1.142 pasangan.
- `random_state=42`.
- Grouping memakai `duplicate_group_id`.
- Assignment sama dipakai Task A dan Task B.
- Audit menemukan nol review leakage dan nol duplicate-group leakage.

## Representasi fitur

TF-IDF dengan konfigurasi:

```text
sublinear_tf=True
min_df=2
ngram_range=(1, 2)
max_features=10000
```

Vectorizer di-fit hanya pada train. ID review, nama kedai, coffee shop ID, rating, URL, dan metadata anotasi tidak menjadi fitur.

## Algoritma dan tuning

### Multinomial Naive Bayes

- Grid alpha: 0,001; 0,003; 0,01; 0,03; 0,1; 0,3; 0,5; 1,0; 2,0.
- Terpilih: Task A 0,01; Task B per aspek 0,03; Task B gabungan 0,03.

### Linear SVM

- `LinearSVC`, `class_weight='balanced'`, `max_iter=5000`, `random_state=42`.
- Grid C: 0,01; 0,03; 0,1; 0,3; 1,0; 3,0; 10,0.
- Terpilih: Task A 1,0; Task B per aspek 10,0; Task B gabungan 1,0.

### Random Forest

- Grid `n_estimators`: 100, 300.
- Grid `max_depth`: None, 20.
- Grid `min_samples_leaf`: 1, 5.
- `class_weight='balanced'`, `random_state=42`, `n_jobs=-1`.
- Terpilih Task A: 300 trees, depth 20, leaf 1.
- Terpilih Task B: 300 trees, unlimited depth, leaf 1.

Hyperparameter dipilih berdasarkan validation macro-F1. Test dievaluasi sekali setelah seleksi.

## Evaluasi

- Task A: macro-F1, micro-F1, precision/recall/F1 per aspek.
- Task B: pooled macro-F1, weighted-F1, recall/precision/F1 negative, F1 tiap kelas, metrik per aspek, dan confusion matrix.
- Macro-F1 menjadi metrik utama karena ketimpangan kelas.
- Recall negative dipakai untuk menilai kemampuan menemukan keluhan.

## Reproduksibilitas

- Python 3.11.9.
- scikit-learn 1.9.1.
- pandas 2.3.3.
- numpy 2.4.6.
- joblib 1.6.0.
- Urutan notebook: `01_preprocessing.ipynb`, `02_data_splitting.ipynb`, `03_modeling_all_models.ipynb`, `04_business_insights.ipynb`.
