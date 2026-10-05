---
summary: CSL export drops original CFF work kinds, date precision and page counts.
issue: uibcdf/ackredit#96
status: resolved
opened: 2026-10-05
closed: 2026-10-05
severity: medium
verification: reproduced
area: [bibliography, formats]
guard: tests/test_cff_csl_export.py::test_discovered_reference_exports_in_a_fresh_offline_reader
normative:
blocked_by: []
supersedes: []
---

# CSL export drops original CFF work kinds, date precision and page counts

## What

After #95 preserves CFF identity and publication metadata, CSL ignores original
`_cff_type`, full publication/release dates and page counts. A preferred book
published on 2024-02-29 with 240 pages reaches the reader as `document`, year
2024 and no `number-of-pages`.

## How

Normally installed baseline `898493f` reproduces the loss outside the checkout.
Its parsed reference and detached payload retain the type, date and count, so
the gap belongs to the report's bounded mapping, not discovery or capture.

## Why

Reference managers choose formatting from the work's category and available
date precision. CSL defines distinct book/report/thesis/periodical kinds and
page-count versus page-range fields. Primary contracts are
[CFF 1.2.0](https://github.com/citation-file-format/citation-file-format/blob/1.2.0/schema-guide.md)
and [CSL 1.0.2](https://docs.citationstyles.org/en/stable/specification.html).

## What was refuted

No network enrichment, schema migration or added runtime dependency is needed;
the missing information already exists in the original payload. CFF source
kinds must not be relabeled as BibTeX source kinds to reuse their mapping.

## Scope and exclusions

Extend explicit CSL mappings for unambiguous CFF kinds, date precision and page
counts. Preserve original fields, literal dates, existing BibTeX interpretation
and unknown-kind fallback. State date precedence; do not mix contradictory
components or infer unspecified days. No complete CFF validation, sibling
source changes, maintainer BibTeX/LaTeX edits or provisional API promotion.

## Acceptance criteria

New guards first fail against the normally installed baseline and pass on the
normally installed candidate outside source. A fresh reader with producer and
network access blocked exports preserved metadata without crediting execution.
Run all repository gates, retain precise evidence and archive this record.

## Resolution (2026-10-05)

An independent CFF-to-CSL table maps fifteen unambiguous original kinds, keeping
existing BibTeX interpretation and unknown-kind fallback. The shared private
calendar reader accepts only full valid YYYY-MM-DD dates. CSL retains available
date precision, uses publication before release dates, and respects explicit
year/month conflicts and literal years. Parsing does not manufacture a year
from compact/week dates or another date field when publication is literal.
CSL `number-of-pages` receives the count separately from `page`.

The forty-two guards first run against normally installed clean baseline
`898493f`: thirty-one fail and eleven pass. All forty-two pass against the
normally installed development candidate outside the checkout. Both use the
unchanged pinned shared `installed_noarch.run_tests` with same-interpreter
provenance checks before and after; installed runtime bytes equal their source.
Two end-to-end guards discover an importable package, preserve its original
payload and export book/dataset bibliography in a fresh subprocess with producer
imports and network connections blocked. The reader records no new credit.

The [qualification receipt](../../devtools/receipts/cff_csl_export_2026-10-05.json)
retains baseline/candidate versions, hashes, complete receptor outcomes and
qualification-tool warnings. Transformation occurs during discovery/reporting,
not during scientific calls. No core dependency, public API classification,
portable schema, sibling source, canonical guide or public archive changed.

All local gates pass: 1,788 full-suite tests, Ruff checks/format, generated
report indexes and strict Sphinx documentation. Hosted CI and public delivery
remain separate evidence; this record does not claim a new public archive.
