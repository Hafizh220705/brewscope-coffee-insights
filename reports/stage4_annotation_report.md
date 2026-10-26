# Laporan Stage 4 — infrastruktur dan persiapan pilot

Tanggal pemeriksaan: **26 Oktober 2026**. Snapshot raw SHA-256
`7b87a53110041da74e976a6c9cb121c1dea7d73be70daeab58b2c07bef775719`.

## Hasil dan status tahap

**Stage 4A telah diimplementasikan dan diuji secara sintetis.** Paket pilot
nyata telah disiapkan sebagai formulir kosong. Akses Gemini project aktual
belum diuji karena API key belum tersedia. Tidak ada anotasi manusia, human
gold, hasil akurasi penelitian, atau full labeling yang diklaim selesai.

| Bagian | Status aktual |
|---|---|
| Stage 4A | Implementasi provider/prompt/schema/pipeline/manusia/evaluasi/ekspor tersedia; pengujian offline dan notebook lulus |
| Stage 4B | 250 kandidat sudah ditugaskan; pengisian manusia, IAA, adjudikasi, QA dan gold belum dilakukan |
| Stage 4C | Belum ada evaluasi Gemini/Ollama versus gold; model awal belum dipilih berdasarkan hasil empiris |
| Stage 4D | Belum dimulai; seluruh output AI masih memerlukan proses QA sebelum ekspor penelitian |
| Stage 5 | Belum siap; tidak ada TF-IDF atau training SVM/Random Forest/Naive Bayes |

## Artefak yang dibuat atau diperbarui

- `notebooks/03_human_ai_labeling.ipynb`: 19 bagian, 20 code cell telah dieksekusi.
- `src/brewscope/annotation/`: providers, runtime/prompt/gates, storage,
  validation, pipeline/usage/checkpoint, human, agreement, evaluation, export.
  Lokasi di bawah package `brewscope` mengikuti konvensi repo.
- `scripts/run_annotation.py`: CLI default dry run, mode synthetic/smoke/pilot/full,
  prepare/submit human, agreement, gold, prompt/protocol freeze, evaluation,
  human review AI, dan ekspor.
- `configs/annotation_runtime.yaml`: Gemini utama, candidate model, kuota null,
  kontrol biaya/privasi/otorisasi/scope, QA dan kriteria full.
- `prompts/absa_gemini_v1.md` serta `.manifest.json`: prompt dan hash sumber
  dibekukan; taxonomy/schema canonical Stage 3 tetap sama.
- `tests/annotation/`: **77 test Stage 4**, termasuk fixture 17 review sintetis,
  adapter SDK yang diinjeksi fake client, dan eksekusi notebook.
- `docs/research/stage4_annotation_protocol.md` serta
  `stage4_methodology_decisions.md`: protokol tim, sumber teknis primer,
  keputusan metode dan perintah kerja berikutnya.
- `data/interim/human_annotations/pilot_manifest.json`,
  `corpus_duplicate_groups.csv`, empat file assignment A/B: metadata dan formulir
  kosong, tanpa label yang direka. Seluruh file nyata ini lokal/diabaikan Git.
- `reports/stage4_notebook_summary.json`, `stage4_environment.json`,
  `stage4_validation_summary.json`: hasil aktual yang dapat diperiksa mesin.
- `pyproject.toml`: extra `annotation`; `.env.example` dan `.env`: placeholder
  `GEMINI_API_KEY` tanpa credential hardcoded; `README.md` dan
  `notebooks/README.md`: entry point dan petunjuk Stage 4.

Tidak dibuat file `human_gold_annotations.jsonl` atau dataset produksi berlabel
tanpa kerja manusia. Artefak label sintetis berada pada checkpoint bertanda
synthetic/fixture, terpisah dari raw dan keluaran penelitian final.

## SDK, model, dan status API

| Item | Hasil pemeriksaan |
|---|---|
| SDK Gemini | **google-genai 2.33.0**, terpasang dan dipin pada extra annotation |
| Dependency terkait | python-dotenv 1.2.4, jsonschema 4.26.0, PyYAML 6.0.3, pandas 2.3.3, tzdata 2026.5 |
| Model awal | **gemini-3.5-flash-lite**, dapat diganti melalui YAML |
| Kandidat brief | gemini-2.5-flash dan gemini-2.5-flash-lite tetap tercatat, akses tidak diasumsikan |
| Structured output | SDK response_json_schema tersedia dan diuji via fake SDK client; canonical dan evidence divalidasi lokal |
| Free Tier publik | Dokumentasi pricing menyatakan model awal memiliki Free Tier teks; dokumentasi model menyatakan structured output |
| Free Tier project aktual | **UNKNOWN / belum diverifikasi**; model lookup tidak membuktikan billing tier |
| RPM/RPD aktual | **Belum diketahui**; YAML null, live generation berhenti sampai diisi dari AI Studio |
| API key | Belum tersedia pada environment/.env saat pemeriksaan; placeholder disiapkan |
| Gemini konektivitas | Tidak dijalankan; tidak ada review yang diunggah |
| Gemini real smoke | **NOT_RUN**; batas implementasi maksimum 5 review dari calibration |
| Request generation Gemini | **0**; token Gemini yang digunakan oleh pekerjaan ini **0** |
| Ollama | Endpoint lokal tersedia; model **qwen2.5:3b** sudah terpasang, tanpa download |
| Inference/evaluasi Ollama | Belum dijalankan; hanya availability metadata diperiksa |

