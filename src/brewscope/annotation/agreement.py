"""Pre-adjudication agreement; abstentions and undefined kappa are explicit."""

from collections import Counter

from .validation import ASPECTS, SENTIMENTS, AnnotationError


def agreement_scores(left, right, labels):
    if len(left) != len(right):
        raise AnnotationError("AGREEMENT_LENGTH_MISMATCH")
    matrix = {a: {b: 0 for b in labels} for a in labels}
    for a, b in zip(left, right):
        matrix[a][b] += 1
    n = len(left)
    raw = sum(a == b for a, b in zip(left, right)) / n if n else None
    ca, cb = Counter(left), Counter(right)
    expected = sum(ca[label] * cb[label] for label in labels) / n**2 if n else None
    kappa = (raw - expected) / (1 - expected) if n and expected < 1 else None
    return {
        "comparable_decisions": n,
        "raw_agreement": raw,
        "cohen_kappa": kappa,
        "undefined_reason": "NO_COMPARABLE_DECISIONS"
        if not n
        else ("DEGENERATE_MARGINALS" if kappa is None else None),
        "disagreements": sum(a != b for a, b in zip(left, right)),
        "confusion_matrix": matrix,
    }


def inter_annotator_agreement(a, b, validator):
    if not a or not b:
        return {
            "status": "NOT_COMPUTED",
            "reason": "INDEPENDENT_HUMAN_ANNOTATIONS_NOT_AVAILABLE",
        }
    for submission in (a, b):
        if submission.get("kind") != "human_original" or not submission.get(
            "independent_attested"
        ):
            raise AnnotationError("INDEPENDENT_HUMAN_ORIGINAL_REQUIRED")
        if not submission["actor"].startswith("human:"):
            raise AnnotationError("HUMAN_ACTOR_REQUIRED")
        if any(r["annotator_id"] != submission["actor"] for r in submission["records"]):
            raise AnnotationError("HUMAN_IDENTITY_MISMATCH")
        validator.batch(submission["records"])
    if a["actor"] == b["actor"]:
        raise AnnotationError("TWO_DISTINCT_HUMANS_REQUIRED")
    if not a["records"] or not b["records"]:
        raise AnnotationError("NO_INDEPENDENT_DECISIONS")
    index_a = {(r["review_id"], r["aspect_category"]): r for r in a["records"]}
    index_b = {(r["review_id"], r["aspect_category"]): r for r in b["records"]}
    if set(index_a) != set(index_b):
        raise AnnotationError("HUMAN_UNIVERSE_MISMATCH")
    result = {"status": "COMPUTED_PRE_ADJUDICATION", "aspects": {}}
    all_presence = ([], [])
    all_sentiment = ([], [])
    totals = Counter()
    for aspect in ASPECTS:
        presence, sentiment = ([], []), ([], [])
        counts = Counter()
        for key, left in index_a.items():
            if key[1] != aspect:
                continue
            right = index_b[key]
            if any(
                left[k] != right[k]
                for k in ("review_text", "coffee_shop_id", "data_origin")
            ):
                raise AnnotationError("HUMAN_REVIEW_CONTEXT_MISMATCH")
            counts["total_decisions"] += 1
            pair = (left, right)
            binary = all(
                r["aspect_presence"] in ("mentioned", "not_mentioned")
                and r["annotation_status"] != "draft"
                for r in pair
            )
            if binary:
                presence[0].append(left["aspect_presence"])
                presence[1].append(right["aspect_presence"])
            else:
                counts["presence_abstentions"] += 1
            counts["presence_disagreements"] += (
                left["aspect_presence"] != right["aspect_presence"]
            )
            if any(r["mixed_sentiment"] for r in pair):
                counts["mixed_excluded_pairs"] += 1
            if all(
                r["aspect_presence"] == "mentioned"
                and r["sentiment"] in SENTIMENTS
                and not r["mixed_sentiment"]
                and r["annotation_status"] == "completed"
                for r in pair
            ):
                sentiment[0].append(left["sentiment"])
                sentiment[1].append(right["sentiment"])
            else:
                counts["sentiment_noncomparable"] += 1
        presence_result = agreement_scores(*presence, ("mentioned", "not_mentioned"))
        sentiment_result = agreement_scores(*sentiment, SENTIMENTS)
        result["aspects"][aspect] = {
            **dict(counts),
            "presence": presence_result,
            "sentiment": sentiment_result,
        }
        for i in (0, 1):
            all_presence[i].extend(presence[i])
            all_sentiment[i].extend(sentiment[i])
        totals.update(counts)
    result.update(totals)
    result["presence"] = agreement_scores(*all_presence, ("mentioned", "not_mentioned"))
    result["sentiment"] = agreement_scores(*all_sentiment, SENTIMENTS)
    result["presence_coverage"] = (
        result["presence"]["comparable_decisions"] / result["total_decisions"]
    )
    result["sentiment_coverage"] = (
        result["sentiment"]["comparable_decisions"] / result["total_decisions"]
    )
    return result
