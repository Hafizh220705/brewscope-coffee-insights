#!/usr/bin/env python3
"""Validate BrewScope canonical annotation records stored as JSON Lines."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import jsonschema

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT_PATH = (
    PROJECT_ROOT / "data" / "processed" / "labeling" / "annotations_full.jsonl"
)
DEFAULT_SCHEMA_PATH = PROJECT_ROOT / "configs" / "labeling" / "annotation_schema.json"

EXPECTED_ASPECTS = frozenset(
    {
        "product_quality",
        "service",
        "price_value",
        "ambience",
        "facilities",
        "cleanliness",
    }
)


@dataclass(frozen=True)
class ValidationResult:
    """Summary returned by the annotation validator."""

    total_records: int
    reviews: int
    errors: int
    first_errors: list[str]

    @property
    def is_valid(self) -> bool:
        return self.errors == 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_schema(schema_path: Path) -> dict[str, Any]:
    """Load and verify the JSON Schema used for canonical annotations."""

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Schema tidak ditemukan: {schema_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Schema bukan JSON valid: {schema_path}: {exc}") from exc

    jsonschema.Draft202012Validator.check_schema(schema)
    return schema


def _schema_errors(
    record: dict[str, Any],
    validator: jsonschema.Draft202012Validator,
) -> Iterable[str]:
    for error in sorted(
        validator.iter_errors(record), key=lambda item: list(item.path)
    ):
        location = ".".join(str(part) for part in error.path) or "record"
        yield f"schema {location}: {error.message}"


def _has_valid_evidence_offset(record: dict[str, Any], evidence: Any) -> bool:
    if not isinstance(evidence, dict):
        return False

    text = record.get("review_text")
    start = evidence.get("start")
    end = evidence.get("end")
    quote = evidence.get("quote")

    return (
        isinstance(text, str)
        and isinstance(start, int)
        and not isinstance(start, bool)
        and isinstance(end, int)
        and not isinstance(end, bool)
        and isinstance(quote, str)
        and 0 <= start < end <= len(text)
        and text[start:end] == quote
    )


def validate_annotations(
    input_path: Path,
    schema_path: Path,
    *,
    error_preview_limit: int = 15,
) -> ValidationResult:
    """Validate schema, identifiers, review-aspect uniqueness, and offsets."""

    schema = load_schema(schema_path)
    validator = jsonschema.Draft202012Validator(schema)
    annotation_ids: set[Any] = set()
    review_aspects: defaultdict[Any, set[Any]] = defaultdict(set)
    errors: list[str] = []
    total_records = 0

    try:
        input_file = input_path.open(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"File anotasi tidak ditemukan: {input_path}") from exc

    with input_file:
        for line_number, raw_line in enumerate(input_file, start=1):
            if not raw_line.strip():
                continue

            total_records += 1
            prefix = f"line {line_number}"

            try:
                record = json.loads(raw_line)
            except json.JSONDecodeError as exc:
                errors.append(f"{prefix}: invalid JSON: {exc.msg}")
                continue

            if not isinstance(record, dict):
                errors.append(f"{prefix}: record must be a JSON object")
                continue

            errors.extend(
                f"{prefix}: {message}" for message in _schema_errors(record, validator)
            )

            annotation_id = record.get("annotation_id")
            if annotation_id in annotation_ids:
                errors.append(f"{prefix}: duplicate annotation_id: {annotation_id!r}")
            annotation_ids.add(annotation_id)

            review_id = record.get("review_id")
            aspect = record.get("aspect_category")
            if aspect in review_aspects[review_id]:
                errors.append(
                    f"{prefix}: duplicate review/aspect: {review_id!r}/{aspect!r}"
                )
            review_aspects[review_id].add(aspect)

            evidence_items = record.get("evidence", [])
            if isinstance(evidence_items, list):
                for evidence_index, evidence in enumerate(evidence_items):
                    if not _has_valid_evidence_offset(record, evidence):
                        errors.append(
                            f"{prefix}: incorrect evidence offset at index "
                            f"{evidence_index}"
                        )

    for review_id, aspects in review_aspects.items():
        if aspects != EXPECTED_ASPECTS:
            missing = sorted(EXPECTED_ASPECTS - aspects)
            unexpected = sorted(aspects - EXPECTED_ASPECTS, key=str)
            errors.append(
                f"review {review_id!r}: incorrect aspect set; "
                f"missing={missing}, unexpected={unexpected}"
            )

    return ValidationResult(
        total_records=total_records,
        reviews=len(review_aspects),
        errors=len(errors),
        first_errors=errors[:error_preview_limit],
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validasi file anotasi kanonis BrewScope."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_PATH,
        help=f"JSONL anotasi (default: {DEFAULT_INPUT_PATH})",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA_PATH,
        help=f"JSON Schema anotasi (default: {DEFAULT_SCHEMA_PATH})",
    )
    parser.add_argument(
        "--max-errors",
        type=int,
        default=15,
        help="Jumlah maksimum detail error yang ditampilkan (default: 15).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.max_errors < 0:
        raise ValueError("--max-errors tidak boleh negatif.")

    result = validate_annotations(
        args.input,
        args.schema,
        error_preview_limit=args.max_errors,
    )
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0 if result.is_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
