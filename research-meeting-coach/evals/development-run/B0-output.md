# Research meeting preparation

## Main update

The baseline accuracy was 72.3 and the compression setup accuracy was 65.1. A 32-frame run returned to around 70, which suggests the difference cannot yet be attributed to compression alone because frame count may matter.

## Incomplete work and blockers

- The advisor-requested early-frame control is only half complete.
- The attention visualization has not been started.
- CUDA was unavailable for one day and delayed the schedule.

## Literature context

One unverified paper note says token pruning may hurt long-context performance. This may be relevant, but the citation details still need verification and the paper does not establish what happened in this project.

## Questions for the advisor

- Should the next priority be resolving the frame-count or token-budget confound, or completing the visualization?
- If only one control can run first, which comparison would be most informative?

## Suggested flow

1. State the current research question.
2. Show the three observed results.
3. Explain the unresolved confounds and incomplete prior action.
4. Ask the advisor to prioritize the next control.
