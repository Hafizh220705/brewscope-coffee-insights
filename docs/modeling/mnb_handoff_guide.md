# Panduan Modeling Multinomial Naive Bayes (Handoff ke SVM & RF)

Dokumen ini adalah panduan kerja untuk rekan yang mengerjakan **Multinomial
Naive Bayes (MNB)** pada notebook modeling. Notebook yang sama akan dilanjutkan
oleh rekan lain untuk **SVM** dan **Random Forest** setelah MNB selesai dan
di-push.

> **Nama notebook: `notebooks/03_modeling_all_models.ipynb` sejak awal.**
> Rekan MNB mengerjakan section MNB lebih dulu, lalu push. Rekan SVM/RF
> menambah section di file yang sama setelahnya. **Jangan rename file setelah
> di-push** — git akan mencatatnya sebagai file baru dan history terbelah.

## 1. Konteks singkat

- Label adalah **pseudo-label** (`auto:lexical_preannotation_v1`), bukan human
  gold. Semua laporan evaluasi harus menyebut ini.
- Split **sudah final**. Jangan membuat split baru dengan alasan apa pun.
- Satu notebook modeling dipakai untuk ketiga algoritma (MNB dulu, lalu SVM
  dan RF menyusul di file yang sama) supaya preprocessing, vectorizer, dan
  split benar-benar identik.
- Mulai dari varian teks `text_clean`. Varian lain (`text_no_stopwords_stemmed`,
  dst.) dieksplorasi setelah baseline selesai.

## 2. Persiapan environment

