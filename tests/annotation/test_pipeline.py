import copy
from datetime import datetime

import pytest

from brewscope.annotation.pipeline import (
    AnnotationPipeline,
    UsageBudget,
    checkpoint_records,
    quality_queue,
)
from brewscope.annotation.providers import MockProvider, ProviderError
from brewscope.annotation.runtime import check_live_gates, privacy_hold, source_reviews
from brewscope.annotation.storage import atomic_json, read_json
from brewscope.annotation.validation import AnnotationError


def make_pipeline(tmp_path, validator, responses, **kwargs):
    provider = MockProvider(responses)
    return AnnotationPipeline(
        provider,
        validator,
        "test prompt",
        {"synthetic": True},
        tmp_path / "run",
        sleep=lambda _: None,
        **kwargs,
    )


def test_dry_run_has_no_side_effects(one, tmp_path, validator):
    review, response = one
    p = make_pipeline(tmp_path, validator, {review["review_id"]: response})
    result = p.run([review])
    assert result["requests"] == 0 and p.provider.calls == 0
    assert not (tmp_path / "run").exists()


def test_checkpoint_resume_avoids_duplicate_requests(one, tmp_path, validator):
    review, response = one
    p = make_pipeline(tmp_path, validator, {review["review_id"]: response})
    assert p.run([review], execute=True)["valid"] == 1
    result = p.run([review], execute=True, resume=True)
    assert result["skipped"] == 1 and result["requests"] == 0 and p.provider.calls == 1
    assert len(checkpoint_records(tmp_path / "run")[0]["records"]) == 6


def test_checkpoint_mismatch(one, tmp_path, validator):
    review, response = one
    p = make_pipeline(tmp_path, validator, {review["review_id"]: response})
    p.run([review], execute=True)
    p.identity = {"new_prompt": True}
    with pytest.raises(AnnotationError, match="CHECKPOINT_FINGERPRINT"):
        p.run([review], execute=True, resume=True)


def test_geographic_metadata_change_does_not_resend_text(one, tmp_path, validator):
    review, response = one
    p = make_pipeline(tmp_path, validator, {review["review_id"]: response})
    p.run([review], execute=True)
    review["geography_status"] = "VERIFIED_INSIDE"
    result = p.run([review], execute=True, resume=True)
    assert result["requests"] == 0 and p.provider.calls == 1


def test_retry_transient_then_success(one, tmp_path, validator):
    review, response = one
    responses = {review["review_id"]: [ProviderError("TEMP", retryable=True), response]}
    p = make_pipeline(tmp_path, validator, responses)
    report = p.run([review], execute=True)
    assert report["requests"] == 2 and report["valid"] == 1


def test_retry_invalid_does_not_fabricate_neutral(one, tmp_path, validator):
    review, _ = one
    p = make_pipeline(
        tmp_path, validator, {review["review_id"]: "garbage"}, max_attempts=2
    )
    report = p.run([review], execute=True)
    assert report["requests"] == 2 and report["invalid"] == 1 and report["valid"] == 0
    assert checkpoint_records(tmp_path / "run", valid_only=False)[0]["records"] == []


def test_quota_stops_without_retry(one, tmp_path, validator):
    review, _ = one
    p = make_pipeline(
        tmp_path,
        validator,
        {review["review_id"]: ProviderError("429", quota_exhausted=True)},
    )
    report = p.run([review], execute=True)
    assert report["status"] == "QUOTA_STOPPED" and p.provider.calls == 1


def test_unknown_delivery_is_not_resent(one, tmp_path, validator):
    review, response = one
    p = make_pipeline(tmp_path, validator, {review["review_id"]: response})
    p.run([review], execute=True)
    path = next((tmp_path / "run/reviews").glob("*.json"))
    state = read_json(path)
    state.update(status="in_flight", records=[])
    atomic_json(path, state)
    report = p.run([review], execute=True, resume=True)
    assert report["interrupted"] == 1 and report["requests"] == 0
    assert report["status"] == "NEEDS_REVIEW" and not report["stage4d_complete"]


def test_mock_cannot_label_real_reviews(one, tmp_path, validator):
    review, response = one
    review["data_origin"] = "authorized_review"
    p = make_pipeline(tmp_path, validator, {review["review_id"]: response})
    with pytest.raises(AnnotationError, match="MOCK_REQUIRES"):
        p.run([review], execute=True)


def test_privacy_holds_and_no_request(one, tmp_path, validator):
    review, response = one
    review["review_text"] += " telepon 081234567890 email saya user@example.org"
    assert privacy_hold(review)
    p = make_pipeline(tmp_path, validator, {review["review_id"]: response})
    report = p.run([review], execute=True)
    assert report["held"] == 1 and report["requests"] == 0


