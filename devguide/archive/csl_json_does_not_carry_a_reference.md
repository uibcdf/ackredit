---
summary: CSL-JSON raised on a year Ackredit itself produces, and mapped a short fixed list so a book reached a reference manager unformattable.
issue: uibcdf/ackredit#44
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: high
verification: measured
area: [formats]
guard: tests/test_csl_fidelity.py
normative:
blocked_by: []
supersedes: []
---

# CSL-JSON does not carry a reference

## What

**It raised on a year Ackredit itself produces.**

```
load_bibtex on an entry with  year = {in press}
  WARNING ACKREDIT-W009: the year is not a number and was kept as written
                         (Hint: formats expecting a numeric year may render it unchanged)

report(format="csl-json")
  ValueError: invalid literal for int() with base 10: 'in press'
```

`ACKREDIT-W009` documents that a biblatex date range and "in press" reach a renderer
legitimately, and its hint promises at worst that a format renders the value unchanged. One
of the seven raised instead, uncaught.

**It dropped the fields a reference manager formats with.** For a book and a conference
paper read from a `.bib` file, it emitted `author`, `issued`, `title` and `page`, and lost
`publisher`, `isbn`, `series`, `edition`, `booktitle` and `editor`. CSL defines a field for
every one of them.

**Every entry was typed `document`**, because Ackredit's six types flatten `@book` and
`@phdthesis` alike into `other`. A manager told that a book is a document cannot format it
as a book. This was found while fixing the two above and is fixed with them.

## How

A numeric year becomes `date-parts` and anything else becomes `issued: {"literal": ...}`,
which is CSL's own mechanism — the same discipline as `uibcdf/ackredit#38`: structure what
can be proven and never guess.

The mapping covers what CSL defines, with `editor` going through `csl_name` as authors do,
because editors are people a manager sorts and abbreviates the same way. Two CSL fields
take several of Ackredit's keys and the first present wins: `container-title` from a
journal or a booktitle, `publisher` from a publisher, a school or an institution, which is
where CSL puts a thesis's university.

The entry type a `.bib` file used, kept by `uibcdf/ackredit#43`, is read into CSL's
vocabulary, falling back to Ackredit's own mapping for an item that came from no file.

## Why

This renderer's whole reason to exist is being read by a machine, and the third time this
shape appeared in it: `uibcdf/ackredit#27` in the `json` format, `#38` in these same
authors, and now the rest of the citation. A book exported to Zotero with no publisher and
no ISBN is a reference the manager cannot format, and nothing said so.

The `ValueError` is the more serious half. Ackredit warned that the year was text, promised
the value would at worst render unchanged, and then raised out of a public renderer on the
state it had itself created.

## What was refuted

- **Passing every key through, as the BibTeX renderer now does.** BibTeX ignores a field it
  does not know; CSL-JSON is a schema, and a processor has no use for an undefined key. The
  mapping has to be bounded, and the guard is what says it is wide enough.
- **Coercing a non-numeric year to a number, or dropping it.** Dropping loses the only
  date there is, and coercion invents one. "in press" is information.
- **Extending Ackredit's type vocabulary so `other` could say "book".** Refused for the
  same reason as in `uibcdf/ackredit#43`: it would bind the vocabulary to one format, when
  CSL and BibTeX disagree about types and CFF has neither.
- **Emitting an editor as a string.** It is the defect closed in `#38` for authors, one
  field across.

## Scope and exclusions

Covers the CSL-JSON renderer. Fields Ackredit stores that CSL does not define — a
`howpublished`, a BibTeX `month` — are not emitted, and that is the schema's decision
rather than a loss.

## Acceptance criteria

- no format raises on a year Ackredit kept as text, checked across all seven — met;
- a non-numeric year arrives as a literal date and a numeric one as date-parts — met;
- every field CSL defines for a book, a conference paper and a thesis arrives — met;
- an editor is a name object — met;
- the entry type reaches CSL's vocabulary, and an item from no file keeps Ackredit's
  mapping — met;
- `tests/test_csl_fidelity.py` guards it: 3 of its 27 tests fail when the literal date is
  removed and 8 when the field mapping is.
