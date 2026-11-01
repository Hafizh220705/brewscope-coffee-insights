# BrewScope Coffee Insights - Hasil Analisis

> **Status label:** pseudo-label berbasis aturan leksikal (`auto:lexical_preannotation_v1`), **bukan** human gold standard. Seluruh metrik dan insight mengacu pada prediksi model yang dilatih terhadap pseudo-label tersebut.

## Ringkasan Eksekutif

- Dataset: **3424 review** Google Maps dari **40 coffee shop** di Jatinangor; Task B memiliki **5598 pasangan review-aspek**.
- **Task A (deteksi aspek)**: model terbaik adalah **SVM** dengan macro-F1 test 0.8775 (micro-F1 0.9133).
- **Task B (sentimen per aspek)**: model terbaik adalah **Random Forest per-aspek** dengan pooled macro-F1 test 0.7013 dan recall `negative` 0.5283.
- Keluhan yang paling sering diprediksi: **service, facilities, cleanliness**.
- Aspek dengan sentimen terbaik: **ambience, cleanliness, product_quality**.
- Prioritas perbaikan disusun per (shop, aspek) dengan minimum support 3 mention.

Catatan cakupan: 471 dari 3424 review (13.76%) tidak mendapat aspek terdeteksi dari model Task A; review tersebut tetap masuk tabel lampiran `task_a_predictions_all.csv` tetapi tidak menyumbang sentimen aspek.

## 1. Konteks Proyek

BrewScope menganalisis ulasan Google Maps coffee shop di Jatinangor dengan pendekatan Aspect-Based Sentiment Analysis (ABSA) untuk menghasilkan prioritas perbaikan strategis per coffee shop. Pipeline: scraping -> preprocessing -> labeling -> splitting -> modelling -> **insight bisnis** (dokumen ini). Detail kontrak: `PROJECT_CONTEXT.md` dan `README.md`.

## 2. Data dan Metodologi

| Elemen | Deskripsi |
|---|---|
| Data Task A | 3424 review, target 6 label biner aspek |
| Data Task B | 5598 pasangan review-aspek, 3 kelas sentimen |
| Split | 70/15/15, dikelompokkan berdasar `duplicate_group_id` (0 kebocoran) |
| Label | pseudo-label leksikal deterministik (`label_brewscope.py`) |
| Fitur | TF-IDF `text_clean` (min_df=2, unigram+bigram, maks 10.000 fitur) |
| Algoritma | MultinomialNB, LinearSVC (SVM), Random Forest |
| Model terpilih | Task A: SVM; Task B: RF per-aspek (baseline utama) |
| Ambang insight | minimum support 3 mention per (shop, aspek) |

## 3. Hasil Modelling dan Pemilihan Model

### 3.1 Perbandingan tiga algoritma (test, pseudo-label)

| model | task_a_macro_f1 | task_a_micro_f1 | task_b_per_aspect_pooled_macro_f1 | task_b_per_aspect_recall_negative | task_b_combined_pooled_macro_f1 |
|---|---|---|---|---|---|
| MNB | 0.6363 | 0.8147 | 0.6017 | 0.4340 | 0.5282 |
| SVM | 0.8775 | 0.9133 | 0.6312 | 0.3962 | 0.5935 |
| RF | 0.8616 | 0.8954 | 0.7013 | 0.5283 | 0.6447 |

### 3.2 Keputusan

- **Task A**: SVM dipilih karena macro-F1 tertinggi sekaligus micro-F1 tertinggi.
- **Task B**: RF per-aspek dipilih karena pooled macro-F1 dan recall `negative` tertinggi - paling penting untuk mendeteksi keluhan.

## 4. Insight Bisnis

### 4.1 Gambaran umum per aspek (prediksi model terpilih)

| aspect | mentions_task_a | n_negative | n_neutral | n_positive | n_total | share_negative | score |
|---|---|---|---|---|---|---|---|
| product_quality | 1644 | 21 | 431 | 1199 | 1651 | 0.0127 | 0.7135 |
| service | 879 | 130 | 172 | 635 | 937 | 0.1387 | 0.5390 |
| price_value | 435 | 24 | 123 | 317 | 464 | 0.0517 | 0.6315 |
| ambience | 2032 | 22 | 172 | 1854 | 2048 | 0.0107 | 0.8945 |
| facilities | 320 | 37 | 140 | 140 | 317 | 0.1167 | 0.3249 |
| cleanliness | 160 | 25 | 13 | 143 | 181 | 0.1381 | 0.6519 |

### 4.2 Kekuatan utama per shop

