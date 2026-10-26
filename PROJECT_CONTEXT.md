# Konteks Proyek BrewScope

> Dokumen ini adalah sumber konteks bersama bagi anggota tim dan AI coding agent selama pengembangan BrewScope. Jika terdapat konflik, ketentuan tugas dosen dan keputusan tim terbaru yang terdokumentasi memiliki prioritas lebih tinggi.

## 1. Ringkasan Eksekutif

**BrewScope** adalah proyek klasifikasi teks dan *Aspect-Based Sentiment Analysis* (ABSA) untuk mengubah ulasan pelanggan coffee shop menjadi:

- sentimen pada setiap aspek yang dibicarakan;
- perbandingan kekuatan dan kelemahan antarcoffee shop;
- identifikasi masalah pelanggan yang berulang; dan
- rekomendasi peluang diferensiasi serta *value proposition* yang dapat ditelusuri kembali ke bukti data.

Proyek ini merupakan **Tugas Besar Pengganti UTS** dengan waktu pengerjaan sekitar tiga minggu. Produk akhir mencakup kode program, eksperimen machine learning yang dapat direproduksi, aplikasi web interaktif, dan paper yang diarahkan untuk diajukan ke jurnal SINTA 3 atau SINTA 4.

Status saat dokumen ini dibuat: **perencanaan / praimplementasi**. Metode akuisisi yang ditetapkan oleh pemilik proyek adalah scraping ulasan Google Maps untuk coffee shop di Jatinangor; daftar kedai, periode data, target volume, dan dasar otorisasinya belum ditetapkan.

## 2. Sumber Persyaratan

Konteks proyek disusun dari dua sumber utama:

1. Project brief BrewScope: tujuan produk, metodologi ABSA, kebutuhan data, dashboard, dan prinsip integritas ilmiah.
2. Slide Tugas Besar Pengganti UTS: ketentuan kelompok, algoritma, penilaian, keluaran, dan durasi pengerjaan.

Ketentuan akademik yang harus dipenuhi:

- satu kelompok terdiri dari empat orang;
- topik berupa klasifikasi data teks;
- menggunakan sedikitnya tiga keluarga algoritma dari ANN, SVM, Ensemble Tree, dan Bayesian;
- menghasilkan kode program;
- menghasilkan paper untuk target SINTA 3 atau SINTA 4;
- menyertakan deklarasi persentase penggunaan AI dan plagiarisme di bawah 30%;
- diselesaikan dalam rentang sekitar tiga minggu.

Komponen penilaian yang terbaca pada slide:

| Komponen | Bobot |
|---|---:|
| Presentasi | 15% |
| Topik | 20% |
| Metode | 25% |
| Kesimpulan dan pembahasan | 40% |

Karena kesimpulan dan pembahasan memiliki bobot terbesar, proyek tidak boleh berhenti pada perbandingan nilai akurasi. Analisis kesalahan, interpretasi hasil, keterbatasan, dan hubungan temuan dengan konteks bisnis harus menjadi bagian utama pekerjaan.

## 3. Pernyataan Masalah

Calon pengusaha coffee shop perlu memahami kondisi kompetitor dan kebutuhan pelanggan, tetapi volume ulasan membuat analisis manual tidak efisien. Sentimen pada sebuah ulasan juga tidak selalu tunggal. Satu ulasan dapat memuji produk tetapi mengeluhkan pelayanan atau fasilitas.

BrewScope harus menjawab pertanyaan berikut:

1. Aspek apa yang dibicarakan pelanggan?
2. Bagaimana sentimen positif, netral, atau negatif terhadap setiap aspek tersebut?
3. Algoritma mana yang memberikan performa paling baik dalam kondisi eksperimen yang adil?
4. Apa kekuatan dan kelemahan coffee shop yang didukung oleh dataset?
5. Masalah apa yang muncul secara konsisten dan dapat menjadi peluang diferensiasi?
6. Bagaimana temuan tersebut diterjemahkan menjadi rekomendasi yang transparan tanpa membuat klaim bisnis berlebihan?

## 4. Tujuan

### 4.1 Tujuan machine learning

