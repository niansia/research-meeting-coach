# Evidence Integrity

Apply a closed-world policy to project facts. The user's scoped material is the complete allowed universe for claims about the project.

## Evidence classes

- `project_fact`: directly supplied observation, measurement, artifact, or recorded event.
- `derived_calculation`: reproducible calculation from supplied facts; record the expression and operands.
- `interpretation`: current explanation consistent with facts but not directly observed.
- `hypothesis`: testable possibility not yet supported as a project result.
- `proposal`: suggested action, experiment, or framing.
- `external_literature`: claim about prior work, kept separate from project evidence.

## Numeric rules

- Copy values, signs, decimal precision, uncertainty, and units exactly.
- Do not calculate deltas, averages, percentages, ranks, thresholds, or significance unless requested or needed for the stated task.
- Record every derived number with a structured `add` or `subtract` operation and measurement-index operands; keep the expression only as a readable description.
- Cite every operand fact for a derived result, not merely one operand.
- Store measurements as typed value/unit/condition/qualifier records. For `text_exact` evidence, metric and condition language must be lexically present in the exact quote, and approximation language must be attached to the relevant value. Otherwise use manual verification.
- Preserve each measurement's condition and exact/approximate qualifier in numeric output. Ordinary prose after a unitless number is not a unit.
- For text inputs, retain a line locator, verification mode, and exact quote. A paraphrase requires explicit manual verification.
- Record numeric presentation-time allocations separately as `presentation_structure` values derived from `meeting.time_budget_min`; never treat them as research evidence.
- Approximate source language such as “around 70” must remain approximate.
- A missing unit, sample size, split, repetition count, or statistic is a gap, not permission to infer one.

## Conflict rules

When sources disagree and no precedence rule exists:

1. retain both values and their locators;
2. label the conflict;
3. prevent either value from becoming the sole basis of a conclusion;
4. turn resolution into a preparation item or ask when decision-relevant.

## Decision-relevant retention

Keep negative results, failed attempts, blocked runs, missing controls, and contradictions when they alter the live hypothesis, resource plan, interpretation, or next action. Do not keep operational trivia that has no effect on any of those.

The deterministic retention gate verifies only facts already marked `retention=required`. Deciding which supplied evidence deserves that mark remains a review judgment; the gate cannot prove that an important negative result was identified in the first place.

## Claim language

Use causal language only when the supplied design supports it. Otherwise prefer descriptions such as “is associated with,” “coincided with,” “is consistent with,” or “may reflect,” and state the live confound.

If a file, image, table, or citation cannot be read or verified, report only that it was not verified.
