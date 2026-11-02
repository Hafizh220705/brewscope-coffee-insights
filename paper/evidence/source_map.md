# Peta Sumber Klaim

| Informasi | Sumber utama |
|---|---|
| Tujuan dan konteks proyek | `README.md`, `RESULTS.md` |
| Data mentah dan kolom | `data/raw/google_maps_reviews_jatinangor_raw.csv` |
| Akuisisi Google Maps | `scripts/scrape_google_maps.py` |
| Taksonomi aspek | `configs/labeling/aspect_taxonomy.yaml` |
| Aturan pelabelan | `scripts/label_brewscope.py`, `docs/annotation/annotation_guidelines.md` |
| QA label | `reports/labeling/qa_report.json` |
| Preprocessing | `notebooks/01_preprocessing.ipynb`, `data/processed/modeling/preprocessing_manifest.json` |
| Split dan leakage audit | `notebooks/02_data_splitting.ipynb`, `data/processed/modeling/splits/split_manifest.json` |
| Konfigurasi MNB | `data/processed/modeling/mnb/mnb_manifest.json` |
| Konfigurasi SVM | `data/processed/modeling/svm/svm_manifest.json` |
| Konfigurasi RF | `data/processed/modeling/rf/rf_manifest.json` |
| Task A per aspek | `reports/tables/modeling/*/task_a_metrics.csv` |
| Task B per aspek | `reports/tables/modeling/*/task_b_metrics_per_aspect.csv` |
| Task B gabungan | `reports/tables/modeling/*/task_b_metrics_combined.csv` |
| Distribusi aspek/sentimen | `reports/tables/preprocessing/` |
| Insight bisnis | `reports/tables/insights/` |
| Environment | manifest model dan `pyproject.toml` |

## Prioritas sumber

1. Manifest model dan CSV hasil.
2. `RESULTS.md`.
3. Notebook eksekusi.
4. `README.md`.
5. `PROJECT_CONTEXT.md` hanya untuk konteks historis; status modeling di sana sudah usang.

## Catatan konsistensi

- Alur aktual: scraping, labeling, preprocessing, splitting, modeling, insight.
- Angka Task A 3.424 adalah subset modeling; 3.538 adalah jumlah ulasan bertulis pada tahap anotasi/preprocessing.
- Insight Task B memakai 5.598 pasangan dari seluruh split.
- Nilai `p_value=0` dalam CSV merupakan hasil pembulatan output; jangan menafsirkannya sebagai probabilitas matematis tepat nol.