- Membangun pipeline pengolahan teks berbahasa Indonesia.
- Mendeteksi kandidat aspek menggunakan pendekatan berbasis aturan.
- Mengklasifikasikan sentimen untuk pasangan aspek dan teks.
- Membandingkan beberapa keluarga algoritma secara adil.
- Memilih model berdasarkan eksperimen aktual, dengan Macro F1 sebagai metrik utama.
- Mengevaluasi deteksi aspek dan klasifikasi sentimen secara terpisah serta *end-to-end*.

### 4.2 Tujuan bisnis

- Mengidentifikasi aspek yang diapresiasi dan dikeluhkan pelanggan.
- Membandingkan performa aspek antarcoffee shop.
- Menemukan celah layanan atau fasilitas yang didukung bukti memadai.
- Menghasilkan rekomendasi *value proposition* berbasis aturan yang dapat dijelaskan.

### 4.3 Tujuan produk

- Menyediakan aplikasi Streamlit yang dapat digunakan secara lokal.
- Menampilkan ukuran sampel bersama setiap persentase atau kesimpulan.
- Menyediakan demo analisis untuk teks ulasan baru.
- Menampilkan status `insufficient_evidence` jika bukti tidak mencukupi.

## 5. Ruang Lingkup MVP

MVP mencakup:

- satu wilayah penelitian utama;
- akuisisi dataset melalui scraping ulasan Google Maps untuk coffee shop di Jatinangor;
- sekitar 5–10 coffee shop jika jumlah dan kualitas datanya memadai;
- ulasan berbahasa Indonesia;
- lima kategori aspek awal;
- deteksi aspek berbasis aturan dan validasi manual;
- klasifikasi sentimen berbasis machine learning;
- perbandingan sedikitnya tiga keluarga algoritma;
- agregasi sentimen per lokasi, kedai, dan aspek;
- dashboard pasar, kompetitor, eksperimen, dan peluang;
- rekomendasi berbasis aturan dan template.

Di luar cakupan MVP:

- scraping real-time setiap kali pengguna memilih lokasi;
- perluasan scraping ke luar wilayah Jatinangor;
- prediksi omzet, keuntungan, atau kelayakan investasi;
- estimasi modal otomatis dari ulasan;
- rekomendasi lokasi paling menguntungkan;
- chatbot atau ketergantungan pada LLM eksternal;
- deep learning berskala besar;
- microservices, Kubernetes, dan infrastruktur cloud kompleks;
- aplikasi mobile.

## 6. Terminologi Inti

| Istilah | Definisi proyek |
|---|---|
| Review | Satu ulasan pelanggan yang memiliki `review_id` unik. |
| Aspect | Dimensi pengalaman pelanggan yang dibicarakan dalam review. |
| Aspect mention | Kemunculan satu aspek pada review atau klausa tertentu. |
| Sentiment | Sikap positif, netral, atau negatif terhadap satu aspek yang disebutkan. |
| Not mentioned | Aspek tidak dibicarakan; bukan kelas netral. |
| Evidence | Jumlah mention, distribusi sentimen, cakupan kedai, dan contoh ulasan pendukung. |
| Opportunity | Masalah berulang yang didukung bukti dan relevan dengan konteks pengguna; bukan jaminan keuntungan. |
| Value proposition | Rekomendasi konsep berbasis opportunity, target pelanggan, dan konsep bisnis. |

Label sentimen:

```text
positive = 1
neutral  = 0
negative = -1
```

Taksonomi aspek awal:

| Kode | Aspek | Contoh cakupan |
|---|---|---|
| A1 | Product Quality | rasa kopi, makanan, minuman, menu, kualitas produk |
| A2 | Price | harga, keterjangkauan, dan nilai terhadap harga |
| A3 | Service | kecepatan, keramahan, akurasi pesanan, barista atau pegawai |
| A4 | Ambience | kenyamanan, kebersihan, suasana, dan tingkat kebisingan |
| A5 | Facilities | Wi-Fi, stopkontak, toilet, kursi, dan ketersediaan tempat duduk |

Taksonomi ini bersifat awal dan hanya boleh diubah berdasarkan audit data, pilot anotasi, serta keputusan tim yang terdokumentasi.

## 7. Pengguna dan Alur Produk

