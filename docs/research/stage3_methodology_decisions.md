# Keputusan metodologi Tahap 3 BrewScope

Versi taksonomi/guideline: **0.1.0-draft**, 25 Oktober 2026 (Asia/Jakarta).
Status: literature-grounded draft; belum divalidasi melalui anotasi aktual.

## 1. Dasar keputusan dan batas bukti

Tahap 3 menggabungkan (a) kategori ABSA pada benchmark restoran; (b) studi ABSA
Indonesia; (c) dimensi survei coffee shop; dan (d) statistik eksplorasi Tahap 2.
Rujukan diverifikasi melalui publisher/ACL, dengan bukti halaman/bagian pada
literature_matrix.csv. Matriks sumber-ke-aspek tersimpan sebagai
`reports/tables/literature_aspect_mapping.csv`.

Survei kepuasan tidak otomatis merupakan taksonomi ABSA, dan kategori penelitian
lain tidak otomatis valid untuk Jatinangor. Coverage keyword adalah petunjuk
sampling, bukan precision/recall atau label kebenaran. Tidak ada anotasi manusia/AI
pada review asli, klasifikasi sentimen, atau training pada tahap ini.

## 2. Keputusan taksonomi

| Kandidat | Keputusan | Alasan dan konsekuensi |
|---|---|---|
| Product Quality | ADAPT | Gabungkan FOOD/DRINKS dan dimensi mutu/menu/porsi menjadi satu kategori operasional |
| Service | ADOPT | Adopsi konsep layanan; batas overlap dan ekspresi Indonesia tetap perlu pilot |
| Price & Value | ADAPT | Harga diperluas menjadi affordability/value, dengan bukti evaluasi biaya |
| Ambience | ADAPT | Suasana/kenyamanan dipakai untuk konteks bekerja-belajar; kebersihan dipisah |
| Facilities | ADAPT | Amenitas/fungsinya dipisah dari suasana dan kebersihan; ada dukungan studi Indonesia/survei |
| Cleanliness | ADAPT | Dimensi kebersihan dibuat operasional tersendiri; bukan klaim kategori mandiri pada semua sumber |
| Location & Accessibility | PROVISIONAL | Ada dukungan literatur, tetapi cakupan lokal dan batas parkir/akses belum divalidasi |
| Food + Drinks | MERGE | Dimasukkan ke product_quality; rincian objek dipertahankan pada evidence |
| Waiting time | MERGE | Dimasukkan ke service; tidak menambah label utama |
| Pujian umum/miscellaneous sebagai label semua aspek | REJECT | Tidak memiliki dukungan untuk menyebarkan polaritas ke aspek yang tidak dibahas |

Enam kategori aktif adalah **pilihan draft setelah evaluasi tujuh kandidat**,
bukan penguncian karena Tahap 2 kebetulan memakai enam keyword. Jumlah kategori
dapat berubah setelah pilot berizin. Location dapat diaktifkan melalui version
bump jika contoh nyata, manfaat, agreement, dan batas kategorinya mendukung.
Kasus yang tidak cocok dicatat sebagai coverage gap, bukan dipaksakan ke kelas lain.

## 3. Formulasi task dan kompatibilitas ML

**Task A: aspect category detection.** Input review; output himpunan 0–6 aspek
aktif. Ini multi-label, bukan enam kelas saling eksklusif. Keyword baseline
eksploratif belum merupakan detector tervalidasi; anotasi manusia diperlukan.

**Task B: sentiment per aspek mentioned.** Input review/context dan aspect_id;
target hanya positive/neutral/negative pada pair yang telah diselesaikan.
not_mentioned merupakan keputusan presence, bukan kelas netral. uncertain adalah
status workflow. Tidak dibuat label dari rating.

Schema menyimpan satu record review–aspect–annotator dan evidence opinion-level.
Untuk long format, satu baris memuat review_id, coffee_shop_id, aspect_id, context,
sentiment, taxonomy_version, annotator/adjudication provenance, dan eligible flag.
Pair mixed memiliki sentiment=null dan tidak masuk subset tiga kelas; semua opini
tetap diarsipkan. Transformasi long-format hanya didemonstrasikan dengan fixture
sintetis pada notebook.

