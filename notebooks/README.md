# Notebook penelitian BrewScope

## Tahap 4 — manusia dan bantuan Gemini

Entry point: [03_human_ai_labeling.ipynb](03_human_ai_labeling.ipynb).
Run All memakai 17 fixture sintetis/MockProvider tanpa jaringan atau API key.
Notebook menyiapkan formulir kosong 250 kandidat asli, bukan label manusia/AI.
Modul reusable dan CLI ada di `src/brewscope/annotation` dan
`scripts/run_annotation.py`, sesuai brief Stage 4.

```powershell
.venv\Scripts\python.exe -m pip install -e ".[annotation,analysis,dev]"
.venv\Scripts\python.exe scripts/run_annotation.py --task prepare-human --execute
.venv\Scripts\python.exe scripts/run_annotation.py --provider mock --mode synthetic --execute --resume
.venv\Scripts\python.exe -m pytest -q
```

Pilih kernel BrewScope dan Restart & Run All. Pengujian repository juga
mengeksekusi notebook Stage 4. Petunjuk key, kuota Free Tier, kerja manusia,
adjudikasi, evaluasi dan ekspor ada di
[protokol Stage 4](../docs/research/stage4_annotation_protocol.md).

Brief Stage 4 memperbarui otorisasi menjadi `OWNER_ATTESTED`, termasuk pilot
dan AI eksternal. Status geografis tetap UNVERIFIED. Gate historis pada dokumen
Stage 3 tidak ditulis ulang; gunakan protokol Stage 4 untuk keputusan operasional
saat ini. Full labeling menunggu gold, evaluasi, QA, scope dan persetujuan.

## Tahap 2 dan 3 — artefak historis

Tahap 3: [02_aspect_taxonomy.ipynb](02_aspect_taxonomy.ipynb) memuat taksonomi
berbasis literatur, schema/pedoman anotasi, fixture sintetis, dan sampling 250
kandidat tanpa label. Anotasi aktual menunggu gate geografis dan hak penggunaan.
Instalasi extra `analysis,dev` di bawah juga mencakup PyYAML dan jsonschema.

Eksekusi otomatis Tahap 3 dari root:

```powershell
.\.venv\Scripts\python.exe -c "from pathlib import Path; import nbformat; from nbclient import NotebookClient; p=Path('notebooks/02_aspect_taxonomy.ipynb'); n=nbformat.read(p,as_version=4); NotebookClient(n,timeout=180,kernel_name='brewscope').execute(); nbformat.write(n,p)"
.\.venv\Scripts\python.exe -m pytest tests/test_stage3_taxonomy_notebook.py -q
```

Notebook memakai sumber lokal dan tidak mengunduh literatur saat Run All.
Jejak verifikasi sumber dan BibTeX tersedia pada `docs/research/`; manifest/hash
konfigurasi dan kandidat tersedia pada `reports/stage3_taxonomy_summary.json`.

Notebook utama Tahap 2 adalah [01_data_audit_eda.ipynb](01_data_audit_eda.ipynb).
Seluruh fungsi analisis berada di notebook; tidak diperlukan module audit terpisah.

## Environment dan kernel

Jalankan dari root repository menggunakan PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[analysis,dev]"
.\.venv\Scripts\python.exe -m ipykernel install --prefix .venv --name brewscope --display-name "BrewScope (.venv)"
```

Buka notebook di editor Jupyter yang digunakan tim, pilih kernel **BrewScope
(.venv)** atau interpreter `.venv`, kemudian **Restart Kernel and Run All**.
Notebook mendukung working directory root maupun `notebooks/`.

Untuk eksekusi otomatis dari root repository:

```powershell
.\.venv\Scripts\python.exe -c "from pathlib import Path; import nbformat; from nbclient import NotebookClient; p=Path('notebooks/01_data_audit_eda.ipynb'); n=nbformat.read(p,as_version=4); NotebookClient(n,timeout=180,kernel_name='brewscope').execute(); nbformat.write(n,p)"
```

## Input dan hasil

Input tunggal: `data/raw/google_maps_reviews_jatinangor_raw.csv`.
Tanggal acuan audit dan semua ambang eksploratif didefinisikan pada bagian 2.
Angka bergantung pada snapshot CSV dan kamus keyword yang digunakan; jika sumber
berubah, jalankan ulang seluruh notebook agar laporan dan grafik tetap sinkron.

Output yang ditulis ulang saat eksekusi:

- `reports/data_audit_report.md`: laporan dengan angka aktual dan interpretasi.
- `reports/data_audit_summary.json`: ringkasan, parameter, versi, checksum, dan kamus aspek.
- `reports/tables/`: tabel kualitas, kedai, duplikasi, rating, panjang teks, dan aspek.
- `reports/figures/`: delapan PNG 300 DPI, juga tertanam dalam output notebook.
- `data/interim/review_audit_flags.csv`: satu baris flag per baris sumber.

Dataset mentah tidak ditulis ulang. Tahap 2 tidak menghasilkan label sentimen,
dataset filtered, atau model. Teks berulang antar-ID dan review pendek tidak
dihapus otomatis. Keputusan audit lama pada `reports/data_validation/` menggunakan
aturan berbeda; gunakan laporan Tahap 2 sebagai rujukan terbaru.

## Pengujian

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_data_audit_notebook.py -q
```

Test membaca cell lokal bertag `audit-core` untuk menguji aturan yang sama dengan
notebook, termasuk dataset kosong, schema hilang, rating invalid, konflik ID,
teks kosong, duplikasi potensial, agregasi kedai, dan boundary keyword.
