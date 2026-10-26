# Keputusan metodologi Stage 4

26 Oktober 2026. Dokumen ini melengkapi keputusan Stage 3; taxonomy dan schema
canonical **0.1.0-draft** tidak dimigrasikan. Enam aspek tetap aktif, lokasi
provisional tidak menjadi kelas produksi.

| Keputusan | Implementasi dan alasan |
|---|---|
| Otorisasi pilot | OWNER_ATTESTED berdasarkan brief Stage 4, termasuk AI eksternal. Izin pihak sumber independen belum terbukti; pemeriksaan publikasi/training akhir tetap dicatat. |
| Geografi | 40 UNVERIFIED dipertahankan. Pilot boleh disiapkan; full memakai keputusan wilayah terpisah beserta bukti. Tidak ada penghapusan raw. |
| Dua task | Presence multi-label 0–6 dan sentiment per aspek mentioned; enam keputusan eksplisit wajib pada setiap review. |
| Schema | Schema inference ringan dikonversi ke schema canonical Stage 3 dan validator semantik lokal. Output hilang tidak diisi otomatis. |
| Evidence | Offset Unicode Python, 0-based/end-exclusive, quote persis slice; hallucination span ditolak, retry terbatas. |
| Mixed | Opini positif dan negatif tetap dua evidence, pair sentiment null; tidak masuk training tiga kelas. Presence tetap mentioned. |
| Uncertain | Abstention/workflow, bukan kelas; notes wajib, tidak menjadi negatif/netral otomatis. |
| General praise | Tidak diberi enam label positif; flag gap. Prompt menangani negasi, implicit, slang, code-switching, typo dan sarkasme. |
| Gemini utama | google-genai 2.33.0 resmi; default kandidat 3.5 Flash-Lite mengikuti dokumentasi terbaru. Pemilihan ilmiah menunggu gold, bukan promosi benchmark eksternal. |
| Provider seam | GeminiProvider, OllamaProvider, MockProvider berbagi structured-response interface. Prompt, validasi, penyimpanan, manusia dan evaluasi terpisah di src/brewscope/annotation sesuai konvensi repo. |
| Tidak ada cloud otomatis | Run All notebook mock/synthetic; live hanya CLI execute setelah gate. Full dibatasi gold, evaluasi, scope, kuota dan persetujuan eksplisit. |
| Kuota | Nilai RPM/RPD null sampai diverifikasi pada project aktual. Counter SQLite per project, reset Pacific, tiap retry dihitung, tidak ada paid fallback. |
| Privasi | Metadata personal tidak dikirim; PII pola ditahan, pemeriksaan kontekstual manusia wajib sebelum batch nyata ke Gemini. Tidak mengubah teks/offset diam-diam. |
| Pilot | Gunakan tepat 250 kandidat Stage 3. Split aktual 50 calibration, 150 development, 50 locked; minimal 3 kandidat/kedai tetap dipenuhi pada union pilot. Tidak dipaksakan per split. |
| Grouping | Teks casefold+whitespace identik digabung lintas kedai; near-match ≥8 token, shared five-token shingle, Jaccard token ≥.85 dan SequenceMatcher ≥.92. Transitive grouping pada full eligible corpus. Ini kandidat kemiripan, bukan deduplikasi/penghapusan. Parafrasa semantik jauh masih perlu pemeriksaan manusia. |
| Manusia | Dua annotator independen, adjudikator ketiga, QA keempat. Paket blind, tidak memuat split locked, rating, keyword atau AI. Slot A/B/C/D tidak dianggap bukti pekerjaan aktual. |
| Gold | Original manusia immutable, disagreement diselesaikan, semua pair diaudit. AI tidak pernah menjadi human gold. Belum tersedia gold nyata. |
| IAA | Praadjudikasi; coverage/abstention, per-aspect support, raw/Kappa/confusion. Kappa tanpa variasi atau data null beralasan. |
| Evaluasi | Detection micro/macro/per-aspect; sentiment pada seluruh gold-mentioned resolved termasuk missed-aspect sebagai error; end-to-end pair P/R/F1. Mixed dan invalid dilaporkan terpisah. |
| Threshold | Proposal eksplisit dalam config; belum dipraregistrasi. Manifest freeze harus ada sebelum locked inference/evaluation. Perubahan setelah holdout dibuka memerlukan evaluasi baru yang jujur. |
| Validitas AI | Valid schema ≠ valid semantik ≠ approved training. Queue prioritas dan random audit; koreksi disimpan event baru. |
| Ekspor | Presence nullable; mixed/uncertain long/archive tetap ada; training hanya pair yang layak. Human gold didahulukan. Tidak membuat dataset produksi berlabel palsu. |
| Leakage | Review/pair/clause/kelompok sama satu split. Gold untuk prompt development bukan independent test classifier. Full split training diputuskan Stage 5/6. |
| Reproducibility | SHA raw/taxonomy/schema/prompt, ID/split/group/seed, model config, waktu, respons, validasi dan request budget tersimpan. Prompt manifest immutable; versi baru wajib bila prompt berubah. |

## Batas klaim dan tahapan

Stage 4A mencakup infrastruktur yang bisa diuji offline; akses Gemini project
aktual belum terbukti tanpa key. Stage 4B membutuhkan kerja manusia nyata.
Stage 4C membutuhkan evaluasi terhadap gold independen; kandidat model default
belum boleh diklaim terbaik. Stage 4D memerlukan generation dan human QC yang
benar-benar selesai. Tidak ada training SVM/RF/Naive Bayes, TF-IDF, tuning
classifier, ranking bisnis, atau dashboard dalam perubahan ini.

## Versi prompt dan pembekuan

Prompt v1 dihasilkan dari taxonomy dan bagian interpretasi pedoman Stage 3;
pernyataan gate historis Stage 3 tidak menjadi instruksi semantik model.
Sidecar `prompts/absa_gemini_v1.manifest.json` mengikat hash prompt dan sumber.
Jika revisi diperlukan, buat file v2, ubah header/version/path di config, lalu
`--task freeze-prompt --execute`; jangan menimpa v1/manifest eksperimen lama.
Manifest evaluation protocol mengikat kriteria, prompt, model, taxonomy dan
snapshot. Gunakan holdout baru jika telah dipakai untuk tuning; freeze bukan
mekanisme untuk menghapus riwayat penggunaan data.

Rujukan teknis primer beserta batas akses/biaya tercatat pada
[protokol Stage 4](stage4_annotation_protocol.md). Dokumen tersebut juga memuat
semua perintah kerja tim dan format adjudikasi/QA. Hasil aktual tersedia pada
`reports/stage4_annotation_report.md`; belum ada hasil akurasi penelitian.
