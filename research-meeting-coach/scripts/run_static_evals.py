#!/usr/bin/env python3
"""Run deterministic blue-team and red-team checks for the bundled skill."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

from validate_numeric_closed_world import validate as validate_numbers
from validate_advisor_profile import validate_profile
from validate_advisor_profile_grounding import validate_profile_grounding
from validate_rms import validate_rms
from validate_source_grounding import approximation_attached, validate_grounding
from compare_outputs import summarize as summarize_comparison
from build_release import (
    is_allowed_package_path,
    is_denied as release_path_is_denied,
    sensitive_post_urls,
    sensitive_secret_types,
)
from score_question_themes import score as score_question_themes
from validate_public_question_seed import validate as validate_public_question_seed


ROOT = Path(__file__).resolve().parent.parent
REQUIRED_CASE_KEYS = {"id", "title", "category", "request", "source_material", "must_include", "must_not_include", "expected_route"}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    errors: list[str] = []
    readme_paths = (
        ROOT.parent / "README.md",
        ROOT.parent / "README.zh-TW.md",
        ROOT.parent / "README.zh-CN.md",
    )
    for package_file in (
        *readme_paths,
        ROOT.parent / "LICENSE",
        ROOT.parent / "CONTRIBUTING.md",
        ROOT.parent / "SECURITY.md",
        ROOT.parent / "CODE_OF_CONDUCT.md",
        ROOT / "VERSION",
        ROOT / "requirements.txt",
        ROOT / "assets" / "deck-outline-template.md",
        ROOT / "assets" / "icon.svg",
        ROOT / "assets" / "readme-before-after.svg",
    ):
        if not package_file.is_file() or package_file.stat().st_size == 0:
            fail(errors, f"required publishable package file is missing or empty: {package_file}")
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if (
        version != "0.3.4-alpha"
        or f'version: "{version}"' not in (ROOT / "SKILL.md").read_text(encoding="utf-8")
        or any(version not in path.read_text(encoding="utf-8") for path in readme_paths)
    ):
        fail(errors, "VERSION, SKILL.md metadata, and trilingual README status are inconsistent")

    demo_dir = ROOT / "examples" / "60-second-demo"
    for demo_file in ("README.md", "raw-notes.md", "previous-meeting.md", "result.csv", "generic-output.md", "advisor-aware-output.md"):
        path = demo_dir / demo_file
        if not path.is_file() or path.stat().st_size == 0:
            fail(errors, f"60-second demo artifact is missing or empty: {demo_file}")
    case_paths = sorted((ROOT / "evals" / "cases").glob("E*.json"))
    if len(case_paths) < 15:
        fail(errors, f"expected at least 15 evaluation case definitions, found {len(case_paths)}")

    ids: set[str] = set()
    categories: set[str] = set()
    routes: set[str] = set()
    for path in case_paths:
        try:
            case = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            fail(errors, f"{path.name}: {exc}")
            continue
        missing = REQUIRED_CASE_KEYS - set(case)
        if missing:
            fail(errors, f"{path.name}: missing keys {sorted(missing)}")
        case_id = case.get("id")
        if case_id in ids:
            fail(errors, f"duplicate evaluation id {case_id}")
        ids.add(case_id)
        categories.add(case.get("category"))
        routes.add(case.get("expected_route"))
        if not case.get("must_include") or not case.get("must_not_include"):
            fail(errors, f"{path.name}: behavioral expectations cannot be empty")

    if "route-elsewhere" not in routes:
        fail(errors, "routing collision case is missing")
    for required in {"progress", "proposal", "mixed", "novice-coaching", "actual-question", "evidence", "continuity", "advisor-profile", "sparse", "routing"}:
        if required not in categories:
            fail(errors, f"missing adversarial category: {required}")

    routing_path = ROOT / "evals" / "routing-cases.json"
    routing_cases = json.loads(routing_path.read_text(encoding="utf-8"))
    if len(routing_cases) < 8:
        fail(errors, "routing collision corpus must contain at least eight cases")
    routing_labels = {item.get("expected") for item in routing_cases if isinstance(item, dict)}
    if routing_labels != {"use-skill", "route-elsewhere"}:
        fail(errors, "routing corpus must cover use-skill and route-elsewhere")

    longitudinal_path = ROOT / "evals" / "longitudinal" / "L01-advisor-baseline-preference.json"
    longitudinal = json.loads(longitudinal_path.read_text(encoding="utf-8"))
    weeks = longitudinal.get("weeks", []) if isinstance(longitudinal, dict) else []
    if len(weeks) != 4:
        fail(errors, "longitudinal case must contain four meetings")
    elif [week.get("role") for week in weeks] != ["profile-training", "profile-training", "profile-training", "profile-holdout"]:
        fail(errors, "longitudinal case must use three training meetings followed by one holdout")
    elif weeks[-1].get("recorded_advisor_behavior") is not None:
        fail(errors, "held-out meeting must not contain feedback before generation")

    rms_path = ROOT / "examples" / "compression-confound" / "research-meeting-state.json"
    brief_path = ROOT / "examples" / "compression-confound" / "meeting-brief.md"
    rms = json.loads(rms_path.read_text(encoding="utf-8"))
    brief = brief_path.read_text(encoding="utf-8")

    development_dir = ROOT / "evals" / "development-run"
    for development_file in ("metadata.json", "B0-output.md", "B1-output.md", "candidate-output.md", "baseline-report.md"):
        path = development_dir / development_file
        if not path.is_file() or path.stat().st_size == 0:
            fail(errors, f"development baseline artifact is missing or empty: {development_file}")
    candidate_output = (development_dir / "candidate-output.md").read_text(encoding="utf-8")
    development_metadata = json.loads((development_dir / "metadata.json").read_text(encoding="utf-8"))
    frozen_files = {
        "source": ROOT / "examples" / "compression-confound" / "raw-notes.md",
        "prompts": ROOT / "evals" / "baseline-prompts.md",
        "B0": development_dir / "B0-output.md",
        "B1": development_dir / "B1-output.md",
        "candidate": development_dir / "candidate-output.md"
    }
    for label, path in frozen_files.items():
        observed_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        expected_hash = development_metadata.get("sha256", {}).get(label)
        if observed_hash != expected_hash:
            fail(errors, f"frozen development artifact hash mismatch: {label}")

    blue_errors = validate_rms(rms)
    if blue_errors:
        fail(errors, f"blue-team RMS failed: {blue_errors}")
    rms_schema_mutations = []
    missing_action_item = copy.deepcopy(rms)
    del missing_action_item["continuity"]["previous_actions"][0]["item"]
    rms_schema_mutations.append(("action missing item", missing_action_item))
    missing_reasoning_text = copy.deepcopy(rms)
    del missing_reasoning_text["reasoning_items"][0]["text"]
    rms_schema_mutations.append(("reasoning item missing text", missing_reasoning_text))
    missing_attack_gap = copy.deepcopy(rms)
    del missing_attack_gap["attack_surface"][0]["gap"]
    rms_schema_mutations.append(("attack-surface item missing gap", missing_attack_gap))
    unexpected_rms_root = copy.deepcopy(rms)
    unexpected_rms_root["unexpected"] = "x"
    rms_schema_mutations.append(("RMS unexpected root property", unexpected_rms_root))
    for mutation_label, mutation in rms_schema_mutations:
        mutation_errors = validate_rms(mutation)
        if not mutation_errors or not any(error.startswith("schema ") for error in mutation_errors):
            fail(errors, f"Python RMS validator diverged from published schema: {mutation_label}")
    grounding_errors, grounding_warnings = validate_grounding(rms, rms_path.parent)
    if grounding_errors or grounding_warnings:
        fail(errors, f"blue-team source grounding failed or requires manual review: errors={grounding_errors}, warnings={grounding_warnings}")
    poisoned_metric = copy.deepcopy(rms)
    poisoned_metric["facts"][0]["measurements"][0]["metric"] = "latency"
    if not validate_grounding(poisoned_metric, rms_path.parent)[0]:
        fail(errors, "red-team RMS metric metadata poisoning was accepted by source grounding")
    poisoned_condition = copy.deepcopy(rms)
    poisoned_condition["facts"][0]["measurements"][0]["condition"] = "new method"
    if not validate_grounding(poisoned_condition, rms_path.parent)[0]:
        fail(errors, "red-team RMS condition metadata poisoning was accepted by source grounding")
    poisoned_qualifier = copy.deepcopy(rms)
    poisoned_qualifier["facts"][2]["measurements"][1]["qualifier"] = "exact"
    if not validate_grounding(poisoned_qualifier, rms_path.parent)[0]:
        fail(errors, "red-team approximate source qualifier promoted to exact in RMS")
    for approximate_phrase in ("around 70", "about 70", "approximately 70", "roughly 70", "約 70", "大約 70"):
        if not approximation_attached(approximate_phrase, "70"):
            fail(errors, f"source qualifier grounding missed supported hedge phrase: {approximate_phrase}")
    if approximation_attached("32-frame run accuracy returned to around 70", "32"):
        fail(errors, "source qualifier grounding attached a hedge to the wrong value")
    numeric_errors = validate_numbers(rms, brief)
    if numeric_errors:
        fail(errors, f"blue-team brief failed numeric gate: {numeric_errors}")
    candidate_numeric_errors = validate_numbers(rms, candidate_output)
    if candidate_numeric_errors:
        fail(errors, f"development candidate output failed numeric gate: {candidate_numeric_errors}")

    timed_rms = copy.deepcopy(rms)
    timed_rms["derived_numbers"].append({
        "token": "2",
        "kind": "presentation_structure",
        "expression": "Allocate two minutes from the supplied meeting time budget.",
        "unit": "min",
        "source_fields": ["meeting.time_budget_min"]
    })
    timed_output = brief + "\nApproximate discussion time: 2 min.\n"
    if validate_rms(timed_rms) or validate_numbers(timed_rms, timed_output):
        fail(errors, "blue-team meeting-time allocation failed")
    if not validate_numbers(timed_rms, brief + "\nApproximate discussion time: 2 seconds from the meeting budget.\n"):
        fail(errors, "red-team presentation-time unit substitution was accepted")
    if not validate_numbers(rms, brief + "\nThe meeting budget is 15 seconds.\n"):
        fail(errors, "red-team source time-budget unit substitution was accepted")

    source_map_output = brief + "\n| [F01] | Baseline accuracy was 72.3 | raw-notes.md:7 |\n"
    if validate_numbers(rms, source_map_output):
        fail(errors, "blue-team numeric source locator failed")

    profile_path = ROOT / "evals" / "fixtures" / "advisor-profile-valid.json"
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    profile_errors = validate_profile(profile)
    if profile_errors:
        fail(errors, f"blue-team advisor profile failed: {profile_errors}")
    profile_schema_mutations = []
    missing_profile_value = copy.deepcopy(profile)
    del missing_profile_value["advisor_profile"]["opening_preference"]["value"]
    profile_schema_mutations.append(("advisor profile dimension missing value", missing_profile_value))
    missing_evidence_note = copy.deepcopy(profile)
    del missing_evidence_note["advisor_profile"]["opening_preference"]["evidence"][0]["note"]
    profile_schema_mutations.append(("advisor evidence missing note", missing_evidence_note))
    unexpected_profile_root = copy.deepcopy(profile)
    unexpected_profile_root["unexpected"] = "x"
    profile_schema_mutations.append(("advisor profile unexpected root property", unexpected_profile_root))
    for mutation_label, mutation in profile_schema_mutations:
        mutation_errors = validate_profile(mutation)
        if not mutation_errors or not any(error.startswith("schema ") for error in mutation_errors):
            fail(errors, f"Python advisor-profile validator diverged from published schema: {mutation_label}")
    profile_grounding_errors, profile_grounding_warnings = validate_profile_grounding(profile, profile_path.parent)
    if profile_grounding_errors or profile_grounding_warnings:
        fail(errors, f"blue-team advisor profile grounding failed: errors={profile_grounding_errors}, warnings={profile_grounding_warnings}")

    bad_ref = copy.deepcopy(rms)
    bad_ref["reasoning_items"][0]["evidence_ids"] = ["F99"]
    if not validate_rms(bad_ref):
        fail(errors, "red-team unknown fact reference was accepted")

    hidden_negative = copy.deepcopy(rms)
    hidden_negative["relevance"]["main"].remove("F03")
    hidden_negative["relevance"]["omit"].append("F03")
    if not validate_rms(hidden_negative):
        fail(errors, "red-team omission of required-retention evidence was accepted")

    invented_option = copy.deepcopy(rms)
    invented_option["asks"][0]["options"][0] = {
        "label": "claimed user option",
        "provenance": "supplied",
        "source_fact_ids": []
    }
    if not validate_rms(invented_option):
        fail(errors, "red-team unsupported supplied option was accepted")

    hallucinated_number = brief + "\nThe professor has an 87% chance of asking this.\n"
    if not validate_numbers(rms, hallucinated_number):
        fail(errors, "red-team hallucinated percentage was accepted")

    budget_as_result = brief + "\nThe model accuracy was 15 [F01].\n"
    if not validate_numbers(rms, budget_as_result):
        fail(errors, "red-team meeting budget reused as a research result was accepted")

    swapped_citations = brief.replace("72.3 [F01]", "72.3 [F02]").replace("65.1 [F02]", "65.1 [F01]")
    if not validate_numbers(rms, swapped_citations):
        fail(errors, "red-team swapped numeric citations were accepted")

    correctly_bound_conditions = "The baseline accuracy was 72.3 [F01], while the compression setup accuracy was 65.1 [F02]."
    if validate_numbers(rms, correctly_bound_conditions):
        fail(errors, "blue-team two-condition numeric sentence was rejected")
    swapped_conditions = "The compression setup accuracy was 72.3 [F01], while the baseline accuracy was 65.1 [F02]."
    if not validate_numbers(rms, swapped_conditions):
        fail(errors, "red-team swapped measurement conditions were accepted")

    fabricated_rms = copy.deepcopy(rms)
    fabricated_rms["facts"][0]["statement"] = "Fabricated project result was 72.3."
    fabricated_grounding_errors, _ = validate_grounding(fabricated_rms, rms_path.parent)
    if not fabricated_grounding_errors:
        fail(errors, "red-team fabricated RMS statement with a real locator was accepted")

    unit_rms = copy.deepcopy(rms)
    unit_rms["facts"].append({
        "id": "F08",
        "evidence_class": "project_fact",
        "fact_type": "measurement",
        "statement": "Latency was 10 ms.",
        "source": {"locator": "synthetic.md:1", "verification": "text_exact", "quote": "Latency was 10 ms."},
        "measurements": [{"metric": "latency", "value": "10", "unit": "ms", "condition": "test", "qualifier": "exact"}]
    })
    if validate_numbers(unit_rms, "Test latency was 10 ms [F08]."):
        fail(errors, "blue-team typed measurement unit was rejected")
    if not validate_numbers(unit_rms, "Test latency was 10 seconds [F08]."):
        fail(errors, "red-team measurement unit substitution was accepted")

    calculation_rms = copy.deepcopy(rms)
    calculation_rms["derived_numbers"].append({
        "token": "7.2",
        "kind": "calculation",
        "expression": "72.3 - 65.1",
        "unit": "unitless",
        "operation": "subtract",
        "operands": [
            {"fact_id": "F01", "measurement_index": 0},
            {"fact_id": "F02", "measurement_index": 0}
        ]
    })
    if validate_numbers(calculation_rms, "Derived difference: 7.2 [F01] [F02]."):
        fail(errors, "blue-team calculation with every operand citation was rejected")
    if not validate_numbers(calculation_rms, "Derived difference: 7.2 [F01]."):
        fail(errors, "red-team calculation with only one operand citation was accepted")
    wrong_calculation = copy.deepcopy(calculation_rms)
    wrong_calculation["derived_numbers"][-1]["token"] = "99.9"
    if not validate_rms(wrong_calculation) or not validate_numbers(wrong_calculation, "Derived difference: 99.9 [F01] [F02]."):
        fail(errors, "red-team arithmetically incorrect declared calculation was accepted")

    if validate_numbers(rms, "Baseline accuracy was 72.3 on the baseline [F01]."):
        fail(errors, "blue-team natural unitless prose was rejected")
    if not validate_numbers(rms, "Our new method achieved 72.3 [F01]."):
        fail(errors, "red-team measurement condition substitution was accepted")
    if validate_numbers(rms, "The 32-frame run returned to around 70 [F03]."):
        fail(errors, "blue-team approximate qualifier was rejected")
    if not validate_numbers(rms, "The 32-frame run returned to 70 [F03]."):
        fail(errors, "red-team approximate measurement promoted to exact was accepted")
    if not validate_numbers(rms, "The reported drop was seven point two points [F01] [F02]."):
        fail(errors, "red-team spelled-out decimal bypass was accepted")

    manual_rms = copy.deepcopy(rms)
    manual_rms["facts"][0]["statement"] = "Baseline accuracy was 82.3."
    manual_rms["facts"][0]["measurements"][0]["value"] = "82.3"
    manual_rms["facts"][0]["source"] = {
        "locator": "manual-observation",
        "verification": "manual",
        "verification_note": "Non-text evidence has not yet been checked by a reviewer."
    }
    manual_findings = validate_numbers(manual_rms, "Baseline accuracy was 82.3 [F01].")
    if not manual_findings or any(item.get("severity") != "warning" for item in manual_findings):
        fail(errors, "manual numeric evidence was not downgraded to manual-review warning")

    impression_profile = copy.deepcopy(profile)
    impression_profile["advisor_profile"]["opening_preference"]["confidence"] = "high"
    impression_profile["advisor_profile"]["opening_preference"]["evidence"][0]["type"] = "student_impression"
    if not validate_profile(impression_profile):
        fail(errors, "red-team high-confidence student impression was accepted")

    demographic_profile = copy.deepcopy(profile)
    demographic_profile["advisor_profile"]["nationality_preference"] = demographic_profile["advisor_profile"].pop("opening_preference")
    if not validate_profile(demographic_profile):
        fail(errors, "red-team demographic advisor-profile dimension was accepted")

    discipline_profile = copy.deepcopy(profile)
    discipline_profile["advisor_profile"]["discipline_preference"] = discipline_profile["advisor_profile"].pop("opening_preference")
    if not validate_profile(discipline_profile):
        fail(errors, "red-team discipline stereotype dimension was accepted")

    fake_profile_source = copy.deepcopy(profile)
    fake_profile_source["advisor_profile"]["opening_preference"]["evidence"][0]["source"]["locator"] = "missing.md:999"
    fake_profile_errors, _ = validate_profile_grounding(fake_profile_source, profile_path.parent)
    if not fake_profile_errors:
        fail(errors, "red-team nonexistent advisor evidence locator was accepted")

    synthetic_ratings = json.loads((ROOT / "evals" / "fixtures" / "human-evaluation-synthetic.json").read_text(encoding="utf-8"))
    comparison_summary, comparison_errors = summarize_comparison(synthetic_ratings)
    if comparison_errors or comparison_summary.get("blind", {}).get("candidate_preference_rate_decisive") != 1.0:
        fail(errors, "comparison aggregator smoke test failed")
    mixed_blinding = copy.deepcopy(synthetic_ratings)
    mixed_blinding["comparisons"] = []
    template = synthetic_ratings["comparisons"][0]
    for index in range(2):
        item = copy.deepcopy(template)
        item.update({"reviewer_id": f"blind-{index}", "blind": True, "preference": "baseline"})
        mixed_blinding["comparisons"].append(item)
    for index in range(8):
        item = copy.deepcopy(template)
        item.update({"reviewer_id": f"non-blind-{index}", "blind": False, "preference": "candidate"})
        mixed_blinding["comparisons"].append(item)
    mixed_summary, mixed_errors = summarize_comparison(mixed_blinding)
    if (
        mixed_errors
        or mixed_summary.get("blind", {}).get("candidate_preference_rate_decisive") != 0.0
        or mixed_summary.get("non_blind", {}).get("candidate_preference_rate_decisive") != 1.0
        or mixed_summary.get("all_ratings_descriptive", {}).get("candidate_preference_rate_decisive") != 0.8
        or mixed_summary.get("headline_metric", {}).get("candidate_preference_rate_decisive") != 0.0
        or "candidate_preference_rate_decisive" in mixed_summary
    ):
        fail(errors, "comparison aggregator mixed blind and non-blind preference metrics")
    invalid_ratings = copy.deepcopy(synthetic_ratings)
    del invalid_ratings["study_id"]
    if not summarize_comparison(invalid_ratings)[1]:
        fail(errors, "comparison aggregator accepted a schema-required metadata omission")

    question_fixture = json.loads((ROOT / "evals" / "question-themes" / "E15-synthetic.json").read_text(encoding="utf-8"))
    question_summary, question_errors = score_question_themes(question_fixture, 2)
    if question_errors or question_summary.get("theme_recall_at_k") != 1.0 or question_fixture.get("synthetic") is not True:
        fail(errors, "synthetic question-theme scorer smoke test failed")
    invalid_question_fixture = copy.deepcopy(question_fixture)
    invalid_question_fixture["predictions"][0].pop("risk")
    invalid_question_fixture["predictions"][0]["rank"] = 0
    if not score_question_themes(invalid_question_fixture, 2)[1]:
        fail(errors, "question-theme scorer accepted invalid rank and missing risk")

    public_seed_path = ROOT / "evals" / "public-question-seed" / "seed-corpus.json"
    taxonomy_path = ROOT / "evals" / "question-theme-taxonomy.json"
    public_seed = json.loads(public_seed_path.read_text(encoding="utf-8"))
    frozen_taxonomy = json.loads(taxonomy_path.read_text(encoding="utf-8"))
    public_seed_summary, public_seed_errors = validate_public_question_seed(public_seed, frozen_taxonomy)
    if public_seed_errors or public_seed_summary.get("record_count") != 15 or public_seed_summary.get("paired_tier_a_count") != 0:
        fail(errors, f"public question seed corpus failed: {public_seed_errors}")

    leaked_public_seed = copy.deepcopy(public_seed)
    leaked_public_seed["records"][0]["url"] = "https://example.invalid/private-source"
    leaked_public_seed["records"][0]["privacy"]["username_stored"] = True
    if not validate_public_question_seed(leaked_public_seed, frozen_taxonomy)[1]:
        fail(errors, "public question seed validator accepted URL and username leakage")

    fake_paired_seed = copy.deepcopy(public_seed)
    fake_paired_seed["records"][0]["evidence_tier"] = "A"
    fake_paired_seed["records"][0]["paired_pre_meeting_material"] = True
    if not validate_public_question_seed(fake_paired_seed, frozen_taxonomy)[1]:
        fail(errors, "public retrospective was accepted as a paired Tier A case")

    drifted_seed = copy.deepcopy(public_seed)
    drifted_seed["records"][0]["mapped_theme_ids"] = ["new-theme-added-after-observation"]
    if not validate_public_question_seed(drifted_seed, frozen_taxonomy)[1]:
        fail(errors, "public seed accepted an unknown frozen-taxonomy mapping")

    local_source_path = ROOT / "evals" / "public-question-seed" / "source-register.local.json"
    if local_source_path.is_file():
        local_sources = json.loads(local_source_path.read_text(encoding="utf-8"))
        _, provenance_errors = validate_public_question_seed(public_seed, frozen_taxonomy, local_sources)
        if provenance_errors:
            fail(errors, f"local public-seed provenance failed: {provenance_errors}")
        tampered_sources = copy.deepcopy(local_sources)
        tampered_sources["sources"][0]["url"] += "?tampered=1"
        if not validate_public_question_seed(public_seed, frozen_taxonomy, tampered_sources)[1]:
            fail(errors, "public seed accepted a tampered source URL fingerprint")

    if not release_path_is_denied(Path("research-meeting-coach/evals/public-question-seed/source-register.local.json")):
        fail(errors, "release filter accepted a local source register")
    if not release_path_is_denied(Path("research-meeting-coach/scripts/__pycache__/validator.cpython-310.pyc")):
        fail(errors, "release filter accepted CPython bytecode")
    if not release_path_is_denied(Path("research-meeting-coach/.env")):
        fail(errors, "release filter accepted an environment file")
    if not release_path_is_denied(Path("research-meeting-coach/real-pilot-case-01.md")):
        fail(errors, "release filter accepted an accidental real-pilot filename")
    if is_allowed_package_path(Path("scratch.md")):
        fail(errors, "release allowlist accepted an unknown package-root file")
    if is_allowed_package_path(Path("private-data"),):
        fail(errors, "release allowlist accepted an unknown package-root directory")
    if not is_allowed_package_path(Path("references/evidence-integrity.md")):
        fail(errors, "release allowlist rejected a documented package directory")
    synthetic_dcard_post = b"https://www.dcard.tw/" + b"f/graduate_school/" + b"p/123456789"
    if not sensitive_post_urls(synthetic_dcard_post):
        fail(errors, "release content scanner missed a Dcard post URL")
    synthetic_reddit_post = b"https://www.reddit.com/" + b"r/PhD/" + b"comments/abcdef/example"
    if not sensitive_post_urls(synthetic_reddit_post):
        fail(errors, "release content scanner missed a Reddit post URL")
    synthetic_ptt_post = b"https://www.ptt.cc/" + b"bbs/graduate/" + b"M.1234567890.A.123.html"
    if not sensitive_post_urls(synthetic_ptt_post):
        fail(errors, "release content scanner missed a PTT post URL")
    synthetic_threads_post = b"https://www.threads.net/" + b"@synthetic/post/" + b"ABC123"
    if not sensitive_post_urls(synthetic_threads_post):
        fail(errors, "release content scanner missed a Threads post URL")
    synthetic_facebook_post = b"https://www.facebook.com/" + b"synthetic/posts/" + b"123456789"
    if not sensitive_post_urls(synthetic_facebook_post):
        fail(errors, "release content scanner missed a Facebook post URL")
    if sensitive_post_urls(b"https://www.dcard.tw/terms"):
        fail(errors, "release content scanner rejected a non-post policy URL")
    if sensitive_post_urls(b"https://www.ptt.cc/"):
        fail(errors, "release content scanner rejected a non-post PTT homepage URL")
    synthetic_openai_key = b"OPENAI_API_KEY=" + b"sk-" + b"proj-" + b"SYNTHETIC1234567890"
    if not sensitive_secret_types(synthetic_openai_key):
        fail(errors, "release content scanner missed an OpenAI-style API key")
    synthetic_github_token = b"GITHUB_TOKEN=" + b"ghp_" + b"ABCDEFGHIJKLMNOPQRSTUVWXYZ123456"
    if not sensitive_secret_types(synthetic_github_token):
        fail(errors, "release content scanner missed a GitHub classic token")
    synthetic_aws_key = b"AWS_ACCESS_KEY_ID=" + b"AKIA" + b"ABCDEFGHIJKLMNOP"
    if not sensitive_secret_types(synthetic_aws_key):
        fail(errors, "release content scanner missed an AWS access key ID")
    if sensitive_secret_types(b"Use the literal prefix sk- only in synthetic documentation."):
        fail(errors, "release content scanner rejected a harmless credential-prefix description")

    if errors:
        print(json.dumps({"status": "failed", "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({
        "status": "passed",
        "case_definition_count": len(case_paths),
        "executed_case_definition_count": 0,
        "cross_model_case_execution_count": 0,
        "development_output_bundle_count": 1,
        "onboarding_demo_count": 1,
        "routing_case_count": len(routing_cases),
        "longitudinal_case_count": 1,
        "public_question_seed_record_count": public_seed_summary.get("record_count"),
        "categories": sorted(categories),
        "checks": [
            "valid RMS accepted",
            "runtime RMS validator enforces the published Draft 2020-12 structure before semantic invariants",
            "exact source locators, quotes, and project-fact spans verified",
            "typed metric, condition, and exact/approximate qualifier metadata grounded to text-exact source quotes",
            "grounded brief accepted",
            "portable trilingual README, policy files, LICENSE, visual assets, example, and frozen development outputs present",
            "self-contained 60-second onboarding demo present",
            "package version metadata is consistent",
            "development source, prompts, and outputs match recorded SHA-256 hashes",
            "meeting-time allocation accepted only when declared from the time budget",
            "meeting-time and presentation-time unit substitution rejected",
            "numeric source locator accepted only in locator context",
            "unknown fact reference rejected",
            "required-retention omission rejected",
            "unsupported supplied option rejected",
            "hallucinated percentage rejected",
            "meeting budget reused as a research result rejected",
            "swapped numeric citations rejected",
            "swapped measurement conditions rejected",
            "measurement unit substitution rejected",
            "derived calculation requires every operand citation",
            "declared calculation result is deterministically recomputed",
            "fabricated RMS statement rejected by exact-source grounding",
            "natural unitless prose accepted without treating ordinary words as units",
            "measurement condition and approximate qualifier substitutions rejected",
            "spelled-out decimal bypass rejected",
            "manual numeric evidence requires manual review",
            "unsupported advisor-profile confidence rejected",
            "demographic advisor-profile dimension rejected",
            "discipline/prestige profile dimensions rejected",
            "advisor-profile evidence locator and quote verified",
            "runtime advisor-profile validator enforces required and additional-property schema boundaries",
            "human-rating comparison aggregator smoke-tested",
            "blind and non-blind human-rating cohorts cannot mix in the headline preference metric",
            "human-rating required metadata enforced",
            "synthetic actual-question theme scorer smoke-tested",
            "question-theme scorer enforces rank/risk constraints",
            "de-identified public question seed corpus validated",
            "public seed URL/username leakage rejected",
            "public retrospective cannot masquerade as paired Tier A",
            "public seed mappings cannot drift beyond the frozen taxonomy",
            "optional local source URL fingerprints verified only when a private register is supplied",
            "release package paths default-deny unknown top-level files and directories",
            "release filter rejects local registers, environment files, private pilot filenames, and CPython bytecode",
            "release content scanner rejects individual Dcard, Reddit, PTT, Threads, and Facebook post URLs",
            "release content scanner rejects common credential and private-key patterns",
            "three-training-plus-one-holdout longitudinal case validated",
            "out-of-scope routing case present"
        ]
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
