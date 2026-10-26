from __future__ import annotations
import argparse
import hashlib
import os
from decimal import Decimal
from pathlib import Path
import pandas as pd
from apify_client import ApifyClient
from dotenv import load_dotenv

# ===== KONFIGURASI =====
PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")

ACTOR_ID = "compass/google-maps-reviews-scraper"

INPUT_CSV = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "google_maps_places_jatinangor.csv"
)

OUTPUT_CSV = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "google_maps_reviews_jatinangor_raw.csv"
)

COLUMNS = [
    "review_id",
    "nama_tempat",
    "rating",
    "tanggal_review",
    "teks_review",
    "url_tempat",
]

# ===== MEMBACA DAFTAR COFFEE SHOP =====
def read_places(max_places: int) -> list[dict]:
    if not INPUT_CSV.is_file():
        raise FileNotFoundError(
            f"Daftar coffee shop tidak ditemukan: {INPUT_CSV}"
        )

    df = pd.read_csv(
        INPUT_CSV,
        encoding="utf-8-sig",
        dtype=str
    ).fillna("")

    if "url" not in df.columns:
        raise ValueError(
            "CSV daftar tempat harus memiliki kolom 'url'."
        )

    df["url"] = df["url"].str.strip()

    df = df[
        df["url"].str.startswith("https://")
    ].drop_duplicates(subset="url")

    return df.head(max_places).to_dict("records")

# ===== NORMALISASI REVIEW =====
def normalize_reviews(items: list[dict]) -> pd.DataFrame:
    rows = []

    for item in items:
        review_text = str(
            item.get("text")
            or item.get("reviewText")
            or ""
        ).strip()

        # Abaikan review tanpa teks
        if not review_text:
            continue

        place_name = str(
            item.get("title")
            or item.get("placeName")
            or ""
        ).strip()

        place_url = str(
            item.get("inputStartUrl")
            or item.get("placeUrl")
            or item.get("url")
            or ""
        ).strip()

        date = str(
            item.get("publishedAtDate")
            or item.get("publishedAt")
            or item.get("publishAt")
            or ""
        ).strip()

        review_id = str(
            item.get("reviewId") or ""
        ).strip()

        # Buat ID jika reviewId tidak tersedia
        if not review_id:
            key = (
                f"{item.get('placeId', '')}|"
                f"{place_url}|{date}|{review_text}"
            )

            review_id = hashlib.sha256(
                key.encode("utf-8")
            ).hexdigest()

        rows.append({
            "review_id": review_id,
            "nama_tempat": place_name,
            "rating": item.get(
                "stars",
                item.get("rating", "")
            ),
            "tanggal_review": date,
            "teks_review": review_text,
            "url_tempat": place_url,
        })

    df = pd.DataFrame(rows, columns=COLUMNS)

    return df.drop_duplicates(subset="review_id")

# ===== MENYIMPAN DATASET =====
def save_reviews(
    new_reviews: pd.DataFrame
) -> tuple[int, int]:

    OUTPUT_CSV.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if OUTPUT_CSV.is_file():
        old_reviews = pd.read_csv(
            OUTPUT_CSV,
            dtype=str,
            encoding="utf-8-sig"
        ).fillna("")

        if not set(COLUMNS).issubset(old_reviews.columns):
            raise ValueError(
                f"Kolom CSV lama tidak cocok: {OUTPUT_CSV}"
            )

        old_reviews = old_reviews[COLUMNS]

    else:
        old_reviews = pd.DataFrame(columns=COLUMNS)

    # Gabungkan dataset lama dan baru
    combined = pd.concat(
        [old_reviews, new_reviews],
        ignore_index=True
    )

    # Hapus duplikat
    combined = combined.drop_duplicates(
        subset="review_id",
        keep="first"
    )

    added = len(combined) - len(old_reviews)

    combined.to_csv(
        OUTPUT_CSV,
        index=False,
        encoding="utf-8-sig"
    )

    return added, len(combined)