| shop_name | strength_aspect | strength_share_positive | strength_n |
|---|---|---|---|
| Fore Coffee - Jatinangor Town Square | cleanliness | 1 | 6 |
| Kopi Menak Rancaekek | cleanliness | 1 | 16 |
| Mokopi Jatinangor | ambience | 0.8136 | 59 |
| Kopi Menak Roastery Jatinangor | cleanliness | 1 | 3 |
| Nora Coffee Jatinangor | price_value | 1 | 3 |
| Imahaing Coffee & Kitchen | ambience | 0.7778 | 9 |
| TOMORO COFFEE - JATINANGOR | cleanliness | 1 | 4 |
| Kopi Kenangan Jatos | cleanliness | 0.9091 | 11 |
| Bagi Kopi Jatinangor | ambience | 0.9231 | 52 |
| beri kopi Jatinangor | ambience | 0.9194 | 62 |

Tabel lengkap 40 shop: `reports/tables/insights/shop_strengths_weaknesses.csv`.

### 4.3 Keluhan utama dan prioritas perbaikan (top 10)

| coffee_shop_id | shop_name | aspect_category | n_negative | n_total | share_negative | score |
|---|---|---|---|---|---|---|
| SHOP_078A43B3179E20 | Mokopi Jatinangor | service | 24 | 43 | 0.5581 | -0.2558 |
| SHOP_A1D0DA69438D15 | HeyHo! Eatery | service | 13 | 41 | 0.3171 | 0.2195 |
| SHOP_078A43B3179E20 | Mokopi Jatinangor | cleanliness | 10 | 17 | 0.5882 | -0.3529 |
| SHOP_47FDC355D261F9 | Bagi Kopi Jatinangor | service | 9 | 33 | 0.2727 | 0.2424 |
| SHOP_8D0052DC7DC62D | Plumeria Cafe & Creative Space | service | 9 | 37 | 0.2432 | 0.3243 |
| SHOP_545D71B99C3B3F | Kopi Setia Jatinangor | service | 8 | 18 | 0.4444 | -0.2222 |
| SHOP_056852433108F5 | Fore Coffee - Jatinangor Town Square | service | 8 | 48 | 0.1667 | 0.5208 |
| SHOP_69F5C38C2B631A | Ngopi Doeloe | service | 7 | 23 | 0.3043 | 0.1304 |
| SHOP_CFA6C16DB93EC3 | Imah Kayu Jatinangor | service | 7 | 29 | 0.2414 | 0.4138 |
| SHOP_B3A06D125BB96B | Djoeroe Coffee | service | 6 | 33 | 0.1818 | 0.4848 |

### 4.4 Sanity check rating eksternal

Rating Google tidak dipakai sebagai target; korelasi Spearman berikut hanya sanity check:

| aspect_category | n | spearman_rho | p_value |
|---|---|---|---|
| product_quality | 1651 | 0.3706 | 0 |
| service | 937 | 0.7079 | 0 |
| price_value | 464 | 0.4770 | 0 |
| ambience | 2048 | 0.1475 | 0 |
| facilities | 317 | 0.4389 | 0 |
| cleanliness | 181 | 0.7503 | 0 |
| ALL | 5598 | 0.4526 | 0 |

Korelasi keseluruhan rho = 0.4526: arah prediksi sentimen model sejalan dengan rating pengguna.

## 5. Rekomendasi Strategis

- Perhatikan **service**: 130 prediksi negative (13.9% dari mention aspek ini). Prioritas tertinggi pada shop di tabel 4.3.
- Perhatikan **facilities**: 37 prediksi negative (11.7% dari mention aspek ini). Prioritas tertinggi pada shop di tabel 4.3.
- Perhatikan **cleanliness**: 25 prediksi negative (13.8% dari mention aspek ini). Prioritas tertinggi pada shop di tabel 4.3.

- Pertahankan kekuatan pada **ambience, cleanliness, product_quality** - aspek dengan proporsi positive tertinggi.
- Gunakan tabel `improvement_priorities.csv` sebagai daftar kerja per shop; filter `n_negative >= 2` untuk sinyal yang lebih konservatif.

## 6. Batasan

- Label adalah pseudo-label berbasis aturan leksikal, bukan human gold.
- Evaluasi mengukur kemampuan model mereproduksi pseudo-label.
- Insight adalah agregasi prediksi model, bukan ground truth sentimen.
- Distribusi sentimen sangat tidak seimbang ke arah positive.
- Beberapa aspek memiliki support `negative` yang rendah; interpretasi keluhan dengan support kecil harus hati-hati.
- Satu review non-Latin dikeluarkan dari modeling (tetap disimpan untuk audit).
- Teks dapat mengandung code-switching Indonesia-Inggris.
- Inferensi Task B dilakukan pada pasangan review-aspek yang sudah ada di dataset anotasi; pipeline end-to-end (Task A lalu Task B pada review baru) adalah future work.

## 7. Artefak dan Cara Reproduksi

Jalankan dari awal: `notebooks/03_modeling_all_models.ipynb` lalu `notebooks/04_business_insights.ipynb` (Python 3.11, environment `brewscope`).

Artefak utama tahap insight:

