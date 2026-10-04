---
summary: Measure installed runtime coverage and verify its public Codecov report.
issue: uibcdf/ackredit#76
status: resolved
opened: 2026-10-01
closed: 2026-10-04
verification: measured
area: [ci, tooling]
guard: tests/test_coverage_workflow.py
normative:
blocked_by: []
supersedes: []
---

# Scoped runtime coverage

## What

Ackredit has executable Python code and a complete maintained test suite; runtime
coverage is applicable. Initial public inspection on 2026-10-04 finds a nonnumeric
badge, a branch HTTP 404 and no completed report. Missing data is not evidence
of non-applicability. The owning issue predates this implementation and is
cross-linked to MolSysSuite #69.

## How

`coverage.yaml` measures the complete unchanged suite against a normally installed
Ackredit wheel outside the checkout on Linux/Python 3.14. Its retained XML is
published from trusted `main` in a separate OIDC job using the verified official
Codecov action v7.1.1 at immutable commit
`303a32d7a59b442fa8d48b6a1cc6825c09c847a5`.
The producer runs weekly on Monday at 06:43 UTC and on manual dispatch; it adds
no second full suite to internal push/skip events. No coverage minimum is imposed.

## Why

Coverage describes which runtime Python statements the parent pytest process
executes. All package modules remain in the denominator, including optional
adapter paths not reached. Only generated `_version.py` constants are excluded.
Third-party dependencies, child processes, docs/examples and developer tools
are outside the percentage. Normalized installed/source path aliases preserve
repository file identity when the retained data is combined.

## What was refuted

A configured upload, queued Codecov application check or cached SVG cannot prove
an accepted complete report. Coverage does not certify scientific correctness,
all optional backends, a full OS/Python matrix or a public package candidate.

## Scope and exclusions

The live badge is withheld until a complete public report matches the tested
source and successful native uploader. The README will explain the last-uploaded
report and weekly/manual cadence, which can lag later internal commits. Central
registry updates and common policy remain owned by MolSysSuite #69.

## Acceptance criteria

Retain the XML, verify its package scope/percentage and actual upload, observe
Codecov's complete main-branch report for the same full source SHA and numeric
repository badge, then adopt the central generated badge and archive this record.
`tests/test_coverage_workflow.py` guards the cadence, full-suite measurement,
explicit scope, unchanged required floor, retained report and trusted uploader.

## Local producer qualification — 2026-10-04

A fresh temporary Python 3.14 environment normally installs the current wheel
with published Pytest Receptor 1.2.1. The full measured selection passes **1,556
tests without skips**. Its XML has **61 runtime modules**, **2,010 executable
lines**, **1,832 covered lines**, or **91.1442786%** line coverage. This is local
evidence, not a public Codecov report. A prior reused temporary environment had
old duplicate distribution metadata; it was replaced rather than lowering the
version guard or changing the required shared editable installation.

The workflow's report-scope verifier checks every runtime module, canonical
source path, unique line counts and covered totals before retention/publication.
Its actual code passes the measured XML and rejects a deliberately omitted
module in an offline regression. Nine focused coverage/tool-pin guard cases pass.
Only the parent process is measured; unrelated subprocess execution is not
combined. The pending hosted upload/public completion remains explicit.

## Hosted source and public acceptance — 2026-10-04

[Runtime coverage 37188364728](https://github.com/uibcdf/ackredit/actions/runs/37188364728)
passes both measurement and publication jobs at
`991084a4d0be3fddbc0f2f79a87818b3a8f0ad18`, using an ordinary installed wheel
on Linux/Python 3.14.7. Native evidence confirms successful external installed
smoke/provenance, scientific test selection, XML generation, scope validation,
retention and the exact artifact's OIDC uploader. GH Run Receptor reports 2/2
successful jobs with one retained artifact. The measured selection is **1,552
passed and 7 skipped**, not a zero-skip qualification. Skips retain the ordinary
profile's missing optional pdflatex/BibTeX engines and developer wheel-build,
versioning and lint tools. They are not hidden or converted into passing tests.

The XML contains all **61** runtime modules and **2,010** executable lines;
**1,821** lines are covered (**90.5970149%**). Its SHA-256 is
`4c4d63736dfde31bfe9443ff555ba91e958262cbfa62859089ab8fe8c4ba6347`.
Seven modules have no executable lines; Codecov's **54** nonempty-file count and
exact line/hit totals match this XML. The difference from the local measurement
retains its different environment/available-tool scope rather than selecting a
higher percentage.

The anonymous canonical central probe observes a **complete** `main` report for
that exact source, **90.59%** service coverage and a numeric live SVG rounded to
**91%**. Native uploader step times, service observation time, source commit time
and branch-cache time remain separate in the [committed receipt](../../devtools/receipts/runtime_coverage_76_2026-10-04.json).
The matching successful upload and complete report authorize the centrally
generated repository-specific badge. The README puts it after the truthful
Tests badge and explains the last-report, parent-process, optional-engine and
weekly/manual scope. No common floor is added and no scientific suite is added
to internal push events. This first observed upload is manual; a future scheduled
upload is not claimed before it executes.

The producer's routine [CI 37188297269](https://github.com/uibcdf/ackredit/actions/runs/37188297269),
[suite policy 37188297662](https://github.com/uibcdf/ackredit/actions/runs/37188297662)
and [publication policy 37188297533](https://github.com/uibcdf/ackredit/actions/runs/37188297533)
pass at that same implementation source. `tests/test_coverage_workflow.py` is the
addressable guard for the measured scope, full selection, retained XML,
trusted-main uploader and omitted-module refusal. Central inventory remains
owner-controlled under MolSysSuite #69; no runtime, release, package or
scientific certification is inferred from this coverage report.
