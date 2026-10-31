# Konteks Proyek BrewScope

Dokumen ini menjadi konteks kerja aktif setelah keputusan arsitektur tanggal
31 Oktober 2026. Seluruh pipeline Stage 2-4 lama telah dihentikan. Baseline
labeling yang berlaku hanya artefak di `labeling/`.

## 1. Tujuan penelitian

BrewScope menggunakan ABSA untuk mengubah ulasan pelanggan menjadi informasi
yang dapat dipakai dalam evaluasi bisnis coffee shop di Jatinangor. Hasil akhir
yang dituju meliputi:

1. aspek yang disebut pada setiap review;
2. sentimen positif, netral, atau negatif pada aspek tersebut;
3. kekuatan dan kelemahan setiap coffee shop;
4. prioritas perbaikan bisnis berdasarkan sentimen dan jumlah dukungan data;
5. perbandingan model SVM, Random Forest, dan Multinomial Naive Bayes.

Judul kerja paper:

> Strategic Prioritization of Jatinangor Coffee Shops Using Comparative
> Machine Learning-Based ABSA

## 2. Data aktif

| Data | Nilai |
|---|---:|
| Review untuk labeling | 3.538 |
| ID review unik | 3.538 |
| Coffee shop | 40 |
| Aspek aktif | 6 |
| Pasangan review-aspek | 21.228 |
| Evidence span | 7.863 |

Sumber yang dipertahankan:

- `data/raw/google_maps_reviews_jatinangor_raw.csv`
- `data/interim/google_maps_places_jatinangor.csv`
- `data/interim/reviews_for_annotation.csv`

Akuisisi ulang tersedia melalui `scripts/scrape_google_maps.py`. Script membaca
daftar URL coffee shop dari file places, menggunakan Actor Apify
`compass/google-maps-reviews-scraper`, dan hanya menjalankan scraping nyata jika
dipanggil dengan `--run` serta dikonfirmasi secara interaktif. Token disimpan
lokal sebagai `APIFY_TOKEN` di `.env` dan tidak dimasukkan ke Git.

Hash sumber `reviews_for_annotation.csv`:

```text
506be36d737a180b2380bd67716a5bb5e3ef3a7f6dfe9d8244744136aedaf932
```

Seluruh 3.538 review pada sumber tersebut tercakup dalam artefak labeling.
Selisih 44 review terhadap snapshot eligible lama 3.582 merupakan perbedaan
snapshot sumber, bukan record yang dibuat atau dipulihkan oleh pipeline baru.

## 3. Taksonomi aspek

Enam aspek aktif:

| ID | Cakupan |
|---|---|
| `product_quality` | Rasa, mutu, porsi, variasi, dan penyajian produk |
| `service` | Interaksi staf, pemesanan, waktu tunggu, dan respons |
| `price_value` | Harga, keterjangkauan, promosi, dan kesepadanan nilai |
| `ambience` | Suasana, interior, kebisingan, dan kenyamanan |
| `facilities` | Wi-Fi, parkir, colokan, toilet, AC, kursi, dan amenitas |
| `cleanliness` | Kebersihan dan higiene ruang, toilet, serta peralatan |

`location_accessibility` tetap provisional dan tidak menjadi aspek ketujuh.
Kasus yang relevan dicatat dengan flag `out_of_taxonomy`.

Taksonomi, schema, dan pedoman aktif berada di:

- `labeling/config/aspect_taxonomy.yaml`
- `labeling/config/annotation_schema.json`
- `labeling/docs/annotation_guidelines.md`

## 4. Arsitektur labeling aktif

```text
reviews_for_annotation.csv
        |
        v
label_brewscope.py
        |
        v
pre-anotasi leksikal enam aspek
        |
        +--> annotations_full.jsonl
        +--> annotations_flat.csv
        +--> review_level_summary.csv
        +--> manual_review_queue.csv
        `--> blind_human_review_pack.csv
                    |
                    v
              human review
                    |
                    v
          dataset final untuk modeling
