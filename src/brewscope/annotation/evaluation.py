"""Gold comparison with missed aspects, abstentions and end-to-end pair errors."""

from collections import Counter

from .storage import digest
from .validation import ASPECTS, SENTIMENTS, AnnotationError


def prf(tp, fp, fn):
    return {
        "precision": tp / (tp + fp) if tp + fp else 0.0,
        "recall": tp / (tp + fn) if tp + fn else 0.0,
        "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0,
        "support": tp + fn,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "undefined_precision": not tp + fp,
        "undefined_recall": not tp + fn,
    }


def classification_metrics(truth, predicted):
    if len(truth) != len(predicted):
        raise AnnotationError("METRIC_LENGTH_MISMATCH")
    if not truth:
        return {
            "status": "UNDEFINED_NO_SUPPORT",
            "support": 0,
            "accuracy": None,
            "macro_f1": None,
            "per_class": {},
            "confusion_matrix": {},
        }
    per_class = {}
    matrix = {a: {b: 0 for b in (*SENTIMENTS, "ABSTAIN_OR_MISSED")} for a in SENTIMENTS}
    for target, guess in zip(truth, predicted):
        matrix[target][guess if guess in SENTIMENTS else "ABSTAIN_OR_MISSED"] += 1
    for label in SENTIMENTS:
        tp = sum(a == b == label for a, b in zip(truth, predicted))
        fp = sum(a != label and b == label for a, b in zip(truth, predicted))
        fn = sum(a == label and b != label for a, b in zip(truth, predicted))
        per_class[label] = prf(tp, fp, fn)
    return {
        "status": "COMPUTED",
        "support": len(truth),
        "accuracy": sum(a == b for a, b in zip(truth, predicted)) / len(truth),
        "macro_f1": sum(m["f1"] for m in per_class.values()) / 3,
        "per_class": per_class,
        "confusion_matrix": matrix,
    }


