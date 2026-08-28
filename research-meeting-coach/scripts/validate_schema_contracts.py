#!/usr/bin/env python3
"""Validate bundled JSON instances against their published Draft 2020-12 schemas."""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:
    print("FAILED: install runtime dependencies with: python -m pip install -r research-meeting-coach/requirements.txt")
    raise SystemExit(2)


ROOT = Path(__file__).resolve().parent.parent


def mappings() -> list[tuple[Path, list[Path]]]:
    return [
        (ROOT / "schemas" / "research-meeting-state.schema.json", [ROOT / "examples" / "compression-confound" / "research-meeting-state.json"]),
        (ROOT / "schemas" / "advisor-profile.schema.json", [ROOT / "evals" / "fixtures" / "advisor-profile-valid.json"]),
        (ROOT / "schemas" / "eval-case.schema.json", sorted((ROOT / "evals" / "cases").glob("E*.json"))),
        (ROOT / "schemas" / "question-theme-taxonomy.schema.json", [ROOT / "evals" / "question-theme-taxonomy.json"]),
        (ROOT / "schemas" / "question-theme-eval.schema.json", [ROOT / "evals" / "question-themes" / "E15-synthetic.json"]),
        (ROOT / "schemas" / "human-evaluation-results.schema.json", [ROOT / "evals" / "fixtures" / "human-evaluation-synthetic.json"]),
        (ROOT / "schemas" / "public-question-seed-corpus.schema.json", [ROOT / "evals" / "public-question-seed" / "seed-corpus.json"]),
    ]


def main() -> int:
    failures: list[dict[str, str]] = []
    schema_count = 0
    instance_count = 0
    for schema_path, instance_paths in mappings():
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:  # jsonschema exposes several schema-error subclasses
            failures.append({"schema": str(schema_path), "instance": "", "error": str(exc)})
            continue
        schema_count += 1
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        for instance_path in instance_paths:
            instance_count += 1
            instance = json.loads(instance_path.read_text(encoding="utf-8"))
            for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path)):
                location = "/".join(str(part) for part in error.absolute_path) or "<root>"
                failures.append({
                    "schema": str(schema_path.relative_to(ROOT)),
                    "instance": str(instance_path.relative_to(ROOT)),
                    "error": f"{location}: {error.message}",
                })
    result = {
        "status": "failed" if failures else "passed",
        "schema_count": schema_count,
        "instance_count": instance_count,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
