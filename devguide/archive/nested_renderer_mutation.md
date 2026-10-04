---
summary: A format renderer can mutate nested registered bibliographic metadata.
issue: uibcdf/ackredit#90
status: resolved
opened: 2026-10-04
closed: 2026-10-04
severity: medium
verification: reproduced
area: [reporting, core]
guard: tests/test_renderer_isolation.py::test_nested_plugin_mutation_preserves_registered_bibliography
normative:
blocked_by: []
supersedes: []
---

# Nested bibliography renderer isolation

## What

The registry and each item have read-only views, but nested authors and
identifiers remain shared. A plugin changes subsequent public reports by
mutating a structured author or clearing the identifiers list.

## How

Both a successful plugin and one that mutates then raises reproduce corruption
in subsequent public JSON and workflow snapshots. The new tests fail before
the repair. Bibliography is now deeply detached before exposing the existing
two-level read-only view; nested list/dict types and plugin signatures remain.

## Why

One rendered output cannot rewrite declarations or the next calculation's
reference metadata. The documented isolation boundary must cover nested data.

## What was refuted

Recursively converting lists to tuples or mappings to proxies would change
ordinary renderer data types and interfere with JSON encoders. Detached copies
preserve them. Saved `Attribution` rendering already detaches its record data;
the regression also guards that case explicitly.

## Scope and exclusions

Report-time input ownership only; no change to registration, tracking/capture,
plugin discovery, runtime dependencies or the portable schema.

## Acceptance criteria

Mutating nested data, including before a renderer exception, cannot change
caller declarations, registered bibliography or saved attribution. The
existing top-level read-only guards and all local/hosted gates pass.

## Local evidence (2026-10-04)

Both successful and failing mutating plugins preserve declarations and later
public JSON/snapshots. Saved rendering remains isolated. Built-in reports
avoid copying unused metadata, while plugins retain their complete-registry
contract. Full local Python 3.14.7 gates pass 1,694 tests, Ruff, report indexes
and strict Sphinx; hosted source/installed gates follow.

## Resolution

Implementation `cb3e58df0a82ecc46da50f1969ddc921a097664e` passes ordinary
CI 37224726278 (seven jobs) and both policy lanes. Installed real-producer
matrix 37228402277 passes all eight Linux/macOS arm64 × Python 3.11–3.14
cells, 48 tests without skips/deselections and the final aggregate. Downloaded
wheel/resource/event identities verify independently; the local aggregate equals
the hosted summary. Reviewed evidence is retained in
`devtools/receipts/workflow_reporting_matrix_2026-10-04.json`. Nested mutation
and mutation-before-failure guards remain in the ordinary installed source CI.
