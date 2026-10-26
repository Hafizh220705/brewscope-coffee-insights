"""Blind assignments, duplicate grouping, immutable human submissions and adjudication."""

import copy
import io
import json
import re
from collections import defaultdict
from difflib import SequenceMatcher

import pandas as pd

from .runtime import source_reviews
from .storage import atomic_text, digest, immutable_json, read_json
from .validation import ASPECTS, AnnotationError


def text_normalize(text):
    return " ".join(text.casefold().split())


def duplicate_groups(reviews):
    """Exact text plus conservative near duplicates; transitive groups span full corpus.

    Near-match candidates share a five-token shingle, >=8 words, token Jaccard>=.85,
    character SequenceMatcher>=.92. This is triage, not proof of semantic identity.
    """
    reviews = sorted(reviews, key=lambda r: r["review_id"])
    parent = {r["review_id"]: r["review_id"] for r in reviews}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        a, b = find(x), find(y)
        parent[max(a, b)] = min(a, b)

    exact, inverted, prepared = {}, defaultdict(list), {}
    for review in reviews:
        rid, text = review["review_id"], text_normalize(review["review_text"])
        if text in exact:
            union(rid, exact[text])
        else:
            exact[text] = rid
        tokens = re.findall(r"\w+", text)
        if len(tokens) < 8:
            continue
        shingles = {tuple(tokens[i : i + 5]) for i in range(len(tokens) - 4)}
        candidates = {other for s in shingles for other in inverted[s]}
        token_set = set(tokens)
        for other in candidates:
            old_text, old_tokens = prepared[other]
            jaccard = len(token_set & old_tokens) / len(token_set | old_tokens)
            if (
                jaccard >= 0.85
                and SequenceMatcher(None, text, old_text, autojunk=False).ratio()
                >= 0.92
            ):
                union(rid, other)
        prepared[rid] = (text, token_set)
        for s in shingles:
            inverted[s].append(rid)
    members = defaultdict(list)
    for rid in parent:
        members[find(rid)].append(rid)
    return {rid: digest(sorted(ids)) for ids in members.values() for rid in ids}


def grouped_subset(groups, target, seed):
    """Subset sum finds closest possible group-preserving size deterministically."""
    options = {0: ()}
    for group in sorted(groups, key=lambda key: digest([seed, key])):
        size = len(groups[group])
        for total, selected in list(options.items()):
            if total + size not in options:
                options[total + size] = (*selected, group)
    best = min(options, key=lambda total: (abs(total - target), total > target, total))
    return set(options[best])


def pilot_design(reviews, candidates, seed=42):
    review_map = {r["review_id"]: r for r in reviews}
    if len(set(candidates)) != 250 or not set(candidates) <= set(review_map):
        raise AnnotationError("PILOT_REQUIRES_ORIGINAL_250_ELIGIBLE_CANDIDATES")
    grouping = duplicate_groups(reviews)
    selected = defaultdict(list)
    for rid in sorted(candidates):
        selected[grouping[rid]].append(rid)
    calibration = grouped_subset(selected, 50, seed)
    remaining = {g: ids for g, ids in selected.items() if g not in calibration}
    locked = grouped_subset(remaining, 50, seed + 1)
    manifest = []
    for rid in sorted(candidates):
        group = grouping[rid]
        split = (
            "calibration"
            if group in calibration
            else ("locked_validation" if group in locked else "development")
        )
        review = review_map[rid]
        manifest.append(
            {
                "review_id": rid,
                "coffee_shop_id": review["coffee_shop_id"],
                "duplicate_group": group,
                "split": split,
                "review_sha256": digest(review["review_text"].encode()),
                "geography_status": review["geography_status"],
            }
        )
    return manifest, grouping


def assignment_templates(reviews, manifest, annotator_id, version):
    if not annotator_id.startswith("human:") or annotator_id in (
        "human:",
        "human:gold",
    ):
        raise AnnotationError("NAMED_HUMAN_ID_REQUIRED")
    sources = {r["review_id"]: r for r in reviews}
    templates = []
    for item in manifest:
        review = sources[item["review_id"]]
        for aspect in ASPECTS:
            templates.append(
                {
                    "annotation_id": digest(
                        [item["review_id"], aspect, annotator_id, version]
                    ),
                    "review_id": review["review_id"],
                    "coffee_shop_id": review["coffee_shop_id"],
                    "data_origin": review["data_origin"],
                    "review_text": review["review_text"],
                    "aspect_category": aspect,
                    "aspect_presence": None,
                    "sentiment": None,
                    "mention_type": None,
                    "mixed_sentiment": False,
                    "evidence": [],
                    "annotation_status": "draft",
                    "annotator_id": annotator_id,
                    "taxonomy_version": version,
                    "adjudication_status": "not_required",
                    "training_eligible": False,
                    "notes": "",
                    "review_flags": [],
                }
            )
    return templates


