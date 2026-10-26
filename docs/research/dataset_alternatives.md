# Alternatif Sumber Data BrewScope selain Scraping Google Maps

**Tanggal audit:** 24 Oktober 2026  
**Cakupan:** dataset teks berbahasa Indonesia, ABSA/sentimen, domain F&B/hospitality, serta strategi pengumpulan data primer coffee shop Jatinangor.

## Ringkasan keputusan

Tidak ditemukan satu dataset publik yang sekaligus memenuhi seluruh kebutuhan berikut:

1. ulasan coffee shop di Jatinangor;
2. memiliki identitas kedai dan metadata lokasi;
3. berlabel aspek dan sentimen;
4. memiliki lisensi serta provenance yang tidak ambigu; dan
5. dapat dipakai untuk insight kompetitor lokal.

Karena itu, strategi yang paling defensible untuk BrewScope adalah **hybrid**:

- **data primer Jatinangor** menjadi dataset utama untuk evaluasi akhir dan insight bisnis;
- **dataset publik berlisensi eksplisit** hanya menjadi data tambahan, sumber kamus aspek, atau benchmark;
- semua klaim tentang kondisi pasar Jatinangor dihitung hanya dari data primer Jatinangor, bukan dari dataset luar daerah atau domain lain.

Rekomendasi praktis untuk proyek tiga minggu:

> Kumpulkan ulasan baru melalui formulir ber-consent yang disebarkan dengan QR di 5–6 coffee shop dan komunitas kampus. Gunakan Telkom Restaurant ABSA (CC0) untuk membantu aspek serta NusaX-Senti (CC BY-SA 4.0) sebagai benchmark sentimen bahasa Indonesia/Sunda. Jangan gunakan dataset eksternal sebagai dasar peringkat kedai Jatinangor.

## Kriteria kelayakan dataset

Sebelum sebuah dataset masuk pipeline, tim harus dapat menjawab:

- Siapa penerbit atau pemilik dataset?
- Dari platform atau proses apa teks diperoleh?
- Apakah lisensi mencakup **data**, bukan hanya kode repository?
- Apakah lisensi mengizinkan penggunaan, modifikasi, pelatihan ML, dan publikasi hasil?
- Apakah isi dataset nyata, sintetis, atau hasil anotasi otomatis?
- Apakah tersedia label sentimen, aspek, kedai, serta lokasi?
- Apakah sumbernya cukup relevan untuk klaim pasar Jatinangor?

Jika lisensi atau hak atas teks ulasan pihak ketiga tidak jelas, status kandidat adalah **tahan/jangan digunakan**, meskipun filenya dapat diunduh.

## Matriks kandidat terverifikasi

| Kandidat | Domain dan label | Lisensi/provenance | Kedai/lokasi Jatinangor | Keputusan |
|---|---|---|---|---|
| Telkom Restaurant ABSA | Review restoran Indonesia; token dan tag aspect term | CC0 pada Telkom University Dataverse | Tidak | **Layak sebagai data bantu deteksi aspek**, bukan klasifikasi sentimen atau insight lokal |
| NusaX-Senti | Sentimen tiga kelas; Indonesia dan 10 bahasa lokal termasuk Sunda | Dataset CC BY-SA 4.0; kode Apache-2.0 | Tidak | **Layak sebagai benchmark/data bantu sentimen** |
| Indonesian Travel Reviews | Attraction, hotel, restaurant; review + ringkasan, tanpa label ABSA | CC BY 4.0 pada Mendeley Data | Tidak | **Layak bila tim bersedia menganotasi subset restoran** |
| PRDECT-ID | Review produk Tokopedia; emosi dan sentimen | CC BY 4.0 pada Mendeley Data | Tidak | Opsional; domain dan label kurang sesuai |
| IndoNLU SmSA | Sentimen tiga kelas, multi-domain | Lisensi tidak konsisten antar-sumber resmi/agregator; teks berasal dari platform pihak ketiga | Tidak | **Tahan sampai ada klarifikasi tertulis** |
| IndoNLU CASA | ABSA review otomotif | Masalah lisensi sama; domain mobil | Tidak | **Tidak disarankan untuk model final** |
| IndoNLU HoASA | ABSA review hotel | Masalah lisensi sama; asal AiryRooms | Tidak | Secara struktur berguna, tetapi **tahan sampai lisensi data jelas** |
| Indonesian F&B ABSA (Zenodo) | 800 review; 4 aspek dan 3 polaritas | Kolom lisensi kosong; campuran Google Reviews dan kartu review internal | Tidak | **Jangan digunakan sebelum izin tertulis** |
| Indonesian Coffee Sentiment (Hugging Face) | Coffee product; diklaim 10.500 baris | Dataset card menyatakan sintetis, tetapi repository sedang kosong | Tidak | **Tidak layak sebagai data penelitian nyata** |
| IndoHotelABSA | Hotel ABSA; metadata hotel/kota | Halaman repositori menyebut CC BY, tetapi dokumen etik menyatakan teks pihak ketiga tidak direlisensikan | Tidak | **Jangan jadikan dataset utama** |

