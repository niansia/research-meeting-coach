# Research Meeting Brief

## Meeting Mission

Choose the next control that best separates compression from frame-count or token-budget effects.

## Opener

The baseline accuracy was 72.3 [F01], while the compression setup was 65.1 [F02]. The 32-frame run returned to around 70 [F03], so the current evidence does not isolate compression as the cause. The advisor-requested early-frame control is only half complete [F04]. I want guidance on which proposed control to prioritize.

## Continuity

The prior early-frame control remains partial; completion is not inferred from the other runs [F04].

## Top Findings

- The supplied configurations have different observed accuracies [F01] [F02] [F03].
- Frame count remains a live confound because the 32-frame run returned to around 70 [F03].
- No evidence-based advisor personalization was applied because no behavioral history was supplied.

## Uncertainty and Alternatives

Compression, frame count, and token budget remain live explanations. Equal-frame and equal-token-budget comparisons are proposals, not completed experiments.

The paper note is external and its citation details are unverified [F05]; it can motivate a hypothesis but cannot establish the project result.

## Decision or Ask

Which proposed control should be prioritized: equal-frame or equal-token-budget?

## Advisor Attack Surface

- Critical: a causal compression claim is not supported until frame count and token budget are controlled [F01] [F02] [F03]. Minimum repair: weaken the claim and prioritize a discriminating control.
- Medium: the paper note is unverified external rationale, not project evidence [F05]. Minimum repair: keep it in backup or verify it before use.

## Main Conversation Outline

- Opening comparison - 3 minutes from the 15-minute meeting budget: show the observed values without a causal claim [F01] [F02] [F03].
- Confound analysis - 5 minutes from the 15-minute meeting budget: explain what remains unresolved [F03].
- Control decision - 4 minutes from the 15-minute meeting budget: ask which proposed control should run first.
- Closing: confirm the selected control and how the partial prior action should be completed [F04].

## Backup / Omit

- Backup: the unverified paper note [F05], the one-day CUDA delay [F06], the unstarted visualization [F07], and implementation details for the proposed controls.
- Omit from the main path: routine activity that does not change the control decision.

## Novice Notes

- Changed: “compression hurts accuracy” became a bounded comparison.
- Why: the settings differ on frame count or budget, so the current evidence cannot identify a cause [F03].
- Try next time: write the strongest alternative explanation beside every central result before drafting the opener.
