# Provenance dataset BrewScope — finalisasi Tahap 2

Tanggal peninjauan: **25 Oktober 2026** (Asia/Jakarta).
Dokumen ini membedakan deklarasi pemilik proyek, bukti pada snapshot lokal,
konfigurasi script saat ini, dan metadata eksekusi historis yang belum tersedia.
Tidak ada API, scraping ulang, pembacaan `.env`, atau pembacaan token pada revisi ini.

## 1. Identitas snapshot dan sumber

| Item | Nilai | Dasar bukti |
|---|---|---|
| Platform sumber | Google Maps | Brief pemilik proyek; URL tempat pada CSV |
| Collection tool | Apify | Brief pemilik proyek; implementasi script saat ini |
| Actor | `compass/google-maps-reviews-scraper` | Brief pemilik proyek dan `ACTOR_ID` pada script; manifest run historis tidak tersedia |
| Dataset | `data/raw/google_maps_reviews_jatinangor_raw.csv` | File lokal yang diaudit |
| Format | CSV, enam kolom | Header snapshot aktual |
| Unit observasi | Ulasan pelanggan | Satu baris per `review_id` dalam snapshot |
| Jumlah observasi | 3.593 | Hasil audit; seluruh ID unik |
| Identitas kedai | 40 | Place ID/URL raw yang dinormalisasi |
| Scope target | Kecamatan Jatinangor, Kabupaten Sumedang, Jawa Barat | Brief penelitian; cakupan aktual belum terverifikasi administratif |
| SHA-256 | `7b87a53110041da74e976a6c9cb121c1dea7d73be70daeab58b2c07bef775719` | Checksum snapshot; diperiksa ulang saat eksekusi notebook |

Snapshot enam kolom merupakan file sumber untuk audit lokal, bukan bukti bahwa
seluruh field asli keluaran Actor telah diarsipkan. Riwayat transformasi historis
ke schema enam kolom belum dibuktikan oleh run manifest atau export Actor asli.
Referensi hasil: `reports/data_audit_summary.json` dan `reports/data_audit_report.md`.

## 2. Metadata historis pengumpulan

| Metadata | Status | Penjelasan |
|---|---|---|
| Tanggal/jam pengambilan | `NOT_DOCUMENTED` | Tidak ditemukan manifest/log run pengambilan pada file penelitian yang tersedia |
| Versi/build Actor | `NOT_DOCUMENTED` | Nama Actor tidak mengidentifikasi build run historis |
| Apify run ID | `NOT_DOCUMENTED` | Tidak ada rekaman ID eksekusi yang dapat dicocokkan dengan snapshot |
| Apify dataset ID | `NOT_DOCUMENTED` | Tidak ada export/manifest dataset asal |
| `maxReviews` aktual historis | `NOT_DOCUMENTED` | Default script terbaru tidak membuktikan argumen CLI yang digunakan dahulu |
| Jumlah tempat yang diproses pada tiap run | `NOT_DOCUMENTED` | 40 identitas teramati pada hasil, bukan bukti jumlah input/run berhasil |
| Metode penentuan daftar kedai | `NOT_DOCUMENTED` | Daftar lokal berisi 40 baris nama/URL; kriteria pemilihan dan tanggal pembentukannya tidak tercatat |
| Filtering review kosong historis | `NOT_DOCUMENTED` | Tidak ada log jumlah review sebelum/sesudah filtering |
| Deduplikasi historis | `NOT_DOCUMENTED` | ID unik saat ini tidak membuktikan metode atau jumlah penghapusan sebelumnya |
| Urutan pemilihan review | `NOT_DOCUMENTED` | Tidak ada input run tersimpan yang menjelaskan newest/relevant/urutan lain |

Rentang tanggal review 2016-09-13 hingga 2026-10-25 adalah waktu publikasi yang
tercantum dalam data, **bukan tanggal akuisisi**. Timestamp filesystem dan waktu
validasi notebook juga tidak dipakai untuk menebak tanggal pengambilan.

