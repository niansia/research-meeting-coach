#!/usr/bin/env python3
"""Score ranked attack-surface themes against recorded advisor questions."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

RISKS = {"Critical", "High", "Medium", "Low"}
DEFAULT_TAXONOMY = Path(__file__).resolve().parent.parent / "evals" / "question-theme-taxonomy.json"


def score(data: Any, k: int, taxonomy: Any | None = None) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    if taxonomy is None:
        try:
            taxonomy = json.loads(DEFAULT_TAXONOMY.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return {}, [f"cannot load taxonomy: {exc}"]
    if not isinstance(taxonomy, dict) or not isinstance(taxonomy.get("themes"), list):
        return {}, ["taxonomy must contain a themes array"]
    if set(taxonomy) - {"taxonomy_version", "freeze_rule", "themes"}:
        errors.append("taxonomy contains unexpected top-level fields")
    for field in ("taxonomy_version", "freeze_rule"):
        if not isinstance(taxonomy.get(field), str) or not taxonomy.get(field, "").strip():
            errors.append(f"taxonomy.{field} is required")
    allowed_theme_ids: set[str] = set()
    for index, item in enumerate(taxonomy["themes"]):
        if not isinstance(item, dict):
            errors.append(f"taxonomy.themes[{index}] must be an object")
            continue
        if set(item) != {"theme_id", "definition", "include", "exclude", "example"}:
            errors.append(f"taxonomy.themes[{index}] fields do not match the taxonomy contract")
        for field in ("theme_id", "definition", "include", "exclude", "example"):
            if not isinstance(item.get(field), str) or not item.get(field, "").strip():
                errors.append(f"taxonomy.themes[{index}].{field} is required")
        theme_id = item.get("theme_id")
        if isinstance(theme_id, str):
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", theme_id):
                errors.append(f"taxonomy.themes[{index}].theme_id is invalid")
            elif theme_id in allowed_theme_ids:
                errors.append(f"duplicate taxonomy theme_id: {theme_id}")
            else:
                allowed_theme_ids.add(theme_id)
    if not allowed_theme_ids:
        errors.append("taxonomy contains no usable theme IDs")
    if errors:
        return {}, errors
    if not isinstance(data, dict):
        return {}, ["root must be an object"]
    extra_top = sorted(set(data) - {"case_id", "synthetic", "taxonomy_version", "annotation_source", "predictions", "actual_questions"})
    if extra_top:
        errors.append(f"unexpected top-level fields: {', '.join(extra_top)}")
    for field in ("case_id", "annotation_source"):
        if not isinstance(data.get(field), str) or not data.get(field, "").strip():
            errors.append(f"{field} is required")
    if not isinstance(data.get("synthetic"), bool):
        errors.append("synthetic must be boolean")
    if not isinstance(data.get("taxonomy_version"), str) or not data.get("taxonomy_version", "").strip():
        errors.append("taxonomy_version is required")
    elif data.get("taxonomy_version") != taxonomy.get("taxonomy_version"):
        errors.append("taxonomy_version does not match the frozen taxonomy")
    predictions = data.get("predictions")
    questions = data.get("actual_questions")
    if not isinstance(predictions, list) or not predictions:
        errors.append("predictions must be a non-empty array")
    if not isinstance(questions, list) or not questions:
        errors.append("actual_questions must be a non-empty array")
    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        errors.append("k must be a positive integer")
    if errors:
        return {}, errors

    valid_predictions: list[tuple[int, str]] = []
    ranks: set[int] = set()
    prediction_themes: set[str] = set()
    for index, item in enumerate(predictions):
        if not isinstance(item, dict):
            errors.append(f"predictions[{index}] must be an object")
            continue
        extra_prediction = sorted(set(item) - {"theme_id", "rank", "risk"})
        if extra_prediction:
            errors.append(f"predictions[{index}] has unexpected fields: {', '.join(extra_prediction)}")
        theme_id = item.get("theme_id")
        rank = item.get("rank")
        if not isinstance(theme_id, str) or not theme_id.strip():
            errors.append(f"predictions[{index}].theme_id is required")
        elif theme_id in prediction_themes:
            errors.append(f"duplicate prediction theme_id: {theme_id}")
        elif theme_id not in allowed_theme_ids:
            errors.append(f"predictions[{index}].theme_id is not in the frozen taxonomy: {theme_id}")
        else:
            prediction_themes.add(theme_id)
        if not isinstance(rank, int) or isinstance(rank, bool) or rank < 1:
            errors.append(f"predictions[{index}].rank must be an integer >= 1")
        elif rank in ranks:
            errors.append(f"duplicate prediction rank: {rank}")
        else:
            ranks.add(rank)
        if item.get("risk") not in RISKS:
            errors.append(f"predictions[{index}].risk is invalid")
        if isinstance(theme_id, str) and theme_id.strip() and isinstance(rank, int) and not isinstance(rank, bool) and rank >= 1:
            valid_predictions.append((rank, theme_id))

    question_theme_sets: list[set[str]] = []
    for index, item in enumerate(questions):
        themes = item.get("theme_ids") if isinstance(item, dict) else None
        if not isinstance(item, dict):
            errors.append(f"actual_questions[{index}] must be an object")
            continue
        extra_question = sorted(set(item) - {"text", "theme_ids"})
        if extra_question:
            errors.append(f"actual_questions[{index}] has unexpected fields: {', '.join(extra_question)}")
        if not isinstance(item.get("text"), str) or not item.get("text", "").strip():
            errors.append(f"actual_questions[{index}].text is required")
        if not isinstance(themes, list) or not themes or not all(isinstance(theme, str) and theme for theme in themes):
            errors.append(f"actual_questions[{index}].theme_ids must be a non-empty string array")
            continue
        if len(themes) != len(set(themes)):
            errors.append(f"actual_questions[{index}].theme_ids contains duplicates")
        unknown_themes = sorted(set(themes) - allowed_theme_ids)
        if unknown_themes:
            errors.append(f"actual_questions[{index}] uses themes outside the frozen taxonomy: {', '.join(unknown_themes)}")
        question_theme_sets.append(set(themes))
    if errors:
        return {}, errors

    top_themes = {theme for _, theme in sorted(valid_predictions)[:k]}
    actual_themes = set().union(*question_theme_sets)
    matched_themes = top_themes & actual_themes
    matched_questions = sum(1 for themes in question_theme_sets if themes & top_themes)
    return {
        "case_id": data.get("case_id"),
        "synthetic": data.get("synthetic"),
        "k": k,
        "theme_recall_at_k": len(matched_themes) / len(actual_themes),
        "question_coverage_at_k": matched_questions / len(question_theme_sets),
        "matched_theme_ids": sorted(matched_themes),
        "unmatched_actual_theme_ids": sorted(actual_themes - top_themes),
    }, []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--taxonomy", type=Path, default=DEFAULT_TAXONOMY)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        taxonomy = json.loads(args.taxonomy.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        summary, errors = {}, [str(exc)]
    else:
        summary, errors = score(data, args.k, taxonomy)
    result = {"status": "failed" if errors else "passed", "errors": errors, "summary": summary}
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif errors:
        print("FAILED")
        for error in errors:
            print(f"- {error}")
    else:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
