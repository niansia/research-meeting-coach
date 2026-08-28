# Security and privacy

## Reporting

Do not open a public issue for a vulnerability or privacy leak. After the repository is published, use GitHub's private vulnerability-reporting or Security Advisory feature. Until then, contact the maintainer privately through the GitHub profile linked in the repository metadata.

Include the affected version, the smallest synthetic reproduction, the likely impact, and whether any release archive contains sensitive material. Do not attach real research notes, credentials, private advisor communications, or identifiable social-media source registers.

## Supported version

This is an early alpha. Security and privacy fixes are applied to the latest released version only.

## Release boundary

Public artifacts must be built with `research-meeting-coach/scripts/build_release.py`. Direct ZIP/RAR archives of a workspace are unsupported because `.gitignore` is not a packaging control. Repository and skill-package paths default to denial outside explicit public roots. The builder rejects local provenance registers, environment files, private/confidential pilot filenames, symlinks, bytecode caches, nested archives, individual Dcard/Reddit/PTT/Threads/Facebook post URLs, and common credential or private-key patterns.

These checks reduce known accidental-release risks; they do not establish that a file is anonymous, consented, non-confidential, or free of every possible credential format. A passing archive still requires manifest review and human inspection before publication.
