#!/usr/bin/env python3
"""Verify advisor-profile evidence against scoped meeting records."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from validate_source_grounding import normalize_space, resolve_locator


def validate_profile_grounding(data: Any, source_root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict) or not isinstance(data.get("advisor_profile"), dict):
        return ["advisor_profile must be an object"], warnings
    for dimension, entry in data["advisor_profile"].items():
        if not isinstance(entry, dict):
            continue
        for index, evidence in enumerate(entry.get("evidence", [])):
            label = f"advisor_profile.{dimension}.evidence[{index}]"
            if not isinstance(evidence, dict) or not isinstance(evidence.get("source"), dict):
                errors.append(f"{label}.source must be an object")
                continue
            source = evidence["source"]
            mode = source.get("verification")
            if mode == "manual":
                warnings.append(f"{label}: advisor evidence requires manual verification ({source.get('verification_note', '')})")
                continue
            if mode != "text_exact":
                errors.append(f"{label}: advisor evidence must be text_exact or explicitly manual")
                continue
            locator = str(source.get("locator", ""))
            resolved = resolve_locator(locator, source_root)
            if resolved is None:
                errors.append(f"{label}: locator must be a relative path plus one line number inside source root: {locator}")
                continue
            path, line_number = resolved
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except OSError as exc:
                errors.append(f"{label}: cannot read {path}: {exc}")
                continue
            if line_number > len(lines):
                errors.append(f"{label}: locator line {line_number} exceeds {path.name} length {len(lines)}")
                continue
            quote = normalize_space(str(source.get("quote", "")))
            source_line = normalize_space(lines[line_number - 1])
            note = normalize_space(str(evidence.get("note", ""))).rstrip(".。")
            if not quote or quote not in source_line:
                errors.append(f"{label}: exact quote is not present at {locator}")
            elif not note or note not in quote.rstrip(".。"):
                errors.append(f"{label}: evidence note is not an exact span of the verified quote")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    try:
        data = json.loads(args.profile.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors, warnings = [str(exc)], []
    else:
        errors, warnings = validate_profile_grounding(data, args.source_root)
    status = "failed" if errors else "manual_review_required" if warnings else "passed"
    result = {"status": status, "errors": errors, "warnings": warnings}
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif errors:
        print("FAILED")
        for error in errors:
            print(f"- {error}")
    elif warnings:
        print("MANUAL REVIEW REQUIRED")
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("PASSED")
    return 1 if errors else 2 if warnings else 0


if __name__ == "__main__":
    sys.exit(main())
