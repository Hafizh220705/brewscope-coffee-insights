"""Full canonical validation plus completeness and Unicode evidence semantics."""

import json
from collections import Counter

from jsonschema import Draft202012Validator

from .storage import digest, read_json

ASPECTS = (
    "product_quality",
    "service",
    "price_value",
    "ambience",
    "facilities",
    "cleanliness",
)
SENTIMENTS = ("positive", "neutral", "negative")
FLAGS = (
    "general_praise",
    "out_of_taxonomy",
    "needs_context",
    "sarcasm",
    "code_switching",
    "misspelling",
)


class AnnotationError(ValueError):
    """Error codes only: no review contents, credentials, or API body in logs."""


class AnnotationValidator:
    def __init__(self, schema_path):
        self.schema = read_json(schema_path)
        Draft202012Validator.check_schema(self.schema)
        self.validator = Draft202012Validator(self.schema)
        self.version = self.schema["properties"]["taxonomy_version"]["const"]
        if tuple(self.schema["properties"]["aspect_category"]["enum"]) != ASPECTS:
            raise AnnotationError("TAXONOMY_MIGRATION_REQUIRED")

    def record(self, record):
        if list(self.validator.iter_errors(record)):
            raise AnnotationError("CANONICAL_SCHEMA_ERROR")
        text = record["review_text"]
        evidence = record["evidence"]
        for span in evidence:
            if not (0 <= span["start"] < span["end"] <= len(text)):
                raise AnnotationError("INVALID_OFFSET")
            if text[span["start"] : span["end"]] != span["quote"]:
                raise AnnotationError("EVIDENCE_MISMATCH")
        polarities = {s["opinion_sentiment"] for s in evidence}
        opposed = {"positive", "negative"} <= polarities
        if opposed != record["mixed_sentiment"]:
            raise AnnotationError("MIXED_EVIDENCE_INCONSISTENT")
        types = {s["mention_type"] for s in evidence}
        if evidence:
            expected_type = "mixed" if len(types) > 1 else next(iter(types))
            if record["mention_type"] != expected_type:
                raise AnnotationError("MENTION_TYPE_INCONSISTENT")
        if record["annotation_status"] == "completed":
            if record["adjudication_status"] == "pending":
                raise AnnotationError("UNRESOLVED_COMPLETED_RECORD")
            if None in polarities:
                raise AnnotationError("UNRESOLVED_EVIDENCE")
            if record["sentiment"] is not None:
                non_neutral = polarities - {"neutral"}
                expected = next(iter(non_neutral)) if non_neutral else "neutral"
                if record["sentiment"] != expected:
                    raise AnnotationError("PAIR_EVIDENCE_POLARITY_MISMATCH")
        if record["annotation_status"] == "uncertain" and not record["notes"].strip():
            raise AnnotationError("UNCERTAINTY_REASON_REQUIRED")
        return record

    def batch(self, records, reviews=None, *, require_complete=True):
        seen = set()
        groups = {}
        for record in records:
            self.record(record)
            identity = (
                record["review_id"],
                record["aspect_category"],
                record["annotator_id"],
                record["taxonomy_version"],
            )
            if identity in seen:
                raise AnnotationError("DUPLICATE_REVIEW_ASPECT_ANNOTATOR")
            seen.add(identity)
            groups.setdefault((record["review_id"], record["annotator_id"]), []).append(
                record
            )
            if reviews is not None:
                source = reviews.get(record["review_id"])
                if source is None or any(
                    record[k] != source[k]
                    for k in ("review_text", "coffee_shop_id", "data_origin")
                ):
                    raise AnnotationError("REVIEW_IDENTITY_MISMATCH")
        for group in groups.values():
            if require_complete and Counter(
                r["aspect_category"] for r in group
            ) != Counter(ASPECTS):
                raise AnnotationError("INCOMPLETE_ASPECT_DECISIONS")
            if (
                len(
                    {
                        (r["review_text"], r["coffee_shop_id"], r["data_origin"])
                        for r in group
                    }
                )
                != 1
            ):
                raise AnnotationError("INCONSISTENT_REVIEW_CONTEXT")
        if (
            reviews is not None
            and require_complete
            and set(reviews) != {r["review_id"] for r in records}
        ):
            raise AnnotationError("MISSING_REVIEW_DECISIONS")
        return records


def inference_schema():
    """API-compatible subset; all richer canonical rules are enforced locally."""

    def enum(values):
        return {
            "type": ["string", "null"] if None in values else "string",
            "enum": values,
        }

    opinion = {
        "type": "object",
        "properties": {
            "quote": {"type": "string"},
            "start": {"type": "integer"},
            "end": {"type": "integer"},
            "opinion_sentiment": enum([*SENTIMENTS, None]),
            "mention_type": enum(["explicit", "implicit"]),
            "target": {"type": "string"},
        },
    }
    opinion["required"] = list(opinion["properties"])
    decision = {
        "type": "object",
        "properties": {
            "aspect_id": enum(list(ASPECTS)),
            "presence": enum(["mentioned", "not_mentioned", "uncertain"]),
            "sentiment": enum([*SENTIMENTS, None]),
            "mention_type": enum(["explicit", "implicit", "mixed", None]),
            "mixed_sentiment": {"type": "boolean"},
            "uncertain": {"type": "boolean"},
            "evidence": {"type": "array", "items": opinion},
            "notes": {"type": "string"},
            "review_flags": {"type": "array", "items": enum(list(FLAGS))},
        },
    }
    decision["required"] = list(decision["properties"])
    return {
        "type": "object",
        "properties": {
            "review_id": {"type": "string"},
            "decisions": {"type": "array", "items": decision},
        },
        "required": ["review_id", "decisions"],
    }


def parse_inference(raw, review, validator, annotator_id):
    try:
        obj = json.loads(raw)
    except (ValueError, TypeError):
        raise AnnotationError("INVALID_JSON") from None
    if list(Draft202012Validator(inference_schema()).iter_errors(obj)):
        raise AnnotationError("INFERENCE_SCHEMA_ERROR")
    if obj["review_id"] != review["review_id"]:
        raise AnnotationError("REVIEW_IDENTITY_MISMATCH")
    if Counter(d["aspect_id"] for d in obj["decisions"]) != Counter(ASPECTS):
        raise AnnotationError("INCOMPLETE_ASPECT_DECISIONS")
    records = []
    for d in obj["decisions"]:
        uncertain = d["uncertain"] or d["presence"] == "uncertain"
        record = {
            "annotation_id": digest(
                [review["review_id"], d["aspect_id"], annotator_id]
            ),
            "review_id": review["review_id"],
            "coffee_shop_id": review["coffee_shop_id"],
            "data_origin": review["data_origin"],
            "review_text": review["review_text"],
            "aspect_category": d["aspect_id"],
            "aspect_presence": d["presence"],
            "sentiment": d["sentiment"],
            "mention_type": d["mention_type"],
            "mixed_sentiment": d["mixed_sentiment"],
            "evidence": d["evidence"],
            "annotation_status": "uncertain" if uncertain else "completed",
            "annotator_id": annotator_id,
            "taxonomy_version": validator.version,
            "adjudication_status": "pending" if uncertain else "not_required",
            # AI validity never constitutes human approval for training.
            "training_eligible": False,
            "notes": d["notes"],
            "review_flags": d["review_flags"],
        }
        records.append(record)
    return validator.batch(records, {review["review_id"]: review})
