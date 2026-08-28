# Development Baseline Report

Run: `development-smoke-2026-08-28-01`

This is a same-session development smoke run, not an independent benchmark. The exact deployment identifier and generation settings were not exposed, and the implementing session had already seen the skill. Do not use this report for a preference percentage or product superiority claim.

## Frozen artifacts

- Source: `../../examples/compression-confound/raw-notes.md`
- Prompts: `../baseline-prompts.md`
- Minimal baseline: `B0-output.md`
- Strong generic baseline: `B1-output.md`
- Candidate: `candidate-output.md`

## Observed differences

| Property | B0 | B1 | Candidate |
|---|---|---|---|
| Identifies frame-count confound | yes | yes | yes |
| Preserves incomplete prior action | yes | yes | yes, with explicit continuity state |
| Separates external paper from project evidence | yes | yes | yes, with evidence class and fact ID |
| Produces an advisor-answerable ask | yes | yes | yes, with proposed-option provenance |
| Exposes prioritized attack surface | no explicit tier | no explicit tier | Critical and Medium with repair actions |
| Produces machine-validatable RMS | no | no | yes |
| Applies evidence-based advisor profile | no | no | explicitly not applied because history is absent |
| Provides novice transfer cue | no | no | yes |

## Interpretation

The strong generic baseline already captures the central confound, evidence boundary, incomplete action, and advisor question. This confirms that generic prompting is a serious baseline and that meeting intent, opener structure, and ordinary evidence caution are not defensible moat claims.

The candidate's observable additions are structured provenance, explicit attack-surface prioritization, advisor-profile gating, option provenance, and novice coaching. Whether those additions improve real meetings remains unmeasured.

## Go / No-Go status

Open. No blind human ratings, correction-burden measurements, actual advisor-question records, or longitudinal learning results are present. The public-quality claim must remain “validated structure and guardrails,” not “better than B1.”
