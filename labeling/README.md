# BrewScope — pre-anotasi ABSA seluruh CSV yang diberikan

**Status: DRAFT / OFFLINE RULE-BASED PRE-ANNOTATION (BUKAN HUMAN GOLD).**

Pre-anotasi dikerjakan pada `../data/interim/reviews_for_annotation.csv`; tidak ada review yang dihilangkan dari input tersebut. Enam aspek aktif selalu diputuskan eksplisit per review. `config/annotation_schema.json` dan `config/aspect_taxonomy.yaml` merupakan dasar struktur dan definisi. Label diperoleh dari metode **aturan leksikal berbasis target, polaritas, negasi, dan klausa**; **tidak** berasal dari API Gemini, LLM lokal, atau penilaian manual menyeluruh. Kualitas semantik setiap label belum diverifikasi.

## Cakupan dan keterbatasan

- Review pada CSV: **3,538** (ID unik: 3,538); kedai: **40** identitas sumber.
- Pasangan review–aspek: **21,228** (6 × 3,538). Tidak ada record yang hilang.
- Evidence opinion-level dengan kutipan dan offset Unicode Python yang valid: **7,863**.
- Pasangan `draft`: **20,905**; pasangan `uncertain`: **323**; pasangan `mixed_sentiment`: **76** (mixed dapat tersimpan dalam draft jika dua polaritas eksplisit ditemukan).
- Antrean QA prioritas: **1,891 review** (**255 HIGH**, **459 MEDIUM**, **1,177 LOW**). Sisa review tetap perlu evaluasi sampling/validasi manusia; tidak berada dalam queue bukan berarti sudah diverifikasi.
- Pemeriksaan struktural: **0 schema/offset error**, tepat enam keputusan unik/review, ID anotasi unik.
- Diagnostic fixture sintetis: **102 / 102** keputusan sesuai contoh referensi; **ini bukan akurasi pada data nyata**.
- Snapshot proyek menyebut 3.582 review eligible teknis, sedangkan file yang diberikan hanya **3,538 review**. Selisih **44 review tidak ada di file input ini** dan tidak dibuat-buat.
- `needs_privacy_review=True` pada input: **0**; `needs_language_review=True`: **768**. Pencarian pola email/telepon/URL di teks menemukan **0** kandidat, namun itu **bukan** bukti tidak adanya PII lain.
- Geografi 40 kedai, ketentuan sumber, gold manusia, IAA, dan evaluasi terhadap gold masih perlu dilaksanakan/verifikasi. Tidak ada data dikirim ke cloud saat proses ini.

## Isi paket

| File | Fungsi |
|---|---|
| `data/canonical/annotations_full.jsonl` | **Output utama**: 21,228 record lengkap sesuai JSON Schema dengan evidence/offset asli dan flag. |
| `data/tabular/annotations_flat.csv` | Representasi tabular seluruh record (kolom `evidence_json` / `review_flags_json`). |
| `data/tabular/review_level_summary.csv` | Satu baris per review, enam aspek sebagai kolom presence/sentiment/mixed/status; tidak ada rating. |
| `data/review/manual_review_queue.csv` | Kandidat yang paling membutuhkan pemeriksaan manusia beserta alasan dan prioritas. |
| `data/review/blind_human_review_pack.csv` | Formulir buta yang hanya memuat teks dan kolom jawaban kosong; tidak berisi rating, hasil AI, atau flag. |
| `data/tabular/shop_id_lookup.csv` | Tabel penghubung ID kedai pseudonim dengan nama/URL sumber; *bukan* verifikasi lokasi. |
| `data/tabular/aspect_label_counts.csv` | Ringkasan angka tiap kombinasi aspek, presence, dan sentimen kandidat. |
| `reports/qa_report.json` | Rekap kualitas struktural, jumlah, flag, keputusan dan diagnostic fixture sintetis. |
| `reports/synthetic_fixture_diagnostic.csv` | Perbandingan terhadap 17 contoh sintetis dari sumber. |
| `data/review/privacy_regex_review_queue.csv` | Daftar pola PII yang tertangkap oleh regex terbatas. |
| `reports/source_coverage.json` | Audit cakupan file sumber, selisih dengan konteks proyek dan flags awal. |
| `config/annotation_schema.json` | Salinan schema yang dipakai untuk pengecekan. |
| `config/aspect_taxonomy.yaml`, `docs/annotation_guidelines.md` | Salinan aturan referensi. |
| `scripts/label_brewscope.py` | Snapshot kode pembentuk pre-anotasi. |
| `scripts/validate_annotations.py` | Pemeriksaan ulang schema, uniqueness, 6 aspek, dan evidence offset. |

## Kolom dan keputusan penting

- Unit: **review–aspek–annotator** dengan `annotator_id = auto:lexical_preannotation_v1`.
- `annotation_status`: `draft` untuk kandidat yang tampak dapat diputuskan secara aturan, `uncertain` untuk kasus dengan objek/polaritas ambigu yang diketahui.
- Semua `training_eligible` diset **false**; tidak ada record yang dipromosikan menjadi gold oleh skrip.
- `not_mentioned` berarti aturan tidak berhasil menemukan bukti aspek; bisa terjadi *false negative* terhadap review yang implisit/sarkastis. Ini bukan ketidakhadiran terverifikasi manusia.
- `neutral` hanya digunakan ketika aspek ditemukan dan klaim terdeteksi sebagai informasi faktual tanpa polaritas.
- `mixed_sentiment=true` mensyaratkan minimal satu evidence positif dan satu negatif pada aspek yang sama; `sentiment=null`. `mention_type=mixed` berbeda maknanya, yaitu explicit + implicit.
- `review_flags=out_of_taxonomy` mempertahankan isu lokasi/akses di luar enam aspek aktif. Tidak membuat label ketujuh.
- `coffee_shop_id` menggunakan hash deterministik dari Google Place ID (jika ada) atau URL, tidak menebak lokasi administratif.
- **Rating tidak dipakai oleh kode** sebagai sentimen; `nama_tempat` dan `url_tempat` juga tidak dibaca untuk memutuskan target atau polaritas aspek (URL hanya dipakai membuat ID kedai).
- Offset evidence adalah indeks karakter Python *0-based, end-exclusive*. Review asli **tidak dinormalisasi** untuk output.

## Menggunakan dan memvalidasi

Jalankan validator dari root repository:

```powershell
python labeling/scripts/validate_annotations.py `
  --input labeling/data/canonical/annotations_full.jsonl `
  --schema labeling/config/annotation_schema.json
```

`scripts/label_brewscope.py` dipertahankan byte-for-byte sebagai provenance
snapshot dari environment pembentukan pre-anotasi. Skrip tersebut masih memakai
path environment asal dan bukan entry point regenerasi pada struktur repository
ini.

Periksa QA HIGH terlebih dahulu, kemudian MEDIUM, LOW dan audit acak semua keputusan; adakan dua anotator independen untuk pilot sesuai protokol Stage 4 sebelum menamai hasil *human gold*. Jangan memperlihatkan file AI pre-annotation kepada annotator yang harus blind. Koreksi disimpan dalam record sumber tersendiri, tidak menimpa hasil anotator lain. Setelah scope/sumber/gold/QA siap, tingkatkan record yang telah disepakati dan barulah tetapkan `training_eligible` berdasarkan kriteria task training.

**Penting:** file ini bukan dataset produksi final, bukan label hasil 3.538 pembacaan individual oleh ahli, bukan evaluasi akurasi Gemini, dan bukan bukti kualitas model ABSA untuk paper.
