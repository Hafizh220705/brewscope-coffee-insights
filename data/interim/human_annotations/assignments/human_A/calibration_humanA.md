# Penjelasan Calibration — Human A

## 1. Tujuan Calibration

Calibration adalah tahap awal anotasi untuk menyamakan pemahaman tentang pedoman pelabelan (*annotation guideline*) sebelum anotasi utama dilakukan. Pada tahap ini, Human A memberi label pada kumpulan data calibration secara mandiri, lalu hasilnya nantinya dibandingkan dengan hasil anotasi Human B.

Tujuan calibration bukan untuk menentukan siapa yang paling benar, melainkan menemukan bagian pedoman yang masih bisa ditafsirkan berbeda dan menyepakati cara menerapkannya secara konsisten.

## 2. Tugas Human A

Sebagai Human A, tugasnya adalah:

1. Membaca pedoman anotasi sebelum mulai memberi label.
2. Menganotasi **50 review calibration** secara mandiri.
3. Memeriksa setiap review untuk enam aspek berikut:
   - `product_quality` — kualitas produk atau makanan/minuman.
   - `service` — pelayanan staf atau proses layanan.
   - `price_value` — harga dan kesesuaian harga dengan nilai yang diterima.
   - `ambience` — suasana atau kenyamanan tempat.
   - `facilities` — fasilitas yang tersedia.
   - `cleanliness` — kebersihan tempat atau fasilitas.
4. Mengisi label berdasarkan isi review dan pedoman anotasi, bukan berdasarkan asumsi pribadi.
5. Menyimpan hasil anotasi sesuai format file yang disediakan.

Dengan demikian, 50 review × 6 aspek menghasilkan **300 catatan anotasi aspek**.

## 3. Label yang Perlu Diperhatikan

Untuk setiap aspek pada setiap review, Human A perlu menentukan:

- **`aspect_presence`** — apakah aspek tersebut disebutkan dalam review, tidak disebutkan, atau tidak dapat dipastikan (`mentioned`, `not_mentioned`, atau `uncertain`).
- **`sentiment`** — sentimen terhadap aspek tersebut, mengikuti pilihan label yang tersedia di guideline, misalnya positif, negatif, netral, atau campuran.
- **`mention_type`** — apakah aspek disebutkan secara eksplisit (`explicit`) atau tersirat (`implicit`), sesuai definisi pada guideline.
- **`evidence`** — kutipan teks review yang mendukung label, termasuk posisi awal dan akhir kutipan jika diwajibkan oleh format data.
- **`annotation_status`** dan **`notes`** — diisi sesuai aturan pada template atau pedoman proyek.

Jika suatu aspek **tidak disebutkan**, gunakan `not_mentioned`. Dalam kondisi tersebut, sentimen dan jenis penyebutan tidak perlu diisi (`null`), dan bukti teks dibiarkan kosong (`[]`) apabila sesuai dengan skema yang disediakan. Jika suatu review benar-benar ambigu, gunakan `uncertain` hanya sesuai ketentuan guideline dan tambahkan catatan bila diperlukan.

## 4. Cara Mengerjakan

1. Buka file calibration Human A yang disediakan.
2. Baca satu review secara utuh.
3. Evaluasi keenam aspek satu per satu.
4. Tentukan apakah setiap aspek disebutkan.
5. Jika disebutkan, tentukan sentimen, jenis penyebutan, dan kutipan bukti yang tepat.
6. Pastikan kutipan bukti benar-benar muncul pada teks review; jangan membuat kutipan atau menyimpulkan hal yang tidak didukung teks.
7. Periksa kembali kelengkapan label dan konsistensi format sebelum menyimpan hasil.

**Penting:** satu review dapat membahas beberapa aspek sekaligus. Namun, bukti dan sentimen harus ditentukan untuk masing-masing aspek, bukan disamakan untuk seluruh review.
