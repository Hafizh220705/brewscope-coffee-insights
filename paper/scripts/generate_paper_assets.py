"""Bangun tabel dan visualisasi pendukung paper dari artefak eksperimen."""
from pathlib import Path
import json
import shutil

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "paper"
FIG = OUT / "figures"
TAB = OUT / "tables"
FIG.mkdir(parents=True, exist_ok=True)
TAB.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid", context="paper")

MODELS = {"mnb": "MNB", "svm": "SVM", "rf": "RF"}
ASPECTS = ["product_quality", "service", "price_value", "ambience", "facilities", "cleanliness"]


def save(name: str) -> None:
    plt.tight_layout()
    plt.savefig(FIG / name, dpi=300, bbox_inches="tight")
    plt.close()


# Tabel statistik dataset dan split
pre = pd.read_csv(ROOT / "reports/tables/preprocessing/preprocessing_dataset_summary.csv")
split = pd.read_csv(ROOT / "reports/tables/splitting/split_summary.csv")
pre.to_csv(TAB / "dataset_statistics.csv", index=False)
split.to_csv(TAB / "split_statistics.csv", index=False)

# Definisi aspek
pd.DataFrame([
    ("product_quality", "Rasa, mutu, porsi, variasi, dan penyajian produk"),
    ("service", "Staf, pemesanan, waktu tunggu, dan respons layanan"),
    ("price_value", "Harga, promosi, keterjangkauan, dan kesepadanan nilai"),
    ("ambience", "Suasana, interior, kebisingan, dan kenyamanan"),
    ("facilities", "Wi-Fi, parkir, colokan, toilet, AC, dan tempat duduk"),
    ("cleanliness", "Kebersihan dan higiene"),
], columns=["aspect", "definition"]).to_csv(TAB / "aspect_definitions.csv", index=False)

# Konfigurasi model
configs = [
    ("MNB", "Task A", "alpha=0.01"), ("MNB", "Task B per-aspect", "alpha=0.03"),
    ("MNB", "Task B combined", "alpha=0.03"),
    ("SVM", "Task A", "C=1.0; class_weight=balanced; max_iter=5000"),
    ("SVM", "Task B per-aspect", "C=10.0; class_weight=balanced; max_iter=5000"),
    ("SVM", "Task B combined", "C=1.0; class_weight=balanced; max_iter=5000"),
    ("RF", "Task A", "n_estimators=300; max_depth=20; min_samples_leaf=1; class_weight=balanced"),
    ("RF", "Task B per-aspect", "n_estimators=300; max_depth=None; min_samples_leaf=1; class_weight=balanced"),
    ("RF", "Task B combined", "n_estimators=300; max_depth=None; min_samples_leaf=1; class_weight=balanced"),
]
pd.DataFrame(configs, columns=["model", "task", "selected_configuration"]).to_csv(TAB / "model_configuration.csv", index=False)

# Ringkasan model dari manifest
rows = []
for key, label in MODELS.items():
    manifest = json.loads((ROOT / f"data/processed/modeling/{key}/{key}_manifest.json").read_text(encoding="utf-8"))
    ta, tb = manifest["task_a"], manifest["task_b"]
    per, combined = tb["per_aspect_models"], tb["combined_model"]
    rows.append({"model": label, "task_a_macro_f1": ta["macro_f1"], "task_a_micro_f1": ta["micro_f1"],
                 "task_b_macro_f1": per["pooled_macro_f1"], "task_b_weighted_f1": per["pooled_weighted_f1"],
                 "task_b_recall_negative": per["pooled_recall_negative"],
                 "task_b_combined_macro_f1": combined["pooled_macro_f1"]})
comparison = pd.DataFrame(rows)
comparison.to_csv(TAB / "model_comparison.csv", index=False)

# Figure 1: distribusi sentimen per aspek
counts = pd.read_csv(ROOT / "reports/tables/preprocessing/sentiment_counts_by_aspect.csv").set_index("aspect_category").loc[ASPECTS]
counts.to_csv(TAB / "sentiment_counts_by_aspect.csv")
counts[["negative", "neutral", "positive"]].plot(kind="bar", stacked=True, color=["#c44e52", "#8c8c8c", "#55a868"], figsize=(9, 5))
plt.xlabel("Aspek"); plt.ylabel("Jumlah pasangan review-aspek"); plt.title("Distribusi Sentimen per Aspek")
plt.xticks(rotation=25, ha="right"); plt.legend(title="Sentimen")
save("01_dataset_distribution.png")

# Figure 2: perbandingan model
long = comparison.melt("model", var_name="metric", value_name="score")
labels = {"task_a_macro_f1": "Task A macro-F1", "task_a_micro_f1": "Task A micro-F1",
          "task_b_macro_f1": "Task B macro-F1", "task_b_weighted_f1": "Task B weighted-F1",
          "task_b_recall_negative": "Task B recall negative", "task_b_combined_macro_f1": "Task B combined macro-F1"}
long["metric"] = long["metric"].map(labels)
plt.figure(figsize=(11, 5.5)); ax = sns.barplot(data=long, x="metric", y="score", hue="model", palette="Set2")
ax.set_ylim(0, 1); ax.set_xlabel(""); ax.set_ylabel("Skor"); ax.set_title("Perbandingan Kinerja Model pada Test Set")
plt.xticks(rotation=25, ha="right"); plt.legend(title="Model", ncol=3)
save("02_model_comparison.png")