# ===== MAIN PROGRAM =====
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Google Maps Reviews Scraper via Apify"
    )

    parser.add_argument(
        "--run",
        action="store_true",
        help="Jalankan Actor dan gunakan kredit Apify"
    )

    parser.add_argument(
        "--max-places",
        type=int,
        default=40
    )

    parser.add_argument(
        "--max-reviews",
        type=int,
        default=170,
        help="Maksimal review per coffee shop"
    )

    parser.add_argument(
        "--charge-cap",
        type=Decimal,
        default=Decimal("0.05"),
        help="Batas tagihan Actor pay-per-event dalam USD"
    )

    args = parser.parse_args()

    # ===== VALIDASI KONFIGURASI =====
    if (
        args.max_places < 1
        or args.max_reviews < 1
        or args.charge_cap <= 0
    ):
        parser.error(
            "max-places, max-reviews, "
            "dan charge-cap harus lebih dari 0"
        )

    places = read_places(args.max_places)

    if not places:
        raise ValueError(
            "Tidak ada URL Google Maps valid."
        )

    print("=" * 55)
    print("GOOGLE MAPS REVIEWS SCRAPER")
    print("=" * 55)

    print(f"Jumlah coffee shop: {len(places)}")
    print(f"Review per tempat: {args.max_reviews}")
    print(
        f"Target maksimal: "
        f"{len(places) * args.max_reviews} review"
    )
    print(f"Charge cap: USD {args.charge_cap}")
    print("=" * 55)

    # ===== PREVIEW MODE =====
    if not args.run:
        print(
            "PREVIEW MODE: Actor belum dijalankan."
        )
        print(
            "Tambahkan --run untuk memulai scraping."
        )
        return

    # ===== LOAD API TOKEN =====
    api_token = os.getenv(
        "APIFY_TOKEN", ""
    ).strip()

    if (
        not api_token
        or api_token == "ISI_TOKEN_APIFY_KAMU"
    ):
        raise ValueError(
            "APIFY_TOKEN belum diisi pada file .env"
        )

    # ===== KONFIRMASI =====
    print(
        "\nPERINGATAN: Proses ini menggunakan kredit Apify."
    )

    confirmation = input(
        "Ketik JALANKAN untuk melanjutkan: "
    )

    if confirmation.strip() != "JALANKAN":
        print("Scraping dibatalkan.")
        return

    # ===== INITIALIZE CLIENT =====
    client = ApifyClient(api_token)

    # ===== ACTOR INPUT =====
    run_input = {
        "language": "id",
        "maxReviews": args.max_reviews,
        "personalData": False,
        "startUrls": [
            {"url": place["url"]}
            for place in places
        ],
    }

    # ===== RUN ACTOR =====
    print("\nMemulai proses scraping...")

    run = client.actor(ACTOR_ID).call(
        run_input=run_input,
        max_total_charge_usd=args.charge_cap,
        restart_on_error=False,
    )

    if run is None:
        raise RuntimeError(
            "Actor tidak mengembalikan informasi run."
        )

    print(f"Run ID: {run.id}")
    print(f"Status: {run.status}")

    # ===== FETCH DATASET =====
    dataset_id = run.default_dataset_id

    if not dataset_id:
        raise RuntimeError(
            "Actor tidak mengembalikan dataset ID."
        )

    print(f"Dataset ID: {dataset_id}")

    items = list(
        client.dataset(dataset_id).iterate_items()
    )

    # ===== PROCESS DATASET =====
    reviews = normalize_reviews(items)

    added, total = save_reviews(reviews)

    # ===== SUMMARY =====
    print("\n" + "=" * 55)
    print("SCRAPING SELESAI")
    print("=" * 55)

    print(f"Total item Apify: {len(items)}")
    print(f"Review teks unik: {len(reviews)}")
    print(f"Review baru: {added}")
    print(f"Total dataset: {total}")
    print(f"Output: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()