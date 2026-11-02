# Keterbatasan dan Risiko Interpretasi

1. Label penelitian merupakan pseudo-label deterministik berbasis leksikal. Evaluasi mengukur kesesuaian model terhadap label tersebut.
2. Distribusi Task B sangat tidak seimbang: 4.217 positive, 1.099 neutral, dan 282 negative.
3. Test set hanya memuat 53 pasangan negative; beberapa aspek hanya memiliki empat sampai delapan sampel negative.
4. Belum tersedia confidence interval, repeated split, bootstrap, atau uji signifikansi antar-model.
5. Satu review non-Latin/unsupported dikeluarkan dari modeling.
6. Teks mengandung code-switching Indonesia–Inggris, typo, slang, dan ekspresi implisit yang dapat lolos dari aturan leksikal.
7. Mixed dan unresolved/uncertain tidak masuk subset Task B tertentu.
8. Insight memakai prediksi atas seluruh split; angka insight bukan estimasi performa generalisasi.
9. Task B dijalankan pada pasangan review-aspek yang sudah tersedia. Pipeline end-to-end untuk review baru belum dievaluasi.
10. Sebanyak 471 review atau 13,76% tidak mendapat aspek prediksi.
11. Cakupan geografis terbatas pada 40 coffee shop di Jatinangor.
12. Representativitas pemilihan kedai, periode pengambilan data, izin sumber, dan perubahan perilaku pengguna dari waktu ke waktu belum dianalisis lengkap.
13. Korelasi rating hanya sanity check. Rating bukan target dan korelasi tidak membuktikan hubungan kausal.
14. Varian preprocessing tersedia, tetapi eksperimen final hanya menggunakan `text_clean` dan `aspect_text_model`.

## Aturan pembahasan

- Jangan memakai accuracy sebagai metrik utama.
- Jangan membandingkan recall per aspek tanpa menyebut support negative.
- Jangan menyebut insight sebagai ground truth kondisi kedai.
- Jangan menggeneralisasi hasil ke luar Jatinangor tanpa eksperimen tambahan.
- Jangan menyatakan model siap produksi sebelum evaluasi end-to-end dan monitoring drift.
