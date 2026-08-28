# Frozen Question-Theme Taxonomy

The canonical machine-readable taxonomy is [question-theme-taxonomy.json](question-theme-taxonomy.json). Version `1.0` uses narrow, falsifiable themes rather than broad labels such as “methodology concern.”

Freeze both the taxonomy version and ranked predictions before the meeting. A theme added after seeing actual advisor questions belongs to a new taxonomy version and cannot retroactively score the earlier meeting.

Each theme records:

- a stable theme ID;
- a bounded definition;
- inclusion and exclusion criteria;
- one concrete example;
- granularity at the specific missing-control, evidence, continuity, or interpretation gap level.

Annotators may assign more than one frozen theme to a question. Disagreements should be retained for review; do not broaden a definition merely to convert a miss into a hit.
