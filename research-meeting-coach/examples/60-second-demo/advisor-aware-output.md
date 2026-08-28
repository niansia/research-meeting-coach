# Advisor-aware brief

## Meeting mission

Choose the next control that best separates compression from frame-count or token-budget effects.

## Evidence boundary

- Observation: baseline was 72.3 [F01], compression setup was 65.1 [F02], and the 32-frame follow-up returned to around 70 [F03].
- Interpretation: the configurations differ, but no supplied evidence isolates compression as the cause.
- Continuity: the advisor-requested early-frame control is still partial [F04].
- External context: the paper note is unverified and cannot establish the project result [F05].

## Attack surface

- **Critical:** the causal claim is unsupported because frame count and token budget remain uncontrolled. Minimum repair: weaken the claim and run a discriminating control.
- **Medium:** the literature note has no verified citation. Minimum repair: verify it or keep it in backup.

## Decision for the advisor

Which proposed control should run first: equal-frame or equal-token-budget?

## Coaching cue

Changed: “compression hurts accuracy” became a bounded comparison.
Why: the compared conditions differ in more than compression.
Try next time: write the strongest alternative explanation beside every central result before drafting the opener.

This example is entirely synthetic and does not claim professor preference or prediction accuracy.

## Source map

| Fact | Source |
|---|---|
| [F01] baseline 72.3 | `raw-notes.md:5` and `result.csv:R1` |
| [F02] compression setup 65.1 | `raw-notes.md:6` and `result.csv:R2` |
| [F03] 32-frame follow-up around 70 | `raw-notes.md:7` and `result.csv:R3` |
| [F04] early-frame control remains partial | `previous-meeting.md:3-5` and `raw-notes.md:11` |
| [F05] unverified paper note | `raw-notes.md:9` |
