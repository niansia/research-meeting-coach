# 60-second demo

This synthetic example is the shortest path from messy weekly material to an advisor-ready decision.

## Try it

Give an Agent Skills-compatible client this directory and prompt:

```text
Use $research-meeting-coach on this 60-second-demo folder. Prepare a 15-minute advisor meeting. Keep unsupported causes uncertain, preserve incomplete prior actions, and end with one decision my advisor can answer.
```

Inputs:

- `raw-notes.md`: the student's unstructured weekly notes;
- `previous-meeting.md`: the prior advisor request that must not disappear;
- `result.csv`: the supplied measurements, including unknown conditions.

Comparison:

- `generic-output.md`: a strong concise generic meeting brief;
- `advisor-aware-output.md`: the advisor-facing critique layer.

Both outputs recognize the central confound. The advisor-aware output additionally externalizes evidence IDs, the unresolved prior action, risk-ranked attack surface, and the decision the meeting should produce. This is an illustrative synthetic comparison, not a scored model benchmark.
