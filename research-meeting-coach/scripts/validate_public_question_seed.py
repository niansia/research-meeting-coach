#!/usr/bin/env python3
"""Validate the de-identified public-question seed corpus and optional local provenance."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ID_RE = re.compile(r"^PQ\d{3}$")
SOURCE_ID_RE = re.compile(r"^SRC\d{3}$")
FINGERPRINT_RE = re.compile(r"^sha256:[a-f0-9]{64}$")
URL_RE = re.compile(r"https?://", re.IGNORECASE)
PLATFORMS = {"dcard", "reddit", "academia-stackexchange", "other"}
ACCESS_METHODS = {"public-search-index", "public-page-manual"}
TIERS = {"B", "C", "D"}
STAGES = {"undergraduate", "masters", "doctoral", "postdoctoral", "faculty", "unknown"}
BROAD_GROUPS = {"computing-engineering", "life-health", "social-humanities", "mathematics", "unknown"}
DISCIPLINE_BASES = {"self-reported", "post-context", "unknown"}
MEETING_TYPES = {"advisor-meeting", "lab-meeting", "project-meeting", "supervision-meeting", "unknown"}
OBSERVATION_TYPES = {"actual-question", "reported-feedback", "reported-pattern", "community-guidance"}


def add(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(
    corpus: dict[str, Any], taxonomy: dict[str, Any], sources: dict[str, Any] | None = None
) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    records = corpus.get("records")
    add(errors, isinstance(corpus.get("corpus_version"), str) and bool(corpus.get("corpus_version")), "corpus_version is required")
    add(errors, isinstance(corpus.get("collected_on"), str), "collected_on is required")
    add(errors, isinstance(corpus.get("purpose"), str) and bool(corpus.get("purpose")), "purpose is required")
    add(errors, isinstance(corpus.get("claim_boundary"), str) and bool(corpus.get("claim_boundary")), "claim_boundary is required")
    add(errors, isinstance(records, list) and bool(records), "records must be a non-empty array")
    if not isinstance(records, list):
        records = []

    taxonomy_ids = {
        item.get("theme_id")
        for item in taxonomy.get("themes", [])
        if isinstance(item, dict) and isinstance(item.get("theme_id"), str)
    }
    add(errors, bool(taxonomy_ids), "taxonomy must contain theme IDs")

    seen_ids: set[str] = set()
    platform_counts: Counter[str] = Counter()
    tier_counts: Counter[str] = Counter()
    discipline_counts: Counter[str] = Counter()
    observation_counts: Counter[str] = Counter()
    mapped_theme_counts: Counter[str] = Counter()
    candidate_theme_counts: Counter[str] = Counter()
    source_refs: dict[str, str] = {}

    for index, record in enumerate(records):
        label = f"records[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label} must be an object")
            continue
        record_id = record.get("id")
        source_id = record.get("source_id")
        fingerprint = record.get("source_fingerprint")
        add(errors, isinstance(record_id, str) and bool(ID_RE.fullmatch(record_id)), f"{label}.id must match PQ###")
        if isinstance(record_id, str):
            add(errors, record_id not in seen_ids, f"duplicate record id: {record_id}")
            seen_ids.add(record_id)
        add(errors, isinstance(source_id, str) and bool(SOURCE_ID_RE.fullmatch(source_id)), f"{label}.source_id must match SRC###")
        add(errors, isinstance(fingerprint, str) and bool(FINGERPRINT_RE.fullmatch(fingerprint)), f"{label}.source_fingerprint is invalid")
        if isinstance(source_id, str) and isinstance(fingerprint, str):
            prior = source_refs.get(source_id)
            add(errors, prior is None or prior == fingerprint, f"{source_id} has inconsistent fingerprints")
            source_refs[source_id] = fingerprint

        platform = record.get("platform")
        tier = record.get("evidence_tier")
        observation = record.get("observation_type")
        add(errors, platform in PLATFORMS, f"{label}.platform is invalid")
        add(errors, record.get("access_method") in ACCESS_METHODS, f"{label}.access_method is invalid")
        add(errors, tier in TIERS, f"{label}.evidence_tier must be B, C, or D")
        add(errors, record.get("author_stage") in STAGES, f"{label}.author_stage is invalid")
        add(errors, record.get("meeting_type") in MEETING_TYPES, f"{label}.meeting_type is invalid")
        add(errors, observation in OBSERVATION_TYPES, f"{label}.observation_type is invalid")
        add(errors, record.get("paired_pre_meeting_material") is False, f"{label} must remain unpaired")

        if isinstance(platform, str):
            platform_counts[platform] += 1
        if isinstance(tier, str):
            tier_counts[tier] += 1
        if isinstance(observation, str):
            observation_counts[observation] += 1
        if tier == "D":
            add(errors, observation == "community-guidance", f"{label}: Tier D must be community-guidance")
        if observation == "actual-question":
            add(errors, tier == "B", f"{label}: actual-question must be Tier B")

        discipline = record.get("discipline")
        if not isinstance(discipline, dict):
            errors.append(f"{label}.discipline must be an object")
        else:
            group = discipline.get("broad_group")
            add(errors, group in BROAD_GROUPS, f"{label}.discipline.broad_group is invalid")
            add(errors, isinstance(discipline.get("label"), str) and bool(discipline.get("label")), f"{label}.discipline.label is required")
            add(errors, discipline.get("basis") in DISCIPLINE_BASES, f"{label}.discipline.basis is invalid")
            if isinstance(group, str):
                discipline_counts[group] += 1

        paraphrase = record.get("paraphrase")
        add(errors, isinstance(paraphrase, str) and len(paraphrase) >= 20, f"{label}.paraphrase is too short")
        if isinstance(paraphrase, str):
            add(errors, not URL_RE.search(paraphrase), f"{label}.paraphrase contains a URL")

        mapped = record.get("mapped_theme_ids")
        candidates = record.get("candidate_theme_ids")
        add(errors, isinstance(mapped, list), f"{label}.mapped_theme_ids must be an array")
        add(errors, isinstance(candidates, list), f"{label}.candidate_theme_ids must be an array")
        if isinstance(mapped, list):
            add(errors, len(mapped) == len(set(mapped)), f"{label}.mapped_theme_ids contains duplicates")
            for theme_id in mapped:
                add(errors, theme_id in taxonomy_ids, f"{label} references unknown frozen theme {theme_id}")
                if isinstance(theme_id, str):
                    mapped_theme_counts[theme_id] += 1
        if isinstance(candidates, list):
            add(errors, len(candidates) == len(set(candidates)), f"{label}.candidate_theme_ids contains duplicates")
            for theme_id in candidates:
                add(errors, isinstance(theme_id, str) and bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", theme_id)), f"{label} has invalid candidate theme")
                add(errors, theme_id not in taxonomy_ids, f"{label}: candidate theme already exists in the frozen taxonomy")
                if isinstance(theme_id, str):
                    candidate_theme_counts[theme_id] += 1

        privacy = record.get("privacy")
        if not isinstance(privacy, dict):
            errors.append(f"{label}.privacy must be an object")
        else:
            add(errors, privacy.get("username_stored") is False, f"{label} stores a username")
            add(errors, privacy.get("direct_quote_stored") is False, f"{label} stores a direct quote")
            add(errors, privacy.get("sensitive_detail_excluded") is True, f"{label} did not confirm sensitive-detail exclusion")

        forbidden_fields = {"url", "username", "author", "direct_quote", "institution"} & set(record)
        add(errors, not forbidden_fields, f"{label} contains forbidden public fields: {sorted(forbidden_fields)}")

    if sources is not None:
        source_items = sources.get("sources") if isinstance(sources, dict) else None
        add(errors, isinstance(source_items, list), "sources.sources must be an array")
        local_map: dict[str, str] = {}
        if isinstance(source_items, list):
            for index, source in enumerate(source_items):
                label = f"sources[{index}]"
                if not isinstance(source, dict):
                    errors.append(f"{label} must be an object")
                    continue
                source_id = source.get("source_id")
                url = source.get("url")
                add(errors, isinstance(source_id, str) and bool(SOURCE_ID_RE.fullmatch(source_id)), f"{label}.source_id is invalid")
                add(errors, isinstance(url, str) and bool(URL_RE.match(url)), f"{label}.url is invalid")
                if isinstance(source_id, str) and isinstance(url, str):
                    add(errors, source_id not in local_map, f"duplicate local source id: {source_id}")
                    local_map[source_id] = "sha256:" + hashlib.sha256(url.encode("utf-8")).hexdigest()
        add(errors, set(local_map) == set(source_refs), "local source IDs do not exactly match public source IDs")
        for source_id, fingerprint in source_refs.items():
            add(errors, local_map.get(source_id) == fingerprint, f"URL fingerprint mismatch for {source_id}")

    summary = {
        "status": "passed" if not errors else "failed",
        "record_count": len(records),
        "paired_tier_a_count": 0,
        "platform_counts": dict(sorted(platform_counts.items())),
        "evidence_tier_counts": dict(sorted(tier_counts.items())),
        "discipline_counts": dict(sorted(discipline_counts.items())),
        "observation_counts": dict(sorted(observation_counts.items())),
        "mapped_theme_counts": dict(sorted(mapped_theme_counts.items())),
        "candidate_theme_counts": dict(sorted(candidate_theme_counts.items())),
        "local_provenance_checked": sources is not None,
    }
    return summary, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", required=True, type=Path)
    parser.add_argument("--taxonomy", required=True, type=Path)
    parser.add_argument("--sources", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        corpus = load_json(args.corpus)
        taxonomy = load_json(args.taxonomy)
        sources = load_json(args.sources) if args.sources else None
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "failed", "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        return 1

    summary, errors = validate(corpus, taxonomy, sources)
    if errors:
        summary["errors"] = errors
    if args.json or errors:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"{summary['status'].upper()}: {summary['record_count']} public seed records")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