def prepare_pilot(root, validator):
    reviews, stage3 = source_reviews(root)
    candidates = pd.read_csv(
        root / "data/interim/annotation_pilot_candidates.csv", dtype=str
    )
    manifest, groups = pilot_design(reviews, candidates.review_id.tolist())
    directory = root / "data/interim/human_annotations"
    metadata = {
        "assignment_version": 1,
        "seed": 42,
        "dataset_sha256": stage3["source_sha256"],
        "pilot_sha256": stage3["pilot_sha256"],
        "taxonomy_version": validator.version,
        "grouping_method": "exact+five-token-shingle-Jaccard.85-SequenceMatcher.92",
        "assignments": manifest,
        "annotation_state": "UNANNOTATED",
        "authorization": "OWNER_ATTESTED",
    }
    immutable_json(directory / "pilot_manifest.json", metadata)
    # Blinded packages only contain canonical blank forms; split/ratings/hints stay private.
    for annotator in ("human:A", "human:B"):
        for phase in ("calibration", "independent"):
            items = [
                m
                for m in manifest
                if (m["split"] == "calibration") == (phase == "calibration")
            ]
            records = assignment_templates(reviews, items, annotator, validator.version)
            destination = (
                directory
                / "assignments"
                / annotator.replace(":", "_")
                / (phase + ".jsonl")
            )
            text = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)
            if destination.exists() and destination.read_text(encoding="utf-8") != text:
                raise AnnotationError("ASSIGNMENT_IMMUTABLE_CONFLICT")
            if not destination.exists():
                atomic_text(destination, text)
    output = io.StringIO()
    pd.DataFrame(
        [
            {"review_id": rid, "duplicate_group": group}
            for rid, group in sorted(groups.items())
        ]
    ).to_csv(output, index=False)
    atomic_text(directory / "corpus_duplicate_groups.csv", output.getvalue())
    return {
        "reviews": len(manifest),
        "shops": len({m["coffee_shop_id"] for m in manifest}),
        "split_counts": {
            k: int(v)
            for k, v in pd.Series([m["split"] for m in manifest]).value_counts().items()
        },
        "template_decisions_per_annotator": len(manifest) * len(ASPECTS),
        "state": "UNANNOTATED",
        "source_sha256": stage3["source_sha256"],
    }


def submit_annotations(path, records, reviews, validator, *, actor, independent=True):
    """Canonical human records only. Keep originals, never rewrite an earlier revision."""
    if not actor.startswith("human:") or actor in ("human:", "human:gold"):
        raise AnnotationError("HUMAN_ACTOR_REQUIRED")
    if not records or any(
        r["annotator_id"] != actor or r["annotation_status"] == "draft" for r in records
    ):
        raise AnnotationError("HUMAN_SUBMISSION_NOT_COMPLETE_OR_WRONG_ACTOR")
    validator.batch(records, reviews)
    envelope = {
        "kind": "human_original",
        "actor": actor,
        "independent_attested": independent,
        "records": records,
        "content_sha256": digest(records),
    }
    immutable_json(path, envelope)
    return envelope


def decision_signature(record):
    """Semantic agreement excludes offsets/wording; evidence still undergoes QC."""
    return tuple(
        record[k]
        for k in (
            "aspect_presence",
            "sentiment",
            "mixed_sentiment",
            "annotation_status",
        )
    )