Pengguna utama adalah calon pengusaha coffee shop. Pengguna sekunder meliputi pemilik coffee shop, analis bisnis, mahasiswa, dan peneliti.

Input aplikasi:

- lokasi target, wajib;
- target pelanggan, opsional;
- konsep bisnis, opsional;
- rentang anggaran, opsional dan hanya sebagai konteks;
- pilihan kompetitor, opsional.

Output aplikasi:

1. Market Overview.
2. Aspect Performance Analysis.
3. Competitor Comparison.
4. Business Opportunity Insights.
5. Value Proposition Recommendation.
6. ML Experiment Dashboard.
7. Review Analysis Demo.

Lokasi hanya boleh ditampilkan jika dataset mendukung lokasi tersebut. Informasi anggaran tidak boleh digunakan untuk membuat estimasi finansial yang tidak berasal dari data relevan.

## 8. Strategi Data dan Etika

### 8.1 Keputusan sumber data

Dataset utama proyek **wajib diperoleh melalui scraping ulasan Google Maps** dengan batas geografis coffee shop di Jatinangor. Hasil scraping direncanakan menjadi sumber untuk validasi, preprocessing, anotasi aspek-sentimen, training, testing, agregasi kompetitor, dan pengambilan keputusan.

Metode akuisisi direncanakan sebagai batch/offline dan bukan scraping real-time dari aplikasi Streamlit. Aplikasi hanya membaca dataset dan artifact yang telah diproses sebelumnya.

Ruang lingkup pengambilan:

- wilayah: Jatinangor;
- objek: coffee shop yang masuk daftar penelitian;
- unit data: ulasan pelanggan dan metadata minimum yang diperlukan;
- bahasa utama: bahasa Indonesia;
- tujuan: eksperimen ABSA dan analisis peluang bisnis;
- frekuensi: pengambilan terjadwal selama fase akuisisi, bukan pemantauan terus-menerus.

### 8.2 Status otorisasi dan risiko

Keputusan internal bahwa data harus berasal dari scraping tidak dengan sendirinya memberikan hak atas platform atau konten pengguna. Sebelum scraper dijalankan, tim masih harus mendokumentasikan dasar otorisasi untuk pengambilan, penyimpanan, anotasi, penggunaan dalam training/testing/validation ML, penayangan kutipan, serta publikasi hasil atau dataset.

Dokumentasi resmi Google yang telah diaudit menyatakan adanya pembatasan terhadap scraping, penyimpanan ulasan, dan penggunaan Google Maps Content untuk pengembangan model ML. Temuan dan tautan sumber primer dicatat di `docs/research/google_maps_data_acquisition.md`. Risiko tersebut harus dilaporkan sebagai limitation dan tidak boleh disembunyikan dari dosen, reviewer, atau pembaca paper.

Jika dasar otorisasi belum tersedia, status dataset adalah **blocked/quarantine**: implementasi teknis dapat direncanakan, tetapi data tidak boleh dimasukkan ke eksperimen yang diklaim patuh sampai keputusan risiko diselesaikan oleh tim dan pihak yang berwenang.

### 8.3 Dokumentasi akuisisi

Setiap sumber data harus memiliki catatan:

- nama dan tautan sumber;
- pemilik atau penerbit;
- lisensi atau dasar izin;
- tanggal akses;
- metode pengambilan;
- batasan penggunaan dan redistribusi;
- cakupan geografis;
- potensi bias.

Khusus proses scraping, catat pula:

- daftar coffee shop dan URL/identifier sumber;
- tanggal dan waktu pengambilan;
- versi scraper serta konfigurasi yang digunakan;
- jumlah request, keberhasilan, kegagalan, dan retry;
- kriteria berhenti dan batas volume;
- struktur HTML/interface sumber yang menjadi dependensi;
- checksum file mentah;
- aturan deduplikasi dan anonimisasi;
- dasar otorisasi dan batas retensi data.

Dataset umum sentiment analysis atau ABSA dari domain lain dapat dipakai sebagai referensi atau eksperimen tambahan, tetapi tidak boleh menjadi dasar klaim pasar coffee shop tertentu.

Skema data mentah minimum:

```text
review_id
shop_id
shop_name
location
review_text
rating
review_date
source
```

