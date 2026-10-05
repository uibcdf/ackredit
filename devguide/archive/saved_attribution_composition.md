---
summary: Compose shared bibliography without conflating independent original result graphs.
issue: uibcdf/ackredit#102
status: resolved
opened: 2026-10-05
closed: 2026-10-05
severity: medium
verification: reproduced
area: [portability, reporting]
guard: tests/test_attribution_bundle.py
normative:
blocked_by: []
supersedes: []
---

# Saved attribution composition

## What

Roadmap theme I needs a reusable offline composition operation after the CLI
milestone #101. Scientific results can reuse references and target labels while
having independent contexts and graphs. Their original boundaries must survive.

## How

`compose_attributions` returns a detached `AttributionBundle`. Its separate
`ackredit.attribution_bundle@1` envelope contains complete original schema-1
members and caller-owned name/context. Preflight equal IDs against complete
bibliographic records; reject conflicts before returning. Shared bibliography
is exported once, while workflow/provenance reports retain per-member graphs.
The explicit CLI bundle mode uses the same provider-owned reader and renderers.

## Why

Unioning independent target-name graphs can create paths no result recorded.
Overwriting producer context or deduplicating entire input results also loses
evidence. A named bundle preserves inputs without crediting another calculation.

## What was refuted

Do not overwrite metadata, guess DOI equivalence, merge software releases,
rename original scientific targets, interpret input order as chronology, or
alter the released schema-1 structural meaning. No live-session aggregation,
producer import, lookup or new execution credit is needed.

## Scope and exclusions

Additive Ackredit tool/format and CLI. The new names have deliberately recorded
pre-1.0 stable intent; the already released portable promise is separate from
this unpublished envelope. Existing provisional names are not promoted. No
dependency, shared adoption requirement, client code/guide or release/tag change.

## Acceptance criteria

- Detached round trips retain each original name, context, bibliography, use
  and graph, including duplicate/reordered/empty inputs and shared graph edges.
- Equal IDs share references; conflicting metadata refuses the entire bundle,
  preserves originals and distinguishes software versions by explicit IDs.
- Workflow/reference numbering and offline fresh CLI/export are faithful.
- A real multi-result producer workflow is retained separately from frozen
  reader fixtures; source and normally installed checks retain actual identities.
- Relevant quality/reporting/documentation checks and exact-head CI pass;
  archive this record and close the implementation issue on completion.

## Source checkpoint — 2026-10-05

The chosen tool, separate envelope, shared-reference workflow renderer and
explicit CLI reader are implemented. Python 3.14.7 source checks pass 1,915
tests without skips; the focused composition/reader/format/API/diagnostic/
qualification selection passes 290. Ruff check/format, report indexes and
strict nitpicky Sphinx pass. Existing individual workflow tests retain their
meaning after factoring shared reference rendering into its owning module.

The installed receiving gate now requires eight passed cases and all three
composition proofs per supported cell. Clean candidate build, actual scientific
receiving and exact-head hosted qualification remain to execute before closing
this issue. These source results neither qualify a public artifact nor promote
the observer/prepared APIs.

## Installed and hosted outcome — 2026-10-05

Implementation source `95ada1a53e7ffcbd8db3ea0165b5f9a03db0966e` passes
[ordinary CI](https://github.com/uibcdf/ackredit/actions/runs/37362311287)
(seven jobs) and both policy lanes. The normally installed
[receiving matrix](https://github.com/uibcdf/ackredit/actions/runs/37362423664)
passes all eight Linux/macOS arm64 × Python 3.11–3.14 cells and the aggregate:
64 tests, no skips/deselections and ten retained artifacts. The pinned actual
PyUnitWizard producer includes its resolved #111 optimization. The original
0.9.0 fallback remains a separately built, normally installed baseline.

All ten original ZIP archives match GitHub's digest and their extracted bytes.
Local reconstruction through the owning qualification tool equals the hosted
matrix. Each cell's complete, integrity-valid receptor stream verifies; its
saved bundle reconstructs with four complete original members and four shared
references. Its workflow rendering equals the retained report. Independent
producer-free readers report zero producer imports and new credits, unchanged
payloads and independent graphs.

A separate local Python 3.14.7 environment also passes all eight scientific
tests and `pip check` with normally installed candidate/producer wheels. Local
and hosted archives have distinct recorded byte identities. This local check
reuses the shared dependency foundation; unyt/sympy/mpmath were added only to
the temporary environment. It is not a new clean public installation.

The [reviewed receipt](../../devtools/receipts/saved_attribution_composition_102_2026-10-05.json)
retains exact source/wheel identities, original archive hashes, cell versions,
proof hashes, offline assertions and scoped local results. The guard exercises
detachment, conflicts, original graphs and fresh CLI refusal/reading; the
scientific gate independently uses real Pint/unyt results, reused and empty
inputs, conflicts and the external-process reader. These tests protect the
failure mechanism rather than merely counting administrative completion.

This completes theme I's implementation and development qualification. Public
Ackredit remains 0.10.1; no tag, published Conda file, stable promotion of
`observe_calls`/`prepare_credit`, consumer minimum or shared adoption is implied.
The separate unpublished bundle preserves the original schema-1 meaning.

## Documentation-head qualification correction — 2026-10-05

The implementation/source and eight-cell installed evidence above remain valid
for original producer `95ada1a`. Later documentation-only head `408c45e` has
incomplete hosted gates: CI 37365792898 passes five jobs, but Linux Python
3.11/3.13 jobs and suite policy 37365793949 are cancelled before any steps in
both attempts 1 and 2. Targeted check-run annotations explicitly report that a
hosted runner could not acquire the jobs after multiple attempts. The single
bounded `--failed` recovery did not resolve acquisition. Publication policy
37365793999 passes. Both overall affected runs remain failures; no cancelled
job is classified as a passed test or shared publisher defect.

Ackredit #102 remains open for this exact-head evidence/recovery, separately
from completed implementation and retained installed qualification. Do not
infer administrative closure or public delivery from this source record.
Subsequent unskipped component checkpoints can establish their own expanded
scope; preserve original producer/archive identities and all missing evidence.
