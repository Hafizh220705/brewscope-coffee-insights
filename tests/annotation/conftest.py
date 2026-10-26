import copy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from brewscope.annotation.human import gold_standard, submit_annotations
from brewscope.annotation.runtime import load_runtime, synthetic_suite
from brewscope.annotation.storage import digest
from brewscope.annotation.validation import AnnotationValidator, parse_inference


@pytest.fixture
def root():
    return ROOT


@pytest.fixture
def validator():
    return AnnotationValidator(ROOT / "schemas/annotation_schema.json")


@pytest.fixture
def suite():
    return synthetic_suite(ROOT)


@pytest.fixture
def config():
    return copy.deepcopy(load_runtime(ROOT))


@pytest.fixture
def one(suite):
    reviews, responses = suite
    review = next(r for r in reviews if r["review_id"] == "SYN4_MULTI")
    return copy.deepcopy(review), copy.deepcopy(responses[review["review_id"]])


@pytest.fixture
def canonical(one, validator):
    import json

    review, response = one
    return parse_inference(json.dumps(response), review, validator, "human:A")


@pytest.fixture
def submissions(canonical, one, validator, tmp_path):
    review, _ = one
    sources = {review["review_id"]: review}
    a = submit_annotations(
        tmp_path / "a.json", canonical, sources, validator, actor="human:A"
    )
    records_b = copy.deepcopy(canonical)
    for r in records_b:
        r["annotator_id"] = "human:B"
        r["annotation_id"] = digest([r["annotation_id"], "B"])
    b = submit_annotations(
        tmp_path / "b.json", records_b, sources, validator, actor="human:B"
    )
    return a, b


@pytest.fixture
def synthetic_gold(submissions, one, validator):
    review, _ = one
    a, b = submissions
    manifest = [
        {
            "review_id": review["review_id"],
            "split": "locked_validation",
            "duplicate_group": "synthetic_group",
            "geography_status": "SYNTHETIC",
        }
    ]
    audit = {
        r["review_id"] + "|" + r["aspect_category"]: {
            "status": "APPROVED",
            "reviewer_id": "human:D",
            "notes": "SYNTHETIC TEST ONLY",
        }
        for r in a["records"]
    }
    return gold_standard(a, b, [], audit, manifest, validator)
