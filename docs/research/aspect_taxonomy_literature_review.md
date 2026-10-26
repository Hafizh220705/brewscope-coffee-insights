# Literatur untuk taksonomi aspek BrewScope

Tanggal peninjauan: **25 Oktober 2026**. Ini adalah tinjauan terarah untuk keputusan
metodologis, bukan systematic literature review dengan klaim pencarian menyeluruh.
Tidak ada review pelanggan BrewScope yang dianotasi dalam proses ini.

## 1. Strategi pemilihan dan tingkat bukti

Lima DOI awal pada brief ditelusuri ke publisher/ACL; kelimanya sesuai metadata
artikel yang ditemukan. Ditambahkan dua studi 2024 tentang pengalaman restoran
dan coffee shop. Lima dari tujuh sumber terbit setelah 2021; dua SemEval
dipertahankan sebagai sumber fondasional.

Judul, penulis, tahun, venue, DOI, dan kategori/atribut yang dinyatakan dicocokkan
dengan sumber primer. Detail dataset, metode, evidence location, dan status ada
di [literature_matrix.csv](../../reports/tables/literature_matrix.csv);
source ID stabil dipakai pada [references.bib](references.bib).

- VERIFIED_FULL_TEXT: metadata dan bagian full text relevan dapat dibaca;
  bukan jaminan validitas seluruh hasil penelitian.
- VERIFIED_METADATA_AND_ABSTRACT: hanya metadata dan klaim abstrak digunakan;
  rincian protokol yang tidak terlihat tidak diasumsikan.
- Verifikasi bibliografi tidak berarti semua metode, performa, atau klaim hak
  penggunaan pada studi terdahulu boleh diwariskan.

## 2. Matriks sumber inti dan lokasi bukti

| Source ID | Sumber | Bukti yang digunakan | Lokasi dan status |
|---|---|---|---|
| pontiki2014 | Pontiki et al. (2014), SemEval-2014 Task 4 | FOOD, SERVICE, PRICE, AMBIENCE, ANECDOTES/MISCELLANEOUS; kategori dan term berbeda; conflict tersedia | §2 p28; §3 Stage2 p30; full text |
| pontiki2016 | Pontiki et al. (2016), SemEval-2016 Task 5 | Entity–attribute/opinion tuple, target, polarity; restoran mencakup food, drinks, ambience, service, location | §2 pp20–21; AppendixA Table11 p30; full text |
| zainuddin2025 | Zainuddin & Rachmat (2025), Joined Journal8(2):218–227 | Abstrak kopi Indonesia menyebut rasa, pelayanan, harga, suasana, waktu tunggu | Abstrak landing page; metadata dan abstrak |
| latifah2026 | Latifah, Erfina, & Warman (2026), Dinamik31(1):323–334 | Lima kategori restoran Sunda: makanan, pelayanan, harga, suasana, fasilitas | §3 pp324–325; Table2/§4.3 p326; full text |
| suksarifanti2024 | Suksarifanti, Anjani, & Nurhayati (2024), JAMADEV5(1):46–56 | Kuesioner product/service quality mencakup fasilitas, kebersihan, interior, lokasi | Method p47; Table3 p50; Table4 p51; full text |
| wiastuti2024 | Wiastuti & Rashid (2024), Turyzm/Tourism34(2):35–46 | Kelompok teori food/service/ambiance/experience/safety, dengan atribut WiFi, cleanliness, value, akses lokasi | Table2 pp38–39; coffee subsection/Table5 p41; full text |
| zanetta2024 | Zanetta et al. (2024), Food Research International186:114369 | Abstrak sintesis mengorganisasi atmosphere, food, service, price & value | Abstrak publisher/PubMed; metadata dan abstrak |

