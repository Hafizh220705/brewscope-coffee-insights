# Pembagian Jobdesc dan Alur Kerja Tim BrewScope

Dokumen kerja terbaru untuk **Hafizh, Niki, Robi, dan Hamam**. Pembagian ini
menggantikan draft berbasis Anggota 1?4. Tanggal pembaruan: **26 Oktober 2026**.

## Dasar pembagian dan posisi proyek

| Hal | Keputusan kerja |
|---|---|
| Kontribusi sebelumnya | Berdasarkan keterangan Hafizh, pekerjaan dari scraping sampai infrastruktur Stage 4A telah ditangani/dikoordinasikan Hafizh. Pekerjaan ini dihitung dalam beban kumulatif. |
| Prinsip keadilan | Hafizh tidak sekaligus mendapat seluruh coding, tiga model, dashboard, dan paper. Niki/Robi/Hamam memiliki keluaran teknis dan tulisan yang dipimpin sendiri. Beban ditinjau berdasarkan waktu aktual dan kompleksitas, bukan jumlah tugas saja. |
| Status saat dibagi | Dataset raw 3.593 review, 3.582 eligible teknis, 40 kedai; audit, taxonomy, dan infrastruktur Stage 4A tersedia. Anotasi manusia/gold/evaluasi model belum selesai. |
| Anotasi manusia | Pilot/gold dikerjakan manusia sungguhan. Niki dan Robi mengisi secara independen; Hamam adjudikasi; Hafizh memeriksa QA. Penugasan ini belum berarti pekerjaan anotasi sudah dilaksanakan. |
| Penggunaan AI berikutnya | Mengikuti alur Stage 4 yang dibahas: Gemini utama, Ollama pembanding opsional untuk eksperimen setelah gold siap. Label AI ditinjau manusia dan dicatat sebagai AI-assisted; tidak menjadi human gold. |
| Model inti | SVM, Random Forest, dan Multinomial Naive Bayes sesuai brief terbaru. ANN hanya tambahan bila diwajibkan dosen, dengan pembagian ulang beban. |
| Batas jadwal | Urutan memakai milestone, tanpa tanggal selesai yang belum disepakati tim. Tenggat dan jam kerja diisi bersama setelah mengukur waktu anotasi pada kalibrasi. |

## 1. Jobdesc utama masing-masing anggota

| Anggota | Peran utama | Tugas Stage 4 | Tugas setelah Stage 4 | Bukti/output yang wajib diserahkan |
|---|---|---|---|---|
| **Hafizh** | Koordinator, pemeriksa QA, dan integrator | Menjelaskan hasil Stage 1?3 kepada tim; memastikan paket dan versi pedoman sesuai; QA semua keputusan gold dan evidence; menjalankan validator/IAA/ekspor menggunakan pipeline yang tersedia; menangani konfigurasi dan pencatatan penggunaan API | Mengintegrasikan hasil preprocessing dan tiga model; memeriksa reproducibility serta serah terima; mereview konsistensi angka final; menulis bagian dataset, scraping, audit, dan keterbatasan data berdasarkan pekerjaan sebelumnya | Catatan QA, hasil validasi/IAA aktual, snapshot dataset terversi, hasil integration check, bagian paper data. Bukan penanggung jawab tunggal implementasi semua modul |
| **Niki** | Annotator A, penanggung jawab NLP dan SVM | Mengisi 50 review kalibrasi dan 200 review independen; menyimpan evidence, kasus ambigu, serta hasil asli sebelum diskusi; membantu perbaikan pedoman saat kalibrasi | Memimpin preprocessing bersama; mempertahankan negasi dan konteks; menyiapkan input Task A/B; mengimplementasikan dan mengevaluasi keluarga SVM memakai split/fitur bersama | Anotasi A, catatan kalibrasi, preprocessing yang dapat dijalankan ulang, konfigurasi/model/prediksi/metrik SVM, tulisan taxonomy?anotasi?preprocessing dan metode SVM |
| **Robi** | Annotator B, penanggung jawab eksperimen dan Random Forest | Mengisi 50 review kalibrasi dan 200 review independen yang sama dengan Niki tanpa melihat jawabannya; menyimpan evidence dan hasil asli sebelum diskusi | Memimpin group-aware split, kontrak fitur bersama dan pemeriksaan leakage; mengimplementasikan Random Forest; menyatukan tabel perbandingan tiga model serta error analysis | Anotasi B, split manifest, konfigurasi fitur/eksperimen bersama, model/prediksi/metrik Random Forest, tabel evaluasi gabungan, tulisan desain eksperimen dan hasil |
| **Hamam** | Adjudikator, penanggung jawab Naive Bayes dan insight bisnis | Membaca pedoman dan mengikuti kalibrasi; menyelesaikan seluruh disagreement/uncertainty setelah anotasi independen dikunci; mencatat alasan; mengoordinasikan human review atas label AI berikutnya | Mengimplementasikan Multinomial Naive Bayes dengan split/fitur bersama; membuat agregasi aspek/sentimen dan prioritas perbaikan berbasis bukti; membuat tampilan/demo sederhana memakai hasil yang telah disepakati | Keputusan adjudikasi, catatan human review, model/prediksi/metrik Naive Bayes, tabel/grafik insight beserta ukuran sampel, demo sederhana, tulisan analisis bisnis dan metode Naive Bayes |

