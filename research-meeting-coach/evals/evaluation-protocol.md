# Evaluation Protocol

The bundled case definitions test corpus coverage, guardrails, and routing structure; they do not constitute model executions and do not prove that professors prefer the output.

## Automated gate

Run:

```text
python scripts/run_static_evals.py
```

This checks the case corpus, RMS invariants, exact-source grounding, typed units, recomputed structured calculations, advisor-profile confidence and source evidence, already-marked evidence retention, unsupported options, frozen question-theme taxonomy, and an out-of-scope route. The result reports case-definition count separately from executed model-run count.

## Behavioral comparison

For each case, generate B0, B1, and candidate outputs using [baseline-prompts.md](baseline-prompts.md). Evaluate:

- factual errors: required target is zero;
- critical-gap coverage against a human annotation;
- dimension scores from `references/meeting-rubric.md`;
- correction burden before the student would present it;
- blind reviewer preference between B1 and candidate;
- whether an explicit advisor-answerable decision or feedback request exists.

Keep synthetic and real cases separate. Never present synthetic scores as user or professor outcomes.

## Public retrospective discovery set

`public-question-seed/seed-corpus.json` is a de-identified convenience sample of public retrospective reports. Use it only to discover candidate taxonomy gaps and discipline-conditioned evidence fields. It cannot be promoted to a held-out pilot because it lacks paired pre-meeting material, frozen predictions, consent, and a prospectively recorded question log.

Validate the releasable corpus with:

```text
python scripts/validate_public_question_seed.py --corpus evals/public-question-seed/seed-corpus.json --taxonomy evals/question-theme-taxonomy.json --json
```

Maintainers who possess the private provenance register outside the repository may also pass its path with `--sources` to verify the URL fingerprints. Do not copy that register into the workspace, publish it, or use the seed to estimate platform or discipline prevalence.

For a release study, add two version-pinned composition baselines without rewriting the frozen development prompts:

- **B2 report-composition baseline:** generate or obtain the same evidence-grounded lab report, then apply a strong generic advisor-critique prompt.
- **B3 adjacent rehearsal baseline:** run a named public advisor-rehearsal skill under its documented version and settings when its output can be obtained lawfully and reproducibly.

If either baseline cannot be run, report it as missing. Do not reconstruct, imitate, or assign it a synthetic score.

## Actual-question holdout

Before the meeting, freeze the versioned [question-theme taxonomy](question-theme-taxonomy.md), ranked attack-surface theme IDs, and their risk tiers. Do not expose the actual advisor questions to generation or advisor-profile training. After the meeting, annotate each recorded question with one or more IDs from that frozen taxonomy and score the frozen artifact with:

```text
python scripts/score_question_themes.py <question-theme-eval.json> --k 3 --json
```

Report theme recall@k and question coverage@k. These are coverage measures, not exact-question prediction accuracy or calibrated probabilities. The bundled `question-themes/E15-synthetic.json` proves only that the scorer runs; it is not empirical evidence.

## Human pilot

Use anonymized material only with permission. A useful pilot pairs raw notes, the student's original outline, actual advisor questions or comments, the revised version, and recorded actions. Report aggregate outcomes and limits; do not publish sensitive project details.

The rubric is not calibrated until multiple human reviewers score overlapping cases and disagreements are examined. A real-world quality claim requires held-out meetings, not only the bundled example.

Store ratings against `schemas/human-evaluation-results.schema.json`, then aggregate them with:

```text
python scripts/compare_outputs.py <ratings.json> --json
```

The aggregator reports separate `blind`, `non_blind`, and `all_ratings_descriptive` cohorts for preferences, factual-error totals, correction burden, and dimension deltas. Only the `blind` cohort is copied into `headline_metric`; the combined descriptive rate must never replace it. The aggregator deliberately does not manufacture significance tests or a Go/No-Go verdict from an underspecified sample.

## Longitudinal entry case

`longitudinal/L01-advisor-baseline-preference.json` supplies three profile-training meetings and one held-out meeting. The holdout must not be counted as evidence before its output is generated and real feedback is recorded.
