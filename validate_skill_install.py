#!/usr/bin/env python3
"""Smoke-test a project-local Agent Skill install through the pinned skills CLI."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SKILL_NAME = "research-meeting-coach"
SKILLS_CLI = "skills@1.5.23"


def find_executable(*names: str) -> str | None:
    for name in names:
        executable = shutil.which(name)
        if executable:
            return executable
    return None


def validate() -> dict[str, object]:
    npx = find_executable("npx", "npx.cmd")
    git = find_executable("git", "git.exe")
    if not npx or not git:
        missing = [name for name, path in (("npx", npx), ("git", git)) if not path]
        return {"status": "failed", "errors": [f"required executable not found: {name}" for name in missing]}

    expected_version = (ROOT / SKILL_NAME / "VERSION").read_text(encoding="utf-8").strip()
    environment = os.environ.copy()
    environment.update({"CI": "1", "NO_COLOR": "1", "FORCE_COLOR": "0"})

    with tempfile.TemporaryDirectory(prefix="research-meeting-coach-install-") as temporary:
        project = Path(temporary)
        initialized = subprocess.run(
            [git, "init", "--quiet"],
            cwd=project,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if initialized.returncode:
            return {"status": "failed", "errors": ["temporary Git project initialization failed"]}

        command = [
            npx,
            "--yes",
            SKILLS_CLI,
            "add",
            str(ROOT),
            "--skill",
            SKILL_NAME,
            "--agent",
            "codex",
            "--copy",
            "--yes",
        ]
        installed = subprocess.run(
            command,
            cwd=project,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if installed.returncode:
            detail = (installed.stderr or installed.stdout).strip()
            return {"status": "failed", "errors": [f"skills CLI install failed: {detail}"]}

        installed_root = project / ".agents" / "skills" / SKILL_NAME
        required = (
            installed_root / "SKILL.md",
            installed_root / "VERSION",
            installed_root / "references" / "evidence-integrity.md",
            installed_root / "schemas" / "research-meeting-state.schema.json",
        )
        missing = [path.relative_to(project).as_posix() for path in required if not path.is_file()]
        if missing:
            return {"status": "failed", "errors": [f"installed file missing: {path}" for path in missing]}

        actual_version = (installed_root / "VERSION").read_text(encoding="utf-8").strip()
        if actual_version != expected_version:
            return {
                "status": "failed",
                "errors": [f"installed version {actual_version!r} does not match {expected_version!r}"],
            }

        return {
            "status": "passed",
            "skills_cli": SKILLS_CLI,
            "skill": SKILL_NAME,
            "version": actual_version,
            "installed_file_count": sum(path.is_file() for path in installed_root.rglob("*")),
            "checks": [
                "local repository discovered as an Agent Skills source",
                "project-local Codex copy install completed",
                "required Skill, reference, and schema files installed",
                "installed version matches repository version",
            ],
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    result = validate()
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif result["status"] == "passed":
        print("PASSED")
    else:
        print("FAILED")
        for error in result.get("errors", []):
            print(f"- {error}")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
