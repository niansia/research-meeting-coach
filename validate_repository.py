#!/usr/bin/env python3
"""Validate repository-only infrastructure that is intentionally absent from the portable Skill ZIP."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REQUIRED_FILES = (
    ".github/workflows/ci.yml",
    ".github/ISSUE_TEMPLATE/bug-report.yml",
    ".github/ISSUE_TEMPLATE/feature-request.yml",
    ".github/ISSUE_TEMPLATE/pilot-feedback.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/RELEASE_CHECKLIST.md",
)
REQUIRED_CI_COMMANDS = (
    "python -m pip install --disable-pip-version-check -r requirements-dev.txt",
    "python research-meeting-coach/scripts/run_static_evals.py",
    "python validate_repository.py --json",
    "python research-meeting-coach/scripts/validate_schema_contracts.py",
    "python research-meeting-coach/scripts/validate_public_question_seed.py",
    "python research-meeting-coach/scripts/build_release.py --json",
)


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"required repository file is missing or empty: {relative}")

    workflow = root / ".github/workflows/ci.yml"
    if workflow.is_file():
        content = workflow.read_text(encoding="utf-8")
        for command in REQUIRED_CI_COMMANDS:
            if command not in content:
                errors.append(f"CI workflow does not run required command: {command}")
        install_command = REQUIRED_CI_COMMANDS[0]
        static_command = REQUIRED_CI_COMMANDS[1]
        if install_command in content and static_command in content and content.index(install_command) > content.index(static_command):
            errors.append("CI workflow must install runtime dependencies before static validation")
        if "permissions:\n  contents: read" not in content:
            errors.append("CI workflow must keep contents permission read-only")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    errors = validate()
    result = {
        "status": "failed" if errors else "passed",
        "repository_file_count": len(REQUIRED_FILES),
        "errors": errors,
        "scope": "repository infrastructure; intentionally not part of the portable release ZIP",
    }
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif errors:
        print("FAILED")
        for error in errors:
            print(f"- {error}")
    else:
        print("PASSED")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