## 3. Konfigurasi script terkini — bukan rekonstruksi historis

Bukti inspeksi: `scripts/scrape_google_maps.py` pada tanggal peninjauan.
Script tidak dijalankan pada audit/revisi ini.

| Parameter | Default/aturan saat ini |
|---|---|
| Actor ID | `compass/google-maps-reviews-scraper` |
| `--max-places` | 40 |
| `--max-reviews` / `maxReviews` | 170 |
| `language` | `id` |
| `personalData` | `False` |
| `--charge-cap` | USD 0.05 |
| Sumber tempat | `data/interim/google_maps_places_jatinangor.csv` |
| Pemilihan URL | URL berawalan `https://`, URL duplikat dibuang, kemudian `head(max_places)` |
| Normalisasi teks | Membaca `text` atau `reviewText`, lalu `strip()`; teks kosong dilewati |
| Identitas review | Menggunakan `reviewId`; jika tidak tersedia, fallback SHA-256 dari placeId, URL, tanggal, teks |
| Deduplikasi script | Berdasarkan `review_id`, `keep=first`, saat normalisasi dan penggabungan CSV lama/baru |

Nilai di atas dapat diubah melalui argumen CLI atau perubahan source. Tidak ada
bukti bahwa satu konfigurasi tersebut menghasilkan seluruh snapshot yang diaudit.
Tidak disimpulkan bahwa semua review tanpa teks pernah terkumpul, atau bahwa
selisih volume terhadap batas 170 menggambarkan kegagalan/kekurangan populasi.

## 4. Perlakuan pada Tahap 2 dan batasan sampling

- File raw dipertahankan; flag audit memiliki satu baris per baris sumber.
- Tidak ada ID duplikat atau konflik ID pada snapshot aktual.
- Sebanyak 11 review simbol/emoji-only adalah **Text Suitability Issue**, severity
  **Moderate**, bukan kegagalan integritas ID.
- Simulasi eligible berjumlah 3.582: field wajib lengkap, rating integer 1–5,
  tanggal valid dan tidak setelah acuan, URL Maps valid, bukan simbol saja,
  tanpa konflik ID, dan salinan enam field identik dihitung sekali.
- Simulasi tidak menghapus raw dan tidak menghasilkan dataset filtered/berlabel.
  Review pendek dan teks sama dengan ID berbeda dipertahankan.
- Ketimpangan 10–151 review/kedai, dominasi bintang 5, seleksi kedai, ketersediaan
  teks, dan kemungkinan urutan/batas pengambilan dapat menimbulkan selection bias.
  CSV tidak cukup untuk mengukur representativitas populasi atau recall pengumpulan.
- Tidak dibuat label sentimen dari rating. Enam aspek eksploratif tetap sama.

## 5. Bukti geografis dan keterbatasan verifikasi

Tabel: `reports/tables/geographic_verification.csv`, satu baris per place key raw.
Status yang didukung: `VERIFIED_INSIDE`, `VERIFIED_OUTSIDE`, `UNVERIFIED`.

Daftar lokal `data/interim/google_maps_places_jatinangor.csv` memuat 40 nama/URL.
Sebanyak 39 nama cocok persis setelah normalisasi dengan nama pada raw; `Ngopi
Doeloe` tidak memiliki kandidat nama yang cocok. Untuk kandidat yang unik,
notebook mengambil koordinat dari pasangan **!3d/!4d** pada URL, bukan titik
viewport **@lat,long**. URL kandidat disimpan sebagai bukti yang dapat diperiksa.

Pencocokan nama hanya menyiapkan kandidat bukti. Place ID raw dan POI pada URL
lokal belum dipastikan identik, alamat belum dikonfirmasi, dan belum dilakukan
pencocokan titik dengan batas administratif yang tervalidasi. Karena itu seluruh
40 identitas masih **UNVERIFIED**; tidak ada kedai yang otomatis dikeluarkan.
Kolom latitude/longitude harus dibaca bersama `coordinate_status` dan `notes`:
koordinat kandidat belum merupakan lokasi terverifikasi.