# Tabel dan heatmap Task A
frames = []
for key, label in MODELS.items():
    df = pd.read_csv(ROOT / f"reports/tables/modeling/{key}/task_a_metrics.csv")
    df = df[(df["split"] == "test") & (df["aspect"].isin(ASPECTS))].copy(); df["model"] = label
    frames.append(df)
task_a = pd.concat(frames, ignore_index=True)
task_a.to_csv(TAB / "task_a_results.csv", index=False)
pivot_a = task_a.pivot(index="model", columns="aspect", values="f1").reindex(index=MODELS.values(), columns=ASPECTS)
plt.figure(figsize=(9, 3.5)); sns.heatmap(pivot_a, annot=True, fmt=".3f", cmap="YlGn", vmin=0, vmax=1)
plt.xlabel("Aspek"); plt.ylabel("Model"); plt.title("Task A: F1 per Aspek pada Test Set")
save("03_task_a_f1_heatmap.png")

# Tabel dan heatmap Task B
frames = []
for key, label in MODELS.items():
    df = pd.read_csv(ROOT / f"reports/tables/modeling/{key}/task_b_metrics_per_aspect.csv")
    df = df[(df["split"] == "test") & (df["aspect"].isin(ASPECTS))].copy(); df["model"] = label
    frames.append(df)
task_b = pd.concat(frames, ignore_index=True)
task_b.to_csv(TAB / "task_b_results.csv", index=False)
pivot_b = task_b.pivot(index="model", columns="aspect", values="macro_f1").reindex(index=MODELS.values(), columns=ASPECTS)
plt.figure(figsize=(9, 3.5)); sns.heatmap(pivot_b, annot=True, fmt=".3f", cmap="YlOrBr", vmin=0, vmax=1)
plt.xlabel("Aspek"); plt.ylabel("Model"); plt.title("Task B: Macro-F1 per Aspek pada Test Set")
save("04_task_b_f1_heatmap.png")

# Figure 5: precision-recall negative
plt.figure(figsize=(8, 5.5)); ax = sns.scatterplot(data=task_b, x="recall_negative", y="precision_negative", hue="model", style="aspect", size="support_negative", sizes=(60, 260), palette="Set2")
ax.set_xlim(-0.03, 1.03); ax.set_ylim(-0.03, 1.03); ax.set_title("Precision–Recall Kelas Negative pada Test Set")
ax.set_xlabel("Recall negative"); ax.set_ylabel("Precision negative"); plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
save("05_negative_precision_recall.png")

# Figure 6: support vs performance
plt.figure(figsize=(8, 5.5)); ax = sns.scatterplot(data=task_b, x="support_negative", y="macro_f1", hue="model", style="aspect", s=110, palette="Set2")
ax.set_xlabel("Support kelas negative"); ax.set_ylabel("Macro-F1"); ax.set_title("Support Negative dan Kinerja Task B")
plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
save("06_support_vs_performance.png")

# Figure 7: distribusi prediksi insight; salin tabel prioritas
shop = pd.read_csv(ROOT / "reports/tables/insights/shop_aspect_sentiment.csv")
summary = shop.groupby("aspect_category")[["n_negative", "n_neutral", "n_positive"]].sum().reindex(ASPECTS)
summary.div(summary.sum(axis=1), axis=0).plot(kind="bar", stacked=True, color=["#c44e52", "#8c8c8c", "#55a868"], figsize=(9, 5))
plt.xlabel("Aspek"); plt.ylabel("Proporsi prediksi"); plt.title("Distribusi Prediksi Sentimen pada Seluruh Data")
plt.xticks(rotation=25, ha="right"); plt.legend(["Negative", "Neutral", "Positive"], title="Sentimen")
save("07_sentiment_distribution.png")

priorities = pd.read_csv(ROOT / "reports/tables/insights/improvement_priorities.csv")
priorities.to_csv(TAB / "improvement_priorities.csv", index=False)
top = priorities.head(15).copy()
plt.figure(figsize=(10, 6)); ax = sns.scatterplot(data=top, x="share_negative", y="n_negative", size="n_total", hue="aspect_category", sizes=(70, 500), alpha=.8)
for _, r in top.iterrows():
    ax.annotate(r["shop_name"], (r["share_negative"], r["n_negative"]), xytext=(4, 3), textcoords="offset points", fontsize=7)
ax.set_xlabel("Proporsi negative"); ax.set_ylabel("Jumlah negative"); ax.set_title("Prioritas Perbaikan Coffee Shop (15 Teratas)")
plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
save("08_improvement_priority.png")

# Salin confusion matrix model terpilih untuk dokumentasi kesalahan klasifikasi.
shutil.copy2(ROOT / "reports/figures/modeling/rf/task_b_confusion_matrix.png", FIG / "09_rf_task_b_confusion_matrix.png")

assert len(comparison) == 3 and len(task_a) == 18 and len(task_b) == 18
assert set(counts.columns) == {"negative", "neutral", "positive"}
print(f"Selesai: {len(list(FIG.glob('*.png')))} figure, {len(list(TAB.glob('*.csv')))} tabel")
