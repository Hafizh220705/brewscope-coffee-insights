# Informasi untuk Abstract

## Latar masalah

Rating agregat Google Maps tidak menjelaskan aspek spesifik yang menjadi kekuatan atau sumber keluhan. BrewScope memakai Aspect-Based Sentiment Analysis untuk mengubah teks ulasan menjadi indikator aspek dan prioritas perbaikan coffee shop.

## Tujuan

1. Mendeteksi enam aspek dalam ulasan.
2. Mengklasifikasikan sentimen negative, neutral, atau positive untuk setiap aspek.
3. Membandingkan MNB, Linear SVM, dan Random Forest.
4. Mengagregasi prediksi menjadi kekuatan, kelemahan, dan prioritas perbaikan per kedai.

## Data dan metode ringkas

- 3.538 ulasan bertulis, 40 coffee shop di Jatinangor.
- Task A: 3.424 ulasan.
- Task B: 5.598 pasangan review-aspek.
- Aspek: product quality, service, price value, ambience, facilities, cleanliness.
- Representasi: TF-IDF unigram–bigram, `min_df=2`, maksimal 10.000 fitur.
- Split group-aware 70/15/15 berdasarkan kelompok duplikat.
- Model: Multinomial Naive Bayes, Linear SVM, Random Forest.
- Metrik utama: macro-F1; metrik pendamping: micro-F1, weighted-F1, dan recall negative.

## Hasil inti

- Task A terbaik: SVM, macro-F1 0,8775; micro-F1 0,9133.
- Task B terbaik: RF per aspek, pooled macro-F1 0,7013; weighted-F1 0,8347; recall negative 0,5283.
- Classifier per aspek mengungguli classifier gabungan pada semua algoritma.
- Service memiliki 130 prediksi negative, tertinggi secara absolut.
- Ambience memiliki score agregat tertinggi, 0,8945.

## Batas klaim

- Label merupakan pseudo-label berbasis aturan leksikal.
- Distribusi kelas condong ke positive.
- Insight bisnis berupa agregasi prediksi, bukan pengukuran lapangan.
