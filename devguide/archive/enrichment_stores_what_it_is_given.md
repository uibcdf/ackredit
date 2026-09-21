---
summary: Fetched metadata was applied unguarded, so entities became characters, a nameless creator became an author, and a record with no title ended the run.
issue: uibcdf/ackredit#41
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: high
verification: measured
area: [core, discovery]
guard: tests/test_enrichment_records.py
normative:
blocked_by: []
supersedes: []
---

# Enrichment stores what it is given

## What

`Registry.enrich_item` fetches from Crossref and DataCite and applies the result. The
fetching and the caching were guarded; applying the record was not.

**HTML entities were stored as characters.** Crossref escapes its text. For
`10.1109/MCSE.2007.55` it returns the container title as
`Computing in Science &amp; Engineering`; Ackredit stored that string, and the LaTeX
escaper then escaped the `&` of `&amp;`:

```bibtex
journal = {Computing in Science \&amp; Engineering}
```

The bibliography printed `&amp;`.

**A record with no title raised `IndexError`.** `data.get("title", [item_id])[0]` uses its
default only when the key is absent, and an empty list is not absent. Nothing caught it: it
escaped into the caller's code, and `enrich_all` stopped there, leaving every later item
unenriched. Every other failure in that function degraded to a diagnostic; this one ended
the run.

**A creator with no name became an author.** The DataCite mapping is
`a.get("familyName", a.get("name"))`, which is `None` when a record has neither, and the
apply step formatted it into `author = {None}`. An empty Crossref creator produced `''` the
same way.

## How

`_first` returns the first element of a list only when there is one, and unescapes it;
`_record_authors` drops a creator that names nobody. Applying a record is wrapped, so a
shape nobody anticipated raises `ACKREDIT-W015` rather than the caller's run.

Unescaping happens on read rather than on write, so the cache stays a faithful copy of what
the API answered and a file written before this is repaired the next time it is used.

## Why

This is the invented-authorship defect of `uibcdf/ackredit#26` arriving from the network
instead of from Ackredit's own table, and the escaping family of `#7`, `#9`, `#25` and
`#37` arriving *before* the renderers rather than inside them. The renderers were right;
what they were handed was already wrong.

The `IndexError` is a different failure and the worse one to meet: enrichment is an
optional convenience, and it ended a scientific run over a metadata quirk in someone else's
record.

## What was refuted

- **Unescaping on the way into the cache.** It makes the cache a transformed copy rather
  than an answer, so a future change to the transformation cannot be applied to what is
  already stored, and every existing cache file would keep its entities.
- **A blanket `try` around the whole of `enrich_item`.** It already has guards where
  failures belong — network, cache read, cache write — and one more around everything would
  hide a defect in the code rather than a quirk in the data. The extraction is total, and
  the wrapper covers only the step that reads a record.
- **Keeping a nameless creator as an empty author to preserve the count.** An author list
  whose length is right and whose names are wrong is worse than a short one; BibTeX renders
  it as a person either way.
- **Reporting every dropped creator and absent title.** Missing data is not a failure, and
  a warning for each would bury `ACKREDIT-W006`, which is the one that means something went
  wrong.

## Scope and exclusions

Covers applying a fetched record. Where the cache lives — `~/.cache/ackredit`, which
ignores `XDG_CACHE_HOME` — is a separate question and not touched here.

## Acceptance criteria

- entities in a title, a journal and an author name arrive as the characters they
  represent, and the cache still holds what the API answered — met;
- a record with an empty title leaves the field unset, and `enrich_all` continues past
  it — met;
- a creator that names nobody is not an author, and nothing called "None" or "" reaches a
  bibliography — met;
- no shape of record raises, and one that cannot be read is reported — met;
- `tests/test_enrichment_records.py` guards it, 19 tests, and catches each of the three
  defects independently when it is reintroduced. The tests apply records through a cache of
  their own and cannot reach the network.
