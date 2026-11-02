# Bahan Pendukung Paper BrewScope

Folder ini berisi fakta, tabel, dan visualisasi untuk paper. Isinya bukan naskah paper siap terbit.

## Struktur

- `evidence/`: catatan terstruktur untuk lima bagian paper.
- `tables/`: tabel ringkas hasil ekstraksi artefak eksperimen.
- `figures/`: visualisasi beresolusi 300 DPI.
- `scripts/generate_paper_assets.py`: generator tabel dan visualisasi.

## Temuan utama

- Data sumber: 3.538 ulasan bertulis dari 40 coffee shop di Jatinangor.
- Task A: 3.424 ulasan untuk klasifikasi multi-label enam aspek.
- Task B: 5.598 pasangan review-aspek untuk tiga kelas sentimen.
- Task A terbaik: Linear SVM, macro-F1 0,8775 dan micro-F1 0,9133.
- Task B terbaik: Random Forest per aspek, pooled macro-F1 0,7013, weighted-F1 0,8347, dan recall negative 0,5283.
- Keluhan prediksi terbanyak: service, facilities, dan cleanliness.
- Ambience memiliki sentiment score agregat tertinggi, 0,8945.

## Regenerasi aset

```powershell
python paper/scripts/generate_paper_assets.py
```

Kebutuhan sudah tersedia dalam optional dependency proyek:

```powershell
python -m pip install -e ".[modeling]"
```

## Urutan pemakaian

1. Baca `evidence/source_map.md` untuk sumber setiap klaim.
2. Pakai `evidence/research_method_notes.md` untuk metode.
3. Ambil angka hasil dari `tables/`, bukan mengetik ulang dari gambar.
4. Gunakan `evidence/limitations.md` saat menyusun interpretasi.
5. Cantumkan caption dan nomor tabel/gambar sesuai template jurnal tujuan.

## Batas interpretasi

Label penelitian merupakan pseudo-label deterministik berbasis leksikal. Metrik harus dibaca sebagai performa terhadap label tersebut. Insight bisnis merupakan agregasi prediksi model dan memerlukan validasi lapangan sebelum dipakai untuk keputusan operasional.
