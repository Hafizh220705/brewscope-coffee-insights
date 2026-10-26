"""Stage 4 CLI. Default: dry run, synthetic input, no network and no label writes."""

import argparse
import csv
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from brewscope.annotation.agreement import inter_annotator_agreement
from brewscope.annotation.evaluation import assess_quality, evaluate_predictions
from brewscope.annotation.export import (
    export_tables,
    regenerate_geographic_scope,
    review_ai_output,
)
from brewscope.annotation.human import (
    gold_standard,
    load_gold,
    prepare_pilot,
    save_gold,
    submit_annotations,
)
from brewscope.annotation.pipeline import (
    AnnotationPipeline,
    UsageBudget,
    checkpoint_records,
    quality_queue,
)
from brewscope.annotation.providers import (
    GeminiProvider,
    MockProvider,
    OllamaProvider,
    ProviderError,
    api_key,
)
from brewscope.annotation.runtime import (
    check_live_gates,
    evaluation_protocol,
    experiment_identity,
    frozen_prompt,
    geographic_scope,
    load_runtime,
    register_prompt,
    source_reviews,
    synthetic_suite,
)
from brewscope.annotation.storage import (
    atomic_json,
    digest,
    immutable_json,
    read_json,
    read_jsonl,
)
from brewscope.annotation.validation import AnnotationError, AnnotationValidator


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--task",
        choices=[
            "annotate",
            "prepare-human",
            "submit-human",
            "agreement",
            "build-gold",
            "evaluate",
            "export",
            "check-provider",
            "freeze-protocol",
            "freeze-prompt",
            "review-ai",
        ],
        default="annotate",
    )
    p.add_argument("--provider", choices=["gemini", "ollama", "mock"], default=None)
    p.add_argument(
        "--mode",
        choices=["synthetic", "smoke-test", "pilot", "full"],
        default="synthetic",
    )
    p.add_argument("--limit", type=int, default=None)
    execution = p.add_mutually_exclusive_group()
    execution.add_argument("--dry-run", action="store_true")
    execution.add_argument("--execute", action="store_true")
    p.add_argument("--resume", action="store_true")
    p.add_argument("--config", type=Path)
    p.add_argument("--checkpoint", type=Path)
    p.add_argument("--input", type=Path)
    p.add_argument("--output", type=Path)
    p.add_argument("--human-a", type=Path)
    p.add_argument("--human-b", type=Path)
    p.add_argument("--annotator")
    p.add_argument(
        "--phase", choices=["calibration", "independent"], default="independent"
    )
    p.add_argument("--adjudications", type=Path)
    p.add_argument("--quality-review", type=Path)
    p.add_argument("--gold", type=Path)
    p.add_argument("--geography-decisions", type=Path)
    p.add_argument(
        "--split", choices=["development", "locked_validation"], default="development"
    )
    return p


def require(args, *fields):
    if any(getattr(args, name) is None for name in fields):
        raise AnnotationError("MISSING_ARGUMENTS:" + ",".join(fields))


def make_provider(name, config):
    if name == "gemini":
        return GeminiProvider(ROOT, config["model"], config["execution"])
    if name == "ollama":
        return OllamaProvider(
            config["ollama"]["model"],
            config["ollama"]["base_url"],
            config["execution"]["timeout_seconds"],
            config["execution"],
        )
    return MockProvider(synthetic_suite(ROOT)[1])


