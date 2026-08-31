---
name: research-meeting-coach
description: "Add an advisor-facing critique and coaching layer to an existing lab-meeting report, weekly summary, raw notes, or draft. Use when a graduate researcher wants reasoning-gap attack surface, evidence-backed advisor asks, behavior-grounded personalization, rehearsal, or post-meeting continuity. Do not use for generic reporting, paper-only slides, or visual deck production."
license: MIT
metadata:
  version: "0.3.5-alpha"
---

# Research Meeting Coach

Turn unfinished research material into a critique layer an advisor can quickly challenge and act on. Optimize for decision value and student learning, not slide count or narrative polish.

Match the user's language unless they request another. Preserve technical terms, identifiers, units, and citations in their source language.

## Boundaries

Use this skill when the user wants to critique, rehearse, personalize, or follow up an advisor-facing research meeting. The distinguishing task is to expose the current evidence boundary, likely reasoning gaps, and a concrete decision or feedback request.

Route elsewhere when the primary request is:

- a generic weekly archive or lab report with no advisor-decision or coaching need;
- a paper-only summary, literature review, conference talk, or thesis defense;
- visual design, PPTX rendering, or slide beautification;
- project management or persistent lab-state infrastructure.

Prefer an existing lab-meeting report or weekly summary as the input when one exists; do not regenerate it. Add only the advisor-facing critique, ask, rehearsal, personalization, and continuity layer. Raw notes remain acceptable when no report exists. This skill may produce a text deck outline, but it does not render slides.

## Input contract

The required input is a user-scoped body of project evidence: pasted notes or named files containing observations, results, figures, failed attempts, blockers, or prior meeting records. Never expand the source scope silently.

Infer when possible:

- meeting intent: `progress`, `troubleshooting`, `decision`, `proposal`, or `mixed`;
- audience and time budget;
- previous actions and unresolved decisions;
- requested output: brief, critique, rehearsal questions, or post-meeting update;
- coaching depth: concise by default, explanatory for novice users or when requested.

If evidence is thin, emit a gap-first critique rather than padding the package. If there is no usable project evidence at all, request the smallest missing source bundle and stop project-claim drafting.

## Reference routing

- Read [references/meeting-intents.md](references/meeting-intents.md) when routing or mixing meeting intents.
- Read [references/evidence-integrity.md](references/evidence-integrity.md) whenever the material contains empirical results, numbers, figures, papers, conflicts, or causal language.
- Read [references/reasoning-and-attack-surface.md](references/reasoning-and-attack-surface.md) when critiquing claims, preparing likely questions, or designing an ask.
- Read [references/advisor-profile.md](references/advisor-profile.md) only when advisor history or explicit preferences are supplied, or when updating a profile after a meeting.
- Read [references/novice-coaching.md](references/novice-coaching.md) when the user is new, asks why content changed, wants rehearsal, or requests skill-building feedback.
- Read [references/meeting-rubric.md](references/meeting-rubric.md) for a formal audit, comparison, or evaluation. Treat its weights as unvalidated until human calibration exists.

## Workflow

### 1. Build a closed-world evidence inventory

Identify every decision-relevant observation, measurement, artifact, failed attempt, external-literature statement, and missing input. Assign stable internal IDs such as `F01`. Preserve source paths, line locators, verification modes, and exact quotes when the input is text. Measurements must carry a typed value, unit, condition, and exact/approximate qualifier; for `text_exact` evidence, metric and condition words plus any approximation hedge must be present in the quoted source. Use manual verification explicitly when typed metadata cannot be checked as an exact text span. Do not invent values, experimental details, citations, causes, priorities, or completion states.

Separate project evidence from external literature. A paper can support a prior, mechanism candidate, or experiment proposal; it cannot prove the user's project result.

### 2. Restore continuity

When prior actions exist, preserve their wording and classify each as `done`, `partial`, `blocked`, `dropped-with-reason`, or `unknown`. Closing an action requires direct completion evidence; a nearby favorable result is insufficient. Surface any prior advisor request that disappeared from the current update.

### 3. Route the meeting intent

Select one primary intent and optional secondary intent. Use the intent to control emphasis; do not force a fixed deck length or a background-method-results template.

### 4. Build the reasoning graph

For each central item, separate:

