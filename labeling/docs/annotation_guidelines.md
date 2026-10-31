# Pedoman anotasi ABSA BrewScope

Versi: **0.1.0-draft**. Status: rancangan berbasis literatur, **belum divalidasi
melalui anotasi korpus**. Semua contoh di dokumen/config/notebook ini **sintetis**.
Tidak ada contoh yang merupakan kutipan review pelanggan yang sedang diaudit.

Taksonomi machine-readable: `configs/aspect_taxonomy.yaml`. Schema:
`schemas/annotation_schema.json`. Jejak literatur dan adaptasi ada di
`aspect_taxonomy_literature_review.md` serta `stage3_methodology_decisions.md`.

## 1. Batas penggunaan dan unit anotasi

Tahap 3 hanya menyusun metode, memvalidasi contoh sintetis, dan memilih kandidat
pilot tanpa label. Seluruh 40 lokasi dan hak penggunaan data masih belum
terverifikasi. Membuka/membagikan isi review untuk anotasi manusia atau AI aktual
menunggu penyelesaian gate pada dokumen keputusan metodologi. CSV kandidat bukan
persetujuan untuk mengirim data ke layanan eksternal.

Unit penyimpanan adalah **review–aspek–annotator**, dengan satu atau lebih bukti
opini di dalamnya. Review lengkap menjadi konteks interpretasi; jangan memberikan
satu sentimen umum kepada review yang membicarakan beberapa aspek.
Annotator tidak diperlihatkan rating bintang, keyword hints, output AI, atau label
annotator lain. Identitas kedai disamarkan bila tidak dibutuhkan untuk memahami teks.

## 2. Enam kategori aktif dan satu kandidat provisional

| ID | Makna operasional | Batas penting |
|---|---|---|
| `product_quality` | Mutu makanan/minuman, rasa, kesegaran, porsi, variasi menu, presentasi | Waktu tunggu adalah service; harga adalah price_value |
| `service` | Keramahan, pemesanan, kecepatan/respons staf, penanganan komplain | Internet lambat adalah facilities |
| `price_value` | Harga, keterjangkauan, promosi, kesepadanan biaya/manfaat | Porsi tanpa evaluasi biaya tetap product_quality |
| `ambience` | Suasana, interior, musik, kebisingan, kenyamanan belajar/bekerja | Fungsi amenitas adalah facilities; kotor/bersih adalah cleanliness |
| `facilities` | Keberadaan, kapasitas, fungsi Wi-Fi/parkir/colokan/toilet/AC/kursi | Kondisi bersih toilet tidak otomatis mendapat label facilities |
| `cleanliness` | Kebersihan/higiene ruang, meja, toilet, peralatan, sampah | Makanan basi tanpa klaim higiene adalah product_quality |

`location_accessibility` dipertahankan sebagai **PROVISIONAL dan tidak aktif**.
Literatur mendukung relevansinya, tetapi pengukuran korpus/pilot lokal serta batas
antara akses jalan dan fasilitas parkir belum divalidasi. Kandidat ini tidak boleh
diam-diam masuk ke enam label aktif. Gunakan flag `out_of_taxonomy` pada kebutuhan
relevan yang belum tertampung dan bawa ke adjudikasi setelah anotasi diizinkan.

## 3. Urutan kerja annotator pada tahap berikutnya

1. Baca review lengkap dalam bentuk aslinya; jangan melakukan stemming atau
   menghapus negasi sebelum membaca.
2. Identifikasi proposisi/opini dan targetnya. Keyword hanya boleh membantu
   riset eksploratif, bukan menggantikan keputusan manusia.
3. Untuk setiap kategori aktif, tetapkan presence: `mentioned`, `not_mentioned`,
   atau `uncertain` bila keputusan memang tidak dapat dibuat.
4. Pada kategori mentioned, pilih evidence minimal yang mempertahankan objek,
   evaluasi, negasi, dan konteks yang menentukan makna.
5. Tentukan polaritas tiap evidence, kemudian sentimen pair sesuai aturan mixed.
6. Catat uncertainty/coverage gap/sarkasme di notes; jangan menebak tanpa bukti.
7. Simpan independen, lalu jalani pemeriksaan/adjudikasi sesuai protokol QA.