## 2. Pembagian operasional anotasi manusia

| Pekerjaan | Hafizh | Niki | Robi | Hamam | Syarat selesai |
|---|---|---|---|---|---|
| Memahami pedoman dan enam aspek | Memfasilitasi dan menjelaskan artefak | Membaca dan mencatat pertanyaan | Membaca dan mencatat pertanyaan | Membaca batas kategori/kasus ambigu | Semua memahami neutral, not_mentioned, uncertain, mixed, dan evidence |
| Kalibrasi 50 review | Memeriksa contoh dan konsistensi teknis | Mengisi paket A: 50 review ? 6 aspek = 300 keputusan | Mengisi paket B: 50 review yang sama ? 6 aspek = 300 keputusan | Membahas perbedaan bersama tim | Catatan kesepakatan dan pedoman dibekukan sebelum tahap independen |
| Anotasi independen 200 review | Memastikan paket dan akses terpisah | Mengisi seluruh 200 review ? 6 aspek = 1.200 keputusan | Mengisi seluruh 200 review yang sama ? 6 aspek = 1.200 keputusan | Menunggu kedua hasil terkunci; belum mengarahkan keputusan | A/B valid, lengkap, disimpan sebagai original, belum didiskusikan bersama |
| Agreement praadjudikasi | Menjalankan utilitas IAA dan memeriksa denominator | Memeriksa kesesuaian hasil dengan original A | Memeriksa kesesuaian hasil dengan original B | Mempelajari daftar disagreement | Raw agreement/Kappa/confusion/support/abstention tersedia dari data nyata |
| Adjudikasi | Memeriksa kelengkapan catatan | Menjelaskan alasan A setelah original dikunci | Menjelaskan alasan B setelah original dikunci | Memutuskan seluruh disagreement/uncertainty beserta evidence dan alasan | Semua pair gold terselesaikan; mixed tetap disimpan dan tidak dijadikan neutral |
| QA gold | Memeriksa seluruh 1.200 keputusan final pada 200 review, termasuk evidence/offset, serta memberi catatan QA | Memperbaiki kesalahan administratif pada revisi A bila diperlukan | Memperbaiki kesalahan administratif pada revisi B bila diperlukan | Menanggapi temuan QA dan memperbarui keputusan melalui revisi terdokumentasi | Validator lulus, QA lengkap, original tetap tersimpan, gold dapat dibentuk |
| Ekspor gold | Menjalankan pembentukan gold dan arsip provenance | Memeriksa format untuk NLP | Memeriksa ID/split untuk eksperimen | Memeriksa label adjudikasi yang diekspor | Gold menyimpan review ID, enam keputusan, split, taxonomy, dan asal keputusan |

**250 review adalah total kandidat unik.** Niki dan Robi masing-masing membaca
250 review yang sama, bukan membagi menjadi 125 review per orang. Masing-masing
mengisi 1.500 keputusan aspek termasuk kalibrasi. Sebanyak 200 review independen
terdiri dari 150 development dan 50 locked validation; A/B tidak diberi penanda
split tersebut. Kalibrasi tidak dihitung sebagai independent test.

### Pemetaan nama ke ID teknis yang sudah tersedia

| Anggota | ID/peran teknis | File kerja/acuan | Cara memakai |
|---|---|---|---|
| Niki | `human:A` / `human_A` | `data/interim/human_annotations/assignments/human_A/calibration.jsonl` dan `independent.jsonl` | Buat salinan file kerja; pertahankan ID teknis dan teks asli |
| Robi | `human:B` / `human_B` | `data/interim/human_annotations/assignments/human_B/calibration.jsonl` dan `independent.jsonl` | Kerjakan sendiri; jangan membuka hasil Niki sebelum dikunci |
| Hamam | `human:C` | Format adjudikasi dalam `docs/research/stage4_annotation_protocol.md` | Catat keputusan dan alasan setelah IAA dihitung |
| Hafizh | `human:D` | Format QA dalam `docs/research/stage4_annotation_protocol.md` | Catat pemeriksaan evidence dan konsistensi final |

