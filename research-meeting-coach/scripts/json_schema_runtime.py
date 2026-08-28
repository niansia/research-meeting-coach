#!/usr/bin/env python3
"""Shared Draft 2020-12 validation for runtime structural-plus-semantic gates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError as exc:  # surfaced as a validation failure, never a partial pass
    Draft202012Validator = None  # type: ignore[assignment,misc]
    FormatChecker = None  # type: ignore[assignment,misc]
    JSONSCHEMA_IMPORT_ERROR: Exception | None = exc
else:
    JSONSCHEMA_IMPORT_ERROR = None


INSTALL_HINT = "python -m pip install -r research-meeting-coach/requirements.txt"


def validate_against_schema(data: Any, schema_path: Path) -> list[str]:
    if JSONSCHEMA_IMPORT_ERROR is not None or Draft202012Validator is None or FormatChecker is None:
        return [f"JSON Schema validation unavailable ({JSONSCHEMA_IMPORT_ERROR}); install runtime dependency with: {INSTALL_HINT}"]
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot load published schema {schema_path.name}: {exc}"]
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:  # jsonschema exposes multiple schema-error subclasses
        return [f"published schema {schema_path.name} is invalid: {exc}"]

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors: list[str] = []
    for error in sorted(validator.iter_errors(data), key=lambda item: [str(part) for part in item.absolute_path]):
        location = "/".join(str(part) for part in error.absolute_path) or "<root>"
        errors.append(f"schema {schema_path.name} at {location}: {error.message}")
    return errors
