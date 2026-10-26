import copy

import pandas as pd
import pytest

from brewscope.annotation.agreement import agreement_scores, inter_annotator_agreement
from brewscope.annotation.human import (
    assignment_templates,
    duplicate_groups,
    gold_standard,
    load_gold,
    pilot_design,
    save_gold,
    submit_annotations,
)
from brewscope.annotation.runtime import source_reviews
from brewscope.annotation.storage import digest
from brewscope.annotation.validation import AnnotationError


def test_blind_templates_have_no_labels_or_hints(one, validator):
    review, _ = one
    manifest = [{"review_id": review["review_id"]}]
    templates = assignment_templates([review], manifest, "human:A", validator.version)
    assert len(templates) == 6
    assert all(
        r["aspect_presence"] is None and r["annotation_status"] == "draft"
        for r in templates
    )
    assert all(
        not any("keyword" in key or "rating" in key or "split" in key for key in r)
        for r in templates
    )


def test_original_250_split_is_reproducible(root):
    reviews, _ = source_reviews(root)
    candidates = pd.read_csv(
        root / "data/interim/annotation_pilot_candidates.csv"
    ).review_id.tolist()
    manifest, grouping = pilot_design(reviews, candidates)
    other, _ = pilot_design(list(reversed(reviews)), list(reversed(candidates)))
    assert manifest == other and len(manifest) == 250
    splits = pd.DataFrame(manifest)
    assert splits.groupby("duplicate_group").split.nunique().max() == 1
    assert splits.split.value_counts().to_dict() == {
        "development": 150,
        "calibration": 50,
        "locked_validation": 50,
    }
    assert len(grouping) == 3582


def test_near_duplicates_grouped():
    texts = [
        "kopinya enak suasananya nyaman sekali buat belajar dan mengerjakan tugas kampus",
        "kopinya enak suasananya nyaman sekali buat belajar dan mengerjakan tugas kampus!",
        "KOPINYA ENAK",
    ]
    reviews = [
        {"review_id": str(i), "review_text": text} for i, text in enumerate(texts)
    ]
    grouping = duplicate_groups(reviews)
    assert grouping["0"] == grouping["1"] and grouping["0"] != grouping["2"]


def test_submission_cannot_overwrite_human(canonical, one, validator, tmp_path):
    review, _ = one
    path = tmp_path / "human.json"
    sources = {review["review_id"]: review}
    submit_annotations(path, canonical, sources, validator, actor="human:A")
    canonical[0]["notes"] = "altered"
    with pytest.raises(ValueError, match="IMMUTABLE"):
        submit_annotations(path, canonical, sources, validator, actor="human:A")


def test_blank_forms_cannot_be_submitted(one, validator, tmp_path):
    review, _ = one
    records = assignment_templates(
        [review], [{"review_id": review["review_id"]}], "human:A", validator.version
    )
    with pytest.raises(AnnotationError):
        submit_annotations(
            tmp_path / "fake.json",
            records,
            {review["review_id"]: review},
            validator,
            actor="human:A",
        )


def test_known_kappa_formula():
    # Raw=.75, expected=.5 => kappa=.5.
    result = agreement_scores(
        ["yes", "yes", "no", "no"], ["yes", "yes", "yes", "no"], ["yes", "no"]
    )
    assert result["raw_agreement"] == 0.75 and result["cohen_kappa"] == 0.5
    assert agreement_scores(["yes"], ["yes"], ["yes", "no"])["cohen_kappa"] is None
    assert (
        agreement_scores([], [], ["yes", "no"])["undefined_reason"]
        == "NO_COMPARABLE_DECISIONS"
    )


def test_no_fake_human_agreement(validator):
    assert inter_annotator_agreement(None, None, validator)["status"] == "NOT_COMPUTED"


def test_agreement_before_adjudication(submissions, validator):
    a, b = submissions
    result = inter_annotator_agreement(a, b, validator)
    assert result["presence"]["comparable_decisions"] == 6
    assert result["sentiment"]["comparable_decisions"] == 2
    assert result["presence"]["raw_agreement"] == 1
    b["records"][0].update(
        annotation_status="uncertain",
        sentiment=None,
        adjudication_status="pending",
        notes="synthetic uncertainty",
    )
    result = inter_annotator_agreement(a, b, validator)
    assert result["sentiment"]["comparable_decisions"] == 1
    assert result["presence"]["comparable_decisions"] == 6


def test_gold_needs_two_humans_and_qc(submissions, one, validator):
    a, b = submissions
    with pytest.raises(AnnotationError, match="TWO_DISTINCT"):
        gold_standard(a, a, [], {}, [], validator)
    manifest = [
        {
            "review_id": one[0]["review_id"],
            "split": "development",
            "duplicate_group": "group",
        }
    ]
    with pytest.raises(AnnotationError, match="HUMAN_QC"):
        gold_standard(a, b, [], {}, manifest, validator)


def test_ai_cannot_be_human_gold(submissions, validator):
    a, b = submissions
    a["kind"] = "ai_prediction"
    with pytest.raises(AnnotationError, match="HUMAN_ORIGINAL"):
        gold_standard(a, b, [], {}, [], validator)


def test_gold_roundtrip_and_hash(synthetic_gold, tmp_path):
    path = tmp_path / "human_gold_annotations.jsonl"
    save_gold(path, synthetic_gold)
    assert load_gold(path) == synthetic_gold
    changed = copy.deepcopy(synthetic_gold)
    changed["rows"][0]["record"]["notes"] = "different"
    with pytest.raises(ValueError):
        save_gold(path, changed)


def test_disagreement_requires_adjudication(submissions, one, validator):
    a, b = submissions
    b["records"][0]["sentiment"] = "negative"
    b["records"][0]["evidence"][0]["opinion_sentiment"] = "negative"
    b["content_sha256"] = digest(b["records"])
    manifest = [
        {
            "review_id": one[0]["review_id"],
            "split": "development",
            "duplicate_group": "group",
        }
    ]
    with pytest.raises(AnnotationError, match="ADJUDICATION_REQUIRED"):
        gold_standard(a, b, [], {}, manifest, validator)