Data harus diperiksa untuk:

- nilai kosong dan teks kosong;
- duplikasi review;
- bahasa selain Indonesia;
- review tidak relevan;
- panjang teks ekstrem;
- informasi pribadi;
- ketimpangan jumlah review antar-kedai;
- ketidakseimbangan label;
- metadata geografis yang tidak dapat diverifikasi.

## 9. Strategi Anotasi

Format pelatihan berbentuk *long format*: satu review dapat menghasilkan beberapa record aspek-sentimen.

Skema anotasi yang direkomendasikan:

```text
review_id
mention_id
shop_id
review_text
context_text
aspect
sentiment
annotation_status
annotator_id
```

`context_text` dapat berupa klausa atau potongan teks yang relevan agar sentimen pada review multi-aspek tidak tercampur. Semua mention tetap terhubung ke `review_id` induknya.

Prosedur anotasi:

1. Menyusun pedoman dengan contoh positif, netral, negatif, *not mentioned*, mixed, dan ambigu.
2. Menjalankan pilot pada sampel kecil.
3. Melakukan anotasi ganda pada sebagian data.
4. Mengukur konsistensi antar-anotator.
5. Melakukan adjudikasi pada perbedaan label.
6. Memperbarui pedoman sebelum anotasi skala penuh.

Kasus opini bertentangan terhadap aspek yang sama harus dipisahkan menjadi mention/klausa jika memungkinkan. Jika tidak dapat dipisahkan dengan andal, data ditandai ambigu untuk peninjauan manual dan tidak dipaksakan menjadi satu label.

## 10. Arsitektur Analisis

```text
Google Maps scraping dan dokumentasi akuisisi
                    ↓
       Data validation dan audit
                    ↓
      Normalisasi teks secara ringan
                    ↓
 Rule-based candidate aspect detection
                    ↓
   Pembentukan pasangan aspect + context
                    ↓
     TF-IDF dan sentiment classifier
                    ↓
       Prediksi sentimen per mention
                    ↓
    Agregasi per kedai/lokasi/aspek
                    ↓
  Opportunity scoring berbasis aturan
                    ↓
 Dashboard dan rekomendasi transparan
```

Deteksi aspek dan klasifikasi sentimen adalah dua tahap berbeda. Proyek tidak boleh mengklaim seluruh pipeline ABSA dipelajari oleh model karena tahap deteksi aspek menggunakan aturan.

## 11. Rancangan Eksperimen

Untuk memenuhi tugas secara paling aman, empat model direncanakan:

| Keluarga | Model awal | Peran |
|---|---|---|
| Bayesian | Multinomial Naive Bayes | Baseline probabilistik |
| SVM | LinearSVC | Kandidat kuat untuk fitur teks sparse |
| Ensemble Tree | Random Forest | Pembanding berbasis ensemble tree |
| ANN | MLPClassifier sederhana | Pemenuhan kategori ANN tanpa deep learning besar |

Minimum akademik adalah tiga algoritma, tetapi empat model mengurangi risiko salah tafsir terhadap slide tugas. Keputusan final harus dikonfirmasi kepada dosen jika waktu atau komputasi menjadi kendala.

Representasi input minimum:

```text
[ASPECT=service] pelayanan cukup lama meskipun kopinya enak
```

Eksperimen fitur yang dapat dibandingkan:

- word TF-IDF unigram dan bigram;
- character n-gram sebagai eksperimen tambahan;
- preprocessing minimal versus normalisasi kata informal;
- teks review penuh versus konteks/klausa yang relevan.

Prinsip eksperimen:

- satu konfigurasi memiliki identitas dan random seed;
- semua model menggunakan data split dan protokol evaluasi yang sama;
- vectorizer hanya di-fit pada training set;
- tuning hanya menggunakan training/validation atau cross-validation;
- test set dikunci sampai konfigurasi final dipilih;
- hasil negatif tetap dilaporkan;
- tidak ada metrik atau hasil eksperimen buatan.

## 12. Pemisahan Data dan Pencegahan Leakage

Satu review dapat menghasilkan beberapa aspect mention. Karena itu semua record dengan `review_id` yang sama wajib berada pada split yang sama.

Protokol awal:

