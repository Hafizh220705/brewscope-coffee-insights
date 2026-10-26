# Protokol anotasi manusia dan AI — Stage 4

Tanggal: **26 Oktober 2026**, taxonomy **0.1.0-draft**, prompt **absa_gemini_v1**.
Entry point: `notebooks/03_human_ai_labeling.ipynb` dan `scripts/run_annotation.py`.
Taksonomi, schema canonical, dan artefak historis Stage 2/3 dipertahankan.

## 1. Otorisasi dan cakupan

Brief Stage 4 yang dikirim pemilik penelitian menyatakan dataset boleh dipakai
untuk penelitian dan diproses layanan AI eksternal, termasuk Gemini. Pernyataan
tersebut dicatat sebagai **OWNER_ATTESTED**. Ini adalah deklarasi pemilik;
belum ada dokumen izin/lisensi pihak sumber yang diverifikasi independen.
Otorisasi ini memperbarui gate operasional Stage 3 untuk persiapan manusia dan
pilot terkontrol. Metadata historis Stage 3 tidak ditulis ulang.

Seluruh 40 kedai masih **UNVERIFIED** secara administratif. Paket pilot tetap
memuat status ini pada manifest koordinator. Kualitas label tidak membuktikan lokasi.
Dataset raw tidak dihapus. Keputusan wilayah kelak disimpan terpisah dalam CSV
`coffee_shop_id,status,evidence_reference`, dengan status `VERIFIED_INSIDE`,
`VERIFIED_OUTSIDE`, atau `UNVERIFIED`. Ekspor dapat diregenerasi dari arsip anotasi
menggunakan `regenerate_geographic_scope`; full inference mensyaratkan keputusan
wilayah lengkap, kemudian mengecualikan yang `VERIFIED_OUTSIDE`.

