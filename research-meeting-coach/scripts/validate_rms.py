#!/usr/bin/env python3
"""Validate the published RMS schema, then its semantic invariants."""

from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from json_schema_runtime import validate_against_schema


INTENTS = {"progress", "troubleshooting", "decision", "proposal", "mixed"}
ACTION_STATUSES = {"done", "partial", "blocked", "dropped-with-reason", "unknown"}
LAYERS = {"observation", "interpretation", "hypothesis", "proposal"}
RISKS = {"Critical", "High", "Medium", "Low"}
NUMBER_RE = re.compile(r"(?<![\w.])([+-]?\d[\d,]*(?:\.\d+)?)(?!\w)")
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "research-meeting-state.schema.json"


def add(error_list: list[str], condition: bool, message: str) -> None:
    if not condition:
        error_list.append(message)


def require_list(data: dict[str, Any], key: str, errors: list[str]) -> list[Any]:
    value = data.get(key)
    if not isinstance(value, list):
        errors.append(f"{key} must be an array")
        return []
    return value


def validate_ids(items: list[Any], prefix: str, label: str, errors: list[str]) -> set[str]:
    seen: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{label}[{index}] must be an object")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id.startswith(prefix) or not item_id[len(prefix):].isdigit():
            errors.append(f"{label}[{index}].id must match {prefix}<digits>")
            continue
        if item_id in seen:
            errors.append(f"duplicate {label} id: {item_id}")
        seen.add(item_id)
    return seen


def validate_source(item: dict[str, Any], label: str, errors: list[str]) -> None:
    source = item.get("source")
    add(errors, isinstance(source, dict), f"{label}.source must be an object")
    if isinstance(source, dict):
        add(errors, isinstance(source.get("locator"), str) and bool(source.get("locator", "").strip()), f"{label}.source.locator is required")
        verification = source.get("verification")
        add(errors, verification in {"text_exact", "manual", "unverified"}, f"{label}.source.verification is invalid")
        if verification == "text_exact":
            add(errors, isinstance(source.get("quote"), str) and bool(source.get("quote", "").strip()), f"{label}.source.quote is required for text_exact verification")
        elif verification in {"manual", "unverified"}:
            add(errors, isinstance(source.get("verification_note"), str) and bool(source.get("verification_note", "").strip()), f"{label}.source.verification_note is required for {verification} verification")


def validate_measurements(fact: dict[str, Any], label: str, errors: list[str]) -> None:
    measurements = fact.get("measurements")
    if fact.get("fact_type") != "measurement":
        add(errors, measurements is None, f"{label}.measurements is allowed only when fact_type=measurement")
        return
    add(errors, isinstance(measurements, list) and bool(measurements), f"{label}.measurements must be a non-empty array")
    if not isinstance(measurements, list):
        return
    typed_values: set[str] = set()
    for index, measurement in enumerate(measurements):
        measurement_label = f"{label}.measurements[{index}]"
        if not isinstance(measurement, dict):
            errors.append(f"{measurement_label} must be an object")
            continue
        for key in ("metric", "value", "unit", "condition"):
            add(errors, isinstance(measurement.get(key), str) and bool(measurement.get(key, "").strip()), f"{measurement_label}.{key} is required")
        value = measurement.get("value")
        if isinstance(value, str):
            add(errors, bool(re.fullmatch(r"[+-]?[0-9][0-9,]*(?:\.[0-9]+)?", value)), f"{measurement_label}.value must be numeric text without a unit")
            typed_values.add(value.replace(",", ""))
        add(errors, measurement.get("qualifier") in {"exact", "approximate"}, f"{measurement_label}.qualifier is invalid")
    statement_values = {match.group(1).replace(",", "") for match in NUMBER_RE.finditer(str(fact.get("statement", "")))}
    missing = sorted(statement_values - typed_values)
    if missing:
        errors.append(f"{label}.measurements does not type statement numbers: {', '.join(missing)}")


