# Contributing

Thank you for helping make research meetings more decision-ready without making unsupported claims.

## Good contributions

- minimal synthetic cases that expose a missed reasoning gap;
- routing fixes that preserve the boundary with generic weekly reports and slide tools;
- validator fixes with both an accepted blue case and a rejected red case;
- onboarding improvements that reduce time to first useful output;
- de-identified pilot feedback that follows the evaluation protocol.

Do not submit unpublished project data, advisor or student identities, private messages, source-register URLs, or allegations about identifiable laboratories. A public GitHub issue is not a confidential research channel.

## Development checks

From the repository root:

```text
python -m pip install -r requirements-dev.txt
python research-meeting-coach/scripts/run_static_evals.py
python validate_repository.py --json
python research-meeting-coach/scripts/validate_schema_contracts.py
python research-meeting-coach/scripts/build_release.py --json
```

Behavior changes should include a realistic synthetic reproduction. Keep actual model execution counts separate from static case-definition counts. Do not claim superiority from the bundled contaminated development run.

## Pull requests

Keep changes narrow. Explain the user problem, the scope boundary, the red case, and the blue case. Avoid adding general rules to `SKILL.md` when a reference, validator, example, or documentation change is more precise.

By contributing, you agree that your contribution is licensed under the repository's MIT License.