- 80% training dan 20% test, disesuaikan jika distribusi data tidak memungkinkan;
- group-aware split menggunakan `review_id` sebagai grup;
- group-aware cross-validation di training set jika ukuran data mencukupi;
- deduplikasi dilakukan sebelum split;
- tidak menggunakan test set untuk memilih preprocessing, fitur, model, atau hyperparameter.

Jika distribusi kelas dan aspek tidak seimbang, proses pembagian harus memeriksa distribusi setelah split. Stratifikasi tidak boleh mengorbankan pemisahan berdasarkan grup.

## 13. Evaluasi

Metrik utama pemilihan model adalah **Macro F1**, karena label kemungkinan tidak seimbang.

Metrik sentiment classifier:

- accuracy;
- macro precision, recall, dan F1;
- weighted F1;
- precision, recall, dan F1 per kelas;
- confusion matrix;
- jumlah sampel setiap label dan aspek.

Evaluasi aspect detection:

- multilabel precision;
- multilabel recall;
- multilabel F1;
- hasil per aspek;
- analisis false positive dan false negative.

Evaluasi *end-to-end*:

- ketepatan pasangan `(aspect, sentiment)` dari review mentah;
- dampak kesalahan aspect detection terhadap hasil akhir.

Analisis kesalahan minimum:

- negasi;
- bahasa informal;
- sentimen implisit;
- review multi-aspek;
- opini bertentangan;
- kata yang ambigu antar-aspek;
- kelas netral;
- kesalahan akibat konteks terlalu panjang atau terlalu pendek.

## 14. Agregasi dan Rekomendasi Bisnis

Untuk setiap lokasi, kedai, dan aspek, sistem menghitung:

```text
total_mentions
positive_count
neutral_count
negative_count
positive_rate
negative_rate
supporting_review_count
shop_coverage
```

Penyebut persentase hanya berasal dari mention yang benar-benar membahas aspek tersebut.

Aspek terbaik atau terburuk tidak boleh ditentukan hanya dari jumlah atau persentase tunggal. Sistem harus mempertimbangkan:

- jumlah mention;
- jumlah review unik;
- proporsi sentimen;
- cakupan beberapa coffee shop;
- ambang bukti minimum;
- ketidakpastian pada sampel kecil.

Recommendation engine bersifat deklaratif dan berbasis aturan:

```text
Temuan terukur
    + relevansi target pelanggan
    + relevansi konsep bisnis
    + ambang kecukupan bukti
    = rekomendasi dan alasan
```

Rekomendasi tidak boleh menyatakan bahwa suatu konsep pasti menguntungkan. Jika bukti tidak mencukupi, keluaran wajib berupa `insufficient_evidence`.

## 15. Struktur Repository yang Direncanakan

```text
brewscope/
├── README.md
├── PROJECT_CONTEXT.md
├── PROJECT_BRIEF.md
├── pyproject.toml
├── .gitignore
├── configs/
│   ├── aspects.yaml
│   ├── experiments.yaml
│   └── recommendations.yaml
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── annotations/
├── notebooks/
│   ├── 01_data_audit.ipynb
│   ├── 02_eda.ipynb
│   └── 03_error_analysis.ipynb
├── src/brewscope/
│   ├── data/
│   ├── preprocessing/
│   ├── aspects/
│   ├── modeling/
│   ├── evaluation/
│   ├── insights/
│   └── recommendation/
├── app/
│   ├── streamlit_app.py
│   └── pages/
├── scripts/
│   ├── validate_data.py
│   ├── prepare_training_data.py
│   ├── train_models.py
│   └── generate_insights.py
├── models/
├── reports/
├── tests/
└── docs/
    ├── dataset_card.md
    ├── annotation_guidelines.md
    ├── methodology.md
    ├── experiment_results.md
    └── limitations.md
```

Notebook digunakan untuk eksplorasi dan komunikasi hasil. Logika yang dibutuhkan training atau aplikasi harus dipindahkan ke `src/brewscope/` agar dapat diuji dan digunakan kembali.

## 16. Checkpoint Implementasi

