# Kajian Akuisisi Data Google Maps untuk Dataset BrewScope

**Status:** keputusan awal berbasis dokumentasi resmi Google  
**Tanggal verifikasi:** 24 Oktober 2026  
**Ruang lingkup:** ulasan Google Maps, Places API (New), Google Business Profile API, penyimpanan data, atribusi, dan penggunaan untuk machine learning

> Catatan: dokumen ini merupakan kajian teknis dan kepatuhan, bukan nasihat hukum. Jika tim tetap ingin memakai konten Google Maps untuk penelitian, mintalah penilaian hukum atau izin tertulis yang secara eksplisit mencakup penyimpanan, anotasi, pelatihan, pengujian, dan publikasi dataset/model.

## Ringkasan keputusan

**Jangan membangun atau menjalankan scraper Google Maps untuk mengumpulkan ulasan sebagai dataset BrewScope.** Jangan pula menganggap Places API sebagai cara legal untuk mengunduh korpus pelatihan.

Alasannya bukan hanya risiko teknis. Ketentuan Google Maps Platform secara eksplisit melarang:

- mengekspor, mengekstrak, atau melakukan scraping terhadap Google Maps Content untuk digunakan di luar layanan;
- melakukan bulk download informasi tempat;
- menyalin dan menyimpan nama bisnis, alamat, atau ulasan pengguna;
- memakai Google Maps Content untuk meningkatkan model machine learning atau AI, termasuk untuk **training, testing, validation, atau fine-tuning**.

