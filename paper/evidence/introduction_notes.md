# Informasi untuk Introduction

## Konteks masalah

- Ulasan daring memuat opini tentang banyak dimensi layanan dalam satu teks.
- Rating bintang merangkum pengalaman, tetapi tidak menunjukkan penyebab kepuasan atau ketidakpuasan.
- Analisis per aspek memungkinkan pengelola membedakan isu produk, layanan, harga, suasana, fasilitas, dan kebersihan.
- Konteks penelitian dibatasi pada coffee shop di Jatinangor.

## Taksonomi aspek

| Aspek | Cakupan |
|---|---|
| product_quality | rasa, mutu, porsi, variasi, penyajian |
| service | staf, pemesanan, waktu tunggu, respons |
| price_value | harga, promosi, keterjangkauan, kesepadanan nilai |
| ambience | suasana, interior, kebisingan, kenyamanan |
| facilities | Wi-Fi, parkir, colokan, toilet, AC, kursi |
| cleanliness | kebersihan dan higiene |

## Calon pertanyaan penelitian

1. Seberapa baik MNB, Linear SVM, dan Random Forest mendeteksi enam aspek dalam ulasan coffee shop?
2. Seberapa baik model tersebut mengklasifikasikan sentimen per aspek?
3. Apakah classifier terpisah per aspek mengungguli classifier gabungan?
4. Model mana paling efektif mendeteksi kelas negative sebagai sinyal keluhan?
5. Aspek apa menjadi kekuatan dan prioritas perbaikan coffee shop di Jatinangor?
6. Apakah sentimen prediksi memiliki hubungan searah dengan rating Google sebagai sanity check eksternal?

## Kontribusi yang didukung codebase

- Pipeline ABSA traditional ML berbahasa Indonesia dari data ulasan sampai insight bisnis.
- Perbandingan tiga keluarga algoritma pada dua task.
- Pembagian data group-aware untuk mencegah kelompok duplikat melintasi split.
- Perbandingan classifier sentimen per aspek dan classifier gabungan.
- Agregasi prediksi menjadi prioritas perbaikan per pasangan kedai-aspek.

## Informasi yang masih membutuhkan literatur eksternal

- Statistik pertumbuhan coffee shop atau penggunaan Google Maps.
- Research gap terhadap studi ABSA Indonesia sebelumnya.
- Alasan teoretis pemilihan traditional ML dibanding transformer.
- Rujukan asli TF-IDF, SVM, MNB, Random Forest, macro-F1, dan ABSA.

Jangan membuat klaim novelty atau generalisasi nasional tanpa tinjauan pustaka tambahan.