Dari root repo (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[preprocessing,modeling]"
```

Sanity check versi (penting untuk kompatibilitas artefak joblib antar rekan):

```powershell
python -c "import sklearn, pandas, numpy; print(sklearn.__version__, pandas.__version__, numpy.__version__)"
```

Target saat ini: **Python 3.11.x + `scikit-learn 1.9.1`**. Ini standar tim.
Python 3.14 dipakai pada percobaan MNB pertama dan artefaknya terbukti
kompatibel (hasil audit lintas versi cocok persis), tetapi Python 3.11 lebih
stabil untuk ekosistem ML — gunakan 3.11 untuk semua pekerjaan modeling
berikutnya. Jika versi rekan lain berbeda jauh, diskusi dulu sebelum
menyimpan artefak model.

## 3. File yang dipakai

| Keperluan | File |
|---|---|
| Task A — aspect detection | `data/processed/modeling/splits/aspect_detection_with_split.csv` |
| Task B — aspect sentiment | `data/processed/modeling/splits/aspect_sentiment_with_split.csv` |

Kolom penting:

- Task A: target = `aspect_product_quality`, `aspect_service`,
  `aspect_price_value`, `aspect_ambience`, `aspect_facilities`,
  `aspect_cleanliness` (biner); teks = varian `text_*`; pembagian =
  kolom `split` (`train` / `validation` / `test`).
- Task B: target = `sentiment` (`negative` / `neutral` / `positive`);
  kelompok aspek = `aspect_category`; teks gabungan pembanding =
  `aspect_text_model`; pembagian = kolom `split`.

Jangan dipakai sebagai fitur: `review_id`, `annotation_id`, `coffee_shop_id`,
`review_text_raw`, rating, nama kedai, `duplicate_group_*`, atau metadata
labeling apa pun.

## 4. Konvensi notebook dan output

- Nama notebook: `notebooks/03_modeling_all_models.ipynb` (satu file untuk
  MNB, SVM, dan RF).
- Jalankan notebook **top-to-bottom tanpa error** sebelum push. Simpan output
  sel (jangan hanya menyimpan kode tanpa hasil).
- Beri penanda section yang jelas: `## Task A — MNB`, `## Task B — MNB`,
  dst. Section SVM dan RF akan menyusul setelah MNB selesai.
- Struktur output per algoritma (jangan menimpa artefak algoritma lain):

```text
reports/tables/modeling/mnb/     # metrik, classification report, prediksi
reports/figures/modeling/mnb/    # confusion matrix, grafik
data/processed/modeling/mnb/     # vectorizer, model, dan artefak eksperimen
```

## 5. Aturan anti-leakage (wajib, berlaku untuk ketiga algoritma)

1. Fit `TfidfVectorizer` **hanya pada baris `train`**.
2. Transform `validation` dan `test` memakai vectorizer train yang sama.
3. Pemilihan hyperparameter (mis. `alpha`) hanya memakai `validation` atau
   cross-validation **di dalam train**. `test` hanya untuk evaluasi akhir.
4. Class weighting / resampling / feature selection (jika ada) hanya pada
   train.
5. Jangan menyentuh atau membuat ulang kolom `split`.

## 6. Task A — Aspect Detection (multi-label)

- Satu baris = satu review. Target = 6 kolom biner sekaligus.
- Bentuk baseline: `OneVsRestClassifier(MultinomialNB())` di atas matriks
  TF-IDF.
- Konfigurasi TF-IDF baseline yang disarankan (seragam untuk ketiga model):

```python
TfidfVectorizer(
    sublinear_tf=True,
    min_df=2,
    ngram_range=(1, 2),
    max_features=10_000,
)
```

- Imbalance: `cleanliness` dan `facilities` langka. Jangan menilai model hanya
  dari accuracy.
- Metrik minimum: macro-F1, micro-F1, dan precision/recall/F1 + support per
  aspek.
- `alpha` MNB: mulai dari `1.0`. Jika menyesuaikan, lakukan pada validation
  (atau `GridSearchCV` di dalam train saja).

### 6.1 Artefak vectorizer untuk handoff (PENTING)

Supaya SVM dan Random Forest membandingkan hal yang sama dengan MNB, **simpan
vectorizer dan matriks TF-IDF Task A** setelah fit pada train:

```python
import joblib
from pathlib import Path

out_dir = Path("data/processed/modeling/mnb/task_a")
out_dir.mkdir(parents=True, exist_ok=True)

joblib.dump(tfidf, out_dir / "tfidf_text_clean.joblib")   # vectorizer ter-fit
joblib.dump(X_train_vec, out_dir / "X_train_text_clean.joblib")
joblib.dump(X_val_vec, out_dir / "X_validation_text_clean.joblib")
joblib.dump(X_test_vec, out_dir / "X_test_text_clean.joblib")
```

Rekan SVM dan RF tinggal `joblib.load` matriks ini — tidak fit ulang, tidak
boleh beda parameter. Jika MNB nanti menambahkan varian teks lain (mis.
`text_no_stopwords_stemmed`), simpan dengan nama file yang mencerminkan varian
tersebut.

### 6.2 Simpan hasil Task A

- Metrik: `reports/tables/modeling/mnb/task_a_metrics.csv` (satu baris per
  aspek + baris macro/micro average; kolom: `aspect`, `precision`, `recall`,
  `f1`, `support`, `split`).
- Prediksi test: `reports/tables/modeling/mnb/task_a_test_predictions.csv`
  (kolom `review_id`, enam kolom probabilitas/prediksi, `split`).
- Model ter-fit: `data/processed/modeling/mnb/task_a/model_mnb.joblib`.

## 7. Task B — Aspect Sentiment Classification

- Satu baris = satu pasangan review-aspek. Target = `negative` / `neutral` /
  `positive`.
- **Baseline utama: classifier terpisah untuk setiap `aspect_category`**
  (6 model MNB).
- **Pembanding: satu classifier gabungan** memakai `aspect_text_model`.
- Distribusi sangat timpang: positive 4.217 / neutral 1.099 / negative 282.
  Prioritaskan **macro-F1** dan **recall kelas negative**. Accuracy menyesatkan.
- Metrik minimum: macro-F1, weighted-F1, recall negative, confusion matrix,
  dan metrik per aspek.

### 7.1 Artefak vectorizer untuk handoff

Simpan vectorizer + matriks per aspek dan untuk model gabungan:

```text
data/processed/modeling/mnb/task_b/
├── tfidf_text_clean_per_aspect.joblib        # dict: aspect_category -> vectorizer ter-fit
├── X_*_text_clean_per_aspect.joblib          # dict: aspect_category -> matriks
├── tfidf_aspect_text_model.joblib            # vectorizer gabungan
└── X_*_aspect_text_model.joblib              # matriks gabungan
```

Rekan SVM dan RF memakai persis artefak ini untuk enam model per-aspek dan
satu model gabungan.

### 7.2 Simpan hasil Task B

- Metrik per aspek: `reports/tables/modeling/mnb/task_b_metrics_per_aspect.csv`.
- Metrik model gabungan: `reports/tables/modeling/mnb/task_b_metrics_combined.csv`.
- Confusion matrix: `reports/figures/modeling/mnb/task_b_confusion_matrix.png`
  (satu grid untuk 6 aspek, dan satu untuk model gabungan; 300 DPI seperti
  konvensi notebook sebelumnya).
- Model ter-fit per aspek: `data/processed/modeling/mnb/task_b/model_mnb_<aspect>.joblib`.
- Prediksi test: `reports/tables/modeling/mnb/task_b_test_predictions.csv`
  (kolom `annotation_id`, `aspect_category`, `sentiment_true`,
  `sentiment_pred`, `split`).

## 8. Manifest eksperimen

Buat `data/processed/modeling/mnb/mnb_manifest.json` berisi minimal:

- tanggal, nama rekan, versi scikit-learn/pandas;
- nama varian teks yang dipakai (`text_clean`);
- konfigurasi vectorizer lengkap;
- konfigurasi model (mis. `OneVsRestClassifier(MultinomialNB(alpha=1.0))`);
- `random_state` yang dipakai (jika ada);
- hash SHA-256 file input split;
- daftar artefak output.

Gunakan hash input yang sudah tercatat di
`data/processed/modeling/splits/split_manifest.json`.

## 9. Checklist selesai MNB (sebelum push)

- [ ] Notebook `03_modeling_all_models.ipynb` jalan top-to-bottom tanpa error
      (section MNB).
- [ ] Tidak ada fit vectorizer di luar train.
- [ ] Test dievaluasi sekali saja, setelah semua tuning selesai.
- [ ] Vectorizer + matriks tersimpan di `data/processed/modeling/mnb/` untuk
      Task A, enam aspek Task B, dan model gabungan.
- [ ] Metrik, prediksi, confusion matrix, dan manifest tersimpan.
- [ ] Laporan evaluasi menyebut label sebagai pseudo-label.
- [ ] Hash input split cocok dengan `split_manifest.json`.

Verifikasi cepat sebelum push:

```powershell
python -c "import pandas as pd, json; m=json.load(open('data/processed/modeling/mnb/mnb_manifest.json', encoding='utf-8')); print(m['date'], m['task_a']['macro_f1'], m['task_b']['macro_f1'])"
```

(sesuaikan isi manifest dengan yang benar-benar ditulis)

## 10. Handoff ke SVM dan Random Forest

Setelah MNB di-push, rekan SVM/RF melanjutkan **di notebook yang sama**
(`notebooks/03_modeling_all_models.ipynb`) dengan menambah section baru
setelah section MNB, dengan kewajiban:

1. `joblib.load` vectorizer dan matriks dari `data/processed/modeling/mnb/`
   untuk `text_clean` — jangan fit ulang.
2. Split train/validation/test identik dengan MNB (dari kolom `split`).
3. Baseline pertama: `LinearSVC` atau `SVC` dalam `OneVsRestClassifier` untuk
   Task A; SVM per aspek untuk Task B. Kemudian Random Forest dengan
   `class_weight='balanced'` (atau `balanced_subsample`).
4. Metrik yang dilaporkan sama persis: macro-F1, micro-F1 (Task A);
   macro-F1, weighted-F1, recall negative (Task B).
5. Artefak disimpan di folder algoritma masing-masing
   (`reports/.../svm/`, `reports/.../random_forest/`) supaya tidak menimpa MNB.
6. Jika eksplorasi varian teks (mis. `text_no_stopwords_stemmed`) dianggap
   perlu, diskusikan dengan seluruh tim agar ketiga algoritma memakai varian
   yang sama sebelum membandingkan.

Perbandingan akhir SVM vs RF vs MNB baru sah jika ketiganya memakai split,
vektor fitur, dan varian teks yang sama.