Larangan tersebut tercantum pada bagian 3.2.3 *Restrictions Against Misusing the Services* dalam [Google Maps Platform Terms of Service](https://cloud.google.com/maps-platform/terms). Versi yang diperiksa mencantumkan perubahan terakhir 26 Agustus 2026.

Dengan demikian, tujuan BrewScope—menyimpan ulasan, memberi anotasi aspek dan sentimen, membagi data menjadi train/validation/test, melatih empat algoritma, lalu menerbitkan hasil—langsung berkonflik dengan pembatasan tersebut bila sumbernya adalah Google Maps Content. Tidak ada pengecualian akademik/nonkomersial yang dinyatakan pada ketentuan itu.

## 1. Scraping antarmuka Google Maps

[Google Maps End User Additional Terms of Service](https://maps.google.com/help/terms_maps/) melarang pengguna untuk menyalin konten, melakukan mass download, atau membuat bulk feed konten, kecuali apabila ada izin lain yang berlaku. Dokumen tersebut terakhir diubah pada 27 Januari 2026.

[Google Terms of Service](https://policies.google.com/terms) juga melarang akses otomatis terhadap konten apabila melanggar instruksi yang dapat dibaca mesin pada halaman, misalnya aturan `robots.txt`, serta menegaskan bahwa konten milik pengguna lain tidak dapat digunakan tanpa izin mereka atau dasar hukum lain yang berlaku.

Konsekuensi praktis:

- Selenium, Playwright, BeautifulSoup, endpoint internal, atau penyedia scraper pihak ketiga tidak mengubah status sumber datanya.
- Rate limiting, jeda acak, rotasi proxy, CAPTCHA bypass, dan teknik anti-deteksi bukan solusi kepatuhan.
- Fakta bahwa ulasan terlihat publik tidak otomatis memberikan lisensi untuk menyalin, menyimpan, mendistribusikan, atau menggunakannya melatih model.
- Dataset yang sudah pernah di-scrape oleh pihak ketiga juga belum tentu boleh digunakan. Tim tetap harus memeriksa asal data dan lisensi dari pemegang hak, bukan hanya lisensi repository yang membagikannya.

## 2. Kemampuan Places API (New)

### 2.1 Place Details

[Place Details (New)](https://developers.google.com/maps/documentation/places/web-service/place-details) mengambil sebuah `Place` berdasarkan `placeId`. Request wajib menyertakan `FieldMask`; tanpa field mask, request gagal. Untuk produksi, Google menyarankan meminta hanya field yang diperlukan karena field memengaruhi biaya dan latensi.

Contoh field mask yang secara teknis dapat meminta data ulasan adalah:

```text
id,displayName,rating,userRatingCount,reviews,attributions
```

Field `reviews` berada pada SKU **Place Details Enterprise + Atmosphere**, sedangkan `rating` dan `userRatingCount` berada pada SKU **Place Details Enterprise**. Daftar tier dan field terkini harus selalu dicek pada [Place Data Fields (New)](https://developers.google.com/maps/documentation/places/web-service/data-fields) sebelum menggunakan API karena produk dan harga dapat berubah.

### 2.2 Isi objek review

Menurut [referensi REST resource `Place`](https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places), objek review dapat berisi:

- `name`: resource name review;
- `relativePublishTimeDescription`;
- `text`: teks yang dilokalkan;
- `originalText`: teks dalam bahasa asal;
- `rating`: nilai 1–5;
- `authorAttribution`: nama tampilan, URI profil, dan URI foto penulis;
- `publishTime`;
- `flagContentUri`;
- `googleMapsUri`;
- `visitDate` pada konteks tertentu.

`Place` juga dapat memuat identitas dan metadata tempat seperti `id`, `displayName`, `types`, alamat, lokasi, rating agregat, serta jumlah rating, tergantung field mask dan SKU yang diminta.

### 2.3 Jumlah review dan pagination

Dokumentasi resmi menyatakan bahwa `reviews[]`:

- diurutkan berdasarkan relevansi; dan
- **mengembalikan maksimal lima review per tempat**.

Places API (New) tidak mendokumentasikan `pageToken`, `nextPageToken`, atau endpoint list-review untuk melanjutkan halaman pada array `reviews` milik sebuah `Place`. Karena kontrak API menetapkan maksimum lima review, review ke-6 dan seterusnya tidak dapat diambil melalui pagination Place Details.

Ini berbeda dari pagination hasil pencarian tempat. Pagination pada Text Search/Nearby Search—jika digunakan—mengatur daftar **tempat**, bukan membuka halaman tambahan untuk seluruh review sebuah tempat.

Implikasi metodologisnya juga buruk untuk riset: lima review yang dipilih berdasarkan relevansi bukan sampel acak maupun korpus lengkap. Distribusinya berpotensi bias dan tidak cukup untuk analisis temporal atau generalisasi per kedai.

## 3. Penyimpanan, atribusi, dan tampilan

### 3.1 Penyimpanan

[Policies and attributions for Places API](https://developers.google.com/maps/documentation/places/web-service/policies) menyatakan bahwa konten Places API tidak boleh di-*prefetch*, di-*cache*, atau disimpan melampaui pengecualian yang diizinkan. `place_id` merupakan pengecualian dan boleh disimpan tanpa batas. Ketentuan utama Google Maps Platform juga secara khusus melarang menyalin dan menyimpan ulasan pengguna.

Karena eksperimen ML memerlukan korpus persisten, hasil anotasi, split reproducible, artefak fitur, dan penggunaan berulang, kebutuhan tersebut tidak cocok dengan pembatasan penyimpanan Google Maps Content.

### 3.2 Atribusi saat konten ditampilkan

Apabila Places API digunakan untuk use case tampilan yang memang diizinkan, aplikasi wajib mengikuti persyaratan berikut:

- konten yang ditampilkan pada peta harus berada pada Google Map;
- jika ditampilkan tanpa peta, tampilkan atribusi/logo Google Maps sesuai panduan;
- jangan menghapus, menyembunyikan, atau mengubah atribusi Google maupun penyedia pihak ketiga;
- bedakan secara visual Google Maps Content dari konten sumber lain;
- untuk review, berikan atribusi penulis menggunakan sumber yang tersedia dan letakkan dekat review;
- berikan akses langsung ke review sumber melalui `googleMapsUri`;
- jelaskan bahwa review secara default diurutkan berdasarkan relevansi dan sebutkan filtering yang diterapkan;
- jika menampilkan objek dengan `flagContentUri`, ikuti persyaratan pelaporan konten Google.

Detailnya terdapat di [kebijakan atribusi Places API](https://developers.google.com/maps/documentation/places/web-service/policies) dan [panduan pelaporan konten](https://developers.google.com/maps/documentation/places/web-service/content-reporting).

Attribution compliance tidak menghapus larangan penyimpanan atau penggunaan untuk ML. Atribusi adalah kewajiban tambahan bagi use case tampilan yang diperbolehkan, bukan lisensi untuk membuat dataset.

## 4. Apakah Places API layak untuk dataset training BrewScope?

**Tidak layak dan tidak sesuai ketentuan standar Google Maps Platform.** Ada tiga alasan independen:

1. **Hak penggunaan:** ketentuan secara eksplisit melarang Google Maps Content untuk training, testing, validation, dan fine-tuning model ML/AI.
2. **Penyimpanan:** dataset dan pipeline reproducible membutuhkan penyimpanan persisten, sementara penyalinan dan penyimpanan review dilarang.
3. **Kelengkapan ilmiah:** API hanya memberikan maksimal lima review yang diurutkan berdasarkan relevansi, tanpa pagination review. Sampelnya tidak lengkap dan tidak representatif.

Places API masih dapat dipakai untuk menampilkan informasi tempat secara real-time dalam aplikasi yang mematuhi ketentuan dan atribusi. Namun, ia tidak boleh dijadikan saluran akuisisi korpus pelatihan BrewScope.

## 5. Google Business Profile API bukan jalan pintas

Untuk bisnis yang terverifikasi dan dimiliki/dikelola oleh pengguna API, [`accounts.locations.reviews.list`](https://developers.google.com/my-business/reference/rest/v4/accounts.locations.reviews/list) secara teknis menyediakan review secara paginated, maksimal 50 item per halaman, menggunakan `nextPageToken`.

Namun akses tersebut:

- hanya berlaku pada lokasi terverifikasi yang dimiliki atau memang diotorisasi untuk dikelola;
- menggunakan OAuth dan membutuhkan akses Business Profile API;
- menurut [Business Profile APIs policies](https://developers.google.com/my-business/content/policies), hanya boleh dipakai untuk membuat, mengelola, dan melaporkan listing milik sendiri atau milik klien yang memberi wewenang;
- melarang penyimpanan konten di luar proyek, kecuali jumlah terbatas untuk peningkatan performa, sementara penyimpanan itu harus sementara (maksimal 30 hari), aman, dan tidak boleh dimanipulasi atau diagregasi.

Anotasi, agregasi, ekstraksi fitur, dan pelatihan model merupakan manipulasi/pengolahan dataset. Karena itu, pagination Business Profile API tidak menjadikannya sumber dataset ML yang patuh berdasarkan kebijakan standar. Kemitraan dengan pemilik kedai juga tidak otomatis memberi hak atas Google Content; izin atau perjanjian yang diperlukan harus mencakup Google dan pemegang hak konten bila relevan.

## 6. Alternatif akuisisi data yang direkomendasikan

### Pilihan utama: data primer dengan persetujuan

Kumpulkan review langsung dari partisipan melalui formulir/survei, bukan menyalinnya dari Google Maps. Formulir perlu menjelaskan secara eksplisit bahwa teks akan:

- disimpan sebagai data penelitian;
- dianotasi berdasarkan aspek dan sentimen;
- digunakan untuk training, validation, dan testing model;
- dianalisis serta dilaporkan dalam bentuk agregat;
- mungkin dipublikasikan sebagai contoh anonim atau dataset, jika memang direncanakan;
- disimpan selama periode yang ditentukan dan dapat ditarik sesuai prosedur penelitian yang berlaku.

Gunakan ID partisipan pseudonim, jangan meminta nama akun Google, URL profil, atau foto. Sediakan pilihan untuk tidak mengizinkan kutipan verbatim pada paper. Apabila responden ingin menyerahkan teks yang pernah mereka tulis di platform lain, minta mereka menuliskannya sendiri melalui formulir dan memberikan lisensi/persetujuan terpisah; jangan mengambilnya otomatis dari platform.

### Kemitraan pengumpulan data dengan coffee shop

Kedai dapat memasang QR menuju formulir penelitian atau membagikannya kepada pelanggan. Mitra hanya membantu distribusi dan tidak boleh memberikan export/salinan Google reviews sebagai dataset. Protokol perlu mencegah pemaksaan, pemberian insentif yang bias, dan pengumpulan identitas yang tidak diperlukan.

### Dataset yang memiliki lisensi eksplisit

Dataset eksternal dapat digunakan bila tim memverifikasi seluruh rantai haknya:

- sumber asal dan metode pengumpulan jelas;
- lisensi dari pemegang hak mengizinkan penyimpanan, modifikasi, karya turunan, analisis ML, dan publikasi yang direncanakan;
- tidak sekadar mengandalkan label lisensi dari pengunggah ulang yang mungkin tidak memiliki hak;
- tidak berasal dari Google Maps atau platform lain yang melarang pengambilan/penggunaan tersebut;
- privacy notice, penghapusan PII, dan batas redistribusi terdokumentasi.

Dataset ABSA bahasa Indonesia yang berlisensi jelas dapat digunakan untuk *pretraining* atau baseline, lalu disesuaikan/evaluasi dengan data primer coffee shop. Kecocokan domain dan label tetap harus diuji.

### Data berizin langsung dari pemegang hak

Tim dapat meminta review original langsung dari penulisnya dengan lisensi tertulis untuk penggunaan riset dan ML. Persetujuan pemilik kedai saja tidak selalu cukup karena teks review ditulis oleh pelanggan. Bila Google Maps Content tetap dianggap esensial, jalur yang aman adalah memperoleh persetujuan tertulis yang secara eksplisit mengesampingkan pembatasan relevan dari pihak-pihak yang berwenang, bukan mencoba menghindari batas API.

## 7. Rekomendasi untuk rencana proyek

1. Batalkan implementasi scraper Google Maps sebagai sumber dataset.
2. Tetapkan protokol pengumpulan data primer dan lembar persetujuan.
3. Lakukan pencarian dataset alternatif yang berlisensi eksplisit sebagai cadangan atau baseline.
4. Buat `dataset_card.md` yang merekam provenance, lisensi, consent, periode pengumpulan, kriteria inklusi, PII handling, dan batas penggunaan.
5. Simpan bukti izin/lisensi bersama catatan versi dan tanggal akses.
6. Setelah sumber data patuh tersedia, baru bangun pipeline ingestion generik dari CSV/JSON agar tidak terikat pada satu platform.

## 8. Checklist keputusan sumber data

Sebuah sumber baru boleh digunakan jika semua pertanyaan berikut terjawab “ya”:

- Apakah pengumpul memiliki hak untuk memperoleh dan menyimpan teks?
- Apakah lisensi/consent secara eksplisit mencakup training, testing, validation, dan publikasi hasil?
- Apakah modifikasi dan anotasi diperbolehkan?
- Apakah redistribusi contoh atau dataset diizinkan, atau sudah dibatasi dengan jelas?
- Apakah identitas personal dapat diminimalkan atau dihapus?
- Apakah proses pengumpulan dapat dijelaskan dan direproduksi secara ilmiah?
- Apakah bukti lisensi/consent tersimpan dan dapat diaudit?

Jika salah satu jawaban belum jelas, data masuk status **quarantine** dan tidak boleh digunakan dalam eksperimen.

## Sumber resmi Google

- [Google Maps Platform Terms of Service](https://cloud.google.com/maps-platform/terms)
- [Google Maps End User Additional Terms of Service](https://maps.google.com/help/terms_maps/)
- [Google Terms of Service](https://policies.google.com/terms)
- [Place Details (New)](https://developers.google.com/maps/documentation/places/web-service/place-details)
- [Place Data Fields (New)](https://developers.google.com/maps/documentation/places/web-service/data-fields)
- [REST Resource: places](https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places)
- [Policies and attributions for Places API](https://developers.google.com/maps/documentation/places/web-service/policies)
- [Report inappropriate content — Places API](https://developers.google.com/maps/documentation/places/web-service/content-reporting)
- [Business Profile API: list reviews](https://developers.google.com/my-business/reference/rest/v4/accounts.locations.reviews/list)
- [Business Profile APIs policies](https://developers.google.com/my-business/content/policies)
- [Business Profile APIs Terms of Service](https://developers.google.com/my-business/content/terms)

