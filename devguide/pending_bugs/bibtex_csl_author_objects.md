---
summary: BibTeX stringifies explicit CSL author objects instead of preserving author identity.
issue: uibcdf/ackredit#78
status: partial
opened: 2026-10-02
closed:
severity: medium
verification: reproduced
area: [formats, attribution]
guard: tests/test_bibtex_csl_authors.py
normative:
blocked_by: []
supersedes: []
---

# Explicit CSL author objects in BibTeX

## What

Sabueso's optional attribution pilot (uibcdf/sabueso#108, provider #75) cites
the UniProt description article with `{"literal": "The UniProt Consortium"}`.
Detached bibliography and CSL-JSON retain this author. BibTeX instead writes
an escaped Python dictionary, so the exported citation loses its author identity.

## How

At committed provider `4577c83`, 14 of the initial 15 focused cases fail;
the plain-string compatibility control passes. The correction processes explicit
objects before converting values to text, escapes their content and then adds
BibTeX syntax braces around literal authors. Personal objects use BibTeX's
`von Last, Jr, First` syntax, preserving suffix and both particle fields.
Delimiters within explicitly declared personal parts are brace-protected.

The [CSL specification](https://docs.citationstyles.org/en/stable/specification.html#name-part-order)
defines separate personal-name parts. BibTeX cannot encode the independent
CSL particle display and sorting options; the documented mapping retains the
declared text, and CSL-JSON retains the original full objects.

## Why

A bibliography must identify an explicitly declared collective correctly.
Consumers should retain original metadata and call the provider renderer,
rather than introducing their own BibTeX repair.

## What was refuted

A braced plain string is escaped as text when registered, and an unbraced
collective is interpreted as a personal name. Neither replaces an explicit
literal object. Guessing which plain strings represent organizations would
change existing name interpretation and is outside this correction.

## Scope and exclusions

BibTeX author rendering, focused regressions and registration documentation.
No name inference, bibliography schema change, consumer implementation,
enrichment, optional hook or guide contract change. Work uses an isolated
checkout because the primary checkout contains independent maintainer BibTeX,
LaTeX, notebook and citation-key edits; those nine files are preserved.

## Acceptance criteria

- Detached rendering and the session renderer preserve mixed author order.
- Explicit literal authors are brace-protected after escaping TeX characters.
- Personal names retain given/family, suffix and declared particle text.
- Existing `.bib` provenance, round trips and plain-string behavior survive.
- Rendering restored attribution adds neither registry entries nor workflow credit.
- A real installed BibTeX processor verifies author count and name parts.
- Local gates pass before committing; publication and issue lifecycle are explicit.

## Validated correction (2026-10-02)

The isolated Python 3.13 source suite passes 1,528 tests. All 17 focused author
regressions pass, including an executed `/usr/bin/bibtex` processor: its
`num.names$` and `format.name$` operations retain the single collective author,
personal suffix and particles. Ruff check/format and devguide index checks pass.
The first full run identified two test-infrastructure corrections (index
regeneration and fixture-owned registry replacement); both are fixed without
changing shared isolation rules. The complete rerun passes.

The correction is prepared independently of the nine maintainer files in the
primary checkout. The record stays partial until the provider fix is merged;
the durable regression above is the eventual closure guard.
