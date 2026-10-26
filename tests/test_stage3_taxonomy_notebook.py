"""Validasi metode Tahap 3 melalui fungsi notebook dan contoh sintetis."""

import copy
import hashlib
import json
import re
from pathlib import Path

import pandas as pd
import pytest
import yaml
from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def config():
    return yaml.safe_load((ROOT / "configs/aspect_taxonomy.yaml").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def schema():
    return json.loads((ROOT / "schemas/annotation_schema.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def core():
    n = json.loads((ROOT / "notebooks/02_aspect_taxonomy.ipynb").read_text(encoding="utf-8"))
    cells = [c for c in n["cells"] if "stage3-core" in c["metadata"].get("tags", [])]
    assert len(cells) == 1
    source = cells[0]["source"]
    if isinstance(source, list):
        source = "".join(source)
    namespace = {"pd": pd, "hashlib": hashlib, "re": re,
                 "Draft202012Validator": Draft202012Validator}
    # Eksekusi hanya definisi fungsi milik repository; tanpa I/O korpus.
    exec(compile(source, "notebook:stage3-core", "exec"), namespace)  # noqa: S102
    return namespace


@pytest.fixture
def records(core, config):
    return core["synthetic_examples"](config)


def test_config_and_schema_agree(config, schema):
    active = [a["id"] for a in config["aspects"] if a["active"]]
    assert len(active) == 6
    assert set(active) == set(schema["properties"]["aspect_category"]["enum"])
    assert schema["properties"]["taxonomy_version"]["const"] == config["taxonomy_version"]
    assert config["examples_origin"] == "SYNTHETIC_ONLY"
    assert [a["id"] for a in config["aspects"] if not a["active"]] == ["location_accessibility"]
    Draft202012Validator.check_schema(schema)


def test_synthetic_fixtures_valid(core, schema, records):
    assert core["validate_batch"](records, schema)
    assert all(r["data_origin"] == "synthetic" for r in records)


def test_neutral_different_from_not_mentioned(core, schema, records):
    neutral = next(r for r in records if r["review_id"] == "SYN_FACILITIES_NEUTRAL")
    absent = next(r for r in records if r["review_id"] == "SYN_ABSENT")
    assert neutral["aspect_presence"] == "mentioned" and neutral["sentiment"] == "neutral"
    assert absent["aspect_presence"] == "not_mentioned" and absent["sentiment"] is None
    absent["sentiment"] = "neutral"
    with pytest.raises(ValidationError):
        core["validate_annotation"](absent, schema)


def test_uncertain_is_workflow_not_sentiment(core, schema, records):
    record = next(r for r in records if r["review_id"] == "SYN_UNCERTAIN")
    assert record["annotation_status"] == "uncertain" and record["sentiment"] is None
    record["sentiment"] = "uncertain"
    with pytest.raises(ValidationError):
        core["validate_annotation"](record, schema)


def test_mixed_keeps_two_opinions_and_excluded_pair(core, schema, records):
    record = next(r for r in records if r["review_id"] == "SYN_MIXED")
    assert {o["opinion_sentiment"] for o in record["evidence"]} == {"positive", "negative"}
    assert record["mixed_sentiment"] and record["sentiment"] is None
    assert not record["training_eligible"]
    record["sentiment"] = "neutral"
    with pytest.raises(ValidationError):
        core["validate_annotation"](record, schema)


def test_opposite_opinions_cannot_hide_mixed(core, schema, records):
    record = next(r for r in records if r["review_id"] == "SYN_MIXED")
    record.update(mixed_sentiment=False, sentiment="positive")
    with pytest.raises(ValueError, match="Mixed"):
        core["validate_annotation"](record, schema)


def test_multi_aspect_long_format(core, schema, records):
    long = core["synthetic_long_format"](records, schema)
    multi = long.loc[long["review_id"].eq("SYN_MULTI")]
    assert len(multi) == 3
    assert set(multi["aspect_category"]) == {"product_quality", "ambience", "facilities"}
    assert set(multi["sentiment"]) == {"positive", "negative"}


def test_overlap_fixture_rules(records):
    dirty = next(r for r in records if r["review_id"] == "SYN_DIRTY")
    missing = next(r for r in records if r["review_id"] == "SYN_MISSING_TOILET")
    assert dirty["aspect_category"] == "cleanliness"
    assert missing["aspect_category"] == "facilities"


def test_evidence_offsets_must_match(core, schema, records):
    record = copy.deepcopy(records[0])
    record["evidence"][0]["quote"] = "Bukan quote aslinya"
    with pytest.raises(ValueError, match="Quote"):
        core["validate_annotation"](record, schema)


def test_provisional_aspect_not_active(core, schema, records):
    record = copy.deepcopy(records[0])
    record["aspect_category"] = "location_accessibility"
    with pytest.raises(ValidationError):
        core["validate_annotation"](record, schema)


def test_stage3_rejects_real_annotation_fixture(core, schema, records):
    record = copy.deepcopy(records[0])
    record["data_origin"] = "authorized_review"
    record["review_id"] = "actual-review-id"
    with pytest.raises(ValueError, match="sintetis"):
        core["validate_annotation"](record, schema)


def test_duplicate_pair_rejected(core, schema, records):
    with pytest.raises(ValueError, match="duplikat"):
        core["validate_batch"]([records[0], records[0]], schema)


def test_completed_mixed_cannot_hide_unresolved_opinion(core, schema, records):
    record = next(r for r in records if r["review_id"] == "SYN_MIXED")
    extra = copy.deepcopy(record["evidence"][0])
    extra["opinion_sentiment"] = None
    record["evidence"].append(extra)
    with pytest.raises(ValueError, match="completed"):
        core["validate_annotation"](record, schema)


def test_unicode_offsets_are_characters_not_bytes(core, schema, config):
    record = core["synthetic_record"](
        "SYN_UNICODE", "☕ Kopinya enak.", "product_quality", "positive",
        config["taxonomy_version"], opinion_specs=[("Kopinya enak", "positive", "explicit")],
    )
    assert record["evidence"][0]["start"] == 2
    assert core["validate_annotation"](record, schema)


def test_training_eligible_requires_resolved_three_class_pair(core, schema, records):
    record = next(r for r in records if r["review_id"] == "SYN_MIXED")
    record["training_eligible"] = True
    with pytest.raises(ValidationError):
        core["validate_annotation"](record, schema)


def test_boundaries_and_multi_keyword_only(core):
    result = core["keyword_indicators"](
        pd.Series(["membaca", "AC dan toilet bersih"]),
        {"Facilities": ["ac", "toilet"], "Cleanliness": ["bersih"]},
        {"facilities": "Facilities", "cleanliness": "Cleanliness"},
    )
    assert not result.iloc[0].any()
    assert result.iloc[1].all()


@pytest.fixture
def sampling_data():
    rows = []
    for i in range(60):
        rows.append({
            "review_id": f"SYN_CANDIDATE_{i:03}", "place_key": f"SHOP_{i % 5}",
            "rating": i % 5 + 1, "word_count": i + 1,
            "passes_basic_quality": i != 0, "confirmed_duplicate_extra": False,
            "keyword_cleanliness": i % 7 == 0, "keyword_facilities": i % 3 == 0,
            "keyword_count": i % 4, "has_slang_hint": i % 3 == 1,
            "possible_mixed_language": i % 4 == 0,
            "potential_text_duplicate": i % 8 == 0,
            "is_short_review": i < 3, "shop_review_count": 12,
        })
    return pd.DataFrame(rows)


def test_sampling_reproducible_unique_metadata_only(core, config, sampling_data):
    policy = copy.deepcopy(config["sampling"])
    policy.update(target=30, minimum_per_shop=2)
    a, _ = core["select_pilot"](sampling_data, policy)
    b, _ = core["select_pilot"](sampling_data.sample(frac=1, random_state=1), policy)
    pd.testing.assert_frame_equal(a, b)
    assert len(a) == 30 and a["review_id"].is_unique
    assert a["place_key"].nunique() == 5
    assert "SYN_CANDIDATE_000" not in a["review_id"].values
    assert set(a["candidate_status"]) == {"UNLABELED_NOT_AUTHORIZED"}
    assert not {"review_text", "teks_review", "sentiment", "aspect_presence"}.intersection(a.columns)


def test_sampling_impossible_minimum_errors(core, config, sampling_data):
    policy = copy.deepcopy(config["sampling"])
    policy.update(target=5, minimum_per_shop=3)
    with pytest.raises(ValueError, match="minimum"):
        core["select_pilot"](sampling_data, policy)


def test_sampling_reports_shortfall(core, config, sampling_data):
    policy = copy.deepcopy(config["sampling"])
    policy.update(target=30, minimum_per_shop=2)
    _, quota = core["select_pilot"](sampling_data, policy)
    assert quota["shortfall"].sum() > 0


def test_literature_links_and_decisions(config):
    literature = pd.read_csv(ROOT / "reports/tables/literature_matrix.csv")
    refs = set(literature["source_id"])
    bib = (ROOT / "docs/research/references.bib").read_text(encoding="utf-8")
    assert refs == set(re.findall(r"@\w+\{([^,]+),", bib))
    for aspect in config["aspects"]:
        assert set(aspect["sources"]).issubset(refs)
