"""Rich archives and Stage 5 tables; preserve mixed/uncertain, enforce group splits."""

import copy
import io
import json
from collections import defaultdict

import pandas as pd

from .human import duplicate_groups
from .storage import atomic_text, digest, immutable_json
from .validation import ASPECTS, SENTIMENTS, AnnotationError


def review_ai_output(archive, corrected_records, *, reviewer_id, reason, validator):
    """Return a new audit event. Never mutate model predictions or human originals."""
    if (
        not reviewer_id.startswith("human:")
        or not reason.strip()
        or archive["status"] != "valid"
    ):
        raise AnnotationError("HUMAN_REVIEW_REQUIREMENTS_NOT_MET")
    sources = {
        r["review_id"]: {
            k: r[k] for k in ("review_text", "coffee_shop_id", "data_origin")
        }
        for r in archive["records"]
    }
    validator.batch(corrected_records, sources)
    if any(r["annotation_status"] == "draft" for r in corrected_records):
        raise AnnotationError("UNFINISHED_HUMAN_REVIEW")
    event = {
        "kind": "human_reviewed_ai",
        "original_request_key": archive["request_key"],
        "original_records_sha256": digest(archive["records"]),
        "reviewer_id": reviewer_id,
        "reason": reason,
        "original_records": archive["records"],
        "corrected_records": copy.deepcopy(corrected_records),
        "model_provenance": archive["provenance"],
    }
    event["sha256"] = digest(event)
    return event


def reviewed_ai_rows(event, assignments, validator):
    """Conversion is explicit; a review event alone cannot overwrite human gold."""
    expected = digest({k: v for k, v in event.items() if k != "sha256"})
    if event.get("kind") != "human_reviewed_ai" or event.get("sha256") != expected:
        raise AnnotationError("INVALID_HUMAN_REVIEW_EVENT")
    validator.batch(event["corrected_records"])
    result = []
    for record in event["corrected_records"]:
        item = assignments.get(record["review_id"])
        if item is None:
            raise AnnotationError("REVIEW_ASSIGNMENT_REQUIRED")
        result.append(
            {
                "record": copy.deepcopy(record),
                "split": item["split"],
                "duplicate_group": item["duplicate_group"],
                "geography_status": item.get("geography_status", "UNVERIFIED"),
                "label_source": "human_reviewed_ai",
                "provenance": event,
            }
        )
    return result


def merge_gold_and_ai(gold_rows, ai_rows):
    """Human gold wins at review level; no mixing different decision sets."""
    human_ids = {r["record"]["review_id"] for r in gold_rows}
    return [
        *gold_rows,
        *[r for r in ai_rows if r["record"]["review_id"] not in human_ids],
    ]


def regenerate_geographic_scope(rows, decisions_path, *, final=False):
    from .runtime import geographic_scope

    reviews = {
        row["record"]["review_id"]: {
            "review_id": row["record"]["review_id"],
            "coffee_shop_id": row["record"]["coffee_shop_id"],
            "geography_status": row.get("geography_status", "UNVERIFIED"),
        }
        for row in rows
    }
    scoped = {
        r["review_id"]: r
        for r in geographic_scope(list(reviews.values()), decisions_path, final=final)
    }
    return [
        {
            **copy.deepcopy(row),
            "geography_status": scoped[row["record"]["review_id"]]["geography_status"],
        }
        for row in rows
        if row["record"]["review_id"] in scoped
    ]


def assert_no_leakage(rows):
    splits = defaultdict(set)
    sources = {}
    for row in rows:
        record = row["record"]
        rid = record["review_id"]
        splits[("review", rid)].add(row["split"])
        splits[("provided_group", row["duplicate_group"])].add(row["split"])
        sources[rid] = record
    # Recompute exact and conservative near-match groups; never trust labels alone.
    grouped = duplicate_groups(list(sources.values()))
    for row in rows:
        splits[("recomputed_group", grouped[row["record"]["review_id"]])].add(
            row["split"]
        )
    if any(len(values) > 1 for values in splits.values()):
        raise AnnotationError("REVIEW_OR_DUPLICATE_GROUP_SPLIT_LEAKAGE")