## Kandidat yang dapat digunakan

### 1. Telkom Restaurant ABSA — pilihan data aspek terbaik

Sumber primer: [Telkom University Dataverse, DOI 10.34820/FK2/UVHF0F](https://doi.org/10.34820/FK2/UVHF0F).

Catatan terverifikasi:

- diterbitkan oleh Ade Romadhony melalui Telkom University Dataverse;
- terms of use menampilkan **CC0 Public Domain Dedication**;
- domainnya review restoran berbahasa Indonesia;
- file terdiri dari 50.536 baris token dan tiga kolom: `Kalimat #`, `Word`, dan `Tag`;
- nomor kalimat 0–859 menunjukkan sekitar 860 unit kalimat/review;
- dataset terkait paper *Aspect Term Extraction Using Deep Learning-Based Approach on Indonesian Restaurant Reviews*.

Keterbatasan penting:

- dataset ini dibuat untuk **aspect term extraction**, bukan klasifikasi polaritas sentimen;
- tidak tersedia kolom `shop_id`, nama kedai, atau lokasi Jatinangor;
- satu observasi pada Dataverse adalah token, bukan satu review utuh;
- taxonomy tag perlu diaudit dan dipetakan ke lima aspek BrewScope.

Peran yang tepat:

- menyusun dan memvalidasi kamus kandidat aspek;
- eksperimen tambahan untuk aspect term extraction;
- membantu menemukan kosakata `product`, `price`, `service`, dan `ambience`;
- tidak dipakai untuk menghitung performa atau reputasi coffee shop Jatinangor.

### 2. NusaX-Senti — pilihan auxiliary sentiment paling defensible

Sumber primer: [repository resmi NusaX](https://github.com/IndoNLP/nusax) dan [dataset card resmi NusaX-Senti](https://huggingface.co/datasets/indonlp/NusaX-senti).

Catatan terverifikasi:

- mencakup bahasa Indonesia, Inggris, serta 10 bahasa lokal Indonesia, termasuk Sunda;
- task sentimen memiliki tiga kelas: negatif, netral, dan positif;
- dataset card menyediakan 500 data train, 100 validation, dan 400 test untuk setiap bahasa;
- repository menyatakan lisensi dataset **CC BY-SA**, sedangkan dataset card memperjelas versinya sebagai **CC BY-SA 4.0**;
- kode repository berlisensi Apache-2.0;
- data merupakan korpus paralel dari dataset sentimen yang diterjemahkan dan diverifikasi penutur lokal.

Keterbatasan penting:

- bukan ABSA;
- bukan dataset khusus coffee shop;
- tidak memiliki nama kedai dan lokasi Jatinangor;
- jika tim mendistribusikan dataset turunan, ketentuan atribusi dan *share-alike* CC BY-SA 4.0 harus dipatuhi.

Peran yang tepat:

- benchmark klasifikasi sentimen bahasa Indonesia;
- pengujian robustness terhadap bahasa Sunda yang mungkin muncul dalam respon Jatinangor;
- eksperimen augmentasi training yang hasilnya tetap diuji pada test set primer Jatinangor;
- bukan sumber market insight.

### 3. Indonesian Travel Reviews — opsi data restoran yang perlu dianotasi

Sumber primer: [Mendeley Data, DOI 10.17632/x2r86kfrhp.1](https://data.mendeley.com/datasets/x2r86kfrhp/1).

Catatan terverifikasi:

- berlisensi **CC BY 4.0**;
- mencakup tiga kategori: attraction, hotel, dan restaurant;
- setiap kategori berisi 100 objek, masing-masing dengan lima review dan satu ringkasan buatan pakar;
- tujuan aslinya adalah text summarization, bukan sentiment analysis atau ABSA.

Peran yang tepat:

- subset 500 review restoran dapat dianotasi sendiri sebagai eksperimen domain tambahan;
- dapat menjadi data pilot untuk menyempurnakan guideline anotasi;
- tidak boleh dianggap mewakili Jatinangor karena identitas wilayah dan sampling lokal tidak memenuhi tujuan tersebut.

### 4. PRDECT-ID — hanya auxiliary umum

Sumber primer: [Mendeley Data, DOI 10.17632/574v66hf2v.1](https://data.mendeley.com/datasets/574v66hf2v/1).

Dataset ini berlisensi **CC BY 4.0** dan berisi review produk Tokopedia dari 29 kategori dengan label emosi/sentimen serta beberapa metadata. Dataset ini berguna untuk eksperimen bahasa ulasan konsumen, tetapi bukan ABSA, bukan domain F&B, dan bukan Jatinangor. Prioritasnya lebih rendah daripada NusaX dan Telkom Restaurant ABSA.

## Kandidat yang tidak boleh langsung digunakan

### IndoNLU SmSA, CASA, dan HoASA

[Paper IndoNLU](https://aclanthology.org/2020.aacl-main.85/) menjelaskan:

- SmSA adalah komentar/review multi-platform dengan label positif, negatif, dan netral;
- CASA berisi sekitar seribu review kendaraan dengan enam aspek;
- HoASA berasal dari review hotel AiryRooms dan memiliki sepuluh aspek.

Ukuran split pada distribusi resmi adalah:

| Dataset | Train | Validation | Test |
|---|---:|---:|---:|
| SmSA | 11.000 | 1.260 | 500 |
| CASA | 810 | 90 | 180 |
| HoASA | 2.283 | 285 | 286 |

Masalah utamanya bukan hanya domain. [Root repository IndoNLU](https://github.com/IndoNLP/indonlu/blob/master/LICENSE) menggunakan Apache-2.0, sementara [dataset card IndoNLU di Hugging Face](https://huggingface.co/datasets/indonlp/indonlu) menyatakan MIT. Folder dataset tidak menyediakan lisensi data per komponen, sedangkan teks berasal dari platform pihak ketiga. Oleh karena itu, tim tidak boleh menyatakan lisensinya sudah pasti atau meredistribusikan data sebelum memperoleh klarifikasi dari maintainer/pemilik data.

### Indonesian Food and Beverage Review Dataset for ABSA

[Record Zenodo](https://zenodo.org/records/19238471) sangat dekat dengan topik: 800 review F&B, aspek food/beverages, service, price, dan ambience, serta polaritas positif/negatif/netral. Namun, bagian `Rights — License` kosong dan deskripsi menyatakan data merupakan campuran Google Reviews dan kartu review internal. Tidak ada bukti pada record bahwa depositor berhak melisensikan ulang semua teks tersebut. Status: **jangan digunakan sampai izin dan pemisahan sumber dibuktikan**.

### Indonesian Coffee Sentiment & Reviews

[Dataset card Hugging Face](https://huggingface.co/datasets/Hadisawara/indonesian-coffee-sentiment-reviews) terlihat menarik karena mengklaim 10.500 contoh coffee review dan lisensi MIT. Namun:

- repository saat audit menyatakan dataset kosong;
- card mengakui data dibuat dari template sintetis;
- label sentimen diturunkan dari template/rating dan skor aspek dibuat berkorelasi secara terkontrol;
- data tidak merepresentasikan opini pelanggan nyata.

Dataset ini boleh dipakai untuk smoke test perangkat lunak, tetapi tidak untuk hasil penelitian atau insight pasar.

### Dataset turunan Google Reviews dengan badge lisensi terbuka

Badge MIT/CC BY pada sebuah repository tidak otomatis membuktikan bahwa depositor memiliki hak untuk melisensikan ulang teks ulasan pihak ketiga. Contohnya, [IndoHotelABSA di Mendeley Data](https://data.mendeley.com/datasets/9vhzg5wkf9/1) menampilkan CC BY 4.0, tetapi dokumentasi etik proyek membedakan anotasi buatan peneliti dari teks review pihak ketiga dan menyatakan teks tersebut tidak direlisensikan.

Kandidat lain yang sumbernya Google Maps atau platform ulasan, meskipun berada di GitHub/Kaggle/Zenodo dan memiliki label lisensi repository, harus ditahan sampai hak atas konten asli dibuktikan.

## Sumber data primer Jatinangor

Data primer adalah satu-satunya jalur yang langsung mendukung keputusan tentang pasar coffee shop Jatinangor.

### Kanal pengumpulan yang disarankan

1. **QR di coffee shop mitra**  
   Kedai membantu menaruh QR atau menyebarkan tautan. Responden menulis pengalaman mereka sendiri ke formulir penelitian. Kedai tidak menyerahkan Google Reviews.

2. **Komunitas kampus Jatinangor**  
   Sebarkan formulir ke mahasiswa/pengunjung yang benar-benar pernah datang ke kedai target. Terapkan pertanyaan penyaring tentang kedai dan rentang waktu kunjungan.

3. **Intercept survey**  
   Anggota tim meminta pelanggan yang baru selesai berkunjung mengisi formulir singkat secara sukarela. Metode ini mengurangi bias ingatan.

4. **Kemitraan atas feedback internal**  
   Data dari form/kartu feedback milik kedai hanya digunakan jika kedai dapat memberikan izin tertulis dan pemberitahuan kepada pelanggan memang mengizinkan penelitian serta pelatihan ML. Jika dasar izinnya tidak jelas, gunakan kemitraan hanya untuk merekrut responden baru.

5. **Data donation / ulasan baru**  
   Responden menulis ulang pengalaman mereka dengan kata-kata sendiri dan memberi izin langsung. Jangan meminta tim menyalin review dari halaman Google Maps.

### Desain formulir yang disarankan

Formulir sebaiknya tidak meminta nama, email, nomor telepon, username, foto, atau informasi pribadi lain yang tidak diperlukan.

Kolom minimum:

```text
response_id                 dibuat otomatis
consent_research            wajib: ya
consent_deidentified_quote  opsional
consent_dataset_release     opsional dan terpisah
shop_code
visit_recency
overall_rating              opsional, 1–5
aspect
aspect_mentioned            ya/tidak
aspect_text                 alasan dengan kata-kata responden
self_reported_sentiment     positive/neutral/negative
submitted_at
collection_channel          qr_shop/campus/intercept
```

Cara termudah menghasilkan pasangan aspek-sentimen yang bersih adalah membuat blok untuk lima aspek BrewScope. Untuk setiap aspek, responden menjawab:

1. apakah mereka ingin mengomentari aspek tersebut;
2. sentimennya positif, netral, atau negatif;
3. alasan singkat dalam teks bebas.

Satu respons kemudian dapat menghasilkan beberapa `aspect mention`. Semua mention tetap memiliki `response_id` yang sama agar tidak terpisah antara train dan test.

### Isi consent minimum

Formulir menjelaskan dengan bahasa sederhana:

- tujuan penelitian;
- data yang dikumpulkan;
- penggunaan teks untuk anotasi, training, testing, dan laporan agregat;
- sifat partisipasi yang sukarela;
- tenggat dan cara menarik data sebelum dataset dibekukan;
- masa penyimpanan dan pihak yang dapat mengakses data;
- kemungkinan menampilkan kutipan yang sudah dianonimkan, hanya jika disetujui;
- kontak tim/penanggung jawab penelitian;
- apakah dataset anonim akan dirilis atau hanya digunakan internal.

Pisahkan persetujuan penelitian internal dari persetujuan merilis dataset. Seseorang dapat setuju ikut penelitian tetapi tidak setuju teksnya dipublikasikan.

[UU Nomor 27 Tahun 2022 tentang Pelindungan Data Pribadi](https://jdih.komdigi.go.id/produk_hukum/view/id/832/t/undangundang%2Bnomor%2B27%2Btahun%2B2022) menetapkan bahwa pengumpulan harus terbatas, spesifik, sah, transparan, sesuai tujuan, aman, dan menjamin hak subjek untuk menarik persetujuan. Pedoman KEPKN juga menyediakan [contoh elemen Persetujuan Setelah Penjelasan](https://kepkn.kemkes.go.id/assets/img/keppkn/file/BUKU_PEDOMAN_DAN_STANDAR_ETIK_PENELITIAN_DAN_PENGEMBANGAN_KESEHATAN_NASIONAL%28KEPKN%29.pdf). Tim tetap harus meminta arahan dosen atau komite etik kampus tentang kebutuhan review etik formal.

### Target operasional yang realistis

Target berikut adalah usulan perencanaan, bukan jaminan kecukupan statistik:

- 5–6 coffee shop;
- 25–40 responden valid per kedai;
- 2–4 aspect mention bermakna per respons;
- sekitar 150–240 respons atau 400–900 pasangan aspek-teks;
- minimal 20–30 respons untuk pilot sebelum pengumpulan penuh;
- 20–30% sampel diperiksa ulang oleh dua anotator.

Jika target tidak tercapai, kurangi jumlah kedai dan cakupan klaim. Lebih baik membandingkan tiga kedai dengan dukungan data cukup daripada sepuluh kedai dengan sampel sangat tipis.

### Quality control

- batasi satu respons per pengalaman/kunjungan yang dilaporkan;
- gunakan `response_id`, bukan identitas pribadi;
- tandai respons identik atau pola spam;
- hapus PII yang tanpa sengaja ditulis di teks bebas;
- lakukan validasi manual apakah teks benar membahas aspek yang dipilih;
- jangan otomatis menganggap rating bintang sebagai ground truth seluruh aspek;
- catat sumber rekrutmen agar bias kanal dapat dianalisis;
- gunakan `shop_code` di dataset kerja dan ungkap nama kedai hanya sesuai keputusan etik serta izin publikasi;
- tampilkan jumlah sampel bersama setiap persentase atau ranking.

## Strategi hybrid tiga minggu

### Minggu 1 — protocol, pilot, dan data tambahan

- Hari 1–2: finalisasi daftar kedai, consent, form, taxonomy, dan dataset card kosong.
- Hari 2–3: hubungi 5–6 kedai; minta mereka menyebarkan QR, bukan menyerahkan Google Reviews.
- Hari 3: pilot pada 20–30 responden.
- Hari 4: revisi pertanyaan yang menghasilkan jawaban terlalu pendek/ambigu.
- Hari 1–5 secara paralel: unduh dan audit checksum/lisensi Telkom Restaurant ABSA serta NusaX-Senti.
- Hari 4–7: mulai pengumpulan penuh dan annotation guideline.

### Minggu 2 — freeze data dan eksperimen

- lanjutkan pengumpulan sampai hari 10 atau 11;
- anonimisasi, deduplikasi, validasi bahasa, dan review manual;
- bentuk long format per aspect mention;
- bekukan test set primer Jatinangor berdasarkan `response_id`;
- jalankan dua konfigurasi terpisah:
  - **primary-only**: train hanya dari data primer;
  - **augmented**: data publik hanya ditambahkan ke bagian training setelah pemetaan label yang terdokumentasi;
- test set final selalu hanya data primer Jatinangor dan tidak digunakan saat tuning.

### Minggu 3 — insight, pembahasan, dan produk

- pilih model dari validation/CV menggunakan Macro F1;
- evaluasi sekali pada test set primer;
- lakukan error analysis per aspek dan kelas;
- hitung insight pasar hanya dari respons primer yang lolos QC;
- gunakan ambang bukti dan keluarkan `insufficient_evidence` jika sampel tipis;
- selesaikan dashboard, paper, deklarasi sumber data, serta keterbatasan.

## Rancangan eksperimen agar sumber data tidak tercampur

| Eksperimen | Train | Validation/Test | Tujuan |
|---|---|---|---|
| E1 Primary-only | Primer Jatinangor train | Primer Jatinangor | Baseline utama dan paling relevan |
| E2 Augmented sentiment | NusaX + primer train | Primer Jatinangor | Menguji apakah data eksternal membantu generalisasi |
| E3 Aspect support | Kamus/temuan Telkom + primer train | Label manual primer | Menguji bantuan data restoran pada aspect detection |
| E4 External benchmark | NusaX split resmi | NusaX split resmi | Pembanding kemampuan umum, tidak untuk klaim lokal |

Jangan menggabungkan semua data lalu melakukan random split. Cara itu dapat membuat test set eksternal mendominasi angka dan menyembunyikan performa buruk pada teks Jatinangor.

## Data mana yang boleh menghasilkan keputusan bisnis?

| Jenis keluaran | Data yang boleh dipakai |
|---|---|
| Performa model di Jatinangor | Test set primer Jatinangor |
| Ranking atau perbandingan kedai | Data primer kedai terkait dengan ukuran sampel memadai |
| Keluhan dominan per aspek | Data primer Jatinangor yang lolos QC |
| Kamus kata aspek | Primer + Telkom Restaurant ABSA |
| Benchmark sentimen umum | NusaX-Senti |
| Klaim seluruh pasar Jatinangor | Tidak boleh dibuat bila sampling tidak representatif |

## Keputusan akhir yang disarankan

1. Jadikan **survei ber-consent** sebagai sumber utama.
2. Gunakan **Telkom Restaurant ABSA CC0** untuk membantu aspect detection.
3. Gunakan **NusaX-Senti CC BY-SA 4.0** hanya sebagai benchmark/augmentasi sentimen.
4. Simpan test set primer Jatinangor sejak awal dan jangan campur dengan data publik.
5. Batasi insight pada kedai dan responden yang benar-benar ada di dataset.
6. Jangan memakai kandidat yang lisensi data atau hak atas teks pihak ketiganya ambigu.
7. Catat DOI, versi, tanggal akses, checksum, lisensi, perubahan preprocessing, dan batas redistribusi pada `docs/dataset_card.md`.

Dengan rancangan ini, BrewScope tetap mengerjakan klasifikasi teks, ABSA, perbandingan sedikitnya tiga algoritma, dan pengambilan keputusan coffee shop Jatinangor—tanpa bergantung pada scraping Google Maps.

