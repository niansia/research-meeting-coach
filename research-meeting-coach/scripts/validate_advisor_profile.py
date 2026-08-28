#!/usr/bin/env python3
"""Validate the published advisor-profile schema, then behavioral provenance rules."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from json_schema_runtime import validate_against_schema


PROHIBITED = {"nationality", "region", "institution", "age", "gender", "discipline", "prestige"}
EVIDENCE_TYPES = {"explicit_feedback", "repeated_behavior", "single_observation", "student_impression"}
CONFIDENCE = {"low", "medium", "high"}
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "advisor-profile.schema.json"


def validate_profile(data: Any) -> list[str]:
    errors = validate_against_schema(data, SCHEMA_PATH)
    if errors:
        return errors
    if data.get("schema_version") != "1.1":
        errors.append("schema_version must be '1.1'")

    prohibited = data.get("prohibited_inference")
    if not isinstance(prohibited, list):
        errors.append("prohibited_inference must be an array")
    else:
        missing = sorted(PROHIBITED - set(prohibited))
        if missing:
            errors.append(f"prohibited_inference is missing: {', '.join(missing)}")

    profile = data.get("advisor_profile")
    if not isinstance(profile, dict):
        return errors + ["advisor_profile must be an object"]

    for dimension, entry in profile.items():
        label = f"advisor_profile.{dimension}"
        dimension_tokens = set(re.findall(r"[a-z]+", dimension.lower()))
        if dimension_tokens & PROHIBITED:
            errors.append(f"{label} is a prohibited demographic dimension")
        if not isinstance(entry, dict):
            errors.append(f"{label} must be an object")
            continue
        confidence = entry.get("confidence")
        if entry.get("basis") != "behavioral_evidence":
            errors.append(f"{label}.basis must be behavioral_evidence")
        if confidence not in CONFIDENCE:
            errors.append(f"{label}.confidence is invalid")
        evidence = entry.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{label}.evidence must contain at least one item")
            continue

        qualifying_high = False
        seen_records: set[tuple[str, tuple[str, ...], str]] = set()
        for index, item in enumerate(evidence):
            item_label = f"{label}.evidence[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{item_label} must be an object")
                continue
            evidence_type = item.get("type")
            if evidence_type not in EVIDENCE_TYPES:
                errors.append(f"{item_label}.type is invalid")
            meeting_ids = item.get("meeting_ids")
            if not isinstance(meeting_ids, list) or not meeting_ids or not all(isinstance(x, str) and x for x in meeting_ids):
                errors.append(f"{item_label}.meeting_ids must contain non-empty strings")
                meeting_ids = []
            if len(meeting_ids) != len(set(meeting_ids)):
                errors.append(f"{item_label}.meeting_ids contains duplicates")
            source = item.get("source")
            if not isinstance(source, dict):
                errors.append(f"{item_label}.source must be an object")
                source = {}
            else:
                if not isinstance(source.get("locator"), str) or not source.get("locator", "").strip():
                    errors.append(f"{item_label}.source.locator is required")
                verification = source.get("verification")
                if verification not in {"text_exact", "manual"}:
                    errors.append(f"{item_label}.source.verification is invalid")
                if verification == "text_exact" and (not isinstance(source.get("quote"), str) or not source.get("quote", "").strip()):
                    errors.append(f"{item_label}.source.quote is required for text_exact verification")
                if verification == "manual" and (not isinstance(source.get("verification_note"), str) or not source.get("verification_note", "").strip()):
                    errors.append(f"{item_label}.source.verification_note is required for manual verification")
            record_key = (str(evidence_type), tuple(sorted(meeting_ids)), str(source.get("locator", "")))
            if record_key in seen_records:
                errors.append(f"{item_label} duplicates an earlier evidence record")
            seen_records.add(record_key)

            if evidence_type == "repeated_behavior" and len(set(meeting_ids)) < 3:
                errors.append(f"{item_label} needs at least three distinct meetings")
            if evidence_type == "explicit_feedback" or (evidence_type == "repeated_behavior" and len(set(meeting_ids)) >= 3):
                qualifying_high = True

        if confidence == "high" and not qualifying_high:
            errors.append(f"{label} cannot have high confidence without explicit feedback or repeated behavior across three meetings")
        if confidence in {"medium", "high"} and all(
            isinstance(item, dict) and item.get("type") == "student_impression" for item in evidence
        ):
            errors.append(f"{label} based only on student impressions must remain low confidence")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    try:
        data = json.loads(args.profile.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result = {"status": "failed", "errors": [str(exc)]}
        print(json.dumps(result, ensure_ascii=False) if args.as_json else f"FAILED: {exc}")
        return 1
    errors = validate_profile(data)
    result = {"status": "passed" if not errors else "failed", "errors": errors}
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif errors:
        print("FAILED")
        for error in errors:
            print(f"- {error}")
    else:
        print("PASSED")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