def export_tables(
    rows, validator, directory, *, allow_synthetic=False, source_terms_reviewed=False
):
    if not rows:
        raise AnnotationError("NO_LABELS_TO_EXPORT")
    validator.batch([row["record"] for row in rows])
    assert_no_leakage(rows)
    for row in rows:
        if row["record"]["data_origin"] == "synthetic" and not allow_synthetic:
            raise AnnotationError("SYNTHETIC_EXPORT_NOT_A_RESEARCH_DATASET")
        if row["label_source"] not in (
            "human_gold",
            "human_reviewed_ai",
        ) or not row.get("provenance"):
            raise AnnotationError("UNREVIEWED_AI_CANNOT_ENTER_STAGE5")
    by_review = defaultdict(list)
    sentiment_rows = []
    for row in rows:
        r = row["record"]
        by_review[r["review_id"]].append(row)
        if r["aspect_presence"] != "not_mentioned":
            eligible = (
                r["training_eligible"]
                and r["annotation_status"] == "completed"
                and r["aspect_presence"] == "mentioned"
                and not r["mixed_sentiment"]
                and r["sentiment"] in SENTIMENTS
            )
            sentiment_rows.append(
                {
                    "review_id": r["review_id"],
                    "coffee_shop_id": r["coffee_shop_id"],
                    "review_text": r["review_text"],
                    "aspect_id": r["aspect_category"],
                    "sentiment": r["sentiment"],
                    "annotation_source": row["label_source"],
                    "taxonomy_version": r["taxonomy_version"],
                    "confidence_or_review_flag": "mixed"
                    if r["mixed_sentiment"]
                    else (
                        "uncertain"
                        if r["annotation_status"] == "uncertain"
                        else "human_reviewed"
                    ),
                    "adjudication_status": r["adjudication_status"],
                    "training_eligible": eligible,
                    "split": row["split"],
                    "geography_status": row.get("geography_status", "UNVERIFIED"),
                }
            )
    presence_rows = []
    for rid, group in sorted(by_review.items()):
        first = group[0]
        r = first["record"]
        row = {
            "review_id": rid,
            "coffee_shop_id": r["coffee_shop_id"],
            "review_text": r["review_text"],
            "label_source": first["label_source"],
            "split": first["split"],
            "geography_status": first.get("geography_status", "UNVERIFIED"),
        }
        if len(group) != 6:
            raise AnnotationError("EXPORT_REQUIRES_ONE_DECISION_SET_PER_REVIEW")
        for entry in group:
            record = entry["record"]
            value = record["aspect_presence"]
            row[record["aspect_category"]] = (
                None
                if value == "uncertain" or record["annotation_status"] == "uncertain"
                else int(value == "mentioned")
            )
        presence_rows.append(row)
    presence = pd.DataFrame(presence_rows)
    for aspect in ASPECTS:
        presence[aspect] = presence[aspect].astype("Int64")
    sentiment = pd.DataFrame(
        sentiment_rows,
        columns=[
            "review_id",
            "coffee_shop_id",
            "review_text",
            "aspect_id",
            "sentiment",
            "annotation_source",
            "taxonomy_version",
            "confidence_or_review_flag",
            "adjudication_status",
            "training_eligible",
            "split",
            "geography_status",
        ],
    )
    # Version directory prevents accidental rewriting of an earlier published snapshot.
    archive_hash = digest(rows)
    directory = directory / archive_hash[:16]
    immutable_json(
        directory / "export_manifest.json",
        {
            "archive_sha256": archive_hash,
            "review_count": len(presence),
            "annotation_pairs": len(rows),
            "synthetic": allow_synthetic,
            "final_geography_verified": all(
                row.get("geography_status") in ("VERIFIED_INSIDE", "VERIFIED_OUTSIDE")
                for row in rows
            ),
            "stage5_ready": not allow_synthetic
            and source_terms_reviewed
            and all(row.get("geography_status") == "VERIFIED_INSIDE" for row in rows)
            and all(row["record"]["annotation_status"] == "completed" for row in rows),
            "source_terms_reviewed": source_terms_reviewed,
        },
    )
    for name, frame in [
        ("aspect_presence_dataset.csv", presence),
        ("aspect_sentiment_dataset.csv", sentiment),
    ]:
        output = io.StringIO()
        frame.to_csv(output, index=False)
        atomic_text(directory / name, output.getvalue())
    atomic_text(
        directory / "annotation_archive.jsonl",
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
    )
    return {
        "directory": str(directory),
        "presence_rows": len(presence),
        "sentiment_rows": len(sentiment),
        "archive_pairs": len(rows),
    }