Sumber publik yang diperiksa pada peninjauan ini:

- [Perbup Sumedang 340/2022 — Batas Desa Mekargalih Kecamatan Jatinangor](https://peraturan.bpk.go.id/Details/266140/perbup-kab-sumedang-no-340-tahun-2022):
  bukti administratif tentang Mekargalih, bukan bukti posisi coffee shop tertentu.
- [Direktori resmi Pemerintah Kabupaten Sumedang](https://www.sumedangkab.go.id/skpd):
  menempatkan kantor Desa Mekargalih di Kecamatan Jatinangor; bukan alamat kedai.
- [LKIP Kecamatan Jatinangor 2021](https://portal-skpd.sumedangkab.go.id/storage/regulasi/1.%20Dokumen%20LKIP%20Kec%20Jatinangor%20Tahun%202021.080622_15_35_23pdf.pdf):
  konteks batas administratif dan peta umum; belum digunakan sebagai poligon
  georeferensi untuk verifikasi per titik.
- Halaman [Kecamatan Jatinangor Dalam Angka 2026](https://sumedangkab.bps.go.id/id/publication/2026/09/28/c1c3e8b08d871bd4bd577b35/kecamatan-jatinangor-dalam-angka-2026.html)
  ditemukan, tetapi pengambilan halaman mengembalikan 403; tidak dijadikan
  bukti verifikasi lokasi kedai.

**Kopi Menak Rancaekek:** kandidat URL lokal mencantumkan -6.9560027,
107.7742435. Nama Rancaekek tidak membuktikan kedai berada di Kecamatan Rancaekek.
Penelusuran direktori sekunder juga memberi alamat administratif yang tidak
konsisten; hal itu tidak dipakai menetapkan `VERIFIED_INSIDE`/`VERIFIED_OUTSIDE`.
Perlu konfirmasi identitas POI, alamat/koordinat, kemudian pemeriksaan batas
administratif Jatinangor. Jika kelak terbukti di luar wilayah, tandai sebagai
kandidat eksklusi dan dokumentasikan keputusan tim, tanpa menghapus raw.

## 6. Hak penggunaan

| Penggunaan | Status |
|---|---|
| Pengumpulan | `PERMISSION_NOT_VERIFIED` |
| Penyimpanan | `PERMISSION_NOT_VERIFIED` |
| Anotasi dan pembagian data kepada annotator | `PERMISSION_NOT_VERIFIED` |
| Training/validasi/pengujian ML | `PERMISSION_NOT_VERIFIED` |
| Publikasi data atau kutipan review | `PERMISSION_NOT_VERIFIED` |

Tidak ditemukan bukti izin spesifik untuk snapshot dalam dokumen yang diperiksa.
Penggunaan Apify tidak dengan sendirinya membuktikan hak penggunaan konten
Google Maps. Temuan audit sumber sebelumnya tersedia di
[google_maps_data_acquisition.md](google_maps_data_acquisition.md).
Tim perlu menyelesaikan bukti hak penggunaan sebelum anotasi aktual, training,
atau publikasi; kelayakan teknis tidak menggantikan pemeriksaan tersebut.

## 7. Kesiapan dan metadata yang perlu dilengkapi

Kualitas teknis siap diproses; persiapan rancangan/sampel pilot bersyarat pada
peninjauan teks dan duplikasi. Kesiapan penggunaan penelitian belum final karena
scope geografis, metadata historis, dan hak penggunaan belum terverifikasi.

Lengkapi run/dataset ID, tanggal akuisisi, build Actor dan input run historis,
log filtering/deduplikasi, metode seleksi kedai, bukti administratif setiap POI,
serta dasar izin per jenis penggunaan. Jangan mengganti `NOT_DOCUMENTED` dengan
default script saat ini atau dugaan berdasarkan hasil data.
