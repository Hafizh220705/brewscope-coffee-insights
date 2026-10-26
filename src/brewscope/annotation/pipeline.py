"""Serial checkpointed inference with durable quota accounting and safe resume."""

import logging
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .providers import ProviderError
from .runtime import check_live_gates, privacy_hold
from .storage import atomic_json, digest, exclusive_run, read_json
from .validation import AnnotationError, inference_schema, parse_inference

LOGGER = logging.getLogger(__name__)


class UsageBudget:
    """Project-wide local ledger. Reserve before network; crashes still consume budget.

    Does not see calls made outside this repository. AI Studio remains authoritative.
    Pacific calendar days follow the provider's RPD reset, including DST.
    """

    def __init__(
        self, path, scope, rpm, daily, *, tpm=None, clock=time.time, sleep=time.sleep
    ):
        if any(type(v) is not int or v <= 0 for v in (rpm, daily)):
            raise AnnotationError("QUOTA_LIMITS_REQUIRED")
        self.path, self.scope, self.rpm, self.daily = Path(path), scope, rpm, daily
        self.tpm, self.clock, self.sleep = tpm, clock, sleep
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS calls (id INTEGER PRIMARY KEY, "
                "scope TEXT, ts REAL, day TEXT, input_est INTEGER, "
                "input_tokens INTEGER, output_tokens INTEGER, total_tokens INTEGER)"
            )

    def _connect(self):
        return sqlite3.connect(self.path, timeout=15)

    def reserve(self, input_estimate):
        if self.tpm and input_estimate > self.tpm:
            raise ProviderError("INPUT_EXCEEDS_TOKEN_RATE_BUDGET", quota_exhausted=True)
        while True:
            now = self.clock()
            day = (
                datetime.fromtimestamp(now, ZoneInfo("America/Los_Angeles"))
                .date()
                .isoformat()
            )
            wait = 0
            with self._connect() as db:
                db.execute("BEGIN IMMEDIATE")
                count = db.execute(
                    "SELECT COUNT(*) FROM calls WHERE scope=? AND day=?",
                    (self.scope, day),
                ).fetchone()[0]
                if count >= self.daily:
                    raise ProviderError(
                        "LOCAL_DAILY_BUDGET_EXHAUSTED", quota_exhausted=True
                    )
                recent = db.execute(
                    "SELECT ts,input_est FROM calls WHERE scope=? AND ts>? ORDER BY ts",
                    (self.scope, now - 60),
                ).fetchall()
                if len(recent) >= self.rpm:
                    wait = recent[0][0] + 60 - now + 0.01
                if (
                    self.tpm
                    and sum(row[1] for row in recent) + input_estimate > self.tpm
                ):
                    wait = max(wait, recent[0][0] + 60 - now + 0.01)
                if not wait:
                    cursor = db.execute(
                        "INSERT INTO calls(scope,ts,day,input_est) VALUES(?,?,?,?)",
                        (self.scope, now, day, input_estimate),
                    )
                    return cursor.lastrowid
            # Small waits allow progress updates/interruption. No unbounded API retry.
            self.sleep(min(wait, 30))

    def record(self, reservation, response):
        with self._connect() as db:
            db.execute(
                "UPDATE calls SET input_tokens=?, output_tokens=?, total_tokens=? WHERE id=?",
                (
                    response.input_tokens,
                    response.output_tokens,
                    response.total_tokens,
                    reservation,
                ),
            )

    def totals(self):
        with self._connect() as db:
            rows = db.execute(
                "SELECT COUNT(*),SUM(input_tokens),SUM(output_tokens),SUM(total_tokens),"
                "COUNT(input_tokens) FROM calls WHERE scope=?",
                (self.scope,),
            ).fetchone()
        return dict(
            zip(
                (
                    "request_attempts",
                    "input_tokens",
                    "output_tokens",
                    "total_tokens",
                    "requests_with_usage",
                ),
                rows,
            )
        )


