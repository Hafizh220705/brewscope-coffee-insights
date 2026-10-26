import copy

import pandas as pd
import pytest

from brewscope.annotation.evaluation import classification_metrics, evaluate_predictions
from brewscope.annotation.export import (
    assert_no_leakage,
    export_tables,
    review_ai_output,
)
from brewscope.annotation.validation import AnnotationError


def test_no_gold_no_metrics(validator):
    assert evaluate_predictions(None, [], validator)["status"] == "NOT_COMPUTED"


def test_perfect_synthetic_predictions(synthetic_gold, canonical, validator):
    result = evaluate_predictions(synthetic_gold, canonical, validator)
    assert result["aspect_detection"]["micro"]["f1"] == 1
    assert result["conditional_sentiment"]["accuracy"] == 1
    assert result["end_to_end"]["micro"]["f1"] == 1
    assert result["origin"] == ["synthetic"]


def test_missing_predictions_penalized(synthetic_gold, validator):
    result = evaluate_predictions(synthetic_gold, [], validator)
    assert result["aspect_detection"]["micro"]["fn"] == 2
    assert result["conditional_sentiment"]["accuracy"] == 0
    assert result["end_to_end"]["micro"]["f1"] == 0
    assert result["missing_prediction_reviews"] == 1


def test_hallucinated_aspect_penalized(synthetic_gold, canonical, validator):
    record = canonical[1]
    record.update(
        aspect_presence="mentioned",
        sentiment="positive",
        mention_type="explicit",
        evidence=copy.deepcopy(canonical[0]["evidence"]),
    )
    result = evaluate_predictions(synthetic_gold, canonical, validator)
    assert result["aspect_detection"]["micro"]["fp"] == 1
    assert result["end_to_end"]["micro"]["fp"] == 1


def test_invalid_output_not_success(synthetic_gold, canonical, validator):
    canonical[0]["evidence"][0]["quote"] = "hallucinated quote"
    result = evaluate_predictions(synthetic_gold, canonical, validator)
    assert result["valid_prediction_reviews"] == 0
    assert len(result["invalid_prediction_review_ids"]) == 1
    assert result["aspect_detection"]["micro"]["fn"] == 2


def test_hallucinated_mixed_aspect_also_penalized(synthetic_gold, canonical, validator):
    record = canonical[1]
    evidence = copy.deepcopy(canonical[0]["evidence"])
    negative = copy.deepcopy(evidence[0])
    negative["opinion_sentiment"] = "negative"
    record.update(
        aspect_presence="mentioned",
        sentiment=None,
        mention_type="explicit",
        mixed_sentiment=True,
        evidence=[*evidence, negative],
    )
    result = evaluate_predictions(synthetic_gold, canonical, validator)
    assert result["aspect_detection"]["micro"]["fp"] == 1
    assert result["end_to_end"]["micro"]["fp"] == 1


def test_mixed_pair_survives_export(suite, validator, tmp_path):
    import json

    from brewscope.annotation.validation import parse_inference

    reviews, responses = suite
    review = next(r for r in reviews if r["review_id"] == "SYN4_MIXED")
    records = parse_inference(
        json.dumps(responses[review["review_id"]]), review, validator, "ai:mock"
    )
    rows = [
        {
            "record": r,
            "split": "development",
            "duplicate_group": "synthetic",
            "geography_status": "SYNTHETIC",
            "label_source": "human_reviewed_ai",
            "provenance": {"fixture": "SYNTHETIC_ONLY"},
        }
        for r in records
    ]
    result = export_tables(rows, validator, tmp_path, allow_synthetic=True)
    table = pd.read_csv(result["directory"] + "/aspect_sentiment_dataset.csv")
    assert len(table) == 1 and pd.isna(table.sentiment.iloc[0])
    assert table.confidence_or_review_flag.iloc[0] == "mixed"
    assert not table.training_eligible.iloc[0]


def test_classification_expected_macro():
    result = classification_metrics(
        ["positive", "negative", "neutral"], ["positive", None, "neutral"]
    )
    assert result["accuracy"] == pytest.approx(2 / 3)
    assert result["macro_f1"] == pytest.approx(2 / 3)
    assert result["confusion_matrix"]["negative"]["ABSTAIN_OR_MISSED"] == 1
    assert classification_metrics([], [])["macro_f1"] is None


def test_export_integrity_and_no_synthetic_research_export(
    synthetic_gold, validator, tmp_path
):
    rows = synthetic_gold["rows"]
    with pytest.raises(AnnotationError, match="SYNTHETIC_EXPORT"):
        export_tables(rows, validator, tmp_path)
    result = export_tables(rows, validator, tmp_path, allow_synthetic=True)
    from pathlib import Path

    directory = Path(result["directory"])
    frame = pd.read_csv(directory / "aspect_presence_dataset.csv")
    assert len(frame) == 1 and frame.product_quality.iloc[0] == 1
    assert frame.service.iloc[0] == 0
    assert result["sentiment_rows"] == 2 and result["archive_pairs"] == 6


def test_uncertain_not_zero_and_mixed_retained(synthetic_gold, validator, tmp_path):
    rows = copy.deepcopy(synthetic_gold["rows"])
    rows[0]["record"].update(
        aspect_presence="uncertain",
        sentiment=None,
        annotation_status="uncertain",
        adjudication_status="pending",
        training_eligible=False,
        notes="SYNTHETIC UNCERTAINTY",
    )
    result = export_tables(rows, validator, tmp_path, allow_synthetic=True)
    frame = pd.read_csv(result["directory"] + "/aspect_presence_dataset.csv")
    assert pd.isna(frame.product_quality.iloc[0])
    sentiments = pd.read_csv(result["directory"] + "/aspect_sentiment_dataset.csv")
    assert not sentiments[
        sentiments.aspect_id == "product_quality"
    ].training_eligible.iloc[0]


def test_same_review_cannot_cross_splits(synthetic_gold):
    rows = copy.deepcopy(synthetic_gold["rows"])
    rows[0]["split"] = "development"
    with pytest.raises(AnnotationError, match="SPLIT_LEAKAGE"):
        assert_no_leakage(rows)


def test_exact_text_with_different_ids_cannot_cross_splits(synthetic_gold):
    rows = copy.deepcopy(synthetic_gold["rows"])
    other = copy.deepcopy(rows)
    for row in other:
        row["record"]["review_id"] = "SYN_OTHER"
        row["split"] = "development"
        row["duplicate_group"] = "intentionally_different_group"
    with pytest.raises(AnnotationError, match="SPLIT_LEAKAGE"):
        assert_no_leakage(rows + other)


def test_human_correction_preserves_original(canonical, validator):
    original = copy.deepcopy(canonical)
    archive = {
        "status": "valid",
        "records": canonical,
        "request_key": "synthetic-key",
        "provenance": {"provider": "mock"},
    }
    corrected = copy.deepcopy(canonical)
    corrected[0]["notes"] = "Human review; synthetic fixture"
    event = review_ai_output(
        archive, corrected, reviewer_id="human:D", reason="test", validator=validator
    )
    assert canonical == original
    assert (
        event["corrected_records"][0]["notes"] != event["original_records"][0]["notes"]
    )


def test_unreviewed_ai_cannot_be_exported(synthetic_gold, validator, tmp_path):
    rows = copy.deepcopy(synthetic_gold["rows"])
    rows[0]["label_source"] = "ai_prediction"
    with pytest.raises(AnnotationError, match="UNREVIEWED_AI"):
        export_tables(rows, validator, tmp_path, allow_synthetic=True)
