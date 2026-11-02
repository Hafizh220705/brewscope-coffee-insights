# Informasi untuk Conclusions

## Kesimpulan yang didukung hasil

1. TF-IDF dan Linear SVM memberikan performa terbaik untuk deteksi aspek, dengan macro-F1 0,8775 dan micro-F1 0,9133.
2. Random Forest terpisah per aspek memberikan performa terbaik untuk klasifikasi sentimen, dengan pooled macro-F1 0,7013 dan recall negative 0,5283.
3. Classifier terpisah per aspek mengungguli classifier gabungan untuk ketiga algoritma.
4. Service menjadi sumber keluhan prediksi terbesar secara absolut.
5. Facilities dan cleanliness memerlukan perhatian karena share negative masing-masing 11,67% dan 13,81%.
6. Ambience menjadi kekuatan umum dengan score 0,8945.
7. Output cocok sebagai alat penyaringan dan prioritisasi awal, bukan pengganti validasi operasional.

## Implikasi praktis

- Kedai dapat memulai audit dari pasangan kedai-aspek ber-volume dan ber-proporsi negative tinggi.
- Volume keluhan dan share negative harus dibaca bersama agar kedai besar tidak otomatis dianggap paling buruk.
- Service layak menjadi fokus lintas-kedai; fasilitas dan kebersihan memerlukan inspeksi kontekstual per lokasi.

## Future work yang beralasan

- Menambah anotasi referensi dan mengukur agreement.
- Menambah sampel kelas negative serta menangani imbalance.
- Mengevaluasi pipeline end-to-end Task A lalu Task B pada review baru.
- Memakai bootstrap confidence interval atau repeated grouped split.
- Membandingkan varian preprocessing yang sudah tersedia.
- Menguji generalisasi pada wilayah dan periode berbeda.
- Memvalidasi prioritas dengan pengelola coffee shop.