- `data/processed/insights/task_a_predictions_all.csv`
- `data/processed/insights/task_b_predictions_all.csv`
- `data/processed/insights/insights_manifest.json`
- `reports/tables/insights/shop_aspect_mentions.csv`
- `reports/tables/insights/shop_aspect_sentiment.csv`
- `reports/tables/insights/shop_strengths_weaknesses.csv`
- `reports/tables/insights/improvement_priorities.csv`
- `reports/tables/insights/rating_sanity_check.csv`
- `reports/figures/insights/shop_sentiment_heatmap.png`
- `reports/figures/insights/top_10_complaints.png`
- `reports/figures/insights/aspect_sentiment_distribution.png`
- `RESULTS.md`

## Lampiran: Profil Coffee Shop

| shop_name | n_reviews | n_mentions_total | mean_score | strength_aspect | weakness_aspect |
|---|---|---|---|---|---|
| Jatinangor coffee 2 | 16 | 18 | 0.9333 | ambience |  |
| JC7 Cafe Jatinangor Center | 10 | 16 | 0.8958 | ambience |  |
| Meet Iokay | 114 | 165 | 0.8542 | facilities |  |
| Aksata Coffee & Roastery, Jatinangor | 66 | 104 | 0.8313 | price_value |  |
| BARRY'S Coffee & Eatery | 13 | 25 | 0.8254 | price_value | ambience |
| Alana Coffee & Eatery | 132 | 227 | 0.8139 | cleanliness | service |
| Kopi Menak Roastery Jatinangor | 60 | 120 | 0.7997 | cleanliness |  |
| Titik Awal Kopitiam Jatinangor (TIWAL) | 131 | 190 | 0.7911 | ambience | service |
| Sky Resto & Cafe | 93 | 157 | 0.7859 | cleanliness | service |
| Kopi Nako Jatinangor | 95 | 144 | 0.7754 | ambience | service |
| Jabarano Coffee - Jaipong Jatinangor | 135 | 225 | 0.7729 | ambience | service |
| Tepi Kopi Jatinangor | 124 | 206 | 0.7667 | cleanliness | product_quality |
| Kopi Menak Rancaekek | 150 | 314 | 0.7431 | cleanliness | product_quality |
| Tekun.id Jatinagor | 105 | 129 | 0.7323 | ambience | service |
| Meramu - Cafe Minuman Rempah Jatinangor | 64 | 60 | 0.7280 | ambience | service |
| Noel Coffee Jatinangor | 90 | 124 | 0.7117 | ambience | price_value |
| Aksen Signature | 99 | 151 | 0.7084 | cleanliness | service |
| Djoeroe Coffee | 126 | 187 | 0.6924 | cleanliness | service |
| Bento Kopi Jatinangor | 77 | 101 | 0.6916 | ambience | price_value |
| Kopi Kenangan Jatos | 122 | 177 | 0.6718 | cleanliness | service |
| Kopi Kenangan - Ruko Jatinangor | 106 | 166 | 0.6713 | cleanliness | service |
| Jaad Cafe Jatinangor | 102 | 164 | 0.6520 | ambience | facilities |
| TOMORO COFFEE - JATINANGOR | 71 | 92 | 0.6155 | cleanliness | facilities |
| Imah Kayu Jatinangor | 118 | 246 | 0.6151 | ambience | service |
| Imahaing Coffee & Kitchen | 15 | 15 | 0.6056 | ambience |  |
| Jumpa Asa Coffee-nity & Eatery | 51 | 84 | 0.5949 | cleanliness | facilities |
| Bagi Kopi Jatinangor | 95 | 161 | 0.5816 | ambience | service |
| Fore Coffee - Jatinangor Town Square | 98 | 138 | 0.5787 | cleanliness | service |
| Plumeria Cafe & Creative Space | 102 | 194 | 0.5645 | ambience | service |
| Heya Space 2.0 | 100 | 155 | 0.5624 | ambience | price_value |
| Nomar Kopi Roastery Jatinangor - Cafe WFC & Ruang Meeting | 55 | 87 | 0.5551 | ambience | service |
| Nora Coffee Jatinangor | 11 | 24 | 0.4917 | price_value | facilities |
| beri kopi Jatinangor | 94 | 167 | 0.4906 | ambience | facilities |
| Ninyuh Coffee Roastery Jatinangor | 83 | 101 | 0.4782 | service |  |
| Eiger Coffee Jatinangor | 42 | 75 | 0.4406 | ambience | service |
| HeyHo! Eatery | 108 | 200 | 0.3862 | ambience | service |
| Toleransi Kopi Jatinangor | 82 | 99 | 0.3658 | ambience | cleanliness |
| Kopi Setia Jatinangor | 86 | 138 | 0.3464 | ambience | service |
| Ngopi Doeloe | 79 | 118 | 0.1964 | ambience | service |
| Mokopi Jatinangor | 104 | 206 | 0.1962 | ambience | service |