Pemilihan model awal mengikuti dokumentasi terbaru, bukan hasil perbandingan
akurasi. Dokumentasi 2.5 memperingatkan akses terbatas untuk project baru.
Rujukan primer diperiksa 26 Oktober 2026:
[model 3.5](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite),
[pricing](https://ai.google.dev/gemini-api/docs/pricing),
[model 2.5](https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash),
[SDK](https://googleapis.github.io/python-genai/),
[rate limits](https://ai.google.dev/gemini-api/docs/rate-limits).

Error API disimpan sebagai kode terklasifikasi; body exception tidak dicetak.
SDK retry internal dimatikan agar setiap retry tercatat counter lokal. Kuota
persisten per project, termasuk request gagal, dengan reset harian Pacific.
Tidak ada paid fallback. Run All notebook tidak menginisialisasi Gemini client.

## Pilot dan label manusia

250 ID Stage 3 dipertahankan, mencakup 40 kedai dan minimal tiga kandidat/kedai
pada union pilot. Pembagian aktual **50 calibration, 150 development, 50 locked
validation**; development+locked adalah 200 review independent annotation.
Grouping pada full eligible corpus menjaga teks identik dan kandidat sangat
mirip bersama. Sampel kuota ini tidak diperlakukan sebagai distribusi alami.

Paket A/B masing-masing 1.500 keputusan draft: 300 calibration, 1.200 independent.
Rating, keyword hints, prediksi AI, label orang lain dan penanda locked tidak
ditampilkan. Presence null pada template berarti belum diisi, bukan absent.
Peran C untuk adjudikasi dan D untuk QA; peran masih slot yang perlu dikerjakan
orang sungguhan. Tidak ada second annotator atau agreement yang direka.

IAA nyata **NOT_COMPUTED**. Gold manusia **NOT_AVAILABLE**. Evaluasi AI terhadap
gold **NOT_COMPUTED**. Semua utilitas tersedia dan diuji menggunakan fixture
sintetis yang tidak menjadi hasil penelitian.

## Pengujian aktual

```text
python -m pytest -q                         119 passed
Stage 4 subset                             77 passed
ruff check                                 All checks passed
pip check                                  No broken requirements found
Notebook Stage 4                            20/20 code cells, 0 error
```

Run notebook memvalidasi **17 review sintetis / 102 canonical decisions**,
termasuk mixed, uncertain, multi-aspek, sarkasme, negasi, slang, Unicode dan
prompt injection fixture. **17 panggilan MockProvider** berhasil pada demonstrasi
tersebut; resume menambah **0 request**. Angka ini bukan request cloud atau
akurasi model. Negative tests notebook menolak invalid JSON, missing aspect dan
hallucinated evidence. Pengujian lain mencakup retry, quota stop, durable budget,
crash/unknown delivery, privasi, immutable human originals, gold/QC, Kappa,
missed/hallucinated aspect, mixed export, split leakage dan hash sumber.

**37 file baseline terlindungi tidak berubah**, termasuk raw, flag/kandidat,
taxonomy/schema Stage 3, laporan, tabel/gambar Stage 2/3 dan notebook sebelumnya.
Tidak ada raw review ditampilkan pada output notebook Stage 4.

## Batas dan pekerjaan berikutnya

Otorisasi operasional adalah **OWNER_ATTESTED**, dari brief Stage 4. Izin sumber
independen tetap belum terverifikasi; seluruh 40 lokasi **UNVERIFIED**. Pilot
terkontrol dan persiapan infrastruktur tidak mengubah fakta tersebut. Periksa
[ketentuan Gemini](https://ai.google.dev/gemini-api/terms) terkait pemrosesan
unpaid services, serta [ketentuan Maps](https://www.google.com/help/terms_maps/)
sebelum publikasi/training akhir. Jangan mempublikasikan raw/assignment nyata.

Pekerjaan yang perlu dilakukan tim: isi key lokal, verifikasi billing dan kuota
project, review privasi batch, kerjakan calibration dan dua anotasi independen,
adjudikasi/QA, buat gold, tuning di development lalu freeze kriteria/protokol,
evaluasi locked, baru putuskan full. Keputusan wilayah disimpan terpisah agar
dataset dapat diregenerasi tanpa menghapus anotasi atau raw. Random audit output
valid diperlukan untuk menaksir kesalahan yang tidak ditangkap validator.

Perintah awal:

```powershell
.venv\Scripts\python.exe scripts/run_annotation.py --task prepare-human --execute
.venv\Scripts\python.exe scripts/run_annotation.py --task check-provider --provider gemini --execute
.venv\Scripts\python.exe scripts/run_annotation.py --provider mock --mode synthetic --execute --resume
```

Perintah submit, IAA, adjudikasi, gold, smoke, eksperimen, freeze, full dan ekspor
terdapat pada [protokol kerja](../docs/research/stage4_annotation_protocol.md).
Jangan menjalankan full sebelum semua gate dan pekerjaan empiris terpenuhi.
