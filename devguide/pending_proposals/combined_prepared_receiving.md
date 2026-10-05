---
summary: Qualify the combined writer and immutable producer declaration optimizations.
issue: uibcdf/ackredit#99
status: active
opened: 2026-10-05
closed:
severity: medium
verification: asserted
area: [integration, performance]
guard: devtools/qualification/test_pyunitwizard.py::test_warmed_backend_plans_retain_credit_and_invalidate_by_value
normative:
blocked_by: []
supersedes: []
---

# Combined prepared attribution receiving checkpoint

## What

The installed receiving workflow still uses PyUnitWizard `33fec8a`, before its
resolved declaration-plan optimization #111. Ackredit #97 reduced repeated
writer allocation independently. Their existing receipts establish their own
inputs, not qualification of the combined current source bundle.

## How

Pin qualified PyUnitWizard closing source
`0e422d06b0af56e4dd2b43cafd00f059221eb405`. Add one mandatory installed test
covering real warmed Pint/unyt conversions with declaration reconstruction and
detachment forbidden. Check repeated independent captures, explicit target
units, software/article roles and original versions, enclosing graph, version
invalidation and nested metadata conflicts preserving completed science and
earlier captures. Retain its saved payload with the existing receiving artifacts.

Require seven passed tests per cell and the new proof in the provider-owned
aggregate. Keep normally installed imports, byte/resource verification, the
actual original 0.9.0 fallback and offline saved readers. Run the exact clean
development bundle across Linux/macOS arm64 and Python 3.11–3.14.

## Why

Faithful lightweight attribution must preserve the pipeline as allocations are
removed. Source inspection or an editable local probe cannot substitute for
the same normally installed files tested in every supported receiving cell.

## What was refuted

Do not infer cumulative qualification or speedup by adding percentages from
the two independent measurements. Do not reinterpret earlier six-test matrix
receipts as evidence for the new warmed path. An editable version string does
not determine which runtime files it imports.

## Scope and exclusions

Development qualification only: no runtime API, dependency floor, canonical
guide, public file, tag or provisional classification changes. PyUnitWizard
owns its release and measurements. Ackredit #84/#87 and MolSysSuite #97 retain
the separate stability and receiving decisions.

## Acceptance criteria

- Real Pint/unyt reuse copies no declarations and retains exact per-capture
  bibliography, uses and graph; version/value changes retain diagnostics.
- Previous gate counts, missing proof, incomplete evidence or changed installed
  files cannot pass aggregation.
- Relevant source/quality/reporting checks and all eight exact installed
  receiving cells pass; downloaded evidence verifies independently.
- Retain exact source/wheel identities and bounded results in the record and
  owning issues. Archive this record on completion; do not promote the APIs.