class AnnotationPipeline:
    def __init__(
        self,
        provider,
        validator,
        system_prompt,
        identity,
        directory,
        *,
        budget=None,
        max_attempts=3,
        backoff_seconds=2,
        sleep=time.sleep,
        max_input_characters=20000,
        runtime_config=None,
        mode="synthetic",
        pilot_evaluation=None,
    ):
        if not 1 <= max_attempts <= 5:
            raise AnnotationError("INVALID_MAX_ATTEMPTS")
        self.provider, self.validator, self.prompt = provider, validator, system_prompt
        self.identity, self.directory, self.budget = identity, Path(directory), budget
        self.max_attempts, self.backoff, self.sleep = (
            max_attempts,
            backoff_seconds,
            sleep,
        )
        self.max_input_characters = max_input_characters
        self.runtime_config, self.mode = runtime_config, mode
        self.pilot_evaluation = pilot_evaluation

    def run(self, reviews, *, execute=False, resume=False, batch_size=1):
        if batch_size < 1:
            raise AnnotationError("INVALID_BATCH_SIZE")
        reviews = sorted(reviews, key=lambda r: r["review_id"])
        if len({r["review_id"] for r in reviews}) != len(reviews):
            raise AnnotationError("DUPLICATE_SOURCE_ID")
        if self.provider.name == "mock" and any(
            r["data_origin"] != "synthetic" for r in reviews
        ):
            raise AnnotationError("MOCK_REQUIRES_SYNTHETIC_REVIEW")
        # Callers must explicitly enable side effects; dry-run creates no state.
        if not execute:
            return {
                "status": "DRY_RUN",
                "planned_reviews": len(reviews),
                "requests": 0,
                "provider": self.provider.name,
            }
        if self.provider.name == "gemini" and self.budget is None:
            raise AnnotationError("GEMINI_REQUIRES_DURABLE_BUDGET")
        if self.provider.name != "mock":
            if self.runtime_config is None:
                raise AnnotationError("LIVE_RUNTIME_GATES_REQUIRED")
            check_live_gates(
                self.runtime_config,
                self.provider.name,
                self.mode,
                reviews,
                execute=execute,
                evaluation=self.pilot_evaluation,
            )
        report = {
            "status": "COMPLETED",
            "planned_reviews": len(reviews),
            "requests": 0,
            "valid": 0,
            "invalid": 0,
            "held": 0,
            "skipped": 0,
            "interrupted": 0,
            "unresolved_existing": 0,
            "stage4d_complete": False,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "usage_missing_requests": 0,
            "run_id": digest(self.identity),
        }
        with exclusive_run(self.directory):
            manifest = self.directory / "manifest.json"
            if manifest.exists():
                if read_json(manifest) != self.identity:
                    raise AnnotationError("CHECKPOINT_FINGERPRINT_MISMATCH")
                if not resume:
                    raise AnnotationError("CHECKPOINT_EXISTS_USE_RESUME")
            else:
                atomic_json(manifest, self.identity)
            for batch_start in range(0, len(reviews), batch_size):
                stop = False
                for review in reviews[batch_start : batch_start + batch_size]:
                    context = {
                        k: review[k]
                        for k in (
                            "review_id",
                            "review_text",
                            "coffee_shop_id",
                            "data_origin",
                        )
                    }
                    # Scope/triage metadata never changes the inference payload.
                    key = digest([self.identity, context])
                    path = self.directory / "reviews" / (key + ".json")
                    prior = read_json(path) if path.exists() else None
                    if prior:
                        if prior["status"] == "in_flight":
                            # Exactly-once delivery cannot be guaranteed over HTTP.
                            # Never silently resend a potentially delivered request.
                            report["interrupted"] += 1
                        elif prior["status"] == "quota_stopped":
                            # Explicit resume may continue a provider-rejected request.
                            prior = None
                        if prior:
                            report["skipped"] += 1
                            if prior["status"] != "valid":
                                report["unresolved_existing"] += 1
                            continue
                    outcome = {
                        "request_key": key,
                        "review_id": review["review_id"],
                        "review_sha256": digest(context),
                        "provenance": self.identity,
                        "geography_status": review.get("geography_status", "SYNTHETIC"),
                        "status": "pending",
                        "attempts": [],
                        "records": [],
                    }
                    if (
                        privacy_hold(review)
                        or len(review["review_text"]) > self.max_input_characters
                    ):
                        outcome.update(
                            status="held", reason="PRIVACY_OR_INPUT_LENGTH_REVIEW"
                        )
                        atomic_json(path, outcome)
                        report["held"] += 1
                        continue
                    for attempt in range(1, self.max_attempts + 1):
                        try:
                            reservation = None
                            if self.budget:
                                # UTF-8 bytes are a conservative local estimate, not actual token usage.
                                estimate = (
                                    len((self.prompt + review["review_text"]).encode())
                                    + len(str(inference_schema()).encode())
                                    + 512
                                )
                                reservation = self.budget.reserve(estimate)
                            outcome["status"] = "in_flight"
                            outcome["started_at"] = datetime.now(
                                ZoneInfo("UTC")
                            ).isoformat()
                            atomic_json(path, outcome)
                            report["requests"] += 1
                            response = self.provider.generate(
                                review, self.prompt, inference_schema()
                            )
                            if self.budget:
                                self.budget.record(reservation, response)
                            for name in (
                                "input_tokens",
                                "output_tokens",
                                "total_tokens",
                            ):
                                value = getattr(response, name)
                                if value is not None:
                                    report[name] += value
                            if response.input_tokens is None:
                                report["usage_missing_requests"] += 1
                            entry = {
                                "attempt": attempt,
                                "raw_response": response.text,
                                "usage": {
                                    n: getattr(response, n)
                                    for n in (
                                        "input_tokens",
                                        "output_tokens",
                                        "total_tokens",
                                    )
                                },
                                "provider_metadata": response.metadata,
                            }
                            outcome["attempts"].append(entry)
                            try:
                                records = parse_inference(
                                    response.text,
                                    review,
                                    self.validator,
                                    "ai:" + self.provider.name,
                                )
                            except AnnotationError as exc:
                                entry["validation"] = str(exc)
                                raise
                            entry["validation"] = "VALID"
                            outcome.update(status="valid", records=records)
                            report["valid"] += 1
                            break
                        except ProviderError as exc:
                            outcome["attempts"].append(
                                {"attempt": attempt, "error": exc.code}
                            )
                            if exc.quota_exhausted:
                                outcome.update(status="quota_stopped", reason=exc.code)
                                report.update(status="QUOTA_STOPPED")
                                stop = True
                                break
                            if not exc.retryable or attempt == self.max_attempts:
                                outcome.update(status="failed", reason=exc.code)
                                report["invalid"] += 1
                                break
                        except AnnotationError as exc:
                            if attempt == self.max_attempts:
                                outcome.update(status="invalid", reason=str(exc))
                                report["invalid"] += 1
                                break
                        # Save received response before any retry/wait.
                        outcome["status"] = "retry_pending"
                        atomic_json(path, outcome)
                        self.sleep(min(30, self.backoff * (2 ** (attempt - 1))))
                    outcome["finished_at"] = datetime.now(ZoneInfo("UTC")).isoformat()
                    atomic_json(path, outcome)
                    LOGGER.info(
                        "review=%s status=%s",
                        digest(review["review_id"])[:12],
                        outcome["status"],
                    )
                    if stop:
                        break
                if report["status"] != "QUOTA_STOPPED" and any(
                    report[k]
                    for k in ("invalid", "held", "interrupted", "unresolved_existing")
                ):
                    report["status"] = "NEEDS_REVIEW"
                atomic_json(self.directory / "last_run_report.json", report)
                if stop:
                    break
        return report


