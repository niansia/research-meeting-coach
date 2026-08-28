#!/usr/bin/env python3
"""Reject output numbers that are not grounded in the RMS fact ledger."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from validate_rms import validate_rms


NUMBER_RE = re.compile(r"(?<![\w.])([+-]?\d[\d,]*(?:\.\d+)?\s*%?)(?!\w)")
FACT_CITATION_RE = re.compile(r"\[(F\d+)\]")
MARKDOWN_PREFIX_RE = re.compile(r"^\s*(?:#{1,6}\s*)?(?:\d+[.)]\s+|[-*+]\s+)")
UNIT_AFTER_RE = re.compile(r"^\s*(?:-|/)?\s*([A-Za-zµμ°][A-Za-z0-9µμ°/%^.-]*)")
SPELLED_DECIMAL_RE = re.compile(
    r"\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s+point\s+(?:zero|one|two|three|four|five|six|seven|eight|nine)(?:[ -]+(?:zero|one|two|three|four|five|six|seven|eight|nine))*\b",
    re.IGNORECASE,
)
HEDGE_RE = re.compile(r"\b(?:about|around|approximately|approx\.?|roughly|nearly|circa)\b|(?:約為|大約|約|接近|ประมาณ)", re.IGNORECASE)
UNIT_ALIASES = {
    "min": {"min", "mins", "minute", "minutes"},
    "frame": {"frame", "frames"},
    "ms": {"ms", "millisecond", "milliseconds"},
    "s": {"s", "sec", "secs", "second", "seconds"},
    "h": {"h", "hr", "hrs", "hour", "hours"},
    "day": {"day", "days"},
    "point": {"point", "points", "pp"},
    "seed": {"seed", "seeds"},
    "run": {"run", "runs"},
    "token": {"token", "tokens"},
    "sample": {"sample", "samples"},
    "epoch": {"epoch", "epochs"},
}


def normalize(token: str) -> str:
    return token.replace(",", "").replace(" ", "")


def numbers(text: str) -> set[str]:
    return {normalize(match.group(1)) for match in NUMBER_RE.finditer(text)}


def fact_number_map(rms: dict[str, Any]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for fact in rms.get("facts", []):
        if not isinstance(fact, dict) or not isinstance(fact.get("id"), str):
            continue
        source = fact.get("source") if isinstance(fact.get("source"), dict) else {}
        text = " ".join(str(value) for value in (fact.get("statement", ""), source.get("quote", "")))
        result[fact["id"]] = numbers(text)
    return result


def fact_locator_number_map(rms: dict[str, Any]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for fact in rms.get("facts", []):
        if not isinstance(fact, dict) or not isinstance(fact.get("id"), str):
            continue
        source = fact.get("source") if isinstance(fact.get("source"), dict) else {}
        result[fact["id"]] = numbers(str(source.get("locator", "")))
    return result


def measurement_metadata_map(rms: dict[str, Any]) -> dict[str, dict[str, list[dict[str, str]]]]:
    result: dict[str, dict[str, list[dict[str, str]]]] = {}
    for fact in rms.get("facts", []):
        if not isinstance(fact, dict) or not isinstance(fact.get("id"), str):
            continue
        fact_measurements: dict[str, list[dict[str, str]]] = {}
        for measurement in fact.get("measurements", []):
            if not isinstance(measurement, dict):
                continue
            value = normalize(str(measurement.get("value", "")))
            unit = str(measurement.get("unit", "")).casefold()
            if value and unit:
                token = f"{value}%" if unit == "%" else value
                fact_measurements.setdefault(token, []).append({
                    "unit": unit,
                    "condition": str(measurement.get("condition", "")),
                    "qualifier": str(measurement.get("qualifier", "")),
                })
        result[fact["id"]] = fact_measurements
    return result


def known_units(rms: dict[str, Any]) -> set[str]:
    units = {alias for aliases in UNIT_ALIASES.values() for alias in aliases} | {"%"}
    for fact in rms.get("facts", []):
        if isinstance(fact, dict):
            for measurement in fact.get("measurements", []):
                if isinstance(measurement, dict):
                    unit = str(measurement.get("unit", "")).casefold()
                    units |= UNIT_ALIASES.get(unit, {unit})
    for item in rms.get("derived_numbers", []):
        if isinstance(item, dict):
            unit = str(item.get("unit", "")).casefold()
            units |= UNIT_ALIASES.get(unit, {unit})
    return units


def observed_unit(line: str, match: re.Match[str], vocabulary: set[str]) -> str | None:
    if "%" in match.group(1):
        return "%"
    suffix = line[match.end():match.end() + 24]
    unit_match = UNIT_AFTER_RE.match(suffix)
    if not unit_match:
        return None
    candidate = unit_match.group(1).rstrip(".,;:").casefold()
    return candidate if candidate in vocabulary else None


def unit_matches(expected: set[str], observed: str | None) -> bool:
    if not expected:
        return True
    if expected == {"unitless"}:
        return observed is None
    expanded = set().union(*(UNIT_ALIASES.get(unit, {unit}) for unit in expected))
    return observed in expanded


def normalized_words(value: str) -> str:
    return " ".join(re.sub(r"[^\w%]+", " ", value.casefold()).split())


def condition_distance(line: str, match: re.Match[str], condition: str) -> int | None:
    words = normalized_words(condition).split()
    if not words:
        return None
    pattern = re.compile(r"\b" + r"[^\w%]+".join(re.escape(word) for word in words) + r"\b", re.IGNORECASE)
    distances: list[int] = []
    for occurrence in pattern.finditer(line):
        if occurrence.end() <= match.start():
            distances.append(match.start() - occurrence.end())
        elif occurrence.start() >= match.end():
            distances.append(occurrence.start() - match.end())
        else:
            distances.append(0)
    return min(distances) if distances else None


def measurement_matches(
    metadata: list[dict[str, str]],
    line: str,
    match: re.Match[str],
    current_unit: str | None,
    known_conditions: set[str],
) -> bool:
    window = line[max(0, match.start() - 36):min(len(line), match.end() + 20)]
    for item in metadata:
        condition = item.get("condition", "")
        expected_distance = condition_distance(line, match, condition)
        competing_distances = [
            distance
            for other in known_conditions
            if normalized_words(other) != normalized_words(condition)
            for distance in [condition_distance(line, match, other)]
            if distance is not None
        ]
        condition_ok = expected_distance is not None and (
            not competing_distances or expected_distance < min(competing_distances)
        )
        qualifier_ok = item.get("qualifier") != "approximate" or bool(HEDGE_RE.search(window))
        if condition_ok and qualifier_ok and unit_matches({item.get("unit", "")}, current_unit):
            return True
    return False


def locator_context(line: str, match: re.Match[str]) -> bool:
    prefix = line[max(0, match.start() - 24):match.start()].lower()
    return bool(
        re.search(r"(?:row|line|page|figure|fig|table|slide|p\.)\s*[_:#=-]?\s*$", prefix)
        or (prefix and prefix[-1] in {":", "#", "_"})
    )


def meeting_context(line: str, match: re.Match[str], meeting: dict[str, Any]) -> bool:
    date = str(meeting.get("date", ""))
    if date and date in line:
        return True
    window = line[max(0, match.start() - 28):min(len(line), match.end() + 28)].lower()
    return bool(re.search(r"\b(?:duration|minutes?|mins?|time budget|date)\b|會議時間|分鐘|日期|时长|分钟|日期", window))


def validate(rms: dict[str, Any], output: str) -> list[dict[str, Any]]:
    rms_errors = validate_rms(rms)
    if rms_errors:
        return [{"line": 0, "numbers": [], "fact_citations": [], "text": "", "severity": "error", "reason": f"RMS is invalid: {'; '.join(rms_errors)}"}]
    fact_numbers = fact_number_map(rms)
    locator_numbers = fact_locator_number_map(rms)
    measurement_metadata = measurement_metadata_map(rms)
    known_conditions = {
        item.get("condition", "")
        for fact_metadata in measurement_metadata.values()
        for entries in fact_metadata.values()
        for item in entries
        if item.get("condition")
    }
    vocabulary = known_units(rms)
    fact_verification = {
        fact.get("id"): (fact.get("source", {}).get("verification") if isinstance(fact.get("source"), dict) else None)
        for fact in rms.get("facts", []) if isinstance(fact, dict)
    }
    derived_calculations: dict[str, set[str]] = {}
    derived_units: dict[str, set[str]] = {}
    derived_structure: dict[str, set[str]] = {}
    for item in rms.get("derived_numbers", []):
        if not isinstance(item, dict) or not item.get("token"):
            continue
        token = normalize(item["token"])
        if item.get("kind") == "calculation":
            derived_calculations.setdefault(token, set()).update(
                operand.get("fact_id") for operand in item.get("operands", []) if isinstance(operand, dict) and isinstance(operand.get("fact_id"), str)
            )
            derived_units.setdefault(token, set()).add(str(item.get("unit", "")).casefold())
        elif item.get("kind") == "presentation_structure":
            derived_structure.setdefault(token, set()).add(str(item.get("unit", "")).casefold())
    meeting = rms.get("meeting", {}) if isinstance(rms.get("meeting"), dict) else {}
    meeting_numbers = numbers(json.dumps(meeting, ensure_ascii=False))
    budget_token = normalize(str(meeting.get("time_budget_min", ""))) if "time_budget_min" in meeting else None
    violations: list[dict[str, Any]] = []

    for line_number, original_line in enumerate(output.splitlines(), start=1):
        line = MARKDOWN_PREFIX_RE.sub("", original_line)
        for word_match in SPELLED_DECIMAL_RE.finditer(line):
            violations.append({
                "line": line_number,
                "numbers": [word_match.group(0)],
                "fact_citations": [],
                "text": original_line,
                "severity": "error",
                "reason": "spelled-out decimal bypasses deterministic numeric validation; use digits and a fact citation",
            })
        citations = list(FACT_CITATION_RE.finditer(line))
        for match in NUMBER_RE.finditer(line):
            token = normalize(match.group(1))
            if token in meeting_numbers and meeting_context(line, match, meeting):
                if token != budget_token or unit_matches({"min"}, observed_unit(line, match, vocabulary)):
                    continue
            if token in derived_structure and meeting_context(line, match, meeting) and unit_matches(derived_structure[token], observed_unit(line, match, vocabulary)):
                continue

            after = [citation for citation in citations if citation.start() >= match.end()]
            before = [citation for citation in citations if citation.end() <= match.start()]
            nearest = min(after, key=lambda citation: citation.start() - match.end()) if after else None
            if nearest is None and before:
                nearest = min(before, key=lambda citation: match.start() - citation.end())

            fact_id = nearest.group(1) if nearest else None
            cited_fact_ids = {citation.group(1) for citation in citations}
            current_unit = observed_unit(line, match, vocabulary)
            required_operands = derived_calculations.get(token, set())
            grounded_in_calculation = bool(required_operands) and required_operands <= cited_fact_ids and unit_matches(derived_units.get(token, set()), current_unit)
            typed_metadata = measurement_metadata.get(fact_id, {}).get(token, []) if fact_id else []
            grounded_in_fact = fact_id is not None and token in fact_numbers.get(fact_id, set()) and (
                measurement_matches(typed_metadata, line, match, current_unit, known_conditions)
                if typed_metadata else unit_matches(set(), current_unit)
            )
            grounded_in_locator = fact_id is not None and token in locator_numbers.get(fact_id, set()) and locator_context(line, match)
            if grounded_in_fact and fact_verification.get(fact_id) != "text_exact":
                violations.append({
                    "line": line_number,
                    "numbers": [token],
                    "fact_citations": [fact_id],
                    "text": original_line,
                    "severity": "warning",
                    "reason": f"numeric support from {fact_id} requires manual source verification",
                })
            if not grounded_in_calculation and not grounded_in_fact and not grounded_in_locator:
                violations.append(
                    {
                        "line": line_number,
                        "numbers": [token],
                        "fact_citations": [fact_id] if fact_id else [],
                        "text": original_line,
                        "severity": "error",
                        "reason": "number/unit/condition/qualifier is not grounded in its nearest fact citation, every declared calculation operand, or meeting-time context",
                    }
                )
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rms", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    try:
        rms = json.loads(args.rms.read_text(encoding="utf-8"))
        output = args.output.read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError) as exc:
        result = {"status": "failed", "violations": [{"reason": str(exc)}]}
        print(json.dumps(result, ensure_ascii=False) if args.as_json else f"FAILED: {exc}")
        return 1

    violations = validate(rms, output)
    errors = [item for item in violations if item.get("severity") != "warning"]
    warnings = [item for item in violations if item.get("severity") == "warning"]
    status = "failed" if errors else "manual_review_required" if warnings else "passed"
    result = {"status": status, "violations": errors, "warnings": warnings}
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif errors:
        print("FAILED")
        for item in errors:
            print(f"- line {item['line']}: {', '.join(item['numbers'])} :: {item['text']}")
    elif warnings:
        print("MANUAL REVIEW REQUIRED")
        for item in warnings:
            print(f"- line {item['line']}: {', '.join(item['numbers'])} :: {item['text']}")
    else:
        print("PASSED")
    return 1 if errors else 2 if warnings else 0


if __name__ == "__main__":
    sys.exit(main())