Tautan primer:
[pontiki2014](https://aclanthology.org/S14-2004/),
[pontiki2016](https://aclanthology.org/S16-1002/),
[zainuddin2025](https://e-journal.ivet.ac.id/index.php/jiptika/article/view/4325),
[latifah2026](https://www.unisbank.ac.id/ojs/index.php/fti1/article/view/10417),
[suksarifanti2024](https://journal.ugm.ac.id/v3/JAMADEV/article/view/12984),
[wiastuti2024](https://czasopisma.uni.lodz.pl/tourism/article/view/21042),
[zanetta2024](https://doi.org/10.1016/j.foodres.2024.114369).

## 3. Interpretasi dan batas bukti

### Formulasi ABSA dari SemEval

SemEval-2014 memisahkan category detection dari polarity dan mengizinkan kategori
implisit. Ketiadaan term bukan bukti ketiadaan aspek. Conflict pada sumber
mencegah pemaksaan opini campuran menjadi neutral.
[PDF §2 dan §3](https://aclanthology.org/S14-2004.pdf).

SemEval-2016 memakai inventori entity–attribute, bukan enam label BrewScope.
FOOD/DRINKS digabung menjadi Product Quality dan LOCATION mendasari kandidat
lokasi; pemetaan tersebut merupakan adaptasi peneliti. Kebijakan unit opini dan
subset tiga kelas BrewScope perlu ditulis sebagai adaptasi, bukan salinan standar.
[PDF §2 dan AppendixA](https://aclanthology.org/S16-1002.pdf).

### Studi ABSA bahasa Indonesia

Zainuddin & Rachmat menguatkan relevansi pengalaman inti kopi dan waktu tunggu.
Endpoint full text view/download 4325/2872 gagal diakses saat peninjauan.
Karena itu hanya kategori dalam abstrak yang dipakai; detail anotasinya belum
diverifikasi. Penggabungan waiting time ke Service adalah keputusan BrewScope.
[Abstrak publisher](https://e-journal.ivet.ac.id/index.php/jiptika/article/view/4325).

Latifah et al. mendukung keberadaan kategori Facilities. Namun §3.4 p325
menyebut manual dengan bantuan LLM pada ambiguitas, sedangkan §4.3 p326
menyebut rule-based. Table2 memberikan setiap review pada setiap aspek dan
pemisahan absent/neutral belum dijelaskan tegas. Ini tidak membuktikan semua
label sumber salah, tetapi protokolnya tidak diwariskan tanpa klarifikasi.
BrewScope memisahkan presence dari sentiment dan tidak mengadopsi klaim bahwa
akses publik otomatis memberi hak penelitian.
[PDF](https://www.unisbank.ac.id/ojs/index.php/fti1/article/download/10417/4376/).

### Dimensi pengalaman kopi/restoran

Suksarifanti et al. adalah survei, bukan anotasi ABSA. Table3 membahas produk;
Table4 memasukkan parkir/WiFi, kebersihan, interior, lokasi, dan kecepatan staf
dalam kelompok layanan. Memisahkan Facilities/Cleanliness secara operasional
merupakan adaptasi BrewScope; enam label kita tidak divalidasi oleh survei itu.
[PDF pp50–51](https://journal.ugm.ac.id/v3/JAMADEV/article/view/12984/4093).

Wiastuti & Rashid mengelompokkan cleanliness sebagai AA4 dan WiFi sebagai AA9
pada kategori awal ambience; location/accessibility adalah EA4. Tiga faktor
empirisnya bukan enam kategori ABSA. Relevansi atribut tidak membuktikan struktur
BrewScope atau generalisasi survei Gen Z kepada semua pelanggan Jatinangor.
[PDF Table2](https://repozytorium.uni.lodz.pl/bitstream/handle/11089/54063/35-46_Wiastutia_Rashid.pdf?isAllowed=y&sequence=1).

Zanetta et al. memberi kerangka empat kelompok besar pengalaman melalui
integrative review. Full text ScienceDirect 403; metadata dan abstrak dicocokkan
pada [PubMed](https://pubmed.ncbi.nlm.nih.gov/38729728/). Tidak digunakan klaim
tabel/detail pengodean yang memerlukan full text.

## 4. Dari literatur menuju kandidat taksonomi

| Kandidat | Asal/pemetaan | Keputusan BrewScope |
|---|---|---|
| Product Quality | FOOD/DRINKS dan atribut kualitas menu | ADAPT: gabungkan makanan/minuman |
| Service | SERVICE dan proses/interaksi pelayanan | ADOPT pada level makna; waiting time MERGE ke sini |
| Price & Value | PRICE dan atribut affordability/value | ADAPT: harga serta kesepadanan |
| Ambience | AMBIENCE/atmosphere/kenyamanan lingkungan | ADAPT; pisahkan kebersihan dan fungsi amenitas |
| Facilities | Fasilitas restoran dan amenitas survei kopi | ADAPT: keberadaan/fungsi/capacity, bukan kebersihan |
| Cleanliness | Atribut toilet, meja, kedai bersih | ADAPT dan pisahkan; belum empirically validated |
| Location & Accessibility | LOCATION dan atribut akses lokasi | PROVISIONAL; perlu validasi korpus/pilot/geografi |
| General praise/miscellaneous | Ada kategori lain pada SemEval | Workflow unresolved/out-of-taxonomy, bukan blanket aspek positif |
| Waiting time | Tersendiri pada abstrak studi kopi | MERGE ke Service; tidak termasuk kecepatan WiFi |

Keputusan ini bukan label yang diklaim diberikan penelitian sumber. Enam
kategori operasional dipertahankan melalui triangulasi teori dan kebutuhan batas
anotasi, bukan karena enam grafik Tahap 2 harus diikuti. Location tetap provisional.

## 5. Hubungan dengan korpus lokal

Coverage Tahap 2 adalah indikasi keyword, bukan accuracy deteksi, construct
validity, atau finalisasi taksonomi. Overlap toilet/meja dapat melibatkan
Facilities dan Cleanliness; aspek implisit dapat luput dari leksikon.
Frekuensi kecil tidak cukup untuk menolak kategori yang didukung teori.

Pilot sesudah gate geografis/izin perlu menyertakan teks tanpa keyword, slang,
ambiguitas umum, serta potensi pengulangan. Contoh anotasi Tahap 3 harus
sintetis; kutipan review asli tidak dipakai selama hak belum terverifikasi.

## 6. Implikasi dan keterbatasan

1. Pisahkan category detection multilabel dari sentiment tiga kelas untuk aspek
   yang disebutkan. Absence bukan neutral.
2. Simpan opini berlawanan tentang aspek sama; jangan gantikan conflict dengan
   neutral atau mayoritas rating.
3. Uji batas Facilities–Cleanliness–Ambience dan location–parking pada pilot.
   Dukungan literatur tidak menggantikan agreement lokal.
4. Jangan menghitung agreement atau performa klasifikasi sebelum label tersedia.
5. Studi survei, restoran umum, kopi, dan ABSA Indonesia berbeda unit/context;
   transfer ke Jatinangor baru merupakan dasar rancangan.
6. Lima sumber diperiksa full text dan dua metadata/abstrak. Keterbatasan akses
   harus tetap dinyatakan pada paper.
