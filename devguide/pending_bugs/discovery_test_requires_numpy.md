---
summary: A discovery guard imports undeclared NumPy in the minimal CI environment.
issue: uibcdf/ackredit#88
status: active
opened: 2026-10-04
closed:
severity: medium
verification: reproduced
area: [tests, integration]
guard: tests/test_hooks_already_loaded.py::test_discovery_credits_nothing_that_was_already_loaded
normative:
blocked_by: []
supersedes: []
---

# Discovery guard requires undeclared NumPy

## What

Ordinary CI 37216802143 for `357083e` fails its five installed test jobs because
the discovery no-sweep test explicitly imports NumPy. The declared minimal
test environment has no NumPy; Ackredit has no NumPy runtime requirement.
The separate real-producer matrix 37216812721 passes all eight installed cells.

## How

GH Run Receptor identifies `ModuleNotFoundError: No module named 'numpy'`.
Targeted retained macOS evidence, `5_Test on macos-15, Python 3.14.txt`, lines
628–639, identifies the exact selector and preload. A fresh-process import
blocker reproduces the same failure even in the rich local development environment.

## Why

The earlier #86 correction removed transitive-import assumptions but explicitly
preloaded NumPy in this remaining case. This replaced one unguaranteed
precondition with another. The no-sweep behavior can be tested with the actual
required modules and should retain the absent-NumPy precondition.

## What was refuted

Adding NumPy to Ackredit or its ordinary test environment would obscure the
test's incidental dependency. The receiving matrix's explicit Pint/unyt/NumPy
requirements are appropriate to that designated scientific gate, not ordinary
core import-hook behavior. No provider implementation change is needed.

## Scope and exclusions

One test's preconditions and its explanatory docstring. Injection/discovery
behavior, runtime imports and core or scientific dependency declarations remain
unchanged. The previous resolved #86 record receives a dated correction.

## Acceptance criteria

The guard proves no credit for already-loaded required modules with NumPy
actively unavailable. The local suite and ordinary exact-source five-job CI
pass. Required dependency imports remain light, with no new runtime dependency.

## Local correction

A MetaPathFinder actively refuses NumPy before Ackredit is imported, reproducing
the old test's explicit-preload failure. The corrected case observes already
imported SMonitor, ArgDigest and PyYAML, asserts NumPy stays unloaded, and proves
the import hook records no discovery credit. All nine fresh-process hook tests
pass locally; the ordinary hosted gate will be linked before closure. This
checkpoint also sorts receiving receipts deterministically and adds negative
aggregate guards for skipped, deselected, failed, unexecuted and duplicate cells.
