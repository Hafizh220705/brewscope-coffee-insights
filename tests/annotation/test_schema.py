import copy
import json

import pytest

from brewscope.annotation.validation import AnnotationError, parse_inference


def test_all_synthetic_cases(suite, validator):
    reviews, responses = suite
    assert len(reviews) >= 13
    for review in reviews:
        records = parse_inference(
            json.dumps(responses[review["review_id"]]), review, validator, "ai:mock"
        )
        assert len(records) == 6
        assert all(not r["training_eligible"] for r in records)


@pytest.mark.parametrize(
    "mutation,code",
    [
        ("invalid_json", "INVALID_JSON"),
        ("missing_aspect", "INCOMPLETE_ASPECT_DECISIONS"),
        ("duplicate_aspect", "INCOMPLETE_ASPECT_DECISIONS"),
        ("wrong_aspect", "INFERENCE_SCHEMA_ERROR"),
        ("hallucinated_quote", "EVIDENCE_MISMATCH"),
        ("wrong_identity", "REVIEW_IDENTITY_MISMATCH"),
        ("neutral_absent", "CANONICAL_SCHEMA_ERROR"),
        ("unreported_mixed", "MIXED_EVIDENCE_INCONSISTENT"),
        ("wrong_offset", "INVALID_OFFSET"),
    ],
)
def test_invalid_response_rejected(one, validator, mutation, code):
    review, obj = one
    if mutation == "missing_aspect":
        obj["decisions"].pop()
    if mutation == "duplicate_aspect":
        obj["decisions"][-1] = obj["decisions"][0]
    if mutation == "wrong_aspect":
        obj["decisions"][0]["aspect_id"] = "location_accessibility"
    if mutation == "hallucinated_quote":
        obj["decisions"][0]["evidence"][0]["quote"] = "tidak ada dalam review"
    if mutation == "wrong_identity":
        obj["review_id"] = "wrong"
    if mutation == "neutral_absent":
        obj["decisions"][1]["sentiment"] = "neutral"
    if mutation == "unreported_mixed":
        span = copy.deepcopy(obj["decisions"][0]["evidence"][0])
        span["opinion_sentiment"] = "negative"
        obj["decisions"][0]["evidence"].append(span)
    if mutation == "wrong_offset":
        obj["decisions"][0]["evidence"][0]["end"] = 9999
    raw = "not json" if mutation == "invalid_json" else json.dumps(obj)
    with pytest.raises(AnnotationError, match=code):
        parse_inference(raw, review, validator, "ai:mock")


def test_mixed_not_neutral(suite, validator):
    reviews, responses = suite
    review = next(r for r in reviews if r["review_id"] == "SYN4_MIXED")
    records = parse_inference(
        json.dumps(responses[review["review_id"]]), review, validator, "ai:mock"
    )
    assert records[0]["mixed_sentiment"] and records[0]["sentiment"] is None
    assert len(records[0]["evidence"]) == 2 and not records[0]["training_eligible"]


def test_unicode_offsets_are_python_characters(suite, validator):
    reviews, responses = suite
    review = next(r for r in reviews if r["review_id"] == "SYN4_UNICODE")
    obj = responses[review["review_id"]]
    assert obj["decisions"][0]["evidence"][0]["start"] == 2
    parse_inference(json.dumps(obj), review, validator, "ai:mock")
    obj["decisions"][0]["evidence"][0]["start"] = 4
    with pytest.raises(AnnotationError):
        parse_inference(json.dumps(obj), review, validator, "ai:mock")


def test_canonical_context_and_taxonomy(canonical, one, validator):
    review, _ = one
    canonical[0]["taxonomy_version"] = "made-up"
    with pytest.raises(AnnotationError):
        validator.batch(canonical, {review["review_id"]: review})


def test_neutral_versus_absent(suite, validator):
    reviews, responses = suite
    review = next(r for r in reviews if r["review_id"] == "SYN4_NEUTRAL")
    records = parse_inference(
        json.dumps(responses[review["review_id"]]), review, validator, "ai:mock"
    )
    assert records[4]["sentiment"] == "neutral"
    assert (
        records[0]["sentiment"] is None
        and records[0]["aspect_presence"] == "not_mentioned"
    )