def gold_standard(a, b, adjudications, quality_review, manifest, validator):
    for submission in (a, b):
        if submission.get("kind") != "human_original" or not submission.get(
            "independent_attested"
        ):
            raise AnnotationError("INDEPENDENT_HUMAN_ORIGINAL_REQUIRED")
        if submission.get("content_sha256") != digest(submission["records"]):
            raise AnnotationError("HUMAN_ORIGINAL_HASH_MISMATCH")
        if not submission["actor"].startswith("human:") or any(
            r["annotator_id"] != submission["actor"] for r in submission["records"]
        ):
            raise AnnotationError("HUMAN_IDENTITY_MISMATCH")
        validator.batch(submission["records"])
    if a["actor"] == b["actor"]:
        raise AnnotationError("TWO_DISTINCT_HUMANS_REQUIRED")
    left = {(r["review_id"], r["aspect_category"]): r for r in a["records"]}
    right = {(r["review_id"], r["aspect_category"]): r for r in b["records"]}
    if not left or set(left) != set(right):
        raise AnnotationError("HUMAN_UNIVERSE_MISMATCH")
    decisions = {(d["review_id"], d["aspect_id"]): d for d in adjudications}
    if len(decisions) != len(adjudications):
        raise AnnotationError("DUPLICATE_ADJUDICATION")
    assignments = {m["review_id"]: m for m in manifest}
    if not {key[0] for key in left} <= set(assignments):
        raise AnnotationError("GOLD_ASSIGNMENT_MISMATCH")
    actors = {a["actor"], b["actor"]}
    rows = []
    for key, original in left.items():
        other = right[key]
        if any(
            original[k] != other[k]
            for k in ("review_text", "coffee_shop_id", "data_origin")
        ):
            raise AnnotationError("HUMAN_REVIEW_CONTEXT_MISMATCH")
        disagreement = decision_signature(original) != decision_signature(other)
        needs_resolution = disagreement or any(
            r["annotation_status"] != "completed" for r in (original, other)
        )
        decision = decisions.get(key)
        if needs_resolution and not decision:
            raise AnnotationError("ADJUDICATION_REQUIRED")
        chosen = copy.deepcopy(original)
        if decision:
            if (
                decision["adjudicator_id"] in actors
                or not decision["adjudicator_id"].startswith("human:")
                or not decision.get("reason", "").strip()
            ):
                raise AnnotationError("INDEPENDENT_ADJUDICATOR_AND_REASON_REQUIRED")
            chosen = copy.deepcopy(decision["record"])
            validator.record(chosen)
            for field in (
                "review_id",
                "coffee_shop_id",
                "review_text",
                "aspect_category",
                "data_origin",
            ):
                if chosen[field] != original[field]:
                    raise AnnotationError("ADJUDICATION_IDENTITY_MISMATCH")
        if (
            chosen["annotation_status"] != "completed"
            or chosen["aspect_presence"] == "uncertain"
        ):
            raise AnnotationError("UNRESOLVED_PAIR_CANNOT_ENTER_GOLD")
        audit = quality_review.get("|".join(key))
        if (
            not audit
            or audit.get("status") != "APPROVED"
            or not audit.get("notes", "").strip()
        ):
            raise AnnotationError("GOLD_HUMAN_QC_REQUIRED")
        forbidden = actors | ({decision["adjudicator_id"]} if decision else set())
        if (
            not audit.get("reviewer_id", "").startswith("human:")
            or audit["reviewer_id"] in forbidden
        ):
            raise AnnotationError("INDEPENDENT_QC_REVIEWER_REQUIRED")
        chosen.update(
            annotator_id="human:gold",
            annotation_id=digest([key, "human:gold"]),
            adjudication_status="resolved",
            training_eligible=(
                chosen["aspect_presence"] == "mentioned"
                and not chosen["mixed_sentiment"]
            ),
        )
        validator.record(chosen)
        rows.append(
            {
                "record": chosen,
                "split": assignments[key[0]]["split"],
                "duplicate_group": assignments[key[0]]["duplicate_group"],
                "geography_status": assignments[key[0]].get(
                    "geography_status", "UNVERIFIED"
                ),
                "label_source": "human_gold",
                "provenance": {
                    "original_annotation_ids": [
                        original["annotation_id"],
                        other["annotation_id"],
                    ],
                    "original_submission_hashes": [
                        a["content_sha256"],
                        b["content_sha256"],
                    ],
                    "adjudication": decision,
                    "quality_review": audit,
                },
            }
        )
    validator.batch([r["record"] for r in rows])
    from .export import assert_no_leakage

    assert_no_leakage(rows)
    return {
        "kind": "adjudicated_human_gold",
        "taxonomy_version": validator.version,
        "data_origin": sorted({r["record"]["data_origin"] for r in rows}),
        "rows": rows,
        "sha256": digest(rows),
    }


def save_gold(path, gold):
    """Immutable envelope for machines, JSONL rows for downstream research tooling."""
    immutable_json(
        path.with_suffix(".manifest.json"),
        {k: v for k, v in gold.items() if k != "rows"},
    )
    text = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in gold["rows"])
    if path.exists() and path.read_text(encoding="utf-8") != text:
        raise AnnotationError("GOLD_IMMUTABLE_CONFLICT")
    if not path.exists():
        atomic_text(path, text)


def load_gold(path):
    from .storage import read_jsonl

    metadata = read_json(path.with_suffix(".manifest.json"))
    metadata["rows"] = read_jsonl(path)
    if digest(metadata["rows"]) != metadata["sha256"]:
        raise AnnotationError("GOLD_HASH_MISMATCH")
    return metadata