Eksperimen berikutnya dapat membandingkan SVM, Random Forest, dan Multinomial
Naive Bayes pada fitur/context serta split yang sama. Alternatif yang perlu
dipraregistrasikan: model per aspek atau model gabungan dengan identitas aspek
dalam input. Tidak cukup memberi review multi-aspek identik ke model tanpa
menyebut aspek yang dituju. Seluruh transformasi fitur di-fit hanya pada train.
Data/split dan metrik tersebut belum dibangun atau dihitung pada Tahap 3.

## 4. Desain kandidat pilot 250 review

Pemilihan bersifat metadata/keyword eksploratif tanpa penilaian polaritas.
Universe adalah 3.582 review yang lolos flag kualitas dasar Tahap 2. Flag tidak
diubah dan raw tidak ditulis ulang. Seed **42**, ranking stabil
SHA-256(seed|review_id), urutan review_id sebagai tie-breaker.

Ambil minimal tiga review per place key (maksimal yang tersedia), kemudian isi
kekurangan kuota kelompok yang tumpang tindih dan lengkapi hingga target 250.
Jumlah setiap kuota adalah minimum eksploratif pada keseluruhan sampel, bukan
alokasi kelompok eksklusif. Satu review dapat memenuhi beberapa kuota.

| Kelompok | Target minimum |
|---|---:|
| Cleanliness keyword candidate | 20 |
| Facilities keyword candidate | 20 |
| Tanpa keyword aspek | 35 |
| Rating rendah 1–2 | 30 |
| Rating tengah 3 | 15 |
| Teks panjang >30 kata | 25 |
| ≥2 keyword aspect indicators | 50 |
| Slang atau indikasi bahasa campuran | 40 |
| Potensi teks berulang | 15 |
| Teks pendek <4 kata | 35 |
| Kedai kecil <30 review | 20 |
| Rating tinggi 4–5 | 30 |

Jika ketersediaan/kapasitas tidak memenuhi seluruh kuota, notebook melaporkan
shortfall, bukan mengganti angka diam-diam. Sampling ini memperkaya kasus sulit;
hasil agreement/performa pilot tidak boleh ditafsirkan sebagai estimasi distribusi
alami. Peluang inklusi dan desain bukan simple random sample sehingga statistik
pilot tidak digunakan untuk estimasi prevalensi tanpa rancangan inferensi baru.

CSV kandidat mempertahankan ID, place key, rating untuk perancang sampling,
panjang teks, flag kesulitan, keyword indicators eksploratif, hash kelompok teks,
alasan terpilih, seed dan gate. **Tidak memuat teks atau label review asli.**
Kandidat geografis UNVERIFIED bukan berarti dinyatakan memenuhi scope; slotnya
ditinjau/diisi ulang setelah keputusan wilayah terdokumentasi.

## 5. Gate sebelum anotasi aktual

1. Verifikasi POI/alamat/koordinat dan inklusi administratif; dokumentasikan
   kandidat luar wilayah dan keputusan tim tanpa menghapus raw.
2. Verifikasi izin anotasi, berbagi data, pemrosesan AI, training, dan publikasi
   sesuai kebutuhan penggunaan. Status saat ini PERMISSION_NOT_VERIFIED.
3. Selesaikan triage simbol/emoji, pengulangan teks, bahasa/relevansi dan privasi.
4. Bekukan versi guideline/schema dan protokol annotator; buat paket annotator
   tanpa bintang, keyword hints, label AI, dan identitas yang tidak diperlukan.

Persiapan metodologi dan daftar kandidat tidak menyatakan bahwa gate telah lulus.

## 6. Rancangan QA Tahap 4 — belum dilaksanakan

Setelah izin dan scope selesai, dua annotator manusia menilai independen. Rencana
awal 250 kandidat dibagi **50 review kalibrasi** untuk memperjelas guideline dan
**200 review penilaian independen** setelah guideline dibekukan. Kelompok teks
duplikat/sangat mirip dan seluruh record/clauses dari satu review harus tetap
bersama; alokasi kelompok aktual dirancang setelah triage, bukan dipaksakan bila
ukuran kelompok tidak cocok dengan angka nominal.

