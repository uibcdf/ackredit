---
summary: The Markdown report and the notebook summary joined inverted names with commas, so two authors read as four.
issue: uibcdf/ackredit#67
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: medium
verification: reproduced
area: [reporting]
guard: tests/test_author_lists.py
normative:
blocked_by: []
supersedes: []
---

# Authors run together in the reports a person reads

## What

Authors are stored as `Family, Given` — what `CITATION.cff` produces and what the
integration guide asks a host to copy. The Markdown report and `ackredit.summary()`
joined them with `", "`, so `["Ruiz, Ana", "Gómez, Luis"]` became
`Ruiz, Ana, Gómez, Luis`: two people or four, and no reader can undo it. BibTeX joins
with ` and ` and was never affected.

Found while writing the example workflow: the example libraries are the first data in
the repository with more than one inverted author on an item that gets rendered, and no
test or page pinned the joining. It was never chosen.

## How

`ackredit/formats/_names.py` gains `author_list`, which separates authors with `"; "`,
escapes each one on its own, and writes a CSL name object as a name rather than as a
dictionary. Both renderers call it, so they cannot drift apart again.

## Why

These are the two lists a person copies from. A list whose boundaries cannot be read
reaches a manuscript with the wrong number of authors.

## What was refuted

Joining with `" and "` like BibTeX reads well for two names and badly for ten, and
"Ruiz, Ana and Gómez, Luis and Pérez, Juan" is still a list a reader has to parse.
Rewriting names to `Given Family` would invent an order the registrant did not write,
which `_names.py` already refuses for CSL-JSON.

## Scope and exclusions

Markdown and the notebook summary. BibTeX, CSL-JSON, LaTeX and JSON carry authors in
their own structured forms and are unchanged; the plain-text and provenance formats show
no authors.

## Acceptance criteria

`tests/test_author_lists.py` renders two inverted names through both lists and recovers
exactly the names registered; against the previous renderers both fail with
`['Ruiz, Ana, Gómez, Luis']`.
