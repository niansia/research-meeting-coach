#!/usr/bin/env python3
"""Aggregate baseline comparisons without mixing blind and non-blind headline metrics."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PREFERENCES = {"baseline", "candidate", "tie"}


def _nonnegative_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0


def _summarize_cohort(items: list[dict[str, Any]]) -> dict[str, Any]:
    preference_counts: Counter[str] = Counter(item["preference"] for item in items)
    factual_totals = {
        system: sum(float(item[f"{system}_factual_errors"]) for item in items)
        for system in ("baseline", "candidate")
    }
    corrections = {
        system: [float(item[f"{system}_corrections"]) for item in items]
        for system in ("baseline", "candidate")
    }
    dimensions = sorted({dimension for item in items for dimension in item["baseline_scores"]})
    dimension_deltas = {
        dimension: [
            float(item["candidate_scores"][dimension]) - float(item["baseline_scores"][dimension])
            for item in items
            if dimension in item["baseline_scores"] and dimension in item["candidate_scores"]
        ]
        for dimension in dimensions
    }
    decisive = preference_counts["baseline"] + preference_counts["candidate"]
    return {
        "rating_count": len(items),
        "preference_counts": {choice: preference_counts[choice] for choice in sorted(PREFERENCES)},
        "candidate_preference_rate_decisive": (preference_counts["candidate"] / decisive) if decisive else None,
        "factual_error_totals": factual_totals,
        "mean_corrections": {
            system: statistics.fmean(values) if values else None for system, values in corrections.items()
        },
        "mean_candidate_minus_baseline_by_dimension": {
            dimension: statistics.fmean(values)
            for dimension, values in dimension_deltas.items()
            if values
        },
    }


def summarize(data: Any) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return {}, ["root must be an object"]
    top_allowed = {"study_id", "baseline_label", "candidate_label", "sampling_notes", "comparisons"}
    extra_top = sorted(set(data) - top_allowed)
    if extra_top:
        errors.append(f"unexpected top-level fields: {', '.join(extra_top)}")
    for field in ("study_id", "baseline_label", "candidate_label"):
        if not isinstance(data.get(field), str) or not data.get(field, "").strip():
            errors.append(f"{field} is required")
    comparisons = data.get("comparisons")
    if not isinstance(comparisons, list) or not comparisons:
        errors.append("comparisons must contain at least one rating")
    if "sampling_notes" in data and not isinstance(data.get("sampling_notes"), str):
        errors.append("sampling_notes must be a string")
    if errors:
        return {}, errors

    for index, item in enumerate(comparisons):
        label = f"comparisons[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        allowed_item = {
            "case_id", "reviewer_id", "blind", "preference",
            "baseline_factual_errors", "candidate_factual_errors",
            "baseline_corrections", "candidate_corrections",
            "baseline_scores", "candidate_scores",
        }
        extra_item = sorted(set(item) - allowed_item)
        if extra_item:
            errors.append(f"{label} has unexpected fields: {', '.join(extra_item)}")
        for field in ("case_id", "reviewer_id"):
            if not isinstance(item.get(field), str) or not item.get(field, "").strip():
                errors.append(f"{label}.{field} is required")
        if item.get("blind") is not True and item.get("blind") is not False:
            errors.append(f"{label}.blind must be boolean")

        preference = item.get("preference")
        if preference not in PREFERENCES:
            errors.append(f"{label}.preference is invalid")

        for system in ("baseline", "candidate"):
            factual_key = f"{system}_factual_errors"
            correction_key = f"{system}_corrections"
            factual_value = item.get(factual_key)
            correction_value = item.get(correction_key)
            if not _nonnegative_number(factual_value):
                errors.append(f"{label}.{factual_key} must be non-negative")
            if not _nonnegative_number(correction_value):
                errors.append(f"{label}.{correction_key} must be non-negative")

        baseline_scores = item.get("baseline_scores")
        candidate_scores = item.get("candidate_scores")
        if not isinstance(baseline_scores, dict) or not isinstance(candidate_scores, dict):
            errors.append(f"{label}.baseline_scores and candidate_scores must be objects")
            continue
        if not baseline_scores or not candidate_scores:
            errors.append(f"{label}.baseline_scores and candidate_scores must not be empty")
            continue
        if set(baseline_scores) != set(candidate_scores):
            errors.append(f"{label} score dimensions do not match")
            continue
        for dimension in sorted(baseline_scores):
            baseline_value = baseline_scores[dimension]
            candidate_value = candidate_scores[dimension]
            if not all(isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 4 for value in (baseline_value, candidate_value)):
                errors.append(f"{label}.{dimension} scores must be between 0 and 4")
                continue

    if errors:
        return {}, errors

    blind_items = [item for item in comparisons if item["blind"] is True]
    non_blind_items = [item for item in comparisons if item["blind"] is False]
    blind_summary = _summarize_cohort(blind_items)
    summary = {
        "status": "summarized",
        "rating_count": len(comparisons),
        "blind_rating_count": len(blind_items),
        "non_blind_rating_count": len(non_blind_items),
        "headline_metric": {
            "cohort": "blind",
            "candidate_preference_rate_decisive": blind_summary["candidate_preference_rate_decisive"],
        },
        "blind": blind_summary,
        "non_blind": _summarize_cohort(non_blind_items),
        "all_ratings_descriptive": _summarize_cohort(comparisons),
        "claim_boundary": "Only the blind cohort may supply the headline preference metric. Non-blind and all-ratings summaries are descriptive and must not be substituted for blind results. This aggregation does not establish significance, calibration, or generalization.",
    }
    return summary, []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ratings", type=Path, help="JSON ratings file")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    try:
        data = json.loads(args.ratings.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result = {"status": "failed", "errors": [str(exc)]}
        print(json.dumps(result, ensure_ascii=False) if args.as_json else f"FAILED: {exc}")
        return 1

    summary, errors = summarize(data)
    if errors:
        result = {"status": "failed", "errors": errors}
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.as_json else "FAILED\n- " + "\n- ".join(errors))
        return 1
    print(json.dumps(summary, ensure_ascii=False, indent=2) if args.as_json else json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
