# Public release checklist

- [ ] Initialize Git, inspect every staged file, and confirm no `.local.json`, `.env`, credential, identifiable/private pilot material, `__pycache__`, `.pyc`, RAR, ZIP, or private path is staged.
- [ ] Push and confirm all six CI jobs pass: Windows, Ubuntu Linux, and macOS on Python 3.11 and 3.13.
- [ ] Confirm `python validate_skill_install.py --json` succeeds with the pinned `skills` CLI.
- [ ] Build the public ZIP with `python research-meeting-coach/scripts/build_release.py --json`.
- [ ] Run `python research-meeting-coach/scripts/validate_portable_release.py --json` and confirm the extracted ZIP passes without repository-only `.github/` files.
- [ ] Attach only the audited ZIP from `dist/` to the GitHub release.
- [ ] When several historical ZIPs exist in `dist/`, select only the version and SHA-256 produced by the current builder run.
- [ ] Verify the release SHA-256 against the builder output.
- [ ] Open the 60-second demo from a clean checkout and test the documented prompt.
- [ ] Do not present public retrospective seed records as paired evaluation or recall@K evidence.