## 3. Flow pengerjaan dari sekarang sampai proyek selesai

| Urutan/milestone | Penanggung jawab utama | Pendukung/reviewer | Pekerjaan dan output | Boleh dilanjutkan ketika |
|---|---|---|---|---|
| **0. Serah terima pekerjaan awal** | Hafizh | Niki, Robi, Hamam | Menunjukkan dataset, hasil audit, taxonomy, pedoman, paket pilot, cara menjalankan repo, dan masalah yang masih terbuka | Semua dapat membuka file kerja dan menjelaskan tujuan dua task ABSA |
| **1. Stage 4B ? Kalibrasi** | Niki dan Robi | Hamam membahas; Hafizh memeriksa | Dua hasil kalibrasi untuk 50 review, daftar kasus ambigu, aturan yang disepakati | Pedoman jelas dan dibekukan; jika definisi berubah, versikan dan catat dampaknya |
| **2. Stage 4B ? Independent annotation** | Niki dan Robi | Hafizh mengelola paket; Hamam menyiapkan format adjudikasi | Original A/B untuk 200 review, lengkap enam keputusan dan evidence | Kedua original dikunci serta lolos validasi; tidak saling melihat hasil sebelumnya |
| **3. Stage 4B ? IAA, adjudikasi, QA, gold** | Hafizh untuk IAA/QA; Hamam untuk adjudikasi | Niki dan Robi menjelaskan disagreement | IAA praadjudikasi, keputusan beralasan, QA, human gold dan provenance | Tidak ada unresolved pair pada gold; original utuh; schema/evidence/split valid |
| **4. Stage 4C ? Eksperimen AI** | Hafizh menjalankan pipeline yang tersedia | Robi memeriksa metrik; Niki meninjau kesalahan bahasa; Hamam meninjau kesalahan kategori/bisnis | Eksperimen Gemini, Ollama opsional; development untuk perbaikan prompt, locked untuk evaluasi akhir; konfigurasi dipilih berdasarkan hasil nyata | API/kuota jelas, gold tersedia, kriteria dipraregistrasi sebelum locked; hasil memenuhi kriteria |
| **5. Stage 4D ? Labeling dan human review** | Hafizh menjalankan batch; Hamam mengoordinasikan review | Niki/Robi membantu review sesuai antrean; seluruh tim memeriksa lokasi | Checkpoint, hasil AI tervalidasi, koreksi manusia, audit acak, arsip dan ekspor presence/sentiment | Scope final dan persetujuan full tersedia; seluruh data dalam scope selesai sesuai QC; tidak ada label tanpa provenance |
| **6. Stage 5 ? Preprocessing, split, fitur** | Niki: preprocessing; Robi: split dan fitur bersama | Hamam memeriksa kesesuaian Naive Bayes; Hafizh review integrasi | Dataset model, preprocessing, split manifest, TF-IDF/pipeline bersama, pemeriksaan leakage | Label/QC siap; review dan duplikat satu split; transformer hanya fit pada training |
| **7. Stage 6 ? Tiga model paralel** | Niki: SVM; Robi: Random Forest; Hamam: Multinomial Naive Bayes | Hafizh memeriksa reproducibility lintas model | Eksperimen Task A deteksi aspek dan Task B sentiment, konfigurasi/prediksi/metrik/artifact tiap keluarga | Ketiganya memakai definisi task, dataset, split dan prosedur evaluasi yang sama |
| **8. Stage 6 ? Evaluasi akhir** | Robi menyatukan laporan | Niki/Hamam menyerahkan hasil; Hafizh mereview angka | Perbandingan detection micro/macro F1, sentiment macro F1/accuracy/per-class, confusion, end-to-end dan error analysis | Pemilihan selesai pada validation; test hanya untuk evaluasi final, tanpa tuning menggunakan test |
| **9. Analisis bisnis dan demo** | Hamam | Niki memeriksa interpretasi aspek; Robi memeriksa hitungan; Hafizh mengintegrasikan | Keunggulan, kelemahan, prioritas perbaikan per kedai/aspek; ukuran sampel dan keterbatasan; demo sederhana | Semua rekomendasi dapat ditelusuri ke data/label dan jumlah bukti memadai; lokasi yang ditampilkan sudah diputuskan |
| **10. Paper, presentasi, dan finalisasi** | Semua sesuai bagian masing-masing | Review silang dan rehearsal bersama | Kode dapat dijalankan, artifact/hasil aktual, paper, deklarasi AI, slide dan demo | Seluruh angka cocok dengan laporan, pembahasan/limitations lengkap, semua anggota memahami hasil |

