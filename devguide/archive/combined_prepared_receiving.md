---
summary: Qualify the combined writer and immutable producer declaration optimizations.
issue: uibcdf/ackredit#99
status: resolved
opened: 2026-10-05
closed: 2026-10-05
severity: medium
verification: reproduced
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

## Resolved outcome — 2026-10-05

Ackredit `cf21cc178720e106081699e9c91c49199aa24122` and the selected clean
PyUnitWizard closing source pass [receiving run
37309592507](https://github.com/uibcdf/ackredit/actions/runs/37309592507):
eight supported cells, seven tests each, 56 passed without skips/deselections,
and a successful aggregate. Each cell normally installs the same three wheels.
The candidate wheel SHA-256 is
`eccdb6983972f234935c4f27867930f8faf0a9ba77c74bab4ce1766d586ef556`;
the producer wheel SHA-256 is
`3f5f0a9c97d7940958a1a5e2ba676733df4e3667c324d0b6e974baf039350e09`.

All ten native artifact ZIP digests and extracted files verify independently.
The supported Pytest Receptor reader accepts every complete event stream;
local reconstruction equals the hosted aggregate. Prepared proofs retain
two Pint and three unyt references per original/reused result, original versions
and description-article roles. Version invalidation and nested metadata conflicts
retain earlier captures and completed numerical/unit results. The original
source-built 0.9.0 fallback and fresh offline readers remain executed.

The separate local normally installed bundle passes seven guards on Python
3.14.7 with `pip check`; it reuses the unchanged public scientific dependency
foundation. Its ZIP bytes differ from hosted wheels and are retained separately.
Relevant source/provider/reporting selections pass 94 tests, Ruff check/format
and devguide indexes pass, and strict Sphinx passes after completing only the
temporary tool environment and enabling the official intersphinx lookup.
Exact-source [CI 37309540581](https://github.com/uibcdf/ackredit/actions/runs/37309540581)
passes seven jobs; suite/publication policy runs 37309541212/37309541269 pass.
All remote conclusions are inspected through GH Run Receptor.

The reviewed receipt is
`devtools/receipts/combined_prepared_receiving_99_2026-10-05.json`. No new timing
claim is derived from this functional checkpoint. Documentation closeout does
not change the tested runtime or qualification inputs. #84/#87 remain provisional;
the public 0.10.1 archive, dependency floors and client guides are unchanged.
