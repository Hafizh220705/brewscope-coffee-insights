# Informasi untuk Results and Discussion

## Perbandingan hasil test

| Model | Task A macro-F1 | Task A micro-F1 | Task B per-aspect macro-F1 | Task B recall negative | Task B combined macro-F1 |
|---|---:|---:|---:|---:|---:|
| MNB | 0,6363 | 0,8147 | 0,6017 | 0,4340 | 0,5282 |
| SVM | **0,8775** | **0,9133** | 0,6312 | 0,3962 | 0,5935 |
| RF | 0,8616 | 0,8954 | **0,7013** | **0,5283** | **0,6447** |

Interpretasi yang didukung:

- SVM terbaik untuk deteksi aspek.
- RF terbaik untuk klasifikasi sentimen per aspek.
- Model per aspek mengungguli model gabungan pada MNB, SVM, dan RF.
- Weighted-F1 RF Task B sebesar 0,8347 jauh di atas macro-F1 0,7013; perbedaan ini konsisten dengan imbalance kelas.

## Task A: SVM per aspek

| Aspek | F1 test |
|---|---:|
| ambience | 0,9514 |
| product_quality | 0,9437 |
| service | 0,8548 |
| cleanliness | 0,8525 |
| price_value | 0,8415 |
| facilities | 0,8209 |

Ambience dan product quality paling mudah dideteksi. Facilities memiliki F1 terendah dan support lebih kecil.

## Task B: RF per aspek

| Aspek | Macro-F1 | Recall negative | Support negative |
|---|---:|---:|---:|
| product_quality | 0,5569 | 0,0000 | 6 |
| service | 0,7196 | 0,8400 | 25 |
| price_value | 0,6449 | 0,5000 | 4 |
| ambience | 0,4287 | 0,0000 | 6 |
| facilities | 0,5278 | 0,1250 | 8 |
| cleanliness | 0,7852 | 1,0000 | 4 |
| pooled | 0,7013 | 0,5283 | 53 |

Pembahasan wajib mempertimbangkan support. Recall 1,0 pada cleanliness berasal dari empat sampel negative; nilainya tidak stabil. Nol recall negative pada product quality dan ambience menunjukkan model gagal menemukan seluruh kasus negative pada test untuk kedua aspek tersebut.

## Distribusi data Task B

| Aspek | Negative | Neutral | Positive | Total |
|---|---:|---:|---:|---:|
| product_quality | 32 | 437 | 1.182 | 1.651 |
| service | 127 | 180 | 630 | 937 |
| price_value | 26 | 96 | 342 | 464 |
| ambience | 34 | 230 | 1.784 | 2.048 |
| facilities | 43 | 141 | 133 | 317 |
| cleanliness | 20 | 15 | 146 | 181 |

Total kelas: 282 negative, 1.099 neutral, 4.217 positive. Positive mencakup sekitar 75,3% pasangan.

## Insight bisnis berbasis prediksi

| Aspek | Negative | Neutral | Positive | Total | Share negative | Score |
|---|---:|---:|---:|---:|---:|---:|
| product_quality | 21 | 431 | 1.199 | 1.651 | 1,27% | 0,7135 |
| service | 130 | 172 | 635 | 937 | 13,87% | 0,5390 |
| price_value | 24 | 123 | 317 | 464 | 5,17% | 0,6315 |
| ambience | 22 | 172 | 1.854 | 2.048 | 1,07% | 0,8945 |
| facilities | 37 | 140 | 140 | 317 | 11,67% | 0,3249 |
| cleanliness | 25 | 13 | 143 | 181 | 13,81% | 0,6519 |

- Service memiliki volume keluhan tertinggi.
- Cleanliness memiliki share negative tinggi, tetapi total mention paling kecil.
- Facilities memiliki score terendah, 0,3249.
- Ambience memiliki score tertinggi dan share negative terendah.
- 471 dari 3.424 review tidak mendapat aspek prediksi; undercoverage 13,76%.

## Prioritas kedai teratas

1. Mokopi Jatinangor—service: 24/43 negative, 55,81%.
2. HeyHo! Eatery—service: 13/41, 31,71%.
3. Mokopi Jatinangor—cleanliness: 10/17, 58,82%.
4. Bagi Kopi Jatinangor—service: 9/33, 27,27%.
5. Plumeria Cafe & Creative Space—service: 9/37, 24,32%.

Minimum support prioritas: tiga mention per pasangan kedai-aspek.

## Sanity check rating

Spearman rho: product quality 0,3706; service 0,7079; price value 0,4770; ambience 0,1475; facilities 0,4389; cleanliness 0,7503; keseluruhan 0,4526.

Interpretasi aman: hubungan searah muncul antara sentimen prediksi dan rating. Korelasi tidak membuktikan validitas kausal atau akurasi label.
