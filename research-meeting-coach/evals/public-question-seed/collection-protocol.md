# Public Question Seed Collection Protocol

Collection date: 2026-08-28 (Asia/Taipei)

## Purpose and non-claims

This seed set is for **taxonomy discovery**: it helps identify reasoning gaps that researchers publicly report being challenged on in advisor, supervisor, or lab meetings. It does not estimate how common a question is, characterize a discipline, predict an individual professor, or replace a consented held-out pilot.

Only a future case containing permissioned pre-meeting material, a frozen prediction, and a separately recorded post-meeting question log may be Tier A. Every public-web record here is Tier B, C, or D and has `paired_pre_meeting_material=false`.

## Inclusion rules

Include a record only when all of the following hold:

1. The page is publicly reachable through an ordinary public search result or public page, without login, membership, or technical bypass.
2. The content concerns an advisor, supervisor, lab, project, or research-supervision meeting.
3. The post supplies a concrete question, feedback event, recurring meeting pattern, or discipline-specific supervision norm.
4. The observation can be paraphrased without a username, institution, laboratory, project secret, health detail, or other identifying narrative.
5. The discipline label is directly self-reported or conservatively supported by the post context. Otherwise it is `unknown`.

Exclude deleted or private posts, private groups, screenshots of private messages, identifiable misconduct allegations, medical or mental-health narratives not needed for the question theme, admissions-only interviews, and items whose useful content cannot be separated from an identifying story.

## Platform handling

- **Dcard:** public search-index results were reviewed manually. No crawler, API, or logged-in access was used.
- **Reddit:** public search-index results and public pages were sampled manually. This is not an API dataset or bulk scrape. Reddit's current research-policy route is the appropriate path before any larger systematic collection.
- **Academia Stack Exchange:** one public question-and-answer page was retained as Tier D community guidance, not as an observed advisor question.
- **Threads and Facebook:** public-web keyword searches returned no sufficiently verifiable results in this pass. No login, group access, browser-session reuse, or automated collection was attempted. Absence here means an indexing/access limitation, not absence of relevant discussions.

Platform terms and community expectations can change. Re-check them before each new collection wave. If the project moves from internal product discovery to publishable human-subjects research, seek institutional ethics review rather than treating public visibility as automatic ethical permission.

Policy references checked for this wave:

- [Dcard user agreement](https://www.dcard.tw/terms) and [privacy policy](https://www.dcard.tw/user-privacy)
- [Reddit Data API Terms](https://redditinc.com/policies/data-api-terms) and [research access guidance](https://support.reddithelp.com/hc/en-us/articles/14945211791892-Developer-Platform-Accessing-Reddit-Data)
- [Meta explanation of unauthorized automated scraping](https://about.fb.com/news/2021/04/how-we-combat-scraping/)
- [AoIR Internet Research Ethics 3.0](https://aoir.org/ire30/) and [Penn IRB social-media research guidance](https://irb.upenn.edu/homepage/social-behavioral-homepage/guidance/types-of-social-behavioral-research/use-of-social-media-as-a-research-activity/)
- [Taiwan Academic Ethics Education Resource Center: Internet behavior research ethics](https://ethics.moe.edu.tw/courses_list/intro/69/)

## Search log

The public-web queries used combinations of:

- Dcard: `研究生 meeting 老師 問 為什麼 實驗`, `研究所 meeting 教授 問題`, `博士生 meeting 教授 問 研究`, `實驗室 meeting 被問 老闆`.
- Reddit: `PI asked lab meeting question`, `advisor asked meeting research progress`, `why did you use lab meeting`, `sample size supervisor`, plus discipline terms for life science, computing, social science, humanities, and mathematics.
- Academia Stack Exchange: `advisor meeting asked research question`, `mathematics advisor meeting proof question`.
- Threads/Facebook: public-domain filters combined with `lab meeting`, `advisor meeting`, `PI asked`, and `PhD`; no retained hits.

This log supports reproducibility of the search strategy, not reproducibility of a search engine's ranking or index.

## De-identification and provenance split

The releasable `seed-corpus.json` stores paraphrases, broad discipline labels, source IDs, and SHA-256 URL fingerprints. It stores no source URL, username, direct quote, institution, or exact laboratory identifier.

Exact page URLs must live outside the repository in a maintainer-controlled private location. `.gitignore` is only a defensive fallback: it does not prevent a direct ZIP/RAR of the working directory from copying a local file. The validator can compare every private URL hash with the public fingerprint when the maintainer supplies the path:

```text
python scripts/validate_public_question_seed.py --corpus evals/public-question-seed/seed-corpus.json --taxonomy evals/question-theme-taxonomy.json --sources <private-source-register-path> --json
```

Without the private register, the same validator still checks the corpus structure, privacy flags, evidence-tier boundary, source fingerprints, and frozen-taxonomy references. Public releases must be created with `scripts/build_release.py`; never archive the workspace directly.

## Evidence tiers

- **Tier B:** first-person public retrospective with a concrete question or feedback event.
- **Tier C:** first-person or close-observer pattern without a specific enough question event.
- **Tier D:** community guidance or a supervision norm, not an observed event.

Tier labels describe provenance strength for theme discovery. They do not score credibility, severity, or advisor quality.