def validate_rms(data: Any) -> list[str]:
    errors = validate_against_schema(data, SCHEMA_PATH)
    if errors:
        return errors

    add(errors, data.get("schema_version") == "1.1", "schema_version must be '1.1'")

    meeting = data.get("meeting")
    add(errors, isinstance(meeting, dict), "meeting must be an object")
    if isinstance(meeting, dict):
        add(errors, meeting.get("intent") in INTENTS, "meeting.intent is invalid")
        audience = meeting.get("audience")
        add(errors, isinstance(audience, list) and bool(audience) and all(isinstance(x, str) and x.strip() for x in audience), "meeting.audience must contain at least one non-empty string")
        if "time_budget_min" in meeting:
            value = meeting["time_budget_min"]
            add(errors, isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0, "meeting.time_budget_min must be positive")

    facts = require_list(data, "facts", errors)
    fact_ids = validate_ids(facts, "F", "facts", errors)
    required_retention: set[str] = set()
    for index, fact in enumerate(facts):
        if not isinstance(fact, dict):
            continue
        label = f"facts[{index}]"
        add(errors, fact.get("evidence_class") in {"project_fact", "external_literature"}, f"{label}.evidence_class is invalid")
        add(errors, fact.get("fact_type") in {"measurement", "observation", "artifact", "event", "failure", "blocker", "record"}, f"{label}.fact_type is invalid")
        add(errors, isinstance(fact.get("statement"), str) and bool(fact.get("statement", "").strip()), f"{label}.statement is required")
        validate_source(fact, label, errors)
        validate_measurements(fact, label, errors)
        retention = fact.get("retention", "normal")
        add(errors, retention in {"required", "normal"}, f"{label}.retention is invalid")
        if retention == "required" and isinstance(fact.get("id"), str):
            required_retention.add(fact["id"])

    reasoning = require_list(data, "reasoning_items", errors)
    reasoning_ids = validate_ids(reasoning, "R", "reasoning_items", errors)
    for index, item in enumerate(reasoning):
        if not isinstance(item, dict):
            continue
        label = f"reasoning_items[{index}]"
        layer = item.get("layer")
        add(errors, layer in LAYERS, f"{label}.layer is invalid")
        refs = item.get("evidence_ids")
        add(errors, isinstance(refs, list), f"{label}.evidence_ids must be an array")
        if isinstance(refs, list):
            unknown = sorted(set(refs) - fact_ids)
            if unknown:
                errors.append(f"{label} references unknown facts: {', '.join(unknown)}")
            if layer in {"observation", "interpretation"} and not refs:
                errors.append(f"{label} requires evidence for layer {layer}")

    asks = require_list(data, "asks", errors)
    ask_ids = validate_ids(asks, "Q", "asks", errors)
    for index, ask in enumerate(asks):
        if not isinstance(ask, dict):
            continue
        label = f"asks[{index}]"
        add(errors, isinstance(ask.get("question"), str) and "?" in ask.get("question", ""), f"{label}.question must be an explicit question")
        refs = ask.get("evidence_ids")
        add(errors, isinstance(refs, list), f"{label}.evidence_ids must be an array")
        if isinstance(refs, list):
            unknown = sorted(set(refs) - fact_ids)
            if unknown:
                errors.append(f"{label} references unknown facts: {', '.join(unknown)}")
        options = ask.get("options", [])
        if not isinstance(options, list):
            errors.append(f"{label}.options must be an array")
            continue
        for option_index, option in enumerate(options):
            option_label = f"{label}.options[{option_index}]"
            if not isinstance(option, dict):
                errors.append(f"{option_label} must be an object")
                continue
            provenance = option.get("provenance")
            add(errors, provenance in {"supplied", "proposed"}, f"{option_label}.provenance is invalid")
            option_refs = option.get("source_fact_ids", [])
            if provenance == "supplied" and not option_refs:
                errors.append(f"{option_label} marked supplied requires source_fact_ids")
            if isinstance(option_refs, list):
                unknown = sorted(set(option_refs) - fact_ids)
                if unknown:
                    errors.append(f"{option_label} references unknown facts: {', '.join(unknown)}")

    gaps = require_list(data, "attack_surface", errors)
    gap_ids = validate_ids(gaps, "G", "attack_surface", errors)
    for index, gap in enumerate(gaps):
        if not isinstance(gap, dict):
            continue
        label = f"attack_surface[{index}]"
        add(errors, gap.get("risk") in RISKS, f"{label}.risk is invalid")
        refs = gap.get("evidence_ids")
        add(errors, isinstance(refs, list), f"{label}.evidence_ids must be an array")
        if isinstance(refs, list):
            unknown = sorted(set(refs) - fact_ids)
            if unknown:
                errors.append(f"{label} references unknown facts: {', '.join(unknown)}")
        add(errors, isinstance(gap.get("minimum_repair"), str) and bool(gap.get("minimum_repair", "").strip()), f"{label}.minimum_repair is required")

    action_ids: set[str] = set()
    continuity = data.get("continuity", {})
    if not isinstance(continuity, dict):
        errors.append("continuity must be an object")
    else:
        actions = continuity.get("previous_actions", [])
        if not isinstance(actions, list):
            errors.append("continuity.previous_actions must be an array")
        else:
            action_ids = validate_ids(actions, "A", "continuity.previous_actions", errors)
            for index, action in enumerate(actions):
                if not isinstance(action, dict):
                    continue
                label = f"continuity.previous_actions[{index}]"
                add(errors, action.get("status") in ACTION_STATUSES, f"{label}.status is invalid")
                if action.get("status") in {"blocked", "dropped-with-reason"}:
                    add(errors, isinstance(action.get("reason"), str) and bool(action.get("reason", "").strip()), f"{label}.reason is required for this status")
                validate_source(action, label, errors)

    derived = data.get("derived_numbers", [])
    if not isinstance(derived, list):
        errors.append("derived_numbers must be an array")
    else:
        fact_by_id = {fact.get("id"): fact for fact in facts if isinstance(fact, dict) and isinstance(fact.get("id"), str)}
        for index, item in enumerate(derived):
            label = f"derived_numbers[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label} must be an object")
                continue
            kind = item.get("kind")
            add(errors, kind in {"calculation", "presentation_structure"}, f"{label}.kind is invalid")
            add(errors, isinstance(item.get("unit"), str) and bool(item.get("unit", "").strip()), f"{label}.unit is required")
            if kind == "calculation":
                operation = item.get("operation")
                operands = item.get("operands")
                add(errors, operation in {"add", "subtract"}, f"{label}.operation is invalid")
                add(errors, isinstance(operands, list) and len(operands) >= 2, f"{label}.operands must contain at least two measurement references")
                if operation == "subtract" and isinstance(operands, list) and len(operands) != 2:
                    errors.append(f"{label}.subtract requires exactly two operands")
                values: list[Decimal] = []
                operand_units: list[str] = []
                if isinstance(operands, list):
                    for operand_index, operand in enumerate(operands):
                        operand_label = f"{label}.operands[{operand_index}]"
                        if not isinstance(operand, dict):
                            errors.append(f"{operand_label} must be an object")
                            continue
                        fact_id = operand.get("fact_id")
                        measurement_index = operand.get("measurement_index")
                        if fact_id not in fact_ids:
                            errors.append(f"{operand_label} references unknown fact: {fact_id}")
                            continue
                        fact = fact_by_id.get(fact_id, {})
                        measurements = fact.get("measurements", []) if isinstance(fact, dict) else []
                        if not isinstance(measurement_index, int) or isinstance(measurement_index, bool) or measurement_index < 0 or measurement_index >= len(measurements):
                            errors.append(f"{operand_label}.measurement_index is out of range")
                            continue
                        measurement = measurements[measurement_index]
                        try:
                            values.append(Decimal(str(measurement.get("value", "")).replace(",", "")))
                        except (InvalidOperation, AttributeError):
                            errors.append(f"{operand_label} references a non-numeric measurement")
                            continue
                        operand_units.append(str(measurement.get("unit", "")))
                if values and len(values) == len(operands or []) and operation in {"add", "subtract"}:
                    if len(set(operand_units)) != 1 or item.get("unit") != operand_units[0]:
                        errors.append(f"{label}.unit must exactly match same-unit add/subtract operands")
                    expected = sum(values, Decimal("0")) if operation == "add" else values[0] - values[1]
                    try:
                        declared = Decimal(str(item.get("token", "")).rstrip("%").replace(",", ""))
                    except InvalidOperation:
                        errors.append(f"{label}.token is not a recomputable decimal")
                    else:
                        if declared != expected:
                            errors.append(f"{label}.token {declared} does not equal recomputed {operation} result {expected}")
            source_fields = item.get("source_fields", [])
            if kind == "presentation_structure":
                add(errors, isinstance(source_fields, list) and "meeting.time_budget_min" in source_fields, f"{label}.source_fields must include meeting.time_budget_min")
                add(errors, isinstance(meeting, dict) and "time_budget_min" in meeting, f"{label} requires meeting.time_budget_min")
            add(errors, isinstance(item.get("expression"), str) and bool(item.get("expression", "").strip()), f"{label}.expression is required")

    relevance = data.get("relevance")
    add(errors, isinstance(relevance, dict), "relevance must be an object")
    if isinstance(relevance, dict):
        all_known = fact_ids | reasoning_ids | ask_ids | gap_ids | action_ids
        placements: dict[str, str] = {}
        for bucket in ("main", "backup", "omit"):
            refs = relevance.get(bucket)
            if not isinstance(refs, list):
                errors.append(f"relevance.{bucket} must be an array")
                continue
            for ref in refs:
                if ref not in all_known:
                    errors.append(f"relevance.{bucket} references unknown item: {ref}")
                if ref in placements:
                    errors.append(f"relevance item {ref} appears in both {placements[ref]} and {bucket}")
                placements[ref] = bucket
        missing_required = sorted(required_retention - set(relevance.get("main", [])) - set(relevance.get("backup", [])))
        if missing_required:
            errors.append(f"decision-relevant facts marked retention=required cannot be omitted or unplaced: {', '.join(missing_required)}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rms", type=Path, help="Path to RMS JSON")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit machine-readable result")
    args = parser.parse_args()

    try:
        data = json.loads(args.rms.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result = {"status": "failed", "errors": [str(exc)]}
        print(json.dumps(result, ensure_ascii=False) if args.as_json else f"FAILED: {exc}")
        return 1

    errors = validate_rms(data)
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
