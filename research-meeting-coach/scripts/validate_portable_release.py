#!/usr/bin/env python3
"""Extract the audited ZIP and run its portable static validation in isolation."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
REPOSITORY_ROOT = PACKAGE_ROOT.parent
REQUIRED_ROOT_FILES = {"README.md", "README.zh-TW.md", "README.zh-CN.md", "release-manifest.json"}


def validate(archive_path: Path) -> dict[str, object]:
    if not archive_path.is_file():
        return {"status": "failed", "errors": [f"release archive not found: {archive_path}"]}

    with zipfile.ZipFile(archive_path) as archive:
        infos = archive.infolist()
        names = {info.filename for info in infos}
        unsafe = [
            info.filename
            for info in infos
            if PurePosixPath(info.filename).is_absolute() or ".." in PurePosixPath(info.filename).parts
        ]
        if unsafe:
            return {"status": "failed", "errors": [f"unsafe archive path: {name}" for name in unsafe]}
        missing = sorted(REQUIRED_ROOT_FILES - names)
        if missing:
            return {"status": "failed", "errors": [f"portable root file missing: {name}" for name in missing]}
        if any(name == ".github" or name.startswith(".github/") for name in names):
            return {"status": "failed", "errors": ["portable release unexpectedly contains .github"]}

        with tempfile.TemporaryDirectory(prefix="research-meeting-coach-release-") as temporary:
            extracted = Path(temporary)
            archive.extractall(extracted)
            command = [
                sys.executable,
                "research-meeting-coach/scripts/run_static_evals.py",
                "--json",
            ]
            completed = subprocess.run(
                command,
                cwd=extracted,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if completed.returncode:
                detail = (completed.stderr or completed.stdout).strip()
                return {"status": "failed", "errors": [f"extracted static validation failed: {detail}"]}

    return {
        "status": "passed",
        "archive": str(archive_path.resolve()),
        "platform": platform.system(),
        "python": platform.python_version(),
        "archive_entry_count": len(infos),
        "checks": [
            "archive paths are extraction-safe",
            "trilingual READMEs and release manifest are present",
            "repository-only .github infrastructure is absent",
            "static validation passes from the extracted portable release",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    version = (PACKAGE_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    archive_path = args.archive or REPOSITORY_ROOT / "dist" / f"research-meeting-coach-{version}.zip"
    try:
        result = validate(archive_path)
    except (OSError, zipfile.BadZipFile) as exc:
        result = {"status": "failed", "errors": [str(exc)]}
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
