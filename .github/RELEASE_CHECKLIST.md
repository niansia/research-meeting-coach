# First public release checklist

- [ ] Confirm the proposed public repository slug `niansia/research-meeting-coach` and visibility with the owner.
- [ ] Initialize Git, inspect every staged file, and confirm no `.local.json`, `.env`, credential, identifiable/private pilot material, `__pycache__`, `.pyc`, RAR, ZIP, or private path is staged.
- [ ] Push and confirm all CI matrix jobs pass.
- [ ] Use GitHub's Actions UI to generate the real workflow badge after the first default-branch run.
- [ ] Replace the provisional install command with `npx skills add <owner>/<repository>` only after it succeeds from a clean temporary environment.
- [ ] Add repository description and topics: `agent-skills`, `research-tools`, `graduate-students`, `phd`, `lab-meeting`, `academic-research`, `research-workflow`, `scientific-reasoning`.
- [ ] Enable Issues, private vulnerability reporting, and Discussions if community support is available.
- [ ] Build the public ZIP with `python research-meeting-coach/scripts/build_release.py --json`.
- [ ] Extract the audited ZIP into a clean temporary directory, install `research-meeting-coach/requirements.txt`, and confirm `python research-meeting-coach/scripts/run_static_evals.py` passes without repository-only `.github/` files.
- [ ] Attach only the audited ZIP from `dist/` to the GitHub release.
- [ ] When several historical ZIPs exist in `dist/`, select only the version and SHA-256 produced by the current builder run.
- [ ] Verify the release SHA-256 against the builder output.
- [ ] Open the 60-second demo from a clean checkout and test the documented prompt.
- [ ] Do not present public retrospective seed records as paired evaluation or recall@K evidence.
