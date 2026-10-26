import importlib.util
import json

import pytest

from brewscope.annotation.export import (
    merge_gold_and_ai,
    review_ai_output,
    reviewed_ai_rows,
)
from brewscope.annotation.runtime import (
    check_live_gates,
    frozen_prompt,
    geographic_scope,
)
from brewscope.annotation.validation import AnnotationError


def cli(root):
    spec = importlib.util.spec_from_file_location(
        "brewscope_annotation_cli", root / "scripts/run_annotation.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cli_default_dry_run(root, capsys):
    assert cli(root).main([]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "DRY_RUN" and result["requests"] == 0


def test_cli_disallows_six_review_smoke(root, capsys):
    assert cli(root).main(["--mode", "smoke-test", "--limit", "6", "--dry-run"]) == 2
    assert "SMOKE_LIMIT_EXCEEDED" in capsys.readouterr().out


def test_cli_smoke_uses_only_calibration(root, monkeypatch):
    module = cli(root)
    manifest = json.loads(
        (root / "data/interim/human_annotations/pilot_manifest.json").read_text()
    )
    calibration_ids = {
        r["review_id"] for r in manifest["assignments"] if r["split"] == "calibration"
    }
    captured = []

    def stop_at_gate(config, provider, mode, reviews, **kwargs):
        captured.extend(r["review_id"] for r in reviews)
        raise AnnotationError("INTENTIONAL_TEST_STOP")

    monkeypatch.setattr(module, "check_live_gates", stop_at_gate)
    assert module.main(["--mode", "smoke-test", "--execute"]) == 2
    assert len(captured) == 5 and set(captured) <= calibration_ids


def test_live_unknown_quota_cannot_start(config, one):
    from datetime import datetime

    config["project"].update(
        billing_tier="FREE_VERIFIED",
        verified_on=datetime.now().date().isoformat(),
        verification_reference="synthetic test",
    )
    with pytest.raises(AnnotationError, match="QUOTA_UNKNOWN"):
        check_live_gates(config, "gemini", "synthetic", [one[0]], execute=True)


def test_real_cloud_requires_manual_privacy_gate(config, one):
    from datetime import datetime

    config["project"].update(
        billing_tier="FREE_VERIFIED",
        verified_on=datetime.now().date().isoformat(),
        verification_reference="synthetic test",
        rpm=1,
        daily_requests=5,
    )
    review = one[0]
    review["data_origin"] = "authorized_review"
    with pytest.raises(AnnotationError, match="PRIVACY_REVIEW"):
        check_live_gates(config, "gemini", "smoke-test", [review], execute=True)


def test_geographic_decisions_preserve_source_and_allow_regeneration(one, tmp_path):
    review = one[0]
    review["geography_status"] = "UNVERIFIED"
    assert geographic_scope([review])[0]["geography_status"] == "UNVERIFIED"
    with pytest.raises(AnnotationError, match="NOT_RESOLVED"):
        geographic_scope([review], final=True)
    path = tmp_path / "scope.csv"
    path.write_text(
        "coffee_shop_id,status,evidence_reference\nSYN_SHOP,VERIFIED_OUTSIDE,SYNTHETIC_EVIDENCE\n"
    )
    assert geographic_scope([review], path, final=True) == []
    assert review["geography_status"] == "UNVERIFIED"


def test_prompt_integrity_frozen(root, config, tmp_path):
    assert frozen_prompt(root, config).startswith("# absa_gemini_v1")
    from shutil import copyfile

    (tmp_path / "prompts").mkdir()
    copyfile(
        root / "prompts/absa_gemini_v1.manifest.json",
        tmp_path / "prompts/absa_gemini_v1.manifest.json",
    )
    (tmp_path / "prompts/absa_gemini_v1.md").write_text("changed")
    for rel in (
        "configs/aspect_taxonomy.yaml",
        "docs/research/annotation_guidelines.md",
    ):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        copyfile(root / rel, tmp_path / rel)
    with pytest.raises(AnnotationError, match="CREATE_NEW_VERSION"):
        frozen_prompt(tmp_path, config)


def test_reviewed_ai_conversion_and_gold_precedence(
    canonical, one, validator, synthetic_gold
):
    archive = {
        "status": "valid",
        "review_id": one[0]["review_id"],
        "request_key": "SYN",
        "records": canonical,
        "provenance": {"provider": "mock"},
    }
    event = review_ai_output(
        archive,
        canonical,
        reviewer_id="human:D",
        reason="SYNTHETIC_TEST",
        validator=validator,
    )
    assignments = {
        one[0]["review_id"]: {
            "split": "locked_validation",
            "duplicate_group": "group",
            "geography_status": "SYNTHETIC",
        }
    }
    rows = reviewed_ai_rows(event, assignments, validator)
    assert len(rows) == 6
    merged = merge_gold_and_ai(synthetic_gold["rows"], rows)
    assert len(merged) == 6 and all(r["label_source"] == "human_gold" for r in merged)


def test_no_fake_synthetic_quality_gate(config, synthetic_gold, canonical, validator):
    from brewscope.annotation.evaluation import assess_quality, evaluate_predictions

    report = evaluate_predictions(synthetic_gold, canonical, validator)
    config["quality"].update(
        criteria_frozen=True, criteria_reference="test", minimum_locked_reviews=1
    )
    assert not assess_quality(report, config, {})["quality_gate_passed"]


def test_incomplete_metrics_and_failed_outputs(synthetic_gold, validator):
    from brewscope.annotation.evaluation import evaluate_predictions

    rid = synthetic_gold["rows"][0]["record"]["review_id"]
    report = evaluate_predictions(
        synthetic_gold, [], validator, output_statuses={rid: "invalid"}
    )
    assert report["invalid_prediction_review_ids"] == [rid]
    assert report["missing_prediction_reviews"] == 0
    assert report["valid_output_coverage"] == 0


def test_notebook_run_all_is_offline(root, monkeypatch):
    import asyncio
    import sys

    import nbformat
    from nbclient import NotebookClient

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    monkeypatch.setenv("IPYTHONDIR", str(root / ".venv/ipython"))
    monkeypatch.setenv("MPLCONFIGDIR", str(root / ".venv/matplotlib"))
    path = root / "notebooks/03_human_ai_labeling.ipynb"
    notebook = nbformat.read(path, as_version=4)
    assert sum(c.cell_type == "code" for c in notebook.cells) == 20
    NotebookClient(
        notebook,
        timeout=180,
        kernel_name="brewscope",
        resources={"metadata": {"path": str(root / "notebooks")}},
    ).execute()
    assert not any(
        o.output_type == "error"
        for c in notebook.cells
        if c.cell_type == "code"
        for o in c.outputs
    )
    nbformat.write(notebook, path)
    summary = json.loads((root / "reports/stage4_notebook_summary.json").read_text())
    assert summary["cloud_generation_requests_in_notebook"] == 0
    assert summary["mock_successful_reviews"] == 17
    assert summary["resume_additional_requests"] == 0