Periksa [ketentuan Google Maps](https://www.google.com/help/terms_maps/) dan bukti
hak sumber sebelum publikasi atau pelatihan akhir. Jangan menganggap layanan
scraper atau deklarasi pemilik sebagai lisensi publikasi ulang. Keputusan terbaru
pemilik membolehkan dataset dan assignment kosong dilacak Git untuk kolaborasi
kelompok. Checkpoint/respons AI, debug serta folder kerja/submission independen
tetap diabaikan. Hasil final direview sebelum dibagikan. Rincian ada di
`data/README.md`; keputusan berbagi tim berbeda dari publikasi ulang terbuka.

## 2. Lingkungan dan Gemini

```powershell
.venv\Scripts\python.exe -m pip install -e ".[annotation,analysis,dev]"
.venv\Scripts\python.exe scripts/run_annotation.py --dry-run
```

SDK resmi yang diuji: **google-genai 2.33.0**. SDK lama `google-generativeai`
tidak digunakan. Integrasi memakai `client.models.generate_content`,
`response_mime_type=application/json`, dan `response_json_schema`; aturan
canonical lengkap diperiksa lokal setelah konversi. Lihat
[dokumentasi SDK](https://googleapis.github.io/python-genai/) dan
[structured output](https://ai.google.dev/gemini-api/docs/structured-output).
Structured output tidak menjamin label benar secara semantik.

Model awal: **gemini-3.5-flash-lite**, kandidat konfigurasi yang belum dipilih
melalui hasil empiris. Dokumentasi model menyatakan dukungan structured output;
halaman pricing mencantumkan Free Tier untuk teks. Kandidat brief
`gemini-2.5-flash` dan `gemini-2.5-flash-lite` tetap tersedia dalam konfigurasi,
tetapi dokumentasi terbaru membatasi akses 2.5 bagi project yang belum pernah
menggunakannya. Karena itu tidak diasumsikan semua akun dapat mengaksesnya.
Rujukan: [model 3.5](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite),
[model 2.5](https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash),
[pricing](https://ai.google.dev/gemini-api/docs/pricing), diperiksa 26 Oktober 2026.

Buat API key di [Google AI Studio](https://aistudio.google.com/api-keys).
Isi `GEMINI_API_KEY` hanya di `.env` lokal atau environment variable. Jangan
memasukkannya ke source, output notebook, screenshot, laporan, atau chat.
`.env` sudah diabaikan Git; placeholder disediakan di `.env.example` dan `.env`.

```powershell
.venv\Scripts\python.exe scripts/run_annotation.py --task check-provider --provider gemini --execute
```

Perintah tersebut hanya membaca metadata model, bukan mengirim review atau
membuktikan billing Free Tier. Saat implementasi ini key belum tersedia;
konektivitas dan akses model project aktual belum diverifikasi.

## 3. Free Tier, privasi, dan kuota

Isi `configs/annotation_runtime.yaml` dari project **aktual** di AI Studio:
`project.billing_tier=FREE_VERIFIED`, `verified_on`, `verification_reference`
(catatan/screenshot privat tanpa key), `rpm`, dan `daily_requests`.
Gunakan tanggal verifikasi maksimum tujuh hari sebelumnya, periksa kembali
billing sebelum setiap sesi. Nilai kuota default `null` sengaja menghentikan
generation cloud. Status Paid/Unknown menghentikan generation; tidak ada paid
fallback. Model lookup tidak dapat memverifikasi billing otomatis.

[Rate limits resmi](https://ai.google.dev/gemini-api/docs/rate-limits) berlaku
per project, berbeda antar model/tier. RPD reset tengah malam Pacific.
Ledger SQLite lokal mencatat setiap upaya request sebelum pengiriman, termasuk
retry dan request yang mungkin terputus. RPM dan RPD persisten berlaku lintas
run memakai `quota_scope` project yang sama. Jika batas input TPM diisi, estimasi
UTF-8 konservatif dipakai sebelum request; token aktual dicatat bila respons
menyediakannya. Pemakaian di aplikasi lain tidak terlihat ledger ini; cocokkan
sisa kuota dengan AI Studio. Counter lokal bukan jaminan billing nol.

[Ketentuan Gemini](https://ai.google.dev/gemini-api/terms) membedakan layanan
gratis dan berbayar. Pada unpaid services, input/output dapat digunakan untuk
pengembangan produk dan ditinjau manusia; jangan mengirim informasi pribadi,
sensitif, atau rahasia. Aturan pemrosesan paid services berbeda. Pertimbangan
ini penting sebelum mengirim review, meskipun kontennya dapat dibaca publik.

Pipeline hanya mengirim ID review dan teks, tanpa nama penulis, URL profil,
rating, nama kedai terpisah, atau keyword hints. Pemindaian email, nomor telepon,
nomor identitas, URL, dan handle menahan review yang dicurigai mengandung PII.
Pola otomatis tidak cukup mendeteksi nama/alamat atau informasi kontekstual.
Sebelum **review nyata** dikirim ke Gemini, pemeriksa harus memeriksa teks batch
yang direncanakan, lalu mengisi `privacy.external_pii_review_completed=true` dan
`review_reference`. Jika perlu redaksi, simpan turunan terversi dan peta offset;
jangan mengubah teks raw atau menebak span. Implementasi saat ini menahan kasus
PII, bukan meredaksinya secara diam-diam. Pilot manusia lokal tidak memerlukan
upload cloud; bagikan hanya paket yang diperlukan kepada anggota tim.

## 4. Paket 250 review manusia

```powershell
.venv\Scripts\python.exe scripts/run_annotation.py --task prepare-human --execute
```

Perintah idempotent menggunakan **250 ID kandidat Stage 3 yang sama**; tidak
mengganti sampling. SHA raw dan artefak Stage 3 diperiksa sebelum paket dibuat.
Hasil pada snapshot saat ini tepat **50 calibration + 150 development + 50
locked_validation**. Development dan locked validation adalah **200 review
anotasi independen**. Kelompok identik atau sangat mirip dipertahankan bersama;
ukuran nominal bisa berubah jika snapshot/pengelompokan berubah dengan alasan
terdokumentasi. Grouping dihitung pada seluruh 3.582 review eligible agar
duplikat di luar pilot dapat mewarisi split yang sama kelak.

File acuan koordinator, tidak digunakan annotator saat pengisian independen:

- `data/interim/human_annotations/pilot_manifest.json`: ID, split, kelompok,
  hash teks, versi, status lokasi; tidak berisi label.
- `corpus_duplicate_groups.csv`: seluruh ID eligible dan kelompoknya.

Repo tim dapat memuat metadata tersebut. Blinding tetap menjadi prosedur kerja:
annotator hanya menggunakan paketnya, tanpa membuka rating/keyword/manifest
split atau jawaban pihak lain selama pengisian independen. Gitignore bukan
kontrol akses per anggota. Original yang belum dikunci disimpan pada folder
`work/` atau `submissions/` yang diabaikan Git dan diserahkan privat ke koordinator.

Paket annotator:

- `assignments/human_A/calibration.jsonl` dan `independent.jsonl`.
- `assignments/human_B/calibration.jsonl` dan `independent.jsonl`.

Masing-masing annotator menerima **1.500 formulir pair**: 300 calibration dan
1.200 independent. Presence awal `null` dan status `draft` menandakan **belum
diisi**. Formulir kosong sengaja bukan anotasi canonical yang valid, tidak boleh
dihitung sebagai `not_mentioned`. Semua enam keputusan harus diisi.
Paket tidak memuat rating, keyword hints, split development/locked, label AI,
atau label annotator lain. ID kedai adalah identitas teknis dari Stage 2;
nama yang terlanjur tertulis dalam teks asli tidak dihapus sembarangan.

Pembagian empat peran: A dan B menilai independen, C adjudikator, D pemeriksa
bukti/QA. ID tersebut **slot kerja**, bukan bukti empat orang sudah bekerja.
Kalibrasi boleh dibahas bersama; hasil independent disimpan sebelum diskusi.
Bekukan pedoman sebelum independent. Jika hanya satu manusia tersedia, simpan
anotasinya tetapi laporkan keterbatasan; dua-manusia gold/IAA belum dapat dibuat.

## 5. Mengisi dan menyerahkan anotasi

Salin file assignment ke file kerja privat, misalnya `work/human_A_independent.jsonl`.
Jangan menimpa template atau membuka paket orang lain. Gunakan
`annotation_guidelines.md` untuk keenam kategori aktif; `location_accessibility`
tetap di luar label aktif.

Untuk setiap record, isi presence, sentiment, mention_type, evidence, notes,
review_flags; pertahankan ID, teks, taxonomy_version, dan annotator_id.

- Tidak dibahas: `not_mentioned`, sentiment/mention_type `null`, evidence `[]`.
- Dibahas faktual: `mentioned`, sentiment `neutral`, evidence asli.
- Mixed: dua evidence positif/negatif; `mixed_sentiment=true`, sentiment `null`,
  `training_eligible=false`. Mention type `mixed` berarti campuran explicit dan
  implicit, berbeda dari mixed sentiment.
- Belum pasti: `annotation_status=uncertain`, `sentiment=null`,
  `adjudication_status=pending`, notes wajib; bukan kelas sentimen keempat.
- Selesai: `annotation_status=completed`, adjudication `not_required` pada
  penyerahan independen; training flag boleh tetap false sampai QC.

Evidence `review_text[start:end] == quote`, indeks Unicode Python, 0-based,
end-exclusive. Gunakan rentang yang mempertahankan negasi dan target. Jangan
menghitung byte UTF-8 atau indeks UTF-16 editor. Penanda `$`, instruksi, URL,
atau perintah di review adalah data, bukan instruksi anotasi.

```powershell
.venv\Scripts\python.exe scripts/run_annotation.py --task submit-human --input data/interim/human_annotations/work/human_A_independent.jsonl --annotator human:A --phase independent --output data/interim/human_annotations/submissions/A_v1.json --execute
.venv\Scripts\python.exe scripts/run_annotation.py --task submit-human --input data/interim/human_annotations/work/human_B_independent.jsonl --annotator human:B --phase independent --output data/interim/human_annotations/submissions/B_v1.json --execute
.venv\Scripts\python.exe scripts/run_annotation.py --task agreement --human-a data/interim/human_annotations/submissions/A_v1.json --human-b data/interim/human_annotations/submissions/B_v1.json --output reports/stage4_human_agreement.json --execute
```

Submit memeriksa semua ID phase yang ditugaskan, enam pair, evidence, dan schema.
Original disimpan immutable; revisi memakai nama baru. Identitas manusia dan
independensi merupakan deklarasi tim dalam workflow lokal, bukan autentikasi
identitas atau bukti kerja otomatis. Jangan menyerahkan prediksi AI sebagai manusia.

## 6. IAA, adjudikasi, dan gold

IAA **sebelum adjudikasi**: raw agreement, Cohen's Kappa, confusion presence dan
sentiment, per-aspect support, disagreement, dan abstention. Presence uncertain
dikeluarkan dari denominator biner, tetapi coverage dilaporkan. Sentiment hanya
pada pair sama-sama mentioned/completed/nonmixed dengan polaritas tiga kelas.
Kappa marginal konstan atau tanpa data menjadi `null` dengan alasan, bukan 0/1
palsu. Jika anotasi independen belum tersedia, status `NOT_COMPUTED`.

File adjudikasi adalah JSON list. Setiap item berisi `review_id`, `aspect_id`,
`adjudicator_id` (contoh slot `human:C`), `reason`, dan `record` canonical final
untuk pair yang diputuskan. C wajib berbeda dari A/B. Semua disagreement dan
uncertainty wajib diselesaikan. Evidence yang berbeda tanpa beda label tetap
diperiksa QA. Jangan menyalin saran Gemini sebagai adjudikasi tanpa keputusan manusia.

File QA adalah JSON object: key `review_id|aspect_id`, value `status=APPROVED`,
`reviewer_id` (slot D), dan `notes` audit. D berbeda dari annotator/adjudikator.
Seluruh pair gold memerlukan pemeriksaan ini. Simpan artefak asli dan catatan.

```powershell
.venv\Scripts\python.exe scripts/run_annotation.py --task build-gold --human-a data/interim/human_annotations/submissions/A_v1.json --human-b data/interim/human_annotations/submissions/B_v1.json --adjudications data/interim/human_annotations/adjudications_v1.json --quality-review data/interim/human_annotations/qc_v1.json --output data/processed/human_gold_annotations.jsonl --execute
```

Gold JSONL menyimpan canonical record beserta split, kelompok, status lokasi,
provenance original, adjudikasi, dan QA; sidecar `.manifest.json` memuat hash.
Tidak ada file gold nyata dibuat pada implementasi awal karena manusia belum
melakukan anotasi.

## 7. Eksperimen AI terkontrol

```powershell
# Aman tanpa key: hanya fixture sintetis, bukan label data penelitian.
.venv\Scripts\python.exe scripts/run_annotation.py --provider mock --mode synthetic --execute --resume
# Setelah key dan project Free Tier/kuota terverifikasi: mulai dari sintetis.
.venv\Scripts\python.exe scripts/run_annotation.py --provider gemini --mode synthetic --limit 1 --execute --resume
# Setelah review privasi batch, smoke review nyata dibatasi maksimum lima.
.venv\Scripts\python.exe scripts/run_annotation.py --provider gemini --mode smoke-test --limit 5 --execute --resume
# Untuk prompt development saja; default split development.
.venv\Scripts\python.exe scripts/run_annotation.py --provider gemini --mode pilot --split development --limit 10 --execute --resume
```

Tanpa `--execute`, semua mode melakukan dry run. `--dry-run` dan `--execute`
saling eksklusif. Notebook Run All selalu mock/synthetic. Full labeling tidak
pernah dimulai otomatis dari notebook. Smoke lima review bukan estimasi akurasi.
Review sama yang pernah terkena smoke masuk development/calibration jika dipakai
untuk tuning; jangan menggunakan locked review untuk debugging prompt.

Retry transient/invalid output terbatas `max_attempts`; exponential backoff,
tanpa retry internal SDK yang melewati counter. HTTP 429 menghentikan run dengan
checkpoint; jangan retry tanpa batas atau mengganti provider berbayar. Respons
invalid disimpan sebagai invalid dan tidak dinormalisasi menjadi neutral/absent.
Respons asli serta error code berada di checkpoint privat, bukan laporan publik.

Resume menggunakan fingerprint dataset/model/prompt/schema/config dan hash teks
review. Status `valid` tidak dikirim lagi. Request yang tersimpan `in_flight`
setelah crash tidak dikirim otomatis karena delivery tidak diketahui. Periksa
ledger/provider dan arsip secara manual; buat eksperimen baru hanya bila memang
perlu, dengan risiko request ulang terdokumentasi. `retry_pending` setelah crash
juga ditahan. Lock yang tertinggal harus diperiksa sebelum dihapus. Tidak ada
jaminan exactly-once HTTP; ledger konservatif mengorbankan kuota untuk keamanan.
Gunakan directory default yang sama; pindah checkpoint/new prompt dapat memulai
eksperimen baru. Jangan menggandakan run identik di folder berbeda.

## 8. Freeze dan evaluasi locked holdout

Threshold pada config adalah **usulan**, belum keputusan empiris: detection
micro-F1 ≥0.80, macro-F1 ≥0.70, sentiment macro-F1 ≥0.70, end-to-end micro-F1
≥0.70, sedikitnya 40 locked reviews, tanpa output invalid/missing. Tim dapat
merevisi **sebelum** melihat locked outputs, kemudian set `criteria_frozen=true`
dan `criteria_reference`. Jalankan freeze yang menghasilkan manifest immutable.

```powershell
.venv\Scripts\python.exe scripts/run_annotation.py --task freeze-protocol --execute
.venv\Scripts\python.exe scripts/run_annotation.py --provider gemini --mode pilot --split locked_validation --execute --resume
.venv\Scripts\python.exe scripts/run_annotation.py --task evaluate --gold data/processed/human_gold_annotations.jsonl --checkpoint <FOLDER_CHECKPOINT> --split locked_validation --output data/interim/stage4_pilot_evaluation.json --execute
```

Perintah memakai `<FOLDER_CHECKPOINT>` sebagai placeholder path, ganti dengan
folder yang dicetak CLI. Evaluation development memakai `--split development`.
Jangan tuning prompt/model pada locked split; jika terlanjur, nyatakan split
terkontaminasi dan rancang holdout baru. Pilot kuota tidak mewakili distribusi alami.

Aspect detection: micro P/R/F1, macro/per-aspect F1 dan support. Conditional
sentiment dihitung pada **seluruh** gold-mentioned terselesaikan; aspek yang
terlewat atau abstained tetap salah, bukan dikeluarkan. Ini gold-conditioned
scoring, bukan klaim eksperimen forced-aspect. End-to-end menghitung pasangan
aspek-sentiment sehingga aspek tambahan/miss terhitung FP/FN. Pair mixed gold
dikecualikan dari evaluasi sentimen tiga kelas dan dilaporkan, tetapi tetap
dinilai presence. Confusion memiliki kolom `ABSTAIN_OR_MISSED`. Macro memakai
enam aspek/tiga sentimen tetap, zero-division=0 disertai flag/support; tidak ada
support sentiment menghasilkan metrik `null`.

Ollama opsional memakai endpoint loopback dan structured schema yang sama.
`qwen2.5:3b` sudah terpasang; availability lokal diperiksa. Tidak ada download.
Ganti `--provider ollama` untuk eksperimen dengan split/protokol yang sama.
Ketersediaan model tidak membuktikan akurasi; perbandingan manusia belum berjalan.

## 9. Human review, full, dan ekspor

Queue menandai invalid/offset, mixed, uncertain, rare aspects, implicit, negatif,
no-keyword pilot, duplikasi/konflik potensial, dan random audit atas output valid.
Prioritas merupakan heuristik, bukan confidence model. Random audit ditentukan
hash seed, fraction default 10%; laporkan denominator dan error temuan audit,
jangan hanya memeriksa kasus sulit.

`review_ai_output` menyimpan original dan koreksi sebagai event baru, reviewer,
alasan, model/prompt, serta hash. CLI `--task review-ai --input <FORM_JSON>
--checkpoint <FILE_REVIEW_CHECKPOINT_JSON> --annotator human:D --output <EVENT_JSON>
--execute` menerima form dengan `corrected_records` (enam record) dan `reason`.
`reviewed_ai_rows` mengonversi event ke arsip ekspor, `merge_gold_and_ai` selalu
mendahulukan gold manusia. Reviewer memutuskan training eligibility; mixed dan
uncertain tetap disimpan, tidak otomatis disetujui. Simpan event immutable.

Full generation mensyaratkan gold manusia nyata, evaluasi locked memenuhi
kriteria, fingerprint eksperimen cocok, project Free Tier/kuota dan privasi
jelas, keputusan wilayah final, pemeriksaan ketentuan sumber, serta
`full.explicitly_approved=true` dengan approval reference. Usulan perintah:

```powershell
.venv\Scripts\python.exe scripts/run_annotation.py --provider gemini --mode full --gold data/processed/human_gold_annotations.jsonl --geography-decisions data/interim/stage4_geographic_decisions.csv --limit 25 --execute --resume
```

Mulai batch kecil lalu tingkatkan limit sesuai sisa kuota; maksimal eligible
3.582 sebelum keputusan scope. Setiap valid prediction tetap menunggu QA.
Stage 4D baru selesai setelah QC dan random audit benar-benar dilakukan.

```powershell
# Ekspor gold yang benar-benar tersedia ke snapshot berversi.
.venv\Scripts\python.exe scripts/run_annotation.py --task export --gold data/processed/human_gold_annotations.jsonl --output data/processed/stage4_exports --execute
```

Output: presence satu baris/review, sentiment long format, arsip evidence lengkap.
Presence uncertain menjadi nilai kosong/null, bukan 0. Mixed/uncertain tetap
ada di long/archive dengan training_eligible=false. Status geografi dipertahankan;
ekspor eksploratif UNVERIFIED tidak dinyatakan siap Stage 5. Gunakan keputusan
wilayah terpisah saat regenerasi. Snapshot hash menghindari overwrite.
Seluruh pair/clause satu review dan kelompok duplikat harus satu split.
Review nonpilot belum diberi train/test final; Stage 5/6 menentukan split lengkap.
Label AI untuk training bukan gold independen untuk klaim akurasi classifier.