def test_budget_durable_per_project_and_rpm(tmp_path):
    now = [datetime.fromisoformat("2026-10-26T12:00:00+00:00").timestamp()]
    waits = []

    def advance(seconds):
        waits.append(seconds)
        now[0] += seconds

    path = tmp_path / "usage.sqlite3"
    budget = UsageBudget(
        path, "same-project", rpm=1, daily=2, clock=lambda: now[0], sleep=advance
    )
    budget.reserve(10)
    budget.reserve(10)
    assert sum(waits) >= 60
    again = UsageBudget(path, "same-project", rpm=10, daily=2, clock=lambda: now[0])
    with pytest.raises(ProviderError, match="DAILY"):
        again.reserve(10)
    assert again.totals()["request_attempts"] == 2
    # Midnight Pacific, not Jakarta/UTC, resets the RPD window.
    now[0] = datetime.fromisoformat("2026-10-27T07:01:00+00:00").timestamp()
    again.reserve(10)


def test_dataset_hash_and_source_scope(root):
    reviews, manifest = source_reviews(root)
    assert len(reviews) == 3582 and manifest["source_sha256"].startswith("7b87a531")
    assert {r["geography_status"] for r in reviews} == {"UNVERIFIED"}
    assert not any("rating" in r for r in reviews)


def test_changed_source_rejected(root, tmp_path):
    from shutil import copyfile

    (tmp_path / "reports").mkdir()
    (tmp_path / "data/raw").mkdir(parents=True)
    copyfile(
        root / "reports/stage3_taxonomy_summary.json",
        tmp_path / "reports/stage3_taxonomy_summary.json",
    )
    (tmp_path / "data/raw/google_maps_reviews_jatinangor_raw.csv").write_text("changed")
    with pytest.raises(AnnotationError, match="DATASET_HASH"):
        source_reviews(tmp_path)


def test_live_free_tier_gate(config, one):
    review, _ = one
    with pytest.raises(AnnotationError, match="FREE_TIER"):
        check_live_gates(config, "gemini", "synthetic", [review], execute=True)
    config["project"].update(
        billing_tier="FREE_VERIFIED",
        verification_reference="test-only",
        verified_on=datetime.now().date().isoformat(),
        rpm=2,
        daily_requests=10,
    )
    check_live_gates(config, "gemini", "synthetic", [review], execute=True)
    config["project"]["billing_tier"] = "PAID"
    with pytest.raises(AnnotationError, match="FREE_TIER"):
        check_live_gates(config, "gemini", "synthetic", [review], execute=True)


def test_smoke_limit_and_full_gates(config, one):
    review, _ = one
    with pytest.raises(AnnotationError, match="SMOKE_LIMIT"):
        check_live_gates(config, "ollama", "smoke-test", [review] * 6, execute=True)
    with pytest.raises(AnnotationError, match="FULL_EXECUTION"):
        check_live_gates(config, "ollama", "full", [review], execute=True)


def test_random_audit_covers_valid_outputs(canonical):
    archive = {"review_id": "SYN4_MULTI", "status": "valid", "records": canonical}
    queue = quality_queue([archive], random_fraction=1)
    assert queue[0]["random_audit"] and "random_audit" in queue[0]["reasons"]


def test_stable_ordering(one, tmp_path, validator):
    review, response = one
    other = copy.deepcopy(review)
    other["review_id"] = "SYN_FIRST"
    other_response = copy.deepcopy(response)
    other_response["review_id"] = other["review_id"]
    p = make_pipeline(
        tmp_path,
        validator,
        {review["review_id"]: response, other["review_id"]: other_response},
    )
    assert p.run([review, other], execute=True, batch_size=2)["valid"] == 2


def test_rate_budget_does_not_count_dryrun(one, tmp_path, validator):
    review, response = one
    budget = UsageBudget(tmp_path / "budget.sqlite3", "project", 10, 10)
    p = make_pipeline(
        tmp_path, validator, {review["review_id"]: response}, budget=budget
    )
    p.run([review])
    assert budget.totals()["request_attempts"] == 0


def test_live_adapter_cannot_bypass_runtime_gates(one, tmp_path, validator):
    review, response = one
    p = make_pipeline(tmp_path, validator, {review["review_id"]: response})
    p.provider.name = "ollama"
    with pytest.raises(AnnotationError, match="LIVE_RUNTIME_GATES"):
        p.run([review], execute=True)
