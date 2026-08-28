# Advisor-Aware Research Meeting Coach

**Turn messy research progress into a decision-ready advisor meeting.**

[繁體中文](README.zh-TW.md)

![Status: early alpha](https://img.shields.io/badge/status-early%20alpha-f59e0b)
![Version: 0.3.3-alpha](https://img.shields.io/badge/version-0.3.3--alpha-2563eb)
![License: MIT](https://img.shields.io/badge/license-MIT-16a34a)
[![CI](https://github.com/niansia/research-meeting-coach/actions/workflows/ci.yml/badge.svg)](https://github.com/niansia/research-meeting-coach/actions/workflows/ci.yml)

You did a week of research. This Agent Skill helps you decide what is actually worth showing, which claim is not supported yet, what your advisor asked for last time, and the one decision they can help make today.

> Early alpha: deterministic integrity checks pass. No professor-preference, student-learning, exact-question prediction, or superiority claim has been established.

![Before and after: messy notes become an evidence-bounded advisor decision](research-meeting-coach/assets/readme-before-after.svg)

## Before → after in 30 seconds

**Messy notes**

```text
Baseline: 72.3
Compression setup: 65.1
32-frame follow-up: around 70
Early-frame control requested last week: half complete
Draft conclusion: “compression hurts accuracy”
```

**Advisor-aware output**

```text
What changed?       The supplied configurations differ.
Can we claim cause? No. Frame count and token budget remain uncontrolled.
What was unfinished? The advisor-requested control is still partial.
What will be challenged? The causal compression claim.
What should the advisor decide? Equal-frame or equal-token-budget control first?
```

The skill does not polish an unsupported story. It exposes the evidence boundary and turns the meeting into a concrete decision.

## Install

This repository follows the [Agent Skills specification](https://agentskills.io/specification). The portable unit is the `research-meeting-coach/` directory.

### Try the current checkout

Open or clone this repository, give your Agent Skills-compatible client access to `research-meeting-coach/`, and invoke `$research-meeting-coach`. Clients without automatic discovery can read `research-meeting-coach/SKILL.md` directly with its supporting files.

### One-line install

```text
npx skills add niansia/research-meeting-coach --skill research-meeting-coach
```

The `skills` CLI supports GitHub owner/repository sources and multiple agents. The command above was verified against the public repository from a clean temporary Git project on 2026-08-28.

## Try this prompt

```text
Use $research-meeting-coach on these notes and my previous-meeting record.
Prepare a 15-minute advisor meeting. Do not invent facts or completion.
Separate observations from interpretations, rank the reasoning gaps,
and end with one decision my advisor can answer.
```

Start with the self-contained [60-second demo](research-meeting-coach/examples/60-second-demo/README.md):

- [raw notes](research-meeting-coach/examples/60-second-demo/raw-notes.md)
- [previous meeting](research-meeting-coach/examples/60-second-demo/previous-meeting.md)
- [result table](research-meeting-coach/examples/60-second-demo/result.csv)
- [strong generic output](research-meeting-coach/examples/60-second-demo/generic-output.md)
- [advisor-aware output](research-meeting-coach/examples/60-second-demo/advisor-aware-output.md)

Everything in the demo is synthetic.

## Why not use a generic prompt?

A strong generic prompt is already useful—this repository's own development example confirms that. The purpose of this skill is to make the harder safeguards and continuity behavior explicit and testable.

| Generic meeting prompt | Advisor-Aware Research Meeting Coach |
|---|---|
| Organizes the update | Identifies what changes the advisor's decision |
| May turn results into a smooth narrative | Separates observation, interpretation, hypothesis, and proposal |
| Starts fresh each week | Preserves prior advisor actions and unresolved status |
| Produces plausible questions | Ranks reasoning gaps without fake probabilities |
| Relies on the model to preserve numbers | Checks output against RMS and, for text-exact evidence, binds values, units, metric, condition, qualifier, and citation back to the quoted source |
| May infer an advisor persona | Allows personalization only from recorded behavior |
| Usually has no holdout contract | Freezes question themes before post-meeting scoring |

## What it produces

- a one-sentence meeting mission;
- a short opener bounded by the supplied evidence;
- the prior advisor action and its actual status;
- a `Critical / High / Medium / Low` reasoning-gap attack surface;
- one advisor-answerable decision or feedback request;
- a main/backup/omit conversation plan;
- novice coaching: `Changed / Why / Try next time`;
- an optional portable Research Meeting State (RMS) for deterministic validation.

If you already have a weekly lab report, use it as input. This skill adds the advisor-facing critique, ask, rehearsal, personalization, and continuity layer rather than regenerating the report.

## How it works

```text
notes / report / draft
        ↓
typed facts + prior actions
        ↓
evidence boundary + attack surface
        ↓
advisor-ready ask + rehearsal + coaching
        ↓
optional RMS and deterministic integrity gates
```

The runtime entry point is [SKILL.md](research-meeting-coach/SKILL.md). Detailed rules are loaded progressively from `references/`; schemas and scripts make important integrity boundaries inspectable.

## Evaluation status—what is and is not proven

Current executable inventory:

- 15 behavioral/adversarial **case definitions**;
- eight routing-collision cases;
- one three-training-plus-one-holdout longitudinal definition;
- 15 de-identified public retrospective seed records for taxonomy discovery;
- zero formal model-generated runs across the 15 cases;
- zero cross-model runs;
- zero permissioned paired real-meeting cases.

Therefore, “15 tests prove the skill works better” would be false. Static checks establish packaging, schema, provenance, routing, and red/blue invariants—not professor preference or learning outcomes.

The bundled B0/B1/candidate development run is intentionally marked contaminated because the same session developed and exercised the artifacts. It shows that a strong generic prompt already catches the central confound, so this project does not claim generic-prompt superiority.

The [public question seed](research-meeting-coach/evals/public-question-seed/seed-corpus.json) is only for taxonomy discovery. Seven records retrospectively report an actual question, but none has paired pre-meeting material; it cannot be used for recall@K or to lower the real-pilot Go/No-Go gate. See the [collection protocol](research-meeting-coach/evals/public-question-seed/collection-protocol.md) and [discipline analysis](research-meeting-coach/evals/public-question-seed/discipline-analysis.md).

## Validate locally

From the repository root:

```text
python -m pip install -r research-meeting-coach/requirements.txt
python research-meeting-coach/scripts/run_static_evals.py
python research-meeting-coach/scripts/validate_schema_contracts.py
python research-meeting-coach/scripts/validate_rms.py research-meeting-coach/examples/compression-confound/research-meeting-state.json
python research-meeting-coach/scripts/validate_source_grounding.py --rms research-meeting-coach/examples/compression-confound/research-meeting-state.json --source-root research-meeting-coach/examples/compression-confound
python research-meeting-coach/scripts/validate_numeric_closed_world.py --rms research-meeting-coach/examples/compression-confound/research-meeting-state.json --output research-meeting-coach/examples/compression-confound/meeting-brief.md
python research-meeting-coach/scripts/build_release.py --json
```

`validate_schema_contracts.py` is a bundled-fixture contract test. It does not accept an arbitrary user artifact. The user-facing `validate_rms.py` and `validate_advisor_profile.py` each run their published Draft 2020-12 schema first and then their additional semantic invariants, so missing required properties and unexpected properties fail at runtime too. If `jsonschema` is absent, they fail with an installation hint instead of silently running only the semantic subset.

`run_static_evals.py` checks only artifacts carried by the portable release. A Git repository checkout has one additional repository-infrastructure gate:

```text
python validate_repository.py --json
```

That second script checks `.github/workflows/ci.yml`, issue forms, the pull-request template, and the release checklist. It and `.github/` are intentionally absent from the portable Skill ZIP; CI runs both layers.

GitHub Actions runs the deterministic checks and audited release build on Python 3.11 and 3.13 across Linux and Windows. The badge at the top reports the current default-branch workflow state.

<details>
<summary>Deterministic limits</summary>

- `retention=required` protects only evidence already marked as required; it cannot decide what the inventory should have marked.
- A value must be closest to its recognized typed condition. This blocks the tested same-line baseline/compression swap but is not full natural-language entailment.
- For `text_exact` measurements, metric and condition use conservative lexical grounding and the qualifier uses value-local hedge matching. This rejects the tested RMS metadata substitutions but is not ontology matching or full semantic provenance; use manual verification when the source wording is indirect.
- Only English decimal phrases shaped like `seven point two` are rejected. Standalone integer or fraction words such as `seventy` or `a tenth` are not parsed.
- Paraphrased or non-text evidence produces `manual_review_required`, not a machine pass.
- Question-theme scores are valid only against a taxonomy frozen before the meeting.

</details>

## Safe releases

Never ZIP/RAR the working directory directly: `.gitignore` is not a packaging control. Build the public archive with:

```text
python research-meeting-coach/scripts/build_release.py --json
```

The builder defaults to denial outside explicit repository and package roots; excludes local registers, environment files, private/confidential pilot filenames, symlinks, caches, bytecode, nested archives, and distribution folders; scans the completed ZIP for individual Dcard, Reddit, PTT, Threads, and Facebook post URLs plus common credential/private-key patterns; validates CRC; and adds a per-file SHA-256 manifest.

This is a defense against known accidental-release paths, not a general PII detector. A permitted Markdown file can still contain an unrecognized name, institution, platform, or secret format. Inspect the manifest and staged files, use synthetic or explicitly permissioned examples only, and never treat a passing build as consent to publish research material.

## Scope and safety

- No project fact, result, citation, cause, or completion state may be invented.
- Advisor preferences require recorded behavior. Demographics, institution, discipline, and prestige are not personality evidence.
- Likely question themes are preparation aids, not exact predictions or calibrated probabilities.
- This skill does not replace advisor judgment, research ethics review, or the student's responsibility for presented claims.
- It does not publish, contact an advisor, or overwrite prior meeting records without explicit authorization.

## Prior art and contribution boundary

[lab-meeting-report-skill](https://github.com/LikC1606/lab-meeting-report-skill) is a mature evidence-grounded weekly-report workflow; consume that report instead of duplicating it. [Advisor Roaster](https://marketplace.agentscli.com/items/nianbaizy-grad-agent-kit-advisor-roaster) is adjacent for strict-advisor rehearsal. Generic reporting, slide rendering, and broad advisor simulation are not claimed as novel here.

The narrower contribution is behavior-grounded advisor profiles, risk-ranked reasoning gaps, portable RMS validation, meeting continuity, and novice coaching. See [AUDIT_REPORT.md](AUDIT_REPORT.md) for the full collision and red/blue audit.

## Help improve the alpha

- Read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a change.
- Use the Pilot Feedback issue form for de-identified experience—never paste unpublished research or identify an advisor, student, or laboratory.
- Report security or privacy problems privately as described in [SECURITY.md](SECURITY.md).
- See the [community conduct policy](CODE_OF_CONDUCT.md).

The next meaningful milestone is five permissioned, prospectively paired meetings—not more retrospective anecdotes.

## License

MIT. See [LICENSE](LICENSE).