## 4. Pekerjaan yang dapat berjalan paralel

| Saat pekerjaan utama berlangsung | Hafizh | Niki | Robi | Hamam |
|---|---|---|---|---|
| Kalibrasi | Memeriksa setup dan konfigurasi Gemini; melengkapi catatan sumber | Membaca/mengisi A | Membaca/mengisi B | Menguasai pedoman dan menyusun daftar kasus sulit |
| Anotasi independen | Menyiapkan pemeriksaan format dan QA | Fokus pada A; belum memakai hasil AI | Fokus pada B; belum memakai hasil AI | Menyiapkan format adjudikasi dan kerangka tulisan, tanpa mengarahkan A/B |
| Menunggu validasi API/kuota | Menyelesaikan konfigurasi dan pencatatan hasil pemeriksaan | Melanjutkan pekerjaan manusia | Melanjutkan pekerjaan manusia | Melanjutkan adjudikasi bila A/B sudah lengkap |
| Scope geografis | Memeriksa 10 kedai dan menggabungkan tabel keputusan | Memeriksa 10 kedai | Memeriksa 10 kedai | Memeriksa 10 kedai |
| Label massal/QC | Memantau batch dan validasi teknis | Membantu kasus bahasa dan menyiapkan desain preprocessing dari fixture | Membantu pemeriksaan konsistensi dan menyiapkan rancangan eksperimen dari fixture | Mengoordinasikan antrean review dan menyiapkan rancangan agregasi dari fixture |
| Modeling | Menjalankan pemeriksaan integrasi dan melengkapi dokumentasi data | Melatih/menganalisis SVM | Melatih/menganalisis Random Forest | Melatih/menganalisis Naive Bayes |
| Penulisan | Dataset, scraping, audit dan keterbatasan data | Anotasi, taxonomy, NLP dan SVM | Protokol eksperimen, Random Forest dan evaluasi | Naive Bayes, insight bisnis, demo dan integrasi naskah |

Daftar 40 kedai dibagi 10 per anggota dari tabel verifikasi sebelum mulai,
sehingga tidak tumpang tindih. Status hanya diubah jika bukti identitas dan batas
wilayah memadai. Jika belum jelas, tetap UNVERIFIED. Tidak ada klaim seluruh
kedai sudah berada di Kecamatan Jatinangor.

## 5. Serah terima dan review silang

| Hasil | Pemilik | Reviewer | Isi serah terima minimum |
|---|---|---|---|
| Original anotasi | Niki / Robi, terpisah | Hafizh: format; Hamam: setelah dikunci | File original, versi pedoman, daftar kasus tidak pasti; tanpa menimpa revisi sebelumnya |
| Adjudikasi | Hamam | Hafizh | Keputusan final, evidence dan alasan setiap disagreement/uncertainty |
| Dataset Stage 5 | Hafizh mengelola ekspor | Niki dan Robi | Hash/version, schema, label_source, ID/group/split, status lokasi, hasil QC |
| Preprocessing | Niki | Hamam | Kode/konfigurasi, contoh input-output, perlakuan negasi, cara mereproduksi |
| Split dan fitur | Robi bersama Niki | Hafizh | Daftar ID per split, kelompok duplikat, parameter fitur, bukti fit hanya training |
| SVM | Niki | Robi | Konfigurasi, seed, model, prediksi dan metrik dari split yang sama |
| Random Forest | Robi | Hamam | Konfigurasi, seed, model, prediksi dan metrik dari split yang sama |
| Naive Bayes | Hamam | Niki | Konfigurasi, seed, model, prediksi dan metrik dari split yang sama |
| Tabel evaluasi gabungan | Robi | Hafizh | Angka dari artifact nyata, support, denominator dan analisis kesalahan |
| Insight dan demo | Hamam | Robi: hitungan; Niki: aspek; Hafizh: integrasi | Sumber label/prediksi, ukuran sampel, rumus/aturan, alasan prioritas, keterbatasan |

Setiap pemilik memperbaiki modulnya sendiri ketika ditemukan masalah; integrasi
bukan berarti seluruh revisi dikembalikan ke Hafizh. Reviewer tidak menilai
hasil miliknya sendiri sebagai satu-satunya pemeriksa.