def evaluate_predictions(
    gold,
    predictions,
    validator,
    *,
    split="locked_validation",
    experiment=None,
    output_statuses=None,
):
    if not gold:
        return {"status": "NOT_COMPUTED", "reason": "HUMAN_GOLD_NOT_AVAILABLE"}
    if gold.get("kind") != "adjudicated_human_gold" or digest(gold["rows"]) != gold.get(
        "sha256"
    ):
        raise AnnotationError("VALIDATED_HUMAN_GOLD_REQUIRED")
    all_gold = [r["record"] for r in gold["rows"]]
    validator.batch(all_gold)
    if any(
        r["annotator_id"] != "human:gold" or r["annotation_status"] != "completed"
        for r in all_gold
    ):
        raise AnnotationError("VALIDATED_HUMAN_GOLD_REQUIRED")
    rows = [row for row in gold["rows"] if row["split"] == split]
    if not rows:
        return {"status": "NOT_COMPUTED", "reason": "REQUESTED_GOLD_SPLIT_EMPTY"}
    gold_map = {
        (r["record"]["review_id"], r["record"]["aspect_category"]): r["record"]
        for r in rows
    }
    gold_reviews = {
        r["review_id"]: {
            k: r[k] for k in ("review_text", "coffee_shop_id", "data_origin")
        }
        for r in gold_map.values()
    }
    # An entire malformed review is invalid, never partially repaired into negatives.
    by_review = {}
    for record in predictions:
        by_review.setdefault(record["review_id"], []).append(record)
    output_statuses = output_statuses or {}
    pred_map, invalid_reviews = (
        {},
        [
            rid
            for rid, status in output_statuses.items()
            if rid in gold_reviews and status != "valid"
        ],
    )
    for rid, records in by_review.items():
        if rid not in gold_reviews:
            raise AnnotationError("PREDICTION_OUTSIDE_REQUESTED_GOLD_SPLIT")
        try:
            validator.batch(records, {rid: gold_reviews[rid]})
        except AnnotationError:
            if rid not in invalid_reviews:
                invalid_reviews.append(rid)
            continue
        pred_map.update({(r["review_id"], r["aspect_category"]): r for r in records})
    detection = {}
    counts = Counter()
    errors = []
    truth_sentiment, predicted_sentiment = [], []
    per_aspect_sentiment = {a: ([], []) for a in ASPECTS}
    true_pairs, pred_pairs = set(), set()
    excluded = {
        key
        for key, r in gold_map.items()
        if r["mixed_sentiment"]
        or r["aspect_presence"] == "uncertain"
        or r["annotation_status"] != "completed"
    }
    for aspect in ASPECTS:
        tp = fp = fn = 0
        for key, target in gold_map.items():
            if key[1] != aspect:
                continue
            predicted = pred_map.get(key)
            target_present = target["aspect_presence"] == "mentioned"
            guess_present = (
                predicted is not None and predicted["aspect_presence"] == "mentioned"
            )
            tp += target_present and guess_present
            fp += not target_present and guess_present
            fn += target_present and not guess_present
            counts["mixed_gold_pairs"] += target["mixed_sentiment"]
            if predicted:
                counts["mixed_predicted_pairs"] += predicted["mixed_sentiment"]
                counts["uncertain_predicted_pairs"] += (
                    predicted["annotation_status"] == "uncertain"
                )
                counts["out_of_taxonomy_flagged_pairs"] += (
                    "out_of_taxonomy" in predicted["review_flags"]
                )
            if (
                target_present
                and target["sentiment"] in SENTIMENTS
                and key not in excluded
            ):
                guess = (
                    predicted["sentiment"]
                    if guess_present and predicted["annotation_status"] == "completed"
                    else None
                )
                truth_sentiment.append(target["sentiment"])
                predicted_sentiment.append(guess)
                per_aspect_sentiment[aspect][0].append(target["sentiment"])
                per_aspect_sentiment[aspect][1].append(guess)
                true_pairs.add((*key, target["sentiment"]))
            if key not in excluded and guess_present:
                label = (
                    predicted["sentiment"]
                    if (
                        predicted["sentiment"] in SENTIMENTS
                        and predicted["annotation_status"] == "completed"
                    )
                    else "ABSTAIN_OR_MIXED"
                )
                pred_pairs.add((*key, label))
            reasons = []
            if predicted is None:
                reasons.append("invalid_or_missing_output")
            elif target_present != guess_present:
                reasons.append(
                    "missed_aspect" if target_present else "hallucinated_aspect"
                )
            elif (
                target_present
                and key not in excluded
                and target["sentiment"] != predicted["sentiment"]
            ):
                reasons.append("sentiment_error_or_abstention")
            if reasons:
                errors.append(
                    {"review_id": key[0], "aspect_id": aspect, "reasons": reasons}
                )
        detection[aspect] = prf(tp, fp, fn)
    pooled = [sum(d[k] for d in detection.values()) for k in ("tp", "fp", "fn")]
    result = {
        "status": "COMPUTED",
        "origin": gold["data_origin"],
        "split": split,
        "gold_sha256": gold["sha256"],
        "review_count": len(gold_reviews),
        "valid_prediction_reviews": len({key[0] for key in pred_map}),
        "invalid_prediction_review_ids": invalid_reviews,
        "missing_prediction_reviews": len(
            set(gold_reviews) - set(by_review) - set(output_statuses)
        ),
        "valid_output_coverage": len({key[0] for key in pred_map}) / len(gold_reviews),
        "aspect_detection": {
            "micro": prf(*pooled),
            "macro_f1": sum(m["f1"] for m in detection.values()) / 6,
            "per_aspect": detection,
        },
        "conditional_sentiment": classification_metrics(
            truth_sentiment, predicted_sentiment
        ),
        "conditional_definition": "Scoring conditioned on all gold-mentioned resolved pairs; "
        "missed/abstained predictions count as wrong. Gold aspects were "
        "not necessarily supplied at inference; not intersection-only accuracy.",
        "sentiment_per_aspect": {
            a: classification_metrics(*p) for a, p in per_aspect_sentiment.items()
        },
        "end_to_end": {
            "micro": prf(
                len(true_pairs & pred_pairs),
                len(pred_pairs - true_pairs),
                len(true_pairs - pred_pairs),
            ),
            "excluded_mixed_or_unresolved_gold_pairs": len(excluded),
            "per_aspect": {
                a: prf(
                    len({p for p in true_pairs & pred_pairs if p[1] == a}),
                    len({p for p in pred_pairs - true_pairs if p[1] == a}),
                    len({p for p in true_pairs - pred_pairs if p[1] == a}),
                )
                for a in ASPECTS
            },
        },
        "exceptions": dict(counts),
        "errors": errors,
        "macro_policy": "Fixed 6 aspects / 3 sentiments; zero-division=0 with support/undefined flags. "
        "No sentiment support => null macro-F1.",
        "experiment": experiment or {},
        "quality_gate_passed": False,
    }
    result["result_sha256"] = digest(result)
    return result


def assess_quality(evaluation, config, experiment):
    """Research thresholds are explicit, frozen before accessing the locked holdout."""
    q = config["quality"]
    actual = evaluation.get("experiment", {})
    matches = actual == experiment
    conditions = {
        "human_gold": evaluation.get("origin") == ["authorized_review"],
        "heldout": evaluation.get("split") == "locked_validation",
        "criteria_frozen": q["criteria_frozen"] and bool(q["criteria_reference"]),
        "minimum_reviews": evaluation.get("review_count", 0)
        >= q["minimum_locked_reviews"],
        "experiment_matches": matches,
        "all_outputs_valid": not evaluation.get("invalid_prediction_review_ids")
        and not evaluation.get("missing_prediction_reviews"),
    }
    try:
        conditions.update(
            detection_micro=evaluation["aspect_detection"]["micro"]["f1"]
            >= q["detection_micro_f1_min"],
            detection_macro=evaluation["aspect_detection"]["macro_f1"]
            >= q["detection_macro_f1_min"],
            sentiment=evaluation["conditional_sentiment"]["macro_f1"]
            >= q["conditional_sentiment_macro_f1_min"],
            end_to_end=evaluation["end_to_end"]["micro"]["f1"]
            >= q["end_to_end_micro_f1_min"],
        )
    except (KeyError, TypeError):
        conditions["metrics_available"] = False
    return {"quality_gate_passed": all(conditions.values()), "checks": conditions}
