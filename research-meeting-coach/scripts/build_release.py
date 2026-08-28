#!/usr/bin/env python3
"""Build and audit a public ZIP from default-deny paths and content checks."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
REPOSITORY_ROOT = PACKAGE_ROOT.parent
ROOT_FILES = {"README.md", "README.zh-TW.md", "README.zh-CN.md", "AUDIT_REPORT.md", "LICENSE", "CONTRIBUTING.md", "SECURITY.md", "CODE_OF_CONDUCT.md", "requirements-dev.txt"}
PACKAGE_ROOT_FILES = {"SKILL.md", "VERSION", "requirements.txt"}
PACKAGE_DIRECTORIES = {"agents", "assets", "evals", "examples", "references", "schemas", "scripts"}
DENIED_PARTS = {"__pycache__", ".git", "dist"}
DENIED_SUFFIXES = {".pyc", ".pyo", ".rar", ".zip"}
DENIED_NAMES = {".env", ".env.local", ".env.production", ".env.development", ".env.test"}
DENIED_NAME_FRAGMENTS = {"confidential", "private", "real-pilot", "source-register"}
PUBLIC_POST_URL_RE = re.compile(
    rb"https?://(?:www\.|m\.)?(?:"
    rb"dcard\.tw/(?:f|p)/[^\s\)\]\"']*/p/\d+|"
    rb"reddit\.com/r/[^\s\)\]\"']+/comments/[A-Za-z0-9_]+|"
    rb"(?:ptt\.cc|pttweb\.cc)/bbs/[^\s/]+/[^\s\)\]\"']+\.html|"
    rb"threads\.net/@[^\s/]+/post/[^\s\)\]\"']+|"
    rb"facebook\.com/(?:[^\s\)\]\"']+/posts/[^\s\)\]\"']+|permalink\.php\?[^\s\)\]\"']+|story\.php\?[^\s\)\]\"']+)"
    rb")",
    re.IGNORECASE,
)
SECRET_PATTERNS = {
    "OpenAI-style API key": re.compile(rb"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{16,}\b"),
    "GitHub classic personal access token": re.compile(rb"\bghp_[A-Za-z0-9]{20,}\b"),
    "AWS access key ID": re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
    "private key block": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}


def is_denied(relative_path: Path | PurePosixPath) -> bool:
    parts = {part.casefold() for part in relative_path.parts}
    name = relative_path.name.casefold()
    return bool(
        parts & DENIED_PARTS
        or relative_path.suffix.casefold() in DENIED_SUFFIXES
        or name in DENIED_NAMES
        or name.startswith(".env.")
        or name.endswith(".local.json")
        or any(fragment in name for fragment in DENIED_NAME_FRAGMENTS)
    )


def is_allowed_package_path(relative_path: Path | PurePosixPath) -> bool:
    """Allow only the documented package surface; unknown top-level paths fail closed."""
    parts = relative_path.parts
    if not parts:
        return False
    if len(parts) == 1:
        return parts[0] in PACKAGE_ROOT_FILES
    return parts[0] in PACKAGE_DIRECTORIES


def is_allowed_archive_path(archive_name: PurePosixPath) -> bool:
    if archive_name == PurePosixPath("release-manifest.json"):
        return True
    if len(archive_name.parts) == 1:
        return archive_name.name in ROOT_FILES
    if archive_name.parts[0] != "research-meeting-coach":
        return False
    return is_allowed_package_path(PurePosixPath(*archive_name.parts[1:]))


def sensitive_post_urls(content: bytes) -> list[str]:
    return [match.group(0).decode("utf-8", errors="replace") for match in PUBLIC_POST_URL_RE.finditer(content)]


def sensitive_secret_types(content: bytes) -> list[str]:
    """Return finding labels without echoing a possible credential into logs."""
    return [label for label, pattern in SECRET_PATTERNS.items() if pattern.search(content)]


def collect_files() -> tuple[list[tuple[Path, PurePosixPath]], list[str]]:
    included: list[tuple[Path, PurePosixPath]] = []
    excluded: list[str] = []
    for name in sorted(ROOT_FILES):
        source = REPOSITORY_ROOT / name
        if not source.is_file() or source.is_symlink():
            raise FileNotFoundError(f"required release file missing: {source}")
        included.append((source, PurePosixPath(name)))
    for source in sorted(path for path in PACKAGE_ROOT.rglob("*") if path.is_file()):
        package_relative = source.relative_to(PACKAGE_ROOT)
        relative = Path("research-meeting-coach") / package_relative
        archive_name = PurePosixPath(relative.as_posix())
        if source.is_symlink() or not is_allowed_package_path(package_relative) or is_denied(archive_name):
            excluded.append(archive_name.as_posix())
            continue
        included.append((source, archive_name))
    return included, excluded


def audit_entries(entries: list[tuple[PurePosixPath, bytes]]) -> list[str]:
    errors: list[str] = []
    names: set[str] = set()
    for archive_name, content in entries:
        name = archive_name.as_posix()
        if name in names:
            errors.append(f"duplicate archive path: {name}")
        names.add(name)
        if archive_name.is_absolute() or ".." in archive_name.parts:
            errors.append(f"unsafe archive path: {name}")
        if not is_allowed_archive_path(archive_name):
            errors.append(f"path outside the public allowlist: {name}")
        if is_denied(archive_name):
            errors.append(f"denied file in release: {name}")
        for url in sensitive_post_urls(content):
            errors.append(f"public post URL leaked in {name}: {url}")
        for secret_type in sensitive_secret_types(content):
            errors.append(f"possible {secret_type} leaked in {name}")
    return errors


def build(output: Path) -> dict[str, object]:
    files, excluded = collect_files()
    entries = [(archive_name, source.read_bytes()) for source, archive_name in files]
    errors = audit_entries(entries)
    if errors:
        raise ValueError("; ".join(errors))

    manifest = {
        "format": "research-meeting-coach-public-release-1",
        "version": (PACKAGE_ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "files": [
            {
                "path": archive_name.as_posix(),
                "sha256": hashlib.sha256(content).hexdigest(),
                "size": len(content),
            }
            for archive_name, content in entries
        ],
    }
    manifest_content = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    entries.append((PurePosixPath("release-manifest.json"), manifest_content))

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for archive_name, content in entries:
            archive.writestr(archive_name.as_posix(), content)

    with zipfile.ZipFile(output, "r") as archive:
        archived_entries = [(PurePosixPath(info.filename), archive.read(info)) for info in archive.infolist()]
        archive_errors = archive.testzip()
    errors = audit_entries(archived_entries)
    if archive_errors:
        errors.append(f"ZIP CRC failure: {archive_errors}")
    if errors:
        output.unlink(missing_ok=True)
        raise ValueError("; ".join(errors))

    return {
        "status": "passed",
        "output": str(output.resolve()),
        "archive_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "file_count": len(entries),
        "excluded_count": len(excluded),
        "excluded": excluded,
        "checks": [
            "repository and package paths default-deny outside explicit public roots",
            "local registers, environment files, private/confidential pilot filenames, and symlinks excluded",
            "__pycache__ and bytecode excluded",
            "nested archives excluded",
            "individual Dcard, Reddit, PTT, Threads, and Facebook post URLs absent",
            "common API-key, access-token, and private-key patterns absent",
            "archive paths safe and unique",
            "ZIP CRC valid",
            "per-file SHA-256 manifest included",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    version = (PACKAGE_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    output = args.output or REPOSITORY_ROOT / "dist" / f"research-meeting-coach-{version}.zip"
    try:
        result = build(output)
    except (OSError, ValueError) as exc:
        result = {"status": "failed", "errors": [str(exc)]}
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else f"FAILED: {exc}")
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else f"PASSED: {result['output']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
