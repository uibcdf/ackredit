---
summary: Loading a .bib file and writing it back flattened its entry types and dropped every field outside a list chosen in advance.
issue: uibcdf/ackredit#43
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: high
verification: measured
area: [core, formats]
guard: tests/test_bibtex_round_trip.py
normative:
blocked_by: []
supersedes: []
---

# A .bib file does not survive a round trip

## What

Measured before the fix, with a book, a conference paper and a thesis:

```bibtex
@book{b1, author = {Knuth, Donald E.}, title = {The {TeX}book},
      publisher = {Addison-Wesley}, year = {1984}, isbn = {0-201-13447-0},
      series = {Computers and Typesetting}}
```

came back as

```bibtex
@misc{b1,
  title = {The {TeX}book},
  author = {Knuth, Donald E.},
  year = {1984}
}
```

The conference paper lost `booktitle`, `pages` and `editor`; the thesis lost `school`.

Two causes.

**The entry type was discarded on the way in.** `_parse_entry` maps `@book` to Ackredit's
`other` and the renderer maps `other` to `@misc`. Ackredit's vocabulary has six types and
BibTeX has fourteen, so everything outside the overlap was flattened.

**The renderer emitted a list of fields chosen in advance**: `title`, `author`, `year`,
`doi`, `url`, `note`, plus `journal`, `volume`, `number` and `pages` only when the type was
`article`. Everything else was dropped although `_parse_entry` had stored it.

## How

An item read from a `.bib` file keeps the entry type it had, in `_bibtex_type`, and the
renderer writes it back. It is bookkeeping rather than a field, hence the underscore, and
the `json` renderer already omits those.

The renderer emits the translations Ackredit needs — `authors` becomes `author` — and then
every other key the item carries, alphabetically. A `.bst` style ignores a field it does
not know, so carrying one costs nothing and dropping one costs the bibliography.

`howpublished` names the kind BibTeX cannot express in its entry type, so it is no longer
added when the entry already says what it is.

## Why

This is the shape of `uibcdf/ackredit#27`, where the `json` format emitted six fixed keys
and discarded the DOI: a renderer with a hardcoded field list silently discarding what it
was given. It is also not only a round-trip defect — a host registering an item with
`publisher=` lost it the same way, and nothing said so.

Found immediately after `uibcdf/ackredit#42`, in the same file and the same pass. That one
made the output invalid; this one made it incomplete, which is the harder of the two to
notice.

## What was refuted

- **Extending Ackredit's type vocabulary to cover BibTeX's fourteen.** It would make the
  vocabulary a mirror of one format's entry types, and CSL-JSON, CFF and package metadata
  each have their own. Keeping the original alongside the mapped type costs one key and
  keeps every renderer free to map as it needs.
- **Adding `publisher`, `isbn`, `school` and the rest to the emitted list.** It fixes the
  measured cases and leaves the next field to be discovered the same way, which is how the
  list came to be fixed in the first place.
- **Emitting `id` and `type` too, for symmetry.** They are Ackredit's keys, not
  bibliographic fields, and `id` is already the citation key.
- **Comparing the two files textually in the guard.** Field order and whitespace differ
  legitimately; the test reads both sides as key-value pairs and asserts nothing is lost,
  so it checks the claim rather than a formatting.

## Scope and exclusions

Covers the BibTeX renderer and the entry type. The other renderers select fields for
reasons of their own: CSL-JSON maps to a schema, and `provenance` is not a bibliography.

## Acceptance criteria

- `@book`, `@inproceedings` and `@phdthesis` come back as themselves — met;
- every field in the source file is present in the output, checked by parsing both rather
  than by listing them — met;
- a field a host registered is emitted, and Ackredit's own keys are not — met;
- an item that never came from a file maps as before, `howpublished` included — met;
- a field from a file is still passed through unescaped, so the provenance rule
  survives — met;
- `tests/test_bibtex_round_trip.py` guards it: 3 of its 16 tests fail when the type is
  flattened again and 10 when the field list is fixed again.