def checkpoint_records(directory, *, valid_only=True):
    archives = [
        read_json(p) for p in sorted((Path(directory) / "reviews").glob("*.json"))
    ]
    return [a for a in archives if a["status"] == "valid"] if valid_only else archives


def quality_queue(archives, candidate_metadata=None, *, seed=42, random_fraction=0.10):
    """Random audit includes valid outputs; priority flags are not confidence scores."""
    if not 0 <= random_fraction <= 1:
        raise AnnotationError("INVALID_AUDIT_FRACTION")
    candidate_metadata = candidate_metadata or {}
    queue = []
    for a in archives:
        reasons = []
        records = a.get("records", [])
        if a["status"] != "valid":
            reasons.append(a["status"])
        for r in records:
            if r["mixed_sentiment"]:
                reasons.append("mixed")
            if r["annotation_status"] == "uncertain":
                reasons.append("uncertain")
            if (
                r["aspect_category"] in ("cleanliness", "facilities")
                and r["aspect_presence"] == "mentioned"
            ):
                reasons.append("rare_aspect")
            if r["mention_type"] in ("implicit", "mixed"):
                reasons.append("implicit")
            if r["sentiment"] == "negative":
                reasons.append("negative_minority")
            reasons.extend(r["review_flags"])
        metadata = candidate_metadata.get(a["review_id"], {})
        if str(metadata.get("keyword_count")) == "0":
            reasons.append("no_keyword")
        if str(metadata.get("potential_text_duplicate", "false")).lower() == "true":
            reasons.append("potential_duplicate_conflict")
        random_pick = (
            int(digest([seed, a["review_id"]])[:12], 16) / 16**12 < random_fraction
        )
        if random_pick:
            reasons.append("random_audit")
        if reasons:
            queue.append(
                {
                    "review_id": a["review_id"],
                    "reasons": sorted(set(reasons)),
                    "random_audit": random_pick,
                    "human_review_status": "PENDING",
                }
            )
    return queue
