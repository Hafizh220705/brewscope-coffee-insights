# BrewScope

BrewScope adalah proyek *Aspect-Based Sentiment Analysis* (ABSA) untuk
menganalisis ulasan coffee shop di wilayah Jatinangor. Alur utamanya mencakup
akuisisi data, validasi, preprocessing teks Bahasa Indonesia, deteksi aspek,
klasifikasi sentimen, evaluasi model, dan penyajian insight melalui Streamlit.

Konteks lengkap proyek tersedia di [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md).
Pembagian pekerjaan tim tersedia di
[docs/project_management/TEAM_WORKPLAN.md](docs/project_management/TEAM_WORKPLAN.md).

Tahap saat ini: **Stage 4A — infrastruktur anotasi manusia dan Gemini**.
Notebook: [03_human_ai_labeling.ipynb](notebooks/03_human_ai_labeling.ipynb).
[Protokol kerja tim](docs/research/stage4_annotation_protocol.md) memuat setup
API, paket manusia, evaluasi dan batas eksekusi. Run All aman tanpa API key.
250 kandidat manusia sudah disiapkan sebagai formulir kosong; human gold,
evaluasi Gemini dan full labeling belum dilakukan.

```powershell
.venv\Scripts\python.exe -m pip install -e ".[annotation,analysis,dev]"
.venv\Scripts\python.exe scripts/run_annotation.py --dry-run
.venv\Scripts\python.exe scripts/run_annotation.py --task prepare-human --execute
```

Brief Stage 4 mencatat `OWNER_ATTESTED` untuk penelitian dan pemrosesan AI
eksternal. Status 40 lokasi tetap `UNVERIFIED`; hak sumber dan wilayah perlu
dituntaskan untuk penelitian final. Rincian terbaru ada pada protokol Stage 4.

## Struktur repository

```text
.
├── app/                    # Aplikasi Streamlit
├── configs/                # Konfigurasi aspek, eksperimen, dan rekomendasi
├── data/
│   ├── raw/                # Data asli hasil akuisisi; jangan diubah langsung
│   ├── interim/            # Data hasil pembersihan sementara
│   ├── processed/          # Data siap training/evaluasi
│   └── annotations/        # Label dan hasil anotasi manual
├── docs/
│   ├── project_management/ # Pembagian kerja dan dokumen koordinasi
│   └── research/           # Catatan riset serta audit sumber data
├── models/                 # Artifact model dan vectorizer
├── notebooks/              # Eksplorasi dan komunikasi hasil
├── reports/                # Metrik, tabel, gambar, dan hasil eksperimen
├── scripts/                # Entry point pekerjaan batch
├── src/brewscope/          # Logika reusable untuk training dan aplikasi
└── tests/                  # Test pada interface module
```

Notebook hanya digunakan untuk eksplorasi. Logika yang dipakai ulang harus
diletakkan di `src/brewscope/` dan diuji melalui interface module-nya.

## Menyiapkan lingkungan Python

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Salin `.env.example` menjadi `.env`, kemudian masukkan token Apify baru hanya
ke `.env`. File tersebut sudah dikecualikan dari Git.

## Menjalankan pengambilan data

```powershell
python scripts/scrape_google_maps.py
```

Hasil mentah ditulis ke `data/raw/google_maps_reviews_jatinangor.csv`, sedangkan
jumlah ulasan dan lokasi file input dapat diatur melalui `.env`.

## Aturan data

- Jangan mengubah file di `data/raw/` secara manual.
- Jangan mencampurkan fixture/demo dengan dataset penelitian.
- Catat sumber, waktu akuisisi, parameter, versi scraper, dan checksum.
- Jangan memasukkan kredensial, proxy, atau data pribadi ke repository.