1. **Repository Setup** — lingkungan, struktur, lint, dan test dasar.
2. **Google Maps Data Acquisition & Authorization Audit** — daftar kedai Jatinangor, rancangan scraping, otorisasi, provenance, dan karantina data mentah.
3. **Data Audit & EDA** — kualitas, distribusi, bias, dan kelayakan scope.
4. **Aspect Taxonomy & Annotation Guideline** — definisi label dan kasus tepi.
5. **Pilot Annotation** — agreement dan perbaikan pedoman.
6. **Preprocessing & Aspect Detection** — baseline dan evaluasi deteksi aspek.
7. **Feature Engineering & Split** — pasangan aspek-teks dan split bebas leakage.
8. **Model Training** — Bayesian, SVM, Ensemble Tree, dan ANN.
9. **Model Evaluation** — pemilihan model dan error analysis.
10. **Business Insight Engine** — agregasi, threshold, dan recommendation rules.
11. **Streamlit Application** — integrasi artifact model dan dashboard.
12. **Testing & Documentation** — validasi akhir, paper, presentasi, dan demo.

Setiap checkpoint harus menjelaskan tujuan, input, output, validasi, keterbatasan, dan acceptance criteria. Checkpoint dependen tidak dimulai sebelum prasyarat kritisnya terpenuhi.

## 17. Acceptance Criteria Checkpoint 1

Checkpoint 1 selesai jika:

- repository Git sudah diinisialisasi;
- struktur minimum proyek tersedia;
- versi Python dan dependency manager ditetapkan;
- `README.md`, `PROJECT_CONTEXT.md`, `.gitignore`, dan `pyproject.toml` tersedia;
- package `brewscope` dapat di-import;
- test smoke berhasil;
- Ruff dan pytest dapat dijalankan;
- random seed dan lokasi artifact dikonfigurasi;
- data mentah dan artifact model tidak otomatis masuk Git;
- instruksi setup dan perintah validasi terdokumentasi;
- tidak ada dataset, review, metrik, atau hasil eksperimen fiktif.

## 18. Pembagian Kerja Awal untuk Empat Anggota

Pembagian berikut adalah titik awal, bukan silo permanen:

| Peran utama | Tanggung jawab |
|---|---|
| Data & Governance | Akuisisi, izin, audit kualitas, dataset card, dan anonimisasi |
| Annotation & NLP | Taksonomi aspek, pedoman anotasi, preprocessing, dan aspect detection |
| Modeling & Evaluation | Split, fitur, training empat model, evaluasi, dan error analysis |
| Product & Research Communication | Streamlit, insight engine, paper, presentasi, dan integrasi hasil |

Setiap hasil penting harus ditinjau minimal satu anggota lain. Semua anggota harus memahami metodologi dan hasil karena presentasi serta paper merupakan keluaran kelompok.

## 19. Integritas Ilmiah dan Penggunaan AI

Tim tidak boleh:

- membuat data pelanggan sintetis lalu menyajikannya sebagai data penelitian;
- mengarang sumber, DOI, kutipan, hasil evaluasi, atau temuan bisnis;
- melatih atau memilih model menggunakan test set;
- membiarkan mention dari review yang sama tersebar ke split berbeda;
- menyatakan seluruh sistem sebagai learned ABSA jika aspect detection masih rule-based;
- menyimpulkan kondisi seluruh pasar dari sampel terbatas;
- menyalin teks hasil AI langsung ke paper tanpa verifikasi dan penyuntingan manusia.

Penggunaan AI harus dicatat secara transparan, misalnya untuk:

- asistensi struktur kode;
- ide pengujian;
- perbaikan tata bahasa;
- penyusunan outline;
- pemeriksaan konsistensi dokumentasi.

Seluruh klaim, sitasi, kode, angka, dan interpretasi tetap harus diverifikasi oleh anggota tim. Deklarasi AI mengikuti format institusi atau jurnal tujuan; target plagiarisme tetap di bawah 30% sesuai slide tugas, tetapi tim sebaiknya mengutamakan orisinalitas dan sitasi yang benar, bukan sekadar mengejar angka pemeriksa kemiripan.

