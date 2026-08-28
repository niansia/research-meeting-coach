# Advisor Profile

Use a profile only to change meeting order, detail depth, backup preparation, or ask style. It must never change project facts or suppress decision-relevant evidence.

## Evidence strength

1. `explicit_feedback`: the advisor directly stated a preference or correction.
2. `repeated_behavior`: the same question or presentation preference occurred across at least three meetings.
3. `single_observation`: one observed behavior; keep confidence low.
4. `student_impression`: a tentative report requiring confirmation.

Nationality, region, institution, age, gender, prestige, and discipline stereotypes are prohibited evidence.

## Update rules

- Store the behavior, meeting IDs, exact note, confidence, source locator, verification mode, and quote.
- Do not raise confidence from repeated copies of the same meeting record.
- Keep contradictory evidence and lower confidence rather than choosing the more convenient signal.
- Never rewrite history. Add a new evidence item and recompute the current interpretation.
- Do not learn a preference from an AI-generated question or suggestion; only recorded advisor behavior counts.

## Application rules

State the applied preference and its evidence when it materially changes the output. If no valid profile evidence exists, say that general meeting principles were used. A preference may affect ordering or depth, but it cannot justify hiding uncertainty, omitting a prior action, or overstating a claim.

Use `schemas/advisor-profile.schema.json` when persisting a profile. Run both `scripts/validate_advisor_profile.py` and `scripts/validate_advisor_profile_grounding.py`; a manual source remains unresolved until a reviewer checks it.
