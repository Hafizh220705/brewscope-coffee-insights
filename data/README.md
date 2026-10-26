# Data penelitian BrewScope untuk kerja kelompok

Keputusan pemilik: dataset dan formulir anotasi kosong dilacak Git agar Hafizh,
Niki, Robi dan Hamam menggunakan snapshot yang sama. Perubahan `.gitignore`
tidak mengunggah data otomatis; data tersedia di GitHub setelah commit/push dan
merge ke branch yang dipakai tim. Gunakan repository dengan akses kelompok.

## File yang dibagikan

| Lokasi | Isi dan penggunaan |
|---|---|
| `raw/google_maps_reviews_jatinangor_raw.csv` | 3.593 review asli, enam kolom; tidak diedit langsung |
| `interim/google_maps_places_jatinangor.csv` | Daftar tempat hasil akuisisi; tidak membuktikan verifikasi administratif |
| `interim/review_audit_flags.csv` | Flag kualitas untuk setiap review; dasar eligible teknis |
| `interim/annotation_pilot_candidates.csv` | 250 kandidat Stage 3 tanpa label; rating dan keyword adalah informasi sampling untuk koordinator |
| `interim/reviews_for_annotation.csv` | File persiapan yang sudah ada; workflow Stage 4 memakai paket assignment di bawah |
| `interim/human_annotations/assignments/human_A/` | Formulir kosong Niki: `calibration.jsonl` dan `independent.jsonl` |
| `interim/human_annotations/assignments/human_B/` | Formulir kosong Robi: `calibration.jsonl` dan `independent.jsonl` |
| `interim/human_annotations/pilot_manifest.json` | Acuan koordinator: ID, kelompok, split dan hash; tanpa label |
| `interim/human_annotations/corpus_duplicate_groups.csv` | Grouping duplikat untuk menjaga split konsisten |
| `processed/` | Dataset final setelah benar-benar tersedia dan direview; saat ini belum berisi label produksi |
| `annotations/` | Lokasi artefak anotasi yang telah disepakati untuk dibagikan; jangan menyimpan jawaban independen yang masih dikerjakan di sini |

SHA-256 snapshot raw:

```text
7b87a53110041da74e976a6c9cb121c1dea7d73be70daeab58b2c07bef775719
```

Raw berisi 3.593 review, eligible teknis 3.582, dan 40 identitas kedai masih
UNVERIFIED. Dataset ini belum menjadi dataset berlabel final.

## File yang tetap lokal

| Pola yang diabaikan | Alasan |
|---|---|
| `.env`, `.env.*` selain `.env.example` | Credential dan konfigurasi lokal |
| `interim/ai_annotation_checkpoints/` | Counter/lock/checkpoint dan respons mentah provider |
| `interim/ai_annotations/` | Output AI sementara sebelum review |
| `interim/debug_maps/` | Screenshot/debug scraping |
| `interim/human_annotations/work/` | Salinan kerja annotator, belum dikunci |
| `interim/human_annotations/submissions/` | Original independen untuk proses koordinator; diserahkan privat |
| `.run.lock`, `.writing-*` di bawah data | State sementara penyimpanan lokal |

## Cara anggota menggunakan data

1. Clone/pull branch tim setelah data digabung, lalu siapkan `.venv` dan `.env`
   sendiri. Credential tidak dibagikan lewat Git.
2. Baca [konteks proyek](../PROJECT_CONTEXT.md) dan
   [pembagian kerja](../docs/project_management/TEAM_WORKPLAN.md).
3. Niki memakai paket `human_A`, Robi memakai `human_B`. Buat salinan di folder
   `interim/human_annotations/work/`, jangan mengedit template bersama.
4. Selama anotasi independen, jangan membuka rating, keyword hints, manifest
   split, prediksi AI atau jawaban annotator lain. Git memberi akses repository
   bersama; independensi dijaga melalui prosedur ini, bukan pembatasan Gitignore.
5. Serahkan hasil kepada koordinator secara privat untuk validasi, IAA dan
   adjudikasi. File mentah/original tidak ditimpa.
6. Setelah QC dan keputusan evaluasi selesai, bagikan keluaran final yang
   disepakati pada `processed/` dengan versi, provenance dan split yang jelas.

Jika snapshot baru diperlukan, catat perubahan dan perbarui manifest/protokol
sesuai tahap. Jangan mengganti raw di belakang hasil audit/label yang sudah ada.
Berbagi dalam kelompok tidak mengubah status otorisasi/geografi atau menjadi
bukti izin publikasi ulang; status tersebut tetap mengikuti dokumentasi riset.
