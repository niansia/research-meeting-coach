# Frozen Baseline Prompts

Use the same model, source bundle, language, and output budget for each variant. Randomize labels before human review.

## B0 - Minimal baseline

```text
Based only on the supplied material, help me prepare for my next research meeting with my advisor.
```

## B1 - Strong generic baseline

```text
Based only on the supplied material, prepare a concise research-meeting brief. Lead with the main result, cite the evidence, distinguish facts from interpretations, state important uncertainty, preserve negative results, and end with a concrete question for my advisor. Do not invent information.
```

## Candidate

Invoke `$research-meeting-coach` with the same source scope. Do not add extra hints that are absent from B1.

## Freeze rules

- Record the model and settings before generating any variant.
- Do not revise one variant after seeing another.
- Do not reveal the system label to reviewers.
- Keep raw outputs, including failures.
- Do not treat the model's self-rating as human evidence.
