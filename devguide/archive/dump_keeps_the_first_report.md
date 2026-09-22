---
summary: dump() wrote the first of several formats to a file and dropped the rest, ignored the file's name, and let two formats sharing an extension overwrite each other.
issue: uibcdf/ackredit#65
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: high
verification: reproduced
area: [reporting]
guard: tests/test_dump_contract.py
normative:
blocked_by: []
supersedes: []
---

# `dump` keeps the first report and drops the rest

## What

Found while running a host library end to end — a package with `_ackredit.py`,
`register_item`/`bind`, a `@scoped_usage` function, and a script and a notebook that
collect the report at the end. All of that worked. `dump`, whose only job is to put the
report on disk, lost it three ways, each in silence:

- `dump("citations.bib", formats=["bibtex", "markdown"])` wrote the BibTeX and
  discarded the Markdown. The code said so in a comment: "we just save the first format
  or markdown".
- `dump("refs.bib")` wrote **Markdown** into a file named `.bib`. The default list of
  four formats was filled in before the branch that handles a file, so the first of
  them, `markdown`, was what every unqualified file received. A user pasting that into a
  LaTeX build gets a Markdown document with a BibTeX name.
- `dump(directory, formats=["text", "provenance"])` wrote both to
  `ackredit_report.txt`, because the two formats share an extension. The file held
  whichever came last.

## How

A file takes one report. Asked for several, `dump` raises `ACKREDIT-E009`
(`ManyFormatsOneFileError`, also a `ValueError`) and writes nothing. Asked for none, it
reads the name: the longest extension wins, so `refs.csl.json` is CSL-JSON rather than
JSON, and the renderer table's own order breaks ties, so `.txt` is plain text. A name
that asks for nothing gets Markdown, as before. An explicit format the name contradicts
is written as asked, with `ACKREDIT-W018`, because a later reader trusts the name.

In a directory, formats sharing an extension are written as
`ackredit_report_<format>.<ext>`. Only a clash is renamed, because the LaTeX report says
`\bibliography{ackredit_report}` and the `.bib` must keep that name.

## Why

This is the silent-data-loss class closed everywhere else in the library — `json`,
CSL-JSON, the BibTeX round trip, aggregation journalling and the DueCredit bridge — in
the one function a user calls precisely to keep the result.

## What was refuted

Writing sibling files for a file path with several formats (`citations.bib` and
`citations.md`) was considered and refused: it would create files the caller never
named, and the contradiction is the caller's to resolve. Refusing the extension mismatch
outright was refused too: the caller was explicit, and warning keeps an intentional
choice possible while saying what the name now hides.

## Scope and exclusions

**This changes what a stable name does.** `dump("refs.bib")` now writes BibTeX, and
`dump("notes.txt")` plain text, where both wrote Markdown. It lands before 1.0.0, where
the deprecation policy in `docs/content/about/stability.md` does not yet bind, and by
that policy's own test — the promise, not the mechanism — it restores the promise rather
than changing it: `dump` saves the report you asked for, and a `.bib` file of Markdown is
not that. The release notes for the next tag must say so.

`report()` and the directory defaults are unchanged.

## Acceptance criteria

`tests/test_dump_contract.py` holds each rule; against the previous `dump` body, 11 of
its 16 tests fail. The five that pass on the old code are there to stop an
overcorrection: an agreeing name, an alias and a meaningless name stay silent, and the
default directory keeps the names the LaTeX report relies on.
