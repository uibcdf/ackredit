---
summary: Observe executed third-party functions through dependency-free declarations.
issue: uibcdf/ackredit#84
status: partial
opened: 2026-10-04
closed:
severity: medium
verification: reproduced
area: [core, integration]
guard: tests/test_function_providers.py::test_normally_installed_provider_and_reader_outside_checkout
normative:
blocked_by: [uibcdf/molsyssuite#97, uibcdf/moli#46]
supersedes: []
---

# Dependency-free function citation providers

## What

Let third-party software declare its bibliography and references for individual
functions without importing Ackredit. Observe actual selected function entries
only within an explicit application context.

## How

A versioned module `__ackredit__` dictionary supplies bibliographic items,
original software/version and reference roles. Functions may carry metadata
attributes without wrapping themselves. The observer reuses scopes, tracking,
sessions and portable capture rather than creating a second attribution system.

## Why

`auto_track_calls` intentionally credits statically discovered calls even in
untaken branches. Import hooks establish package-level credit. Neither proves
that a particular dependency function ran. Provider declarations can give both
software and description articles and avoid guessing citations from names.

## What was refuted

Automatic import sweeps, mandatory provider dependencies and universal profiling
are outside this implementation. Existing coarse APIs retain their contracts.

## Scope and exclusions

Direct exports of explicitly selected, already imported modules; synchronous
functions and awaited coroutine functions. Pre-activation aliases, generators,
descriptors, native internal calls and child processes are excluded. The new
surface is provisional until provider and receiving review, not suite policy.

## Acceptance criteria

Normally installed dependency-free producer; no credit on declaration or
untaken branches; reused references in independent captures; original versions,
roles and pipeline graph preserved after serialization; exception propagation,
restoration and concurrent-context isolation. Document limits and measure costs.

## Implemented development boundary

`observe_calls` and the provisional `ackredit.provider@1` schema implement the
bounded proposal. The installed test builds both Ackredit and a dependency-free
producer normally, blocks Ackredit during producer use, then captures actual
calls and restores saved records in a separate producer-blocked reader.
Behavioral guards cover untaken branches, software/article roles, two versions
sharing an article, nested captures/observers, unrelated threads, concurrent
tasks, expired inherited leases, original exception propagation, declaration
conflicts, registry replacement, tracking failures and export rebinding.

Declarations are normalized/detached at activation, and their contextual keys
are prepared once. Actual entries still go through the shared session/capture
and journal writers on every invocation. Registry contents and captured
identities are compared, not cached by mutable identity. Unsupported custom
module subclasses are refused before mutation as well as generators.

MolSysSuite #97 records the shared-provider impact before publication. Real
producer/receiving review and promotion or removal of the provisional API
remain open; the installed fixture is not evidence of scientific adoption.

## Hosted installation correction

Initial exact-source CI 37203629536 passed lint, docs and Linux 3.11/3.12, but
the new receiving test failed on Linux 3.13/3.14 and macOS 3.14. GH Run Receptor
identified the single failed test; its retained macOS log at lines 681–690
identifies `BackendUnavailable: Cannot import 'setuptools.build_meta'`.
The minimal runtime test environments legitimately omit build backends.

The receiving test now uses normal pip build isolation for both packages,
honoring their declared `[build-system]` requirements rather than requiring
incidental setuptools/versioningit installations in the runtime interpreter.
`--no-deps` remains: scientific runtime dependencies are supplied by the test
environment. No runtime environment/tooling policy change or skip is introduced.
The public 0.9.0 artifact and provider implementation are unchanged by this
test-only correction; the final hosted execution will be linked in the issue.

The durable receiving guard creates a fresh build interpreter without inherited
site-packages and verifies Versioningit is absent there. Normal pip installs
both packages into the target directory with their isolated build requirements;
the consumer interpreter supplies its existing runtime dependency foundation.
This recreates the minimal-builder precondition locally and prevents accidental
reliance on the maintainer environment's build tools.

## First real producer: PyUnitWizard (2026-10-04)

Implementation and measurements are owned by uibcdf/pyunitwizard#94, linked to
the existing actually executed backend pilot (#92). The lazy public facade
revealed that requiring all declared exports in `vars(module)` refused a normal
PEP 562 module even though the declaration names its public functions.

Three test-first reproductions failed on the previous implementation. The
observer now resolves only declared missing exports with `getattr` during
explicit activation, validates function-level metadata after resolution, and
diagnoses loader errors through E012 before installing wrappers or bibliography.
Normal producer loader caching may occur during preflight; those side effects
are owned by the loader and cannot be promised atomic rollback. Custom module
subclasses remain refused. No import sweep or new protocol field is introduced.

Guards cover requested-name precision, no declaration credit, restoration of
the original resolved function, loader failure and conflicting lazy-function
metadata. Real PyUnitWizard tests distinguish entry into a public function
(including no-op/failed calls) from successful child backend dispatch: the
former cites PyUnitWizard, while only completed dispatch earns backend credit.
Cross-component protocol review remains open.

The local expanded gate passes 1,635 tests without skips on Python 3.14.7;
Ruff, report indexes and strict Sphinx (`-n -W --keep-going`) pass. The final
installed and hosted source receipts are linked in the issue after publication.

## Coupled installed receiving gate (2026-10-04)

`devguide/receiving_validation.md` documents the new manual exact-source gate.
One builder creates a candidate/real-producer wheel bundle and a separate
source-built original 0.9.0 API baseline. The Linux/macOS arm64 × Python
3.11–3.14 consumers verify archive and installed-resource hashes, run outside
the repositories, and retain the actual portable pipeline and fresh-reader
evidence. The final aggregation uses Pytest Receptor's supported artifact reader
and requires eight distinct cells, five passed tests per cell and no skips,
deselections or incomplete evidence. Missing Pint/unyt is a failure in this
designated gate rather than an optional skip.

The five receiving tests pass locally on Python 3.14.7 with normally installed
Ackredit `d3fd892` and PyUnitWizard `33fec8a`. They cover numerical/unit parity,
reference counts, unused backends, software/article roles, original versions,
pipeline parentage, no-op/failed entries, optional-provider absence, a fresh
producer-blocked reader and the genuine original 0.9.0 backend-credit fallback.
The source-built 0.9.0 wheel is not the published Conda file. Archive tampering,
editable imports, changed installed citation resources and partial-matrix
evidence are refused by `tests/test_qualification_bundle.py`.

Hosted execution is still pending at this pre-publication checkpoint; the issue
will retain its exact-source run and receipts. This is receiving evidence, not
API promotion or release certification. Review remains with MolSysSuite #97
and MOLI #46; the canonical client guide is unchanged.

The first hosted receiving execution, 37216812721, passes all eight cells and
the final aggregate for exact source `357083e`. Downloaded evidence independently
verifies with the supported receptor reader: 40 passed tests, no skips or
deselections, the same candidate/producer/baseline wheels in every cell, and
matching installed resources. Candidate wheel SHA-256 is
`9192c8aa08d02b79a24a8883c00b473896a1636fe2d7dff8a2623837198e98b9`.
The full ordinary CI for that revision exposed the unrelated missing-NumPy
discovery-test precondition tracked in #88. Its correction and the deterministic
receipt-order refinement require their own final checkpoint; neither changes
the provisional runtime implementation or promotes its API.

The corrected source `fc00a6c` completes that checkpoint: CI 37217509058 passes
all seven jobs; receiving run 37217520167 passes all ten jobs, including the
eight installed cells and aggregate, with 40 tests and no skips/deselections.
MolSysSuite and Conda publication policy gates also pass. The downloaded
bundle's installed-resource identities and complete receptor event streams
verify independently locally. The reviewed public evidence is retained in
`devtools/receipts/function_provider_matrix_2026-10-04.json`, including source,
wheel hashes, original versions, per-cell graph/roles and fresh-process checks.
The separate test defect #88 is resolved and archived. Provider/receiver review
and provisional API classification remain open under #84/#87/#97/MOLI #46.