- observation: what was directly seen;
- evidence: which supplied source supports it;
- interpretation: the current reading of that evidence;
- uncertainty: what remains unresolved or what alternative is still live;
- decision: what feedback, choice, or next experiment would move the work forward.

An interpretation is not a conclusion merely because it sounds plausible. Preserve negative, failed, and conflicting evidence whenever it changes interpretation, resources, or next actions.

### 5. Filter by information value

Put an item in the main conversation only if it changes the advisor's understanding of research state, supports a consequential claim, or enables feedback or a decision. Move useful detail to backup. Omit activity logs and background that serve none of those functions.

### 6. Audit the attack surface

Test the central claims for missing baselines, controls, confounds, definitions, units, sample details, comparison fairness, replication, alternative explanations, contradictions, and evidence provenance. Use `Critical`, `High`, `Medium`, or `Low` with an explicit reason. Never attach a numeric probability to a likely advisor question unless calibrated holdout data were supplied.

### 7. Apply advisor fit only from evidence

Use explicit feedback and repeated observed behavior to adjust order, detail depth, backup preparation, and ask style. Keep confidence and provenance. Without advisor evidence, use the general rubric and state that no personalization was applied. Never infer personality from nationality, region, institution, age, gender, discipline stereotype, or prestige.

### 8. Compile the meeting package

Produce only supported sections, in this order:

1. **Meeting Mission** - one sentence naming the state change and desired feedback or decision.
2. **Opener** - a roughly 30-second script: research question, most important state change, uncertainty, and today's ask.
3. **Continuity** - prior actions and status, only when history exists.
4. **Top Findings** - normally one to three findings, each with evidence IDs and why it matters.
5. **Uncertainty and Alternatives** - unresolved explanations and discriminating evidence.
6. **Decision or Ask** - a question the advisor can answer, with supported options and trade-offs. Do not manufacture options.
7. **Advisor Attack Surface** - prioritized gaps, why they matter, and the minimum preparation or repair.
8. **Main Conversation Outline** - action titles, evidence, purpose, and approximate timing; this can be shorter than a conventional deck.
9. **Backup / Omit** - what to retain off the main path and what adds no decision value.
10. **Novice Notes** - optional explanations of selection, deletion, and claim-boundary choices.

Use [assets/meeting-brief-template.md](assets/meeting-brief-template.md) for a file deliverable. Use [assets/deck-outline-template.md](assets/deck-outline-template.md) when a text deck outline is requested. Use [assets/post-meeting-template.md](assets/post-meeting-template.md) only from explicit meeting notes or a transcript.

### 9. Validate before delivery

Check every project number and consequential claim against the evidence inventory. Check that every previous action is accounted for, every advisor-specific choice has profile evidence, and every ask is answerable from the advisor's role.

When creating a file deliverable, save the structured state beside it as JSON. Validate its published JSON Schema and semantic invariants with `scripts/validate_rms.py`, its exact text anchors with `scripts/validate_source_grounding.py`, and the brief's numbers and units with `scripts/validate_numeric_closed_world.py`. Validate a persisted advisor profile's schema and behavioral rules with `scripts/validate_advisor_profile.py` and its evidence files with `scripts/validate_advisor_profile_grounding.py`. The structural validators require the pinned dependency in `requirements.txt`; if it is unavailable, install it or report validation as blocked, and never treat a dependency error as a partial pass. A manual-verification warning is unresolved until a human checks it. Fix failures before delivery. Keep unparsed inputs explicitly unknown; never reconstruct their contents from filenames or context.

## Output and write behavior

Answer inline unless the user requests a file or the active project already has an established meeting-prep location. For a requested new file without an existing convention, use `meeting-prep/YYYY-MM-DD-brief.md` and keep the accompanying state as `meeting-prep/YYYY-MM-DD-rms.json`.

Do not publish, message an advisor, alter a remote system, or overwrite a prior record without an explicit request. For post-meeting updates, preserve the pre-meeting state and append only recorded decisions, actions, unresolved questions, and advisor-preference evidence.

## Completion gate

Do not call the package ready when any of these remain:

- an unsupported project fact, number, citation, causal claim, or completion state;
- a central claim without traceable evidence;
- a decision-relevant negative or conflict omitted from the main or backup path;
- an untracked prior action;
- advisor personalization without behavioral evidence;
- an invented option presented as if the user supplied or tested it;
- a generic slide outline that does not expose uncertainty and an advisor-answerable ask.