```

`annotations_full.jsonl` merupakan sumber kebenaran kanonis. File CSV lain
adalah proyeksi untuk analisis atau human review.

## 5. Metode pre-anotasi

Label dibuat secara offline dan deterministik menggunakan:

- pola target per aspek;
- pemisahan klausa;
- kata polaritas positif dan negatif;
- penanganan negasi;
- aturan overlap antaraspek;
- deteksi sentimen campuran;
- evidence dengan offset karakter Unicode Python.

Rating tidak digunakan untuk menetapkan aspek atau sentimen. Nama dan URL kedai
tidak digunakan untuk menentukan polaritas. Tidak ada data yang dikirim ke
Gemini, Ollama, atau layanan cloud pada pipeline ini.

Annotator provenance:

```text
auto:lexical_preannotation_v1
```

## 6. Status labeling

| Status | Jumlah |
|---|---:|
| `draft` | 20.905 |
| `uncertain` | 323 |
| Mixed sentiment | 76 |
| `training_eligible=true` | 0 |

Pre-anotasi bukan human gold dan belum menyatakan akurasi semantik. Nilai
`not_mentioned` berarti aturan tidak menemukan bukti aspek; nilai tersebut masih
dapat berupa false negative.

## 7. Human review

`manual_review_queue.csv` berisi 1.891 review:

| Prioritas | Jumlah |
|---|---:|
| HIGH | 255 |
| MEDIUM | 459 |
| LOW | 1.177 |

Urutan review:

1. selesaikan HIGH;
2. lanjutkan MEDIUM;
3. lanjutkan LOW;
4. lakukan audit acak pada review di luar antrean;
5. simpan koreksi manusia dengan provenance annotator;
6. promosikan hanya keputusan yang telah disepakati menjadi training eligible.

`blind_human_review_pack.csv` berisi 3.538 review dengan seluruh kolom jawaban
kosong. File tersebut tidak memuat rating, pre-label, atau flag otomatis.

## 8. Validasi dan integritas

Baseline sudah memenuhi:

- tepat enam aspek unik per review;
- 21.228 `annotation_id` unik;
- seluruh record valid terhadap JSON Schema;
- seluruh quote cocok dengan evidence offset;
- seluruh 17 checksum artefak cocok;
- hash input cocok dengan `qa_report.json`;
- semua record masih `training_eligible=false`.

Validator:

```powershell
python labeling/scripts/validate_annotations.py `
  --input labeling/data/canonical/annotations_full.jsonl `
  --schema labeling/config/annotation_schema.json
```

Validasi tersebut menguji struktur dan integritas, bukan kebenaran semantik
label.

## 9. Modeling setelah human review

Task A adalah deteksi multi-label enam aspek pada tingkat review. Task B adalah
klasifikasi sentimen tiga kelas untuk pasangan aspek yang disebut dan telah
diselesaikan.

Model utama:

- Support Vector Machine;
- Random Forest;
- Multinomial Naive Bayes.

Seluruh model harus memakai split review dan duplicate group yang sama. Fitur
dan preprocessing dipelajari hanya dari training set. Evaluasi utama menggunakan
micro/macro F1 untuk deteksi aspek serta macro F1 dan confusion matrix untuk
sentimen.

Insight bisnis dihitung per coffee shop berdasarkan jumlah mention, dukungan
label, distribusi sentimen, kekuatan, keluhan, dan prioritas peningkatan. Insight
tidak boleh dibentuk dari label draft yang belum direview.

## 10. Batasan aktif

- Seluruh 40 identitas geografis masih `UNVERIFIED`.
- Pemeriksaan regex privasi tidak membuktikan seluruh teks bebas PII.
- Perfect match pada fixture sintetis bukan akurasi data nyata.
- Human gold, IAA, dan evaluasi semantik belum tersedia.
- `label_brewscope.py` dipertahankan sebagai snapshot provenance dan masih
  menggunakan path dari environment pembentukannya.

## 11. Sumber kebenaran

Jika terdapat informasi lama yang bertentangan, gunakan urutan berikut:

1. `labeling/data/canonical/annotations_full.jsonl`;
2. `labeling/reports/qa_report.json`;
3. `labeling/config/annotation_schema.json`;
4. `labeling/config/aspect_taxonomy.yaml`;
5. `labeling/docs/annotation_guidelines.md`;
6. dokumen konteks ini.