Pada 200 review penilaian, simpan label dua manusia sebelum diskusi. Orang ketiga
mengadjudikasi disagreement; orang keempat mengaudit bukti/offset serta konsistensi.
Pisahkan hasil praadjudikasi dari gold pascaadjudikasi.

Ukuran yang direncanakan, **belum dihitung**:

- Presence: agreement mentah dan Cohen's Kappa per kategori; laporan prevalensi,
  contingency table, dan kasus kategori tanpa variasi (Kappa dapat undefined).
- Sentimen: Kappa/konfusi pada pair yang sama-sama dinilai mentioned dan memiliki
  polaritas terselesaikan; laporkan denominator dan disagreement presence terpisah.
- Aspect detection: micro/per-aspect precision, recall, F1 dan macro-F1 terhadap
  gold; set-aspek adalah multi-label. Empty set bukan enam sentimen netral.
- Sentimen per aspek: Macro-F1 tiga kelas, per-class support dan confusion matrix;
  mixed/uncertain dilaporkan terpisah, tidak disembunyikan sebagai neutral.
- Evidence: audit quote/offset dan error kategori, negasi, implicit target,
  overlap, mixed, slang/sarkasme, serta aspek di luar taksonomi.

Untuk Kappa presence, keputusan biner adalah mentioned/not_mentioned. Uncertain
diperlakukan sebagai abstention: laporkan jumlah dan coverage pair yang dapat
dinilai, lalu hitung agreement pada pair yang sama-sama memiliki keputusan
biner, sambil melaporkan disagreement/abstention pada seluruh universe. Untuk
Kappa sentimen tiga kelas, mixed/uncertain bukan kelas tambahan; keluarkan dari
denominator tersebut dan laporkan jumlahnya terpisah. Jangan hanya menyajikan
agreement pada subset mudah tanpa menyebut coverage dan kasus yang dikeluarkan.

Precision=TP/(TP+FP), recall=TP/(TP+FN), F1=2PR/(P+R); denominator nol dilaporkan
dengan konvensi eksplisit, bukan mengarang agreement. Kappa mengoreksi kesepakatan
yang diharapkan dari marginal annotator dan sensitif terhadap prevalensi; jangan
memakai satu threshold universal sebagai bukti validitas taksonomi.

## 7. Gold, perbandingan AI-manusia, dan leakage

Rencana awal: gold 200 review hasil adjudikasi, dengan sekitar **50 review locked
validation** dan sisanya untuk pengembangan protokol setelah grouping. Review
kalibrasi bukan independent holdout. Jangan melakukan prompt tuning menggunakan
locked gold; jangan memperlihatkan label manusia kepada AI saat evaluasi. Akses
review oleh AI hanya setelah izin sesuai jalur pemrosesan yang dipilih.

Bandingkan AI dengan gold menggunakan task/denominator yang sama dan laporkan
disagreement khususnya aspek langka, no-keyword, implicit, dan mixed. Klaim performa
baru dibuat setelah eksperimen aktual. Pilot ini bukan final model test set secara
otomatis: jika dipakai untuk revisi guideline/prompt/fitur, pisahkan dari final
test penelitian. Bekukan grouping review/duplikasi sebelum split; seluruh record
aspek/clauses dari review yang sama berada pada split sama. Pertimbangkan holdout
kedai bila tujuan generalisasi ke kedai baru, dengan metrik terpisah.

## 8. Versioning dan keputusan yang menunggu pilot

Catat taxonomy version, guideline/schema hash, dataset hash, candidate manifest,
seed, annotator anonim, waktu kerja, AI model/prompt/version bila kelak digunakan,
serta alasan adjudikasi. Perubahan definisi kategori memerlukan versi baru dan
review ulang label terdampak; jangan mencampur label lintas versi tanpa migrasi.

Pilot perlu menguji (a) pemisahan cleanliness/facilities/ambience; (b) perluasan
price ke value; (c) menu/porsi dalam product; (d) task implicit; (e) granularitas
mixed; (f) penanganan pujian umum; (g) aktivasi location/accessibility; dan (h)
kecukupan sampling aspek langka. Tidak ada keputusan tersebut yang diklaim telah
tervalidasi empiris sekarang.
