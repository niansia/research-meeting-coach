# Seed Corpus Analysis: Discipline-Conditioned Question Surfaces

This is a qualitative discovery memo over 15 de-identified public records, not a prevalence study. The sample is small, convenience-based, self-selected, platform-skewed, and unpaired with pre-meeting artifacts.

## What the seed supports

The strongest cross-cutting gap is **rationale for a choice**. Public accounts describe being challenged on method conventions, experimental time points, concentrations, primers, and analysis approaches. This suggests a general attack-surface family:

> What was chosen, what alternatives existed, and what evidence or constraint justifies this choice?

The second recurring family is **progress and continuity**: whether visible progress is adequate, whether a prior direction was completed before a new one replaced it, and how work is made observable when it is done outside a physical lab.

The third family is **validity and scope**: sample derivation, replication, measurement trust, practical applicability, and whether a result survives a competing explanation.

The final recurring family is **conceptual fit and provenance**: where a solution came from, whether a case fits a theory, whether a proof can be explained at different depths, and whether a new topic is feasible given the literature and local expertise.

## Observed strata, without personality stereotypes

| Broad group | Seed support | Seed observations | Candidate preparation fields |
|---|---:|---|---|
| Life and health | 5 records: 4 Tier B, 1 Tier C | Method/parameter rationale, measurement validity, replication, project origin | parameter rationale; controls; protocol deviations; measurement QC; biological or clinical interpretation |
| Computing and engineering | 5 records: 4 Tier B, 1 Tier C | Remote-work visibility, shifting technical directions, solution provenance, theory-to-system applicability | matched baselines; implementation provenance; failure logs; resource constraints; practical-system test |
| Social sciences and humanities | 2 records: both Tier B | Sampling-frame justification and theory-to-case fit | unit/case selection; positionality where relevant; construct operationalization; alternative interpretation; transferability limits |
| Mathematics | 1 record: Tier D guidance, no observed event | Public guidance emphasizes explaining a proof at multiple levels of detail | statement and assumptions; proof skeleton; key lemma; failure point; examples or counterexamples |
| Unknown or weakly specified | 2 records: both Tier B | Progress adequacy and convention rationale | no discipline-specific adapter justified from this stratum |

These rows describe **evidence objects and reasoning tasks**, not advisor personalities. The skill must not infer that an individual professor will ask a question because of discipline alone. Discipline may route an optional checklist only when the user's own project evidence establishes the field.

## Taxonomy decision

The frozen `question-theme-taxonomy` remains at version 1.0. Retrospective seed data must not be used to rewrite the taxonomy and then score the same records as if they were held out.

For a future version 1.1, the following candidate families deserve annotation on new, independent records:

1. `choice-rationale`: method, parameter, analysis, or convention choice lacks an explicit justification.
2. `progress-adequacy`: the evidence presented does not make the amount, direction, or decision value of progress clear.
3. `provenance-or-ownership`: the origin of a solution, decision, implementation, or contribution is unclear.
4. `scope-or-applicability`: the case, sample, theory, or system does not yet support the claimed scope.
5. `conceptual-explanation-depth`: a proof, mechanism, method, or theory cannot yet be explained at the level the meeting requires.

Candidate IDs in the seed corpus are finer-grained discovery labels. They must be consolidated with independent annotators before a taxonomy change.

## Product implication

Do not add a fixed section for every discipline to `SKILL.md`. A better next experiment is a small, evidence-routed domain adapter that asks for the relevant missing fields only when the project type warrants them. The advisor profile remains behavior-based; discipline does not become a personality dimension.

The public seed closes a discovery gap, not the empirical Go/No-Go gate. That gate still requires at least five permissioned cases with:

1. pre-meeting material;
2. frozen candidate and B1 outputs;
3. a post-meeting log of actual questions or comments;
4. blind usefulness and correction-burden ratings; and
5. strict separation between profile-training meetings and held-out meetings.
