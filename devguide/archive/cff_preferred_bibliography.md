---
summary: Typed preferred CFF works lose their bibliography and inherit software identity.
issue: uibcdf/ackredit#95
status: resolved
opened: 2026-10-05
closed: 2026-10-05
severity: medium
verification: reproduced
area: [discovery, bibliography]
guard: tests/test_cff_preferred_fidelity.py::test_discovered_preferred_article_retains_its_own_bibliography
normative:
blocked_by: []
supersedes: []
---

# Preferred CFF works lose their bibliography and inherit software identity

## What

Public 0.10.1 treats a preferred article as software, loses publication fields,
and borrows the root software's omitted DOI and version. This follows from both
`parse_cff` merging different works and discovery forcing `type="software"`.

## How

A clean public Linux/Python 3.14.7 installation reproduces the defect using a
software CFF with version 9.0.0 and DOI 10.1234/software, plus a preferred article
with year 2024, journal, volume 12, issue 3 and bounds 101–115. CSL output has the
article's title/authors but software type/DOI/version and none of those fields.

## Why

The [CFF 1.2.0 specification](https://github.com/citation-file-format/citation-file-format/blob/1.2.0/schema-guide.md#preferred-citation)
identifies a preferred work as another reference selected instead of the root.
Accurate attribution requires keeping that identity and its own bibliography.

## What was refuted

The exact released public bytes reproduce this; it is not editable installation
drift, a dependency failure, formatter escaping or a shared publishing defect.
The existing author/DOI parsing guards do not cover work type or publication
fields. CFF `pages` means page count, so it cannot become a page range.

## Scope and exclusions

Fix CFF selection, supported field normalization and hook discovery. Preserve
manual precedence, root software/shipped-paper behavior and historical fallback
for an untyped partial preferred block. Typed preferred works do not borrow
root/shipped fields. Do not credit the complete `references` list, add network
access/dependencies or stabilize provisional provider APIs. Consumer guide
copies and sibling source are outside scope.

## Acceptance criteria

Durable guards first fail against 0.10.1, then verify preferred work identity,
original bibliography, own/missing DOI, root dataset type, page bounds versus
counts, selected publication date, manual precedence, and detached export without
crediting execution. Run all local gates and archive the resolved record.

## Resolution (2026-10-05)

The bounded CFF reader selects typed preferred works without root fallback,
normalizes publication metadata, and keeps unknown work kinds under `other`
with original `_cff_type` metadata. A preferred work gets its own discovered
identity; root CFFs retain matching software/dataset identities and distinct
shipped papers. The hook uses trusted internal registration for parser-generated
bookkeeping; public registration still rejects reserved user-supplied fields.

The eighteen regression guards execute through the unchanged pinned shared
`installed_noarch.run_tests` helper, with same-interpreter provenance checks
before and after. On the clean public 0.10.1 archive, sixteen fail and two pass.
All eighteen pass on the normally installed development candidate outside the
checkout, whose CFF/hook bytes equal this change. The
[qualification receipt](../../devtools/receipts/cff_preferred_2026-10-05.json)
retains exact archive identity, runtime/test hashes, receptor integrity and
separate baseline/candidate outcomes. The reported assert-rewrite warnings
come from preimported qualification tools; they are retained, not suppressed.

The existing CFF/authority guards also pass, including partial untyped fallback
and software bindings/shipped-paper behavior. The new detached-report guard
removes the reader's registry through a reversible monkeypatch; it does not
erase import-time declarations for other tests. Development release notes make
clear that the unchanged public 0.10.1 archive does not contain this repair.

All local gates pass: Ruff checks/format, 1,741 full-suite tests, generated
report indexes and strict Sphinx documentation. No hosted-matrix or new-public-
archive claim follows from these local results.