def workflow(args):
    config = load_runtime(ROOT, args.config)
    name = args.provider or config["provider"]
    validator = AnnotationValidator(ROOT / "schemas/annotation_schema.json")
    execute = args.execute and not args.dry_run
    if args.task == "freeze-prompt":
        if not execute:
            return {"status": "DRY_RUN", "task": args.task}
        return register_prompt(ROOT, config)
    if args.task == "freeze-protocol":
        if not execute:
            return {"status": "DRY_RUN", "task": args.task}
        return evaluation_protocol(ROOT, config, freeze=True)
    if args.limit is not None and args.limit < 1:
        raise AnnotationError("LIMIT_MUST_BE_POSITIVE")
    if args.task == "check-provider":
        if name == "gemini" and not api_key(ROOT):
            return {
                "status": "NOT_CHECKED",
                "reason": "GEMINI_API_KEY_MISSING",
                "requests": 0,
            }
        if not execute:
            return {"status": "DRY_RUN", "provider": name, "requests": 0}
        provider = make_provider(name, config)
        try:
            return provider.available()
        finally:
            if hasattr(provider, "close"):
                provider.close()
    if args.task == "prepare-human":
        if not execute:
            return {"status": "DRY_RUN", "task": args.task, "reviews": 250}
        return prepare_pilot(ROOT, validator)
    if args.task == "review-ai":
        require(args, "input", "output", "checkpoint", "annotator")
        if not execute:
            return {"status": "DRY_RUN", "task": args.task}
        form = read_json(args.input)
        archive = read_json(args.checkpoint)
        event = review_ai_output(
            archive,
            form["corrected_records"],
            reviewer_id=args.annotator,
            reason=form["reason"],
            validator=validator,
        )
        immutable_json(args.output, event)
        return {"status": "HUMAN_REVIEW_SAVED", "review_id": archive["review_id"]}
    if args.task in ("submit-human", "agreement", "build-gold", "evaluate", "export"):
        if not execute:
            return {"status": "DRY_RUN", "task": args.task, "requests": 0}
        if args.task == "submit-human":
            require(args, "input", "output", "annotator")
            sources, _ = source_reviews(ROOT)
            manifest = read_json(
                ROOT / "data/interim/human_annotations/pilot_manifest.json"
            )
            assigned = {
                m["review_id"]
                for m in manifest["assignments"]
                if (m["split"] == "calibration") == (args.phase == "calibration")
            }
            reviews = {r["review_id"]: r for r in sources if r["review_id"] in assigned}
            result = submit_annotations(
                args.output,
                read_jsonl(args.input),
                reviews,
                validator,
                actor=args.annotator,
                independent=args.phase == "independent",
            )
            return {
                "status": "HUMAN_SUBMISSION_VALIDATED",
                "decisions": len(result["records"]),
            }
        if args.task == "agreement":
            require(args, "human_a", "human_b", "output")
            result = inter_annotator_agreement(
                read_json(args.human_a), read_json(args.human_b), validator
            )
            atomic_json(args.output, result)
            return result
        if args.task == "build-gold":
            require(
                args, "human_a", "human_b", "adjudications", "quality_review", "output"
            )
            manifest = read_json(
                ROOT / "data/interim/human_annotations/pilot_manifest.json"
            )["assignments"]
            result = gold_standard(
                read_json(args.human_a),
                read_json(args.human_b),
                read_json(args.adjudications),
                read_json(args.quality_review),
                manifest,
                validator,
            )
            expected = {m["review_id"] for m in manifest if m["split"] != "calibration"}
            if {r["record"]["review_id"] for r in result["rows"]} != expected:
                raise AnnotationError("INDEPENDENT_GOLD_UNIVERSE_MISMATCH")
            save_gold(args.output, result)
            return {"status": "HUMAN_GOLD_SAVED", "pairs": len(result["rows"])}
        require(args, "gold", "output")
        gold = load_gold(args.gold)
        if args.task == "export":
            rows = gold["rows"]
            if args.geography_decisions:
                rows = regenerate_geographic_scope(
                    rows, args.geography_decisions, final=True
                )
            return export_tables(
                rows,
                validator,
                args.output,
                source_terms_reviewed=config["full"]["source_terms_reviewed"],
            )
        require(args, "checkpoint")
        if (
            args.split == "locked_validation"
            and not config["quality"]["criteria_frozen"]
        ):
            raise AnnotationError("FREEZE_QUALITY_CRITERIA_BEFORE_LOCKED_EVALUATION")
        if args.split == "locked_validation":
            evaluation_protocol(ROOT, config)
        archives = checkpoint_records(args.checkpoint, valid_only=False)
        ids = {
            r["record"]["review_id"] for r in gold["rows"] if r["split"] == args.split
        }
        predictions = [
            r for a in archives for r in a["records"] if r["review_id"] in ids
        ]
        experiment = read_json(args.checkpoint / "manifest.json")
        result = evaluate_predictions(
            gold,
            predictions,
            validator,
            split=args.split,
            experiment=experiment,
            output_statuses={
                a["review_id"]: a["status"] for a in archives if a["review_id"] in ids
            },
        )
        result.update(assess_quality(result, config, experiment))
        result["result_sha256"] = digest(
            {k: v for k, v in result.items() if k != "result_sha256"}
        )
        atomic_json(args.output, result)
        return {
            "status": result["status"],
            "quality_gate_passed": result["quality_gate_passed"],
        }

    prompt = frozen_prompt(ROOT, config)
    if args.mode == "synthetic":
        reviews, _ = synthetic_suite(ROOT)
        dataset_hash = digest(reviews)
    else:
        reviews, manifest = source_reviews(ROOT)
        reviews = geographic_scope(
            reviews, args.geography_decisions, final=args.mode == "full" and execute
        )
        dataset_hash = manifest["source_sha256"]
        if args.mode == "smoke-test":
            assignments = read_json(
                ROOT / "data/interim/human_annotations/pilot_manifest.json"
            )["assignments"]
            selected = {
                r["review_id"] for r in assignments if r["split"] == "calibration"
            }
            reviews = [r for r in reviews if r["review_id"] in selected]
        if args.mode == "pilot":
            assignments = read_json(
                ROOT / "data/interim/human_annotations/pilot_manifest.json"
            )["assignments"]
            selected = {r["review_id"] for r in assignments if r["split"] == args.split}
            if (
                args.split == "locked_validation"
                and not config["quality"]["criteria_frozen"]
            ):
                raise AnnotationError("FREEZE_QUALITY_CRITERIA_BEFORE_LOCKED_INFERENCE")
            if args.split == "locked_validation":
                evaluation_protocol(ROOT, config)
            reviews = [r for r in reviews if r["review_id"] in selected]
    limit = (
        args.limit
        if args.limit is not None
        else (5 if args.mode == "smoke-test" else len(reviews))
    )
    if args.mode == "smoke-test" and limit > 5:
        raise AnnotationError("SMOKE_LIMIT_EXCEEDED")
    reviews = sorted(reviews, key=lambda r: r["review_id"])[:limit]
    if not execute:
        return {
            "status": "DRY_RUN",
            "provider": name,
            "mode": args.mode,
            "planned_reviews": len(reviews),
            "requests": 0,
            "label_files_written": 0,
        }
    if name == "mock" and args.mode != "synthetic":
        raise AnnotationError("MOCK_CANNOT_LABEL_REAL_REVIEWS")
    evaluation = None
    if args.mode == "full":
        require(args, "gold")
        path = ROOT / config["full"]["pilot_evaluation_path"]
        evaluation = read_json(path) if path.exists() else None
        gold = load_gold(args.gold)
        if not evaluation or evaluation.get("gold_sha256") != gold["sha256"]:
            raise AnnotationError("FULL_REQUIRES_MATCHING_HUMAN_GOLD")
        if evaluation.get("result_sha256") != digest(
            {k: v for k, v in evaluation.items() if k != "result_sha256"}
        ):
            raise AnnotationError("EVALUATION_HASH_MISMATCH")
    if name != "mock":
        check_live_gates(
            config, name, args.mode, reviews, execute=True, evaluation=evaluation
        )
    provider = make_provider(name, config)
    identity = experiment_identity(ROOT, config, provider, prompt, dataset_hash)
    directory = args.checkpoint or (
        ROOT / "data/interim/ai_annotation_checkpoints" / digest(identity)[:16]
    )
    try:
        if name != "mock":
            availability = provider.available()
            if not availability["accessible"]:
                raise AnnotationError("MODEL_UNAVAILABLE")
        if (
            args.mode == "full"
            and not assess_quality(evaluation, config, identity)["quality_gate_passed"]
        ):
            raise AnnotationError("EVALUATION_DOES_NOT_MATCH_CURRENT_EXPERIMENT")
        budget = None
        if name == "gemini":
            project = config["project"]
            budget = UsageBudget(
                ROOT / "data/interim/ai_annotation_checkpoints/usage.sqlite3",
                project["quota_scope"],
                project["rpm"],
                project["daily_requests"],
                tpm=project["input_tokens_per_minute"],
            )
        pipeline = AnnotationPipeline(
            provider,
            validator,
            prompt,
            identity,
            directory,
            budget=budget,
            max_attempts=config["execution"]["max_attempts"],
            backoff_seconds=config["execution"]["backoff_seconds"],
            max_input_characters=config["execution"]["max_input_characters"],
            runtime_config=config,
            mode=args.mode,
            pilot_evaluation=evaluation,
        )
        result = pipeline.run(
            reviews,
            execute=True,
            resume=args.resume,
            batch_size=config["execution"]["batch_size"],
        )
        queue = quality_queue(
            checkpoint_records(directory, valid_only=False),
            candidate_metadata={
                r["review_id"]: r
                for r in csv.DictReader(
                    (ROOT / "data/interim/annotation_pilot_candidates.csv")
                    .read_text(encoding="utf-8")
                    .splitlines()
                )
            },
            random_fraction=config["quality"]["random_audit_fraction"],
        )
        atomic_json(directory / "human_review_queue.json", queue)
        if budget:
            result["project_local_usage"] = budget.totals()
        return {
            **result,
            "checkpoint": str(directory),
            "human_review_cases": len(queue),
        }
    finally:
        if hasattr(provider, "close"):
            provider.close()


def main(argv=None):
    args = parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        result = workflow(args)
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 0
    except (AnnotationError, ProviderError) as exc:
        print(json.dumps({"status": "STOPPED", "reason": str(exc)}, ensure_ascii=True))
        return 2
    except Exception:  # noqa: BLE001 -- never echo unknown errors carrying secrets
        # Unknown errors may carry credentials or review text. Never echo their body.
        print(
            json.dumps(
                {
                    "status": "STOPPED",
                    "reason": "UNEXPECTED_ERROR_CHECK_LOCAL_CONFIGURATION",
                }
            )
        )
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
