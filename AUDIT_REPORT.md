# Collision, Provenance, and Red/Blue Audit

Date: 2026-08-28 (Asia/Taipei)

## Revised verdict

No exact public skill named or positioned as `research-meeting-coach` was found in the reviewed sources. That is not a uniqueness claim: public skill registries are large and fast-moving. A 2026 healthcare-skill study alone filtered 557 healthcare skills from 58,159 public ClawHub skills, so a small repository scan cannot establish global novelty ([paper](https://arxiv.org/abs/2605.02709)).

There is substantial mechanism-level convergence with [lab-meeting-report-skill](https://github.com/LikC1606/lab-meeting-report-skill), not merely topic adjacency. A broad “weekly research material to decision-ready meeting” positioning would look derivative and route ambiguously. Version `0.3.4-alpha` therefore positions this package above existing reports: it consumes a lab-meeting report, weekly summary, draft, or raw notes and adds advisor-facing critique, personalization, rehearsal, and auditable state.

[Advisor Roaster](https://marketplace.agentscli.com/items/nianbaizy-grad-agent-kit-advisor-roaster) is a direct adjacent competitor for strict-advisor question rehearsal and defense preparation. The remaining boundary is not “anticipates advisor questions”; it is behavior-grounded personalization with evidence/confidence controls, auditable project provenance, and held-out question-theme evaluation without exact-question or personality-prediction claims.

## Convergent baseline safeguards

The following concepts materially overlap with `lab-meeting-report-skill` v1.3 and are not claimed as differentiation:

| Shared design requirement | Public prior art | This package |
|---|---|---|
| Evidence classes | source fact, derived calculation, interpretation, hypothesis | project fact, external literature, calculation, interpretation, hypothesis, proposal |
| Numeric fidelity | preserve supplied values and units; constrain new calculations | closed-world numeric validator with fact citations |
| Negative/conflicting evidence | retain failures, negative results, and unresolved conflicts | once assigned, `retention=required` prevents a fact from disappearing |
| Action continuity | explicit prior-action status; no unsupported completion inference | direct completion evidence is required to close an action |
| Conflict without authority | preserve unresolved values when no precedence exists | record both sources and keep authority unresolved |
| Meeting lifecycle | separate preparation from recorded post-meeting decisions | preserve pre-meeting state and append attributed decisions/actions |
| Thin input | produce a shorter evidence-bound output | produce a gap-first critique without padding |
| Option provenance | do not make invented alternatives look supplied or tested | `supplied` options require source fact IDs; generated options are `proposed` |
| Unreadable input | report the read failure without reconstructing content | leave unparsed inputs explicitly unknown |
| Language handling | follow the request language and preserve technical identifiers | same portability requirement |

These are convergent integrity constraints for research communication. They remain because removing them would reduce correctness, not because they create a moat. The implementation uses independently written schemas, a pinned public JSON Schema runtime, and project-specific semantic validators; no competitor code is vendored.

## Defensible contribution boundary

The current distinct layer is limited to five claims:

1. **Behavior-evidenced advisor profile.** Explicit feedback, repeated behavior across distinct meetings, single observations, and student impressions have different confidence ceilings. A deterministic validator blocks unsupported high confidence and demographic profile dimensions.
2. **Advisor attack surface.** Gaps are prioritized by decision consequence (`Critical`, `High`, `Medium`, `Low`) with minimum repair actions; no uncalibrated question probabilities are allowed.
3. **Novice coaching and fading.** `Changed / Why / Try next time` exposes reusable reasoning moves and avoids unmeasured learning claims.
4. **Portable RMS contract.** Facts, reasoning layers, asks, attack surface, continuity, relevance, and advisor-profile references are external JSON with a public schema and validator rather than an internal-only ledger.
5. **Bounded numeric provenance.** Each output number, known unit, lexical measurement condition, and approximate qualifier is checked against its nearest fact citation, every declared calculation operand, or meeting-time context. Add/subtract results are recomputed. This is stronger than token matching but is not full natural-language entailment.

Meeting-intent routing, a short opener, a meeting mission, ordinary uncertainty language, and main/backup filtering are useful but not differentiation claims.

## Closest public work reviewed

| Public skill | Collision level | Composition rule |
|---|---|---|
| [lab-meeting-report-skill](https://github.com/LikC1606/lab-meeting-report-skill) | Very high at the evidence/reporting layer | Prefer its validated report as input; do not regenerate or republish it. |
| [slide-deck-for-lab-meeting](https://github.com/aipoch/medical-research-skills/tree/main/awesome-med-research-skills/Academic%20Writing/slide-deck-for-lab-meeting) | High for goal routing and honest deck structure | Use this package only for advisor critique/rehearsal; yield visual design and rendering. |
| [research-lab-skills](https://github.com/zi-yue-1129/research-lab-skills) | Medium for persistent experiments, failures, decisions, and progress slides | Consume its project state or report; do not duplicate lab-memory infrastructure. |
| [weekly-lab-update](https://github.com/chtc66/academic-skills/tree/main/weekly-lab-update) | Medium for weekly notes to group-meeting outline | Route generic weekly reporting there; invoke this layer only for advisor-specific critique or coaching. |
| [academic-researcher-skill](https://github.com/Scottthe3rd/academic-researcher-skill) | Low to medium for broad supervisor/pre-advisor review | Keep this package meeting-specific; do not simulate a full research program or committee. |
| [Advisor Roaster](https://marketplace.agentscli.com/items/nianbaizy-grad-agent-kit-advisor-roaster) | High for strict-advisor simulation, weaknesses, questions, and defenses | Do not claim generic advisor simulation as novelty; require recorded behavior for personalization and score themes only after holdout release. |

Reviewed local snapshots from the first audit pass:

- `lab-meeting-report-skill`: `f6c06b7388ac`
- `research-lab-skills`: `3041838e9288`
- `medical-research-skills`: `f5ef65b9bea7`
- `academic-researcher-skill`: `d17e1db8d660`
- `academic-skills`: `126e2351d75d`

The public `lab-meeting-report-skill` page was rechecked on 2026-08-28 and identifies v1.3 as retaining evaluated v1.2 safeguards while redesigning inputs, outputs, and adapters.

## Red/blue revision history

### Round 1 - Routing collision

- Red: the original frontmatter competed directly with weekly-report and deck skills.
- Blue: frontmatter now says this is an additive critique layer over an existing report, summary, draft, or raw notes. Eight positive/negative routing cases enforce the boundary.

### Round 2 - Wording and lineage risk

- Red: several rules and phrases closely resembled `lab-meeting-report-skill`, while the first audit understated the convergence.
- Blue: the overlap is now itemized above, shared safeguards are explicitly disclaimed as differentiation, copied-sounding wording was rewritten, and `must_retain` became the RMS-specific `retention=required` contract.

### Round 3 - Numeric citation swapping

- Red: a line-level number check could accept swapped citations when every needed fact ID appeared on the line.
- Blue: each numeric token now resolves its nearest fact citation; swapped citations must fail.

### Round 4 - Structural-number confusion

- Red: legitimate presentation-time allocations failed the research-number gate, while a value equal to the meeting budget could be reused as a project result.
- Blue: presentation-structure numbers are typed separately, cite `meeting.time_budget_min`, and pass only in time/date context.

### Round 5 - Advisor overfitting

- Red: one student impression could become a high-confidence advisor preference.
- Blue: high confidence requires explicit feedback or repeated behavior across at least three distinct meetings; demographic dimensions are prohibited.

### Round 6 - Evidence retention and option provenance

- Red: decision-changing negative evidence could disappear, or generated options could masquerade as supplied choices.
- Blue: facts marked `retention=required` must appear in main or backup; supplied options require source fact IDs.

### Round 7 - Publishability and benchmark honesty

- Red: the package lacked a README, LICENSE, readable example, deck template, longitudinal entry case, output comparator, and actual frozen baseline outputs.
- Blue: all are now present. The same-session development run is explicitly contaminated and therefore cannot support a superiority claim.

### Round 8 - RMS trust root and measurement units

- Red: a fabricated RMS statement could borrow a real locator, and a correct numeric value could be emitted with the wrong unit.
- Blue: text-exact project facts now require a line locator, exact quote, and exact statement span; manual verification remains visibly unresolved. Measurements carry typed value/unit/condition/qualifier records, and unit substitution fails.

### Round 9 - Partial-operand calculation citation

- Red: a derived result passed when only one of several operand facts was cited.
- Blue: every declared operand fact ID is now required on the result line. A one-operand citation fails while the full operand set passes.

### Round 10 - Evaluation-count honesty and actual-question holdout

- Red: “ten behavioral cases pass” conflated case-file validation with model execution, while question coverage had no frozen prediction/holdout scorer.
- Blue: output now reports 15 case definitions, zero executed case-definition runs, zero cross-model runs, and one development bundle separately. A synthetic scorer fixture validates the metric pipeline only; it is explicitly not an advisor outcome.

### Round 11 - Calculation correctness

- Red: a declared `99.9` result passed when its readable expression and cited operands actually produced `7.2`.
- Blue: calculations now use structured `add` or `subtract` operations with fact and measurement-index operands. The RMS validator deterministically recomputes the result and the numeric gate rejects an invalid RMS.

### Round 12 - Qualifier, condition, and unitless prose

- Red: “around 70” could become exact `70`, a baseline value could be relabeled as a new-method result, and ordinary words such as “on” or “while” were misread as units.
- Blue: approximate measurements require a nearby hedge, typed conditions must appear on the numeric line, and units are recognized only from a bounded vocabulary plus declared units. Spelled-out decimal sequences are rejected rather than escaping the scanner.

### Round 13 - Advisor evidence trust root

- Red: a structurally valid profile could cite a nonexistent meeting note, while discipline and prestige dimensions were not aligned with the written policy.
- Blue: advisor evidence now carries locator, verification mode, and quote; a separate grounding validator checks the record. Discipline and prestige are prohibited by both schema and executable validation.

### Round 14 - Benchmark executable/schema convergence

- Red: the human comparator accepted missing study labels, while the question scorer accepted rank zero, missing risk, duplicate themes, and theme drift beyond its schema.
- Blue: both executables enforce their required metadata and bounded fields. Question scoring also requires a version-matched frozen taxonomy with inclusion and exclusion criteria.

### Round 15 - Public-retrospective contamination and privacy

- Red: public anecdotes could be mislabeled as real paired evaluation cases, leak source URLs or usernames into the release, drift the frozen taxonomy after observation, or silently lose provenance when a URL changes.
- Blue: a 15-record public seed corpus is explicitly limited to Tier B/C/D taxonomy discovery. The public JSON contains paraphrases and URL hashes only; a private register outside the repository preserves exact provenance. Executable checks reject direct URLs, username flags, fake Tier A pairing, unknown frozen-taxonomy mappings, and tampered URL fingerprints.

### Round 16 - Archive leakage and same-line condition swapping

- Red: a direct RAR of the workspace ignored `.gitignore` and bundled the source URL register plus eight CPython 3.10 cache files. Separately, valid values and fact citations could be paired with the wrong same-line conditions, reversing the reported direction while passing the numeric gate.
- Blue: the real source register was moved outside the repository and the legacy cache directory was removed from the package tree. `build_release.py` now uses explicit public roots, excludes local/bytecode/archive artifacts, scans the completed ZIP for Dcard and Reddit post URLs, verifies CRC, and emits a SHA-256 manifest. Numeric validation now requires the cited condition to be the closest recognized typed condition to its value; a baseline/compression swap fails while the correctly bound sentence passes.
- Residual limit: standalone number words such as `seventy` and fractional phrases such as `a tenth` are not parsed. README now states that the executable rejection covers English `digit-word point digit-word` decimal phrases only.

### Round 17 - GitHub onboarding and claim conversion

- Red: a technically rigorous README still made a new visitor read architecture and audit detail before learning how to try the skill. There was no CI workflow, self-contained first-run folder, contribution path, pilot issue form, or tested repository install command.
- Blue: the first screen now leads with the student problem, a visual before/after, a short output contrast, an invocation prompt, and a transparent generic-prompt comparison. A six-file synthetic 60-second demo, pinned cross-platform GitHub Actions matrix, structured issue forms, contribution/security/conduct documents, UI icon, and release checklist were added.
- Honest boundary: the proposed `npx skills add niansia/research-meeting-coach --skill research-meeting-coach` command remains labeled provisional until a public remote exists and the command succeeds from a clean environment. No CI badge or installation-count badge is shown before those external states exist.

### Round 18 - Package default-deny and content-secret bypasses

- Red: package traversal allowed any new file below `research-meeting-coach/`. A PTT post URL, an `.env` containing an OpenAI-style key, and an unlisted `real-pilot-case-01.md` therefore entered an otherwise valid release. The post scanner covered only Dcard and Reddit.
- Blue: package top-level paths now default to denial outside `SKILL.md`, `VERSION`, and the seven documented resource directories. Environment files and private/confidential/real-pilot filename fragments are denied anywhere. Completed entries are scanned for individual Dcard, Reddit, PTT, Threads, and Facebook post URLs plus common OpenAI/GitHub/AWS/private-key patterns; possible credentials are reported by type without echoing the token.
- Residual limit: directory allowlisting and lexical scanning are not a general PII, consent, or confidentiality classifier. A permitted Markdown file may still contain an unrecognized identity, institution, platform URL, or secret format, so manifest and staged-file review remains mandatory.

### Round 19 - Portable self-test, RMS metadata trust, and blinded aggregation

- Red: the audited ZIP omitted `.github/` by design while `run_static_evals.py` required its CI file, so repository validation passed but the portable release's documented self-test always failed. Separately, a text-exact RMS could relabel `accuracy` as `latency`, `baseline` as `new method`, or `around 70` as exact because only value/unit were grounded to the quote. Finally, two blind baseline preferences plus eight non-blind candidate preferences produced an ambiguous combined candidate rate of 0.8.
- Blue: portable static validation now requires only files shipped in the release. Root `validate_repository.py` owns CI, issue-form, PR-template, and release-checklist checks, and CI runs both layers. Text-exact source grounding now checks metric words, exact condition spans, and value-local English/Chinese approximation hedges. The comparison aggregator emits separate `blind`, `non_blind`, and `all_ratings_descriptive` cohorts; `headline_metric` copies only the blind candidate-preference rate and the old ambiguous top-level rate is absent.
- Residual limit: metric and condition grounding is lexical rather than ontological, and qualifier detection covers a bounded hedge vocabulary. Indirect or non-text evidence must use manual verification. Human-study aggregation still establishes neither significance nor generalization.

### Round 20 - Published-schema and runtime-validator convergence

- Red: `validate_schema_contracts.py` proved only that 21 bundled fixtures matched their schemas. The user-facing RMS and advisor-profile Python validators did not apply those schemas, so seven schema-invalid mutations—missing action `item`, reasoning `text`, attack-surface `gap`, profile `value`, evidence `note`, and unexpected RMS/profile root properties—all passed the semantic-only validators.
- Blue: both user-facing validators now run the exact published Draft 2020-12 schema before their existing semantic checks through a shared runtime module. All seven mutations fail through the Python API and CLI. `jsonschema==4.26.0` is pinned in the portable package, CI installs it before static tests, and a missing dependency produces a hard validation failure with an install hint rather than a reduced pass.
- Honest boundary: `validate_schema_contracts.py` remains a fixture/schema contract suite, not an arbitrary-file CLI. Arbitrary RMS and advisor-profile files belong to their named runtime validators.

## Definition-of-done status

### Implemented

- Discriminating trigger description and a 130-line progressive-disclosure entry point (well below the 500-line recommendation).
- Five intents, scoped inputs, RMS schema, numeric validator, continuity, optional advisor profile, and full text output contract.
- README, MIT LICENSE, and a complete synthetic raw notes -> RMS -> brief -> deck outline example.
- Fifteen adversarial/behavior case definitions, eight routing cases, and one three-training-plus-one-holdout longitudinal definition.
- Exact-source grounding, advisor-evidence grounding, typed measurement/qualifier/condition validation, recomputed calculations, and a frozen-taxonomy question-theme scorer.
- Frozen B0, B1, and candidate development outputs with contamination metadata.
- Human-rating schema and deterministic `compare_outputs.py` aggregator.
- Fifteen de-identified public retrospective seed records across Dcard, Reddit, and Academia Stack Exchange, with a collection protocol, discipline-stratified discovery memo, and an optional local provenance check.
- Product-first GitHub README, self-contained 60-second demo, pinned Linux/Windows CI matrix, privacy-aware issue templates, and contributor/security guidance.
- Default-deny public package roots with post-URL and common credential-pattern scanning, plus an explicit human-review boundary.
- Separate portable/repository validation, text-exact typed-metadata grounding, and blind-only headline comparison metrics.
- Published-schema-first runtime validation for arbitrary RMS and advisor-profile artifacts, with explicit dependency failure.

### Still open before an empirical release claim

- At least five anonymized real pilot cases.
- Blind human comparison against B1 with correction burden and factual-error review.
- Permissioned, prospectively paired advisor-question or comment records for attack-surface coverage; the public retrospective seed does not satisfy this requirement.
- A cross-model run using known model IDs and settings.
- Longitudinal holdout feedback demonstrating that advisor personalization helps rather than overfits.

`slide-patterns.md` and `domain-cs-ee.md` remain intentionally deferred: presentation rendering and domain-specific content are not required to validate the advisor-critique layer.

Deterministic limits are explicit. The retention gate cannot identify evidence that should have been marked `retention=required`; it only prevents already-marked facts from disappearing. Lexical metric/condition checks and bounded qualifier hedges do not prove full claim-level semantic entailment. Manual/non-text evidence remains a human-review obligation, not a machine pass.

## Honest limit and Go/No-Go

The bundled development run shows that B1 already identifies the central confound, preserves the incomplete action, separates the paper note, and asks an advisor-answerable question. That finding weakens any claim that generic meeting structure is the product moat.

Current Go/No-Go status: **open, not passed**. Automated checks establish packaging, schema, routing, and provenance invariants. They do not establish professor preference, question-theme recall, correction burden, or student learning. Until blind human and held-out longitudinal data exist, the defensible public statement is “an auditable advisor-critique layer,” not “better research meetings” or “better than a strong generic prompt.”
