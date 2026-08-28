# Reasoning and Attack Surface

## Reasoning graph

Represent each central item as:

```text
Observation -> Evidence -> Interpretation -> Uncertainty -> Decision
```

Keep nodes sparse. If the evidence does not support an interpretation, leave it open instead of repairing the story with a plausible explanation.

## Risk tiers

- `Critical`: the central claim is unsupported, contradicted, causally overstated, or blocked by a core confound. Repair before the meeting or weaken the claim.
- `High`: a missing baseline, unfair comparison, unclear definition/unit/sample, or strong alternative explanation prevents confident advice.
- `Medium`: not fatal to the central claim, but likely to affect implementation, advisor preference, or backup preparation.
- `Low`: detail that does not change the immediate interpretation or decision.

Risk is about decision consequence, not rhetorical severity. Do not fabricate likelihood percentages.

## Audit prompts

For every central claim, ask:

- Which exact evidence IDs support it?
- Is the comparator fair and the unit or denominator clear?
- What baseline or control is missing?
- What confound or alternative explanation remains?
- Does another supplied source conflict with it?
- Is the result replicated or only observed once?
- What evidence would discriminate among the live explanations?
- Does this gap prevent an advisor decision, or merely belong in backup?

## Ask construction

A strong ask contains:

1. the decision or feedback requested;
2. the evidence already available;
3. the unresolved constraint or uncertainty;
4. only user-supplied or clearly labeled proposed options;
5. the consequence of choosing or delaying.

Do not turn “What do you think?” into false precision. If options are not supported, ask for prioritization criteria or permission to generate options, rather than presenting invented alternatives as established choices.