## 6. Pembagian paper dan presentasi

| Bagian | Penulis/pembicara utama | Kontributor/reviewer |
|---|---|---|
| Masalah penelitian dan manfaat bisnis | Hamam | Hafizh menyesuaikan dengan scope aktual; semua menyepakati klaim |
| Data, scraping, audit dan provenance | Hafizh | Robi memeriksa angka; Niki/Hamam memeriksa keterbacaan |
| Taxonomy, anotasi, agreement dan preprocessing | Niki | Robi menjelaskan anotasi B; Hamam adjudikasi; Hafizh IAA/QA |
| Split, fitur dan desain eksperimen | Robi | Niki memeriksa preprocessing/fitur; Hafizh memeriksa leakage |
| SVM | Niki | Robi |
| Random Forest | Robi | Hamam |
| Multinomial Naive Bayes | Hamam | Niki |
| Hasil, perbandingan dan error analysis | Robi menggabungkan | Niki/Hamam menulis temuan modelnya; Hafizh memeriksa konsistensi |
| Insight bisnis dan demonstrasi | Hamam | Niki/Robi memeriksa interpretasi dan hitungan |
| Discussion, limitations dan conclusion | Semua menulis temuan area masing-masing | Hamam menyatukan naskah; Hafizh memeriksa konsistensi akhir |
| Sitasi, format, deklarasi AI dan materi presentasi | Semua bertanggung jawab atas bagiannya | Hamam menggabungkan format; simulasi presentasi seluruh anggota |

## 7. Kapan tahap dianggap selesai

| Tahap | Kriteria selesai |
|---|---|
| Stage 4B | Dua original manusia tersedia; IAA dihitung sebelum adjudikasi; gold sudah diadjudikasi dan lolos QA |
| Stage 4C | Evaluasi AI terhadap gold tersedia, analisis kesalahan selesai, kriteria mutu terpenuhi dan konfigurasi dipilih berdasarkan hasil |
| Stage 4D / seluruh Stage 4 | Seluruh data eligible dalam scope final selesai dilabeli dan direview sesuai protokol; checkpoint/arsip lengkap; ekspor presence/sentiment valid dan siap Stage 5 |
| Stage 5 | Preprocessing/split/fitur dapat direproduksi dan bebas leakage yang diperiksa |
| Stage 6 | Tiga keluarga model sudah dibandingkan dengan prosedur adil, evaluasi final dan error analysis tersimpan |
| Proyek keseluruhan | Kode, hasil aktual, analisis bisnis, paper, deklarasi dan presentasi/demo telah direview bersama |

## 8. Monitoring agar beban tetap adil

| Mekanisme | Pelaksanaan |
|---|---|
| Langkah pertama | Hafizh melakukan serah terima singkat; Niki/Robi mulai kalibrasi; Hamam membaca pedoman dan menyiapkan pembahasan |
| Pencatatan progres | Tiap anggota mencatat tugas, waktu aktual, lokasi artifact, status dan blocker; jangan mengisi kontribusi yang belum dilakukan |
| Ukur beban anotasi | Catat durasi aktual kalibrasi; gunakan untuk memperkirakan 200 review independen, bukan menebak kecepatan universal |
| Rebalancing | Bila disagreement/QC besar, stabilkan pedoman dan kurangi beban downstream Hamam/Hafizh; bila NLP/modeling berat, sederhanakan tampilan dan bagi ulang pekerjaan non-anotasi tanpa mengubah independensi A/B |
| Milestone review | Review bersama setelah kalibrasi, gold, data model, evaluasi, dan draft paper; setiap hasil memiliki pemilik serta reviewer |
| Pekerjaan tambahan | ANN, eksperimen ekstra, atau UI tambahan memerlukan pembagian ulang; tidak otomatis menjadi tugas Hafizh |
| Prioritas | Label dan evaluasi yang benar, pembahasan yang kuat, lalu tampilan. Jangan mengorbankan kualitas gold demi mengejar kosmetik aplikasi |

Rujukan implementasi: [protokol Stage 4](../research/stage4_annotation_protocol.md),
[pedoman anotasi](../research/annotation_guidelines.md), dan
[laporan Stage 4](../../reports/stage4_annotation_report.md). Pemeriksaan API
terbaru ada pada `reports/stage4_gemini_connection_check.json`; key sudah terbaca,
tetapi model lookup terakhir menerima HTTP 429. Anotasi manusia dapat berjalan
sambil akses model dan kuota diselesaikan. Tidak ada proses anotasi real yang
dinyatakan sudah selesai hanya karena rencana ini telah dibuat.