## 4. Presence dan sentimen

| Nilai | Penggunaan |
|---|---|
| `positive` | Penilaian menguntungkan terhadap aspek yang benar-benar disebut |
| `neutral` | Aspek disebut tanpa evaluasi polaritas yang jelas, misalnya pernyataan faktual |
| `negative` | Keluhan atau penilaian merugikan terhadap aspek yang disebut |
| `not_mentioned` | Presence; aspek tidak didukung teks, sehingga `sentiment=null` |
| `uncertain` | Status workflow/presence tidak pasti; bukan kelas sentimen keempat |

Neutral bukan pengganti teks yang tidak dipahami. Jika target/polaritas ambigu,
gunakan annotation_status=uncertain, sentiment=null, training_eligible=false,
dan notes yang menjelaskan alasan. Kasus yang belum terselesaikan tidak masuk gold.

Contoh sintetis:

- “Pelayanannya ramah.” → service mentioned, explicit, positive.
- “Pesanan baru datang setelah satu jam.” → service mentioned, implicit, negative.
  Keterlambatan pesanan mendukung target layanan tanpa kata pelayanan.
- “Di sini tersedia Wi-Fi.” → facilities mentioned, explicit, neutral jika tidak
  ada konteks evaluatif lain.
- “Kopinya enak.” → product_quality positive; kategori lain not_mentioned.
  Ketiadaan keyword tidak cukup untuk menyimpulkan not_mentioned pada review lain.
- “Bagus banget, recommended!” → jangan memberi semua aspek positive. Dalam
  taksonomi aktif ini pujian umum tanpa objek tidak mendukung kategori tertentu;
  catat general_praise/coverage gap, bukan membuat kategori bisnis baru.

## 5. Multi-aspek dan overlap

“Kopinya enak, tempatnya nyaman, tapi parkir susah.” memiliki tiga klaim terpisah:
product_quality positive, ambience positive, facilities negative. Simpan tiga
record pair dengan review_id yang sama dan evidence sesuai klaimnya.

Pilih kategori berdasarkan **objek dan predikat**, bukan nomina tunggal.

| Contoh sintetis | Keputusan |
|---|---|
| Toiletnya kotor. | cleanliness negative; tidak otomatis facilities negative |
| Toiletnya tidak tersedia. | facilities negative; tidak ada klaim cleanliness |
| Toiletnya tersedia, tetapi kotor. | facilities neutral dan cleanliness negative; dua klaim mandiri |
| Mejanya kotor. | cleanliness negative |
| Tempatnya sempit. | ambience negative untuk kenyamanan ruang; jika konteks kapasitas tempat duduk, tinjau facilities |
| Kursi kosong tidak tersedia. | facilities negative untuk kapasitas amenitas |
| Wi-Fi lambat. | facilities negative |
| Pelayanan lambat. | service negative |
| Harga mahal tapi porsinya besar dan memuaskan. | price_value negative dan product_quality positive |
| Menu mencantumkan porsi 200 ml. | product_quality neutral; angka porsi saja bukan evaluasi positif |
| Jalan menuju kedai sulit dilalui. | kandidat location_accessibility; flag out_of_taxonomy, bukan otomatis facilities |

Jangan menduplikasi satu predikat menjadi dua kategori hanya karena konsepnya
berdekatan. Bila keduanya masuk akal tetapi tidak dapat dipilih, gunakan uncertain
dan adjudikasi. Perubahan aturan overlap memerlukan versi guideline baru.

## 6. Mixed sentiment dalam kategori yang sama

Contoh sintetis: “Kopinya enak, tapi minuman lainnya terlalu manis.”

Simpan dua evidence pada record product_quality yang sama: satu positive dan satu
negative. Pair memiliki mixed_sentiment=true, sentiment=null, dan
training_eligible=false. Mixed tidak boleh dirata-ratakan menjadi neutral atau
dipaksa mengikuti rating. Jika sudah disepakati annotator/adjudicator, record mixed
boleh completed/resolved sambil tetap dikeluarkan dari subset training tiga kelas.

