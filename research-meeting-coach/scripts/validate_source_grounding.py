#!/usr/bin/env python3
"""Verify RMS source locators and exact quotes against user-scoped text files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


LOCATOR_RE = re.compile(r"^(?P<path>.+):(?P<line>[1-9][0-9]*)$")
GENERIC_METRIC_TOKENS = {"count", "number", "rate", "score", "value"}


def normalize_space(value: str) -> str:
    return " ".join(value.split())


def normalize_lexical(value: str) -> str:
    return normalize_space(re.sub(r"[_/\-]+", " ", value).casefold())


def phrase_present(text: str, phrase: str) -> bool:
    normalized_text = normalize_lexical(text)
    normalized_phrase = normalize_lexical(phrase)
    if not normalized_phrase:
        return False
    if re.search(r"[^\x00-\x7F]", normalized_phrase):
        return normalized_phrase in normalized_text
    return bool(re.search(rf"(?<!\w){re.escape(normalized_phrase)}(?!\w)", normalized_text))


def metric_present(quote: str, metric: str) -> bool:
    """Conservatively bind a canonical metric to words in an exact quote."""
    if phrase_present(quote, metric):
        return True
    quote_tokens = set(re.findall(r"[^\W\d_]+", normalize_lexical(quote), re.UNICODE))
    metric_tokens = [
        token
        for token in re.findall(r"[^\W\d_]+", normalize_lexical(metric), re.UNICODE)
        if token not in GENERIC_METRIC_TOKENS
    ]
    return bool(metric_tokens) and all(token in quote_tokens or f"{token}s" in quote_tokens for token in metric_tokens)


def approximation_attached(quote: str, value: str) -> bool:
    compact_quote = quote.replace(",", "")
    compact_value = re.escape(value.replace(",", ""))
    value_token = rf"(?<![\d.]){compact_value}(?![\d.])"
    english_prefix = r"(?:around|about|approximately|approx\.?|roughly|circa)\s*(?:the\s+)?"
    cjk_prefix = r"(?:約|大約|大概|近)\s*"
    symbol_prefix = r"(?:~|≈)\s*"
    suffix = r"\s*(?:approximately|roughly|or\s+so|左右|上下)"
    return bool(
        re.search(rf"(?:{english_prefix}|{cjk_prefix}|{symbol_prefix}){value_token}", compact_quote, re.IGNORECASE)
        or re.search(rf"{value_token}{suffix}", compact_quote, re.IGNORECASE)
    )


def source_items(rms: dict[str, Any]) -> list[tuple[str, dict[str, Any], dict[str, Any] | None]]:
    items: list[tuple[str, dict[str, Any], dict[str, Any] | None]] = []
    for index, fact in enumerate(rms.get("facts", [])):
        if isinstance(fact, dict) and isinstance(fact.get("source"), dict):
            items.append((f"facts[{index}]", fact["source"], fact))
    continuity = rms.get("continuity", {})
    if isinstance(continuity, dict):
        for index, action in enumerate(continuity.get("previous_actions", [])):
            if isinstance(action, dict) and isinstance(action.get("source"), dict):
                items.append((f"continuity.previous_actions[{index}]", action["source"], None))
    return items


def resolve_locator(locator: str, source_root: Path) -> tuple[Path, int] | None:
    match = LOCATOR_RE.fullmatch(locator)
    if not match:
        return None
    root = source_root.resolve()
    candidate = (root / match.group("path")).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate, int(match.group("line"))


def unit_present(quote: str, value: str, unit: str) -> bool:
    if unit.casefold() == "unitless":
        return True
    escaped_value = re.escape(value.replace(",", ""))
    compact_quote = quote.replace(",", "")
    if unit == "%":
        return bool(re.search(rf"{escaped_value}\s*%", compact_quote))
    return bool(re.search(rf"{escaped_value}\s*(?:-|\s)?\s*{re.escape(unit)}\b", compact_quote, re.IGNORECASE))


def validate_grounding(rms: dict[str, Any], source_root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for label, source, fact in source_items(rms):
        mode = source.get("verification")
        if fact and fact.get("evidence_class") == "project_fact" and mode == "unverified":
            errors.append(f"{label}: project_fact cannot use unverified source verification")
        if mode == "manual":
            warnings.append(f"{label}: source requires manual verification ({source.get('verification_note', '')})")
            continue
        if mode == "unverified":
            warnings.append(f"{label}: source is explicitly unverified ({source.get('verification_note', '')})")
            continue
        if mode != "text_exact":
            errors.append(f"{label}: unsupported or missing source verification mode")
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
        if not quote or quote not in source_line:
            errors.append(f"{label}: exact quote is not present at {locator}")
            continue

        if fact and fact.get("evidence_class") == "project_fact":
            statement = normalize_space(str(fact.get("statement", ""))).rstrip(".。")
            comparable_quote = quote.rstrip(".。")
            if not statement or statement not in comparable_quote:
                errors.append(f"{label}: project_fact statement is not an exact text span at {locator}; use manual verification for a paraphrase")

        if fact and fact.get("fact_type") == "measurement":
            for index, measurement in enumerate(fact.get("measurements", [])):
                if not isinstance(measurement, dict):
                    continue
                value = str(measurement.get("value", ""))
                unit = str(measurement.get("unit", ""))
                metric = str(measurement.get("metric", ""))
                condition = str(measurement.get("condition", ""))
                qualifier = str(measurement.get("qualifier", ""))
                if value.replace(",", "") not in quote.replace(",", ""):
                    errors.append(f"{label}.measurements[{index}]: value {value!r} is absent from the exact quote")
                elif not unit_present(quote, value, unit):
                    errors.append(f"{label}.measurements[{index}]: unit {unit!r} is not attached to value {value!r} in the exact quote")
                if not metric_present(quote, metric):
                    errors.append(f"{label}.measurements[{index}]: metric {metric!r} is not lexically grounded in the exact quote")
                if not phrase_present(quote, condition):
                    errors.append(f"{label}.measurements[{index}]: condition {condition!r} is not an exact lexical span in the quote")
                attached_approximation = approximation_attached(quote, value)
                if qualifier == "approximate" and not attached_approximation:
                    errors.append(f"{label}.measurements[{index}]: approximate qualifier has no hedge attached to value {value!r} in the exact quote")
                if qualifier == "exact" and attached_approximation:
                    errors.append(f"{label}.measurements[{index}]: exact qualifier contradicts hedge language attached to value {value!r} in the exact quote")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rms", required=True, type=Path)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    try:
        rms = json.loads(args.rms.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors, warnings = [str(exc)], []
    else:
        errors, warnings = validate_grounding(rms, args.source_root)
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
