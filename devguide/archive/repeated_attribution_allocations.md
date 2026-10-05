---
summary: Avoid redundant allocations when recording repeated attribution.
issue: uibcdf/ackredit#97
status: resolved
opened: 2026-10-05
closed: 2026-10-05
verification: reproduced
area: [core, performance, integration]
guard: tests/test_prepared_credit.py::test_repeated_prepared_credit_retains_new_parents_and_independent_results
normative:
blocked_by: []
supersedes: []
---

# Repeated attribution allocations

## What

Repeated fixed uses and graph nodes allocate temporary dictionaries and sets
after the same observation has already been retained. This is unnecessary work
in the locked session and capture paths, including prepared backend credit.

## How

Retain use keys per builder and create graph nodes only when absent. Continue
registry comparison and bibliography conflict preflight before every repeated
credit. New parents, independent captures and journal state changes must still
be observed. Keep existing locks and public validation/detachment.

## Why

The installed real PyUnitWizard benchmark and a 3,000-conversion profile locate
repeated graph/use work within the remaining fixed attribution cost. Measure
the original and candidate with identical scientific dependencies, retain raw
samples and identify installed package files. Profiling locates work; it does
not demonstrate a speedup.

## What was refuted

Do not skip bibliography validation because a use key is already present.
Session deduplication cannot replace per-capture observation. A previously seen
target can acquire another parent. Do not cache public mutable input identities
or optimize the sibling producer by copying its implementation into Ackredit.

## Scope and exclusions

Ackredit-owned writer allocation only. PyUnitWizard's repeated declaration
copies are reported separately in uibcdf/pyunitwizard#111. No API stabilization,
portable schema change, dependency, client requirement or release is implied.
Related prepared-credit review remains uibcdf/ackredit#87 and
uibcdf/molsyssuite#97.

## Acceptance criteria

- Repeated credits retain original bibliography, context and graph edges in
  every independent capture and journal replay.
- Changed bibliography fails before any builder mutation, including warmed
  repeated-use paths.
- Normally installed Pint/unyt calculations retain numerical results,
  software/article roles and versions; saved reports work without producers.
- Paired measurements retain unchanged controls and all raw samples; complete
  the documented local gates.

## Implementation and measurements

Each builder checks the normalized use key after bibliography preflight and
retains a new use once. Capture/session target nodes are created only when
absent; session caller indexes retain their original order and journal change
semantics. Locks and per-call registry checks remain unchanged.

Two added public-behavior guards pass before and after optimization: repeated
prepared credit retains new parents, independent captures, immutable snapshots
and journal replay; a warmed duplicate public use still rejects changed
bibliography before any builder is mutated. The expanded prepared-credit module
has ten guards; the focused capture/lifecycle/session selection has 61 passes.
These are semantic protections for the fast path, not a claimed functional bug
that the original code failed.

Normally installed originals and candidate files use identical scientific
dependencies on Linux/Python 3.14.7. The 15-sample core prepared/captured medians
are 2.57/4.25/5.85 µs before and 1.65/2.59/3.53 µs after (plain/one/two captures).
The real unchanged PyUnitWizard benchmark runs three independent process pairs,
alternating order, with seven samples per scenario. One-value backend-captured
trial medians range from 86.63–90.72 to 84.00–85.16 µs; combined function/backend
capture ranges from 106.22–111.25 to 101.10–102.52 µs. Ordinary controls drift
from 42.87–45.68 to 44.38–44.42 µs. Bigger arrays retain a fixed attribution
offset rather than one reference per element; all cases and raw samples are in
`devtools/receipts/repeated_attribution_97_2026-10-05.json`.

Four unchanged receiving guards pass for both normal installations, using the
shared same-interpreter import guard and a bounded local fixture adapter.
Original runtime/distribution versions match, relevant installed package bytes
match expected source, and both prefixes pass `pip check`. Pint/unyt numerical
results, original versions, software/article roles, reused captures, graph,
failed/no-op boundaries, absent optional provider and producer/network-blocked
saved workflow reading remain faithful. This checkpoint does not rerun a hosted
matrix, release a package or qualify the original 0.9.0 fallback again.

The prior producer-owned profiling result is reported as PyUnitWizard #111;
no sibling source or release work changed. The pre-publication shared-provider
impact notice is MolSysSuite #97 comment 5991102624. Existing API provisionality
and the open #84/#87 review are unchanged.

## Completion

The Python 3.14.7 local gate passes 1,791 tests without skips; Ruff, formatting,
report indexes and strict Sphinx pass. The raw receipt identifies the normally
installed sources and scientific dependencies and retains the complete timing
samples. This resolves the allocation checkpoint; the separately tracked API
stability review and PyUnitWizard producer optimization remain open.