## 20. Risiko Utama

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Scraping Google Maps tidak memiliki dasar otorisasi yang memadai | Kritis | Dokumentasikan keputusan, minta penilaian/izin tertulis dari pihak berwenang, dan karantina data sampai statusnya jelas |
| Perubahan struktur halaman atau mekanisme anti-otomasi | Tinggi | Pisahkan adapter sumber, gunakan logging/checkpoint, dan jangan bergantung pada selector rapuh tanpa test |
| Data scraping tidak lengkap atau bias | Tinggi | Catat periode, kriteria pengambilan, missingness, urutan review, dan batas representativitas |
| Metadata lokasi/kedai tidak tersedia | Tinggi | Batasi klaim geografis dan fitur kompetitor |
| Waktu anotasi tidak cukup | Tinggi | Pilot lebih awal, fokus pada scope kecil tetapi berkualitas |
| Label tidak seimbang | Sedang–tinggi | Gunakan Macro F1, laporan per kelas, dan split terkontrol |
| Aspect detection lemah | Tinggi | Evaluasi terpisah, iterasi kamus, dan validasi manusia |
| Review multi-aspek membingungkan model | Tinggi | Gunakan konteks/klausa dan pasangan aspek-teks |
| Rekomendasi terlalu spekulatif | Tinggi | Threshold bukti, alasan eksplisit, dan `insufficient_evidence` |
| Paper dikerjakan terlalu akhir | Tinggi | Kumpulkan tabel, konfigurasi, gambar, dan catatan diskusi sejak eksperimen pertama |
| Overengineering | Sedang | Fokus pada pipeline lokal modular dan kebutuhan penilaian |

## 21. Keputusan yang Masih Terbuka

Keputusan berikut harus diselesaikan sebelum checkpoint terkait:

- sumber dataset telah diputuskan: scraping Google Maps untuk coffee shop di Jatinangor;
- dasar otorisasi untuk mengambil, menyimpan, mengolah, dan menggunakan ulasan dalam ML;
- daftar coffee shop, periode data, target volume, dan kriteria inklusi;
- informasi pengguna apa saja yang harus dihapus atau dipseudonimkan;
- kebijakan retensi, redistribusi, dan penghapusan data mentah;
- izin menampilkan nama kedai dan kutipan review;
- unit anotasi final dan proporsi anotasi ganda;
- aturan adjudikasi untuk mixed sentiment;
- jumlah minimum bukti untuk insight bisnis;
- kebutuhan empat model versus tiga model setelah konfirmasi dosen;
- jurnal SINTA target dan template penulisannya;
- tanggal mulai dan tenggat pasti karena slide hanya menyebut durasi dan tanggal tanpa tahun yang jelas.

## 22. Definition of Done Proyek

Proyek dianggap selesai jika:

- sumber, metode scraping, provenance, dan status otorisasi dataset terdokumentasi;
- scope scraping terbatas pada daftar coffee shop Jatinangor yang disepakati;
- data mentah memiliki checksum, log pengambilan, dan aturan retensi;
- taxonomy serta annotation guideline tersedia;
- aspect detection telah diuji terhadap label manual;
- semua model wajib berhasil dilatih dengan protokol yang sama;
- test set bebas leakage berdasarkan `review_id`;
- model terbaik dipilih dari hasil aktual menggunakan Macro F1;
- hasil dapat direproduksi dari konfigurasi dan random seed;
- error analysis dan keterbatasan terdokumentasi;
- dashboard menampilkan sample size bersama insight;
- rekomendasi dapat ditelusuri ke data pendukung;
- aplikasi dapat dijalankan lokal;
- test utama berhasil;
- paper, presentasi, kode, dan dokumentasi akhir tersedia;
- tidak ada data, metrik, sitasi, atau klaim yang difabrikasi.

## 23. Aturan Pemeliharaan Dokumen

- Perubahan scope, taxonomy, protokol evaluasi, atau aturan rekomendasi harus memperbarui dokumen ini.
- Keputusan teknis yang sulit dibatalkan sebaiknya dicatat sebagai ADR di `docs/adr/`.
- Angka hasil eksperimen tidak dimasukkan sebelum eksperimen benar-benar dijalankan.
- Bagian "Keputusan yang Masih Terbuka" diperbarui ketika keputusan disepakati.
- Semua anggota tim membaca dokumen ini sebelum mengubah pipeline inti.