Jika polaritas salah satu klaim belum jelas, annotation_status=uncertain dan
adjudication_status=pending. Jangan mengisi mixed=true hanya karena ada kata “tapi”;
harus ada bukti positif **dan** negatif pada kategori sama.

Evidence opinion-level tidak dibuang. Bila penelitian berikutnya memilih task
clause-level, pertahankan review_id asal dan buat protokol eksperimen terpisah.
Jangan memasukkan review lengkap yang identik dua kali dengan target bertentangan
ke training tiga kelas tanpa konteks pembeda. Seluruh clause dari satu review
harus berada pada split yang sama.

## 7. Bahasa informal, negasi, dan konteks

| Situasi | Contoh sintetis dan aturan |
|---|---|
| Negasi | “Tempatnya tidak nyaman.” → ambience negative; pertahankan kata tidak pada evidence |
| Negasi berlapis | “Bukan berarti tidak enak.” memerlukan konteks; jika evaluasi belum jelas, uncertain |
| Pelemahan | “Tidak terlalu mahal, masih cocok buat mahasiswa.” → price_value positive karena keterjangkauan dijelaskan |
| Slang | “Kopinya enak bgt.” → product_quality positive bila bgt dipahami; bentuk asli tetap disimpan |
| Code-switching | “Wi-Fi is very slow.” → facilities negative; bahasa Inggris tidak otomatis tidak relevan |
| Salah eja | “Pelayananya rmah.” dapat service positive bila makna jelas; jangan mengubah quote asli |
| Sarkasme eksplisit | “Cepat banget, sampai menunggu satu jam!” → kandidat service negative bila konteks jelas ironi |
| Sarkasme tidak pasti | Bila ironi tidak dapat dibuktikan dari konteks teks, uncertain + alasan; jangan menebak niat |
| Keluhan tanpa objek | “Lambat sekali.” → needs_context/uncertain; jangan memilih service bila tidak ada target |
| Emoji saja | Tetap disimpan di raw dan ditandai tidak eligible pada simulasi; jangan menjadikannya label sentimen aspek otomatis |

Review sangat pendek tetap dapat informatif. “Kopinya enak” tidak dikeluarkan
karena hanya dua kata. Pengulangan teks dengan ID berbeda belum membuktikan data
tidak sah; keputusan deduplikasi merupakan proses terpisah dan terdokumentasi.

## 8. Evidence, offset, dan schema

Quote adalah span kontigu dari teks asli. start/end memakai indeks karakter
Unicode Python, 0-based, end-exclusive; bukan offset byte atau indeks UTF-16.
Validator memastikan review_text[start:end] == quote dan start < end. Bila perlu
dua span terpisah, simpan dua evidence, bukan menyambungkannya menjadi quote palsu.
Contoh implicit tetap memerlukan evidence tekstual dan target inferensi yang jelas.

Record memuat annotation_id, review_id, coffee_shop_id, aspect_category,
aspect_presence, sentiment, mention_type, evidence, mixed_sentiment,
annotation_status, annotator_id, taxonomy_version, adjudication_status,
training_eligible, notes, dan review_flags. ID sintetik memakai prefix SYN_.

CSV kandidat pilot **tidak** memuat review_text, evidence, label presence,
sentiment, atau annotation_status. Metadata rating dan keyword hanya untuk
perancang sampling; paket annotator pada tahap berizin harus menyembunyikannya.

## 9. Pemeriksaan mutu dan adjudikasi

Protokol lengkap terdapat pada stage3_methodology_decisions.md. Dua manusia
menilai secara independen. Hitung agreement **sebelum** adjudikasi; nilai yang
disepakati setelah diskusi bukan ukuran independensi. Ketidaksepakatan presence,
polaritas, evidence, dan batas kategori dicatat terpisah. Adjudicator membaca
alasan kedua pihak; jangan memilih berdasarkan siapa yang lebih senior.

Guideline ini belum mengklaim accuracy, agreement, kelayakan model, atau validitas
empiris taksonomi. Revisi berdasarkan pilot harus diproses melalui versioning dan
reanotasi contoh yang terdampak, setelah izin penggunaan tersedia.
