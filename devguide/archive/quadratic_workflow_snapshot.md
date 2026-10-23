---
summary: Avoid repeated full-use scans when snapshotting enclosing workflows.
issue: uibcdf/ackredit#133
status: resolved
opened: 2026-10-22
closed: 2026-10-22
severity: medium
verification: reproduced
area: [core, performance, attribution]
guard: tests/test_workflow_snapshot_scale.py
normative:
blocked_by: []
supersedes: []
---

# Enclosing workflow snapshot reconciliation

## What

`get_attribution()` tests every legacy item/caller pair with `any(...)` over the
builder's contextual uses. The list grows as missing plain uses are added. This
suggests quadratic work for a large enclosing workflow; the original lifecycle
benchmark measures capture snapshots instead of this path.

## How

Extend the existing lifecycle owner with an enclosing-workflow case and measure
plain/contextual/mixed credit at increasing sizes. Retain raw paired samples,
source identities and complete payload fingerprints. If supported, build a
snapshot-local presence index while preserving contextual variants and order.
Use a deterministic work-bound regression, not a wall-clock threshold.

## Why

The maintainer resumed roadmap L's lightweight review on 2026-10-22. Reading a
finished workflow should not repeatedly search an ever-growing list. This
investigation does not weaken declaration/reader validation or introduce caches.

## What was refuted

Source inspection alone is not a timing result or installed release proof.
Capture-snapshot measurements cannot substitute for enclosing-workflow snapshots.

## Scope and exclusions

Ackredit's snapshot reconciliation and its existing measurement tool. No client
source, public API/schema, dependency floor or earlier artifact changes. Synthetic
scaling is distinct from scientific numerical parity, full pipeline overhead,
installed dependency closure and separately qualified public delivery.

## Acceptance criteria

- Measured plain/contextual/mixed cases expose the cost with bound original inputs.
- A deterministic guard fails for repeated full-use scans and passes after repair.
- Complete use order/variants, bibliography/versions, graph, legacy fallback,
  independent captures and session isolation remain intact.
- Applicable source checks pass; release/version and exact-file gates stay explicit.

## Resolution and measured limits

Snapshot reconciliation now builds one local set of represented item/caller
pairs, adding missing legacy pairs in their original traversal order. Rich
context variants remain separate uses; no cache or state mutation is introduced.
The existing public snapshot remains the owning reusable operation.

Six deterministic tests count comparisons through accepted string names, for
plain/contextual/mixed workflows with distinct references or callers. All six
fail before repair (at least 32,640 comparisons for 256 uses); they pass with
the local index. A separate fidelity control passes on both versions and checks
context variants, original observed metadata, snapshot-time legacy fallback,
unknown references, use order, graph, detached data and session isolation.
The initial post-repair capture/portable gate passes 43 tests without skips.

The paired editable-source study uses the same retained measurement tool,
fixed inputs, five timing and two allocation samples per case/side, separate
child interpreters and alternating case order within each side. For 5,000 uses,
plain/contextual/mixed snapshot medians fall from 1,200/1,266/1,281 ms to
243/327/272 ms. All 126 full payload fingerprints agree. Peak traced Python
allocation increases by 0.79–0.81 MiB there for the temporary index. Small cases
have overlapping/noisy timings, not a universal speedup. Raw samples, measured
tool source and identities are retained in the owning performance receipt.

This is not RSS, a full scientific workflow, current-client qualification or an
installed public performance claim. The release follow-up is #134, preparing
0.12.1 with unchanged contract floors. Preserve original 0.12.0 bytes and proof.

Final local source qualification covers 6,441 passing cases across the complete
run and six targeted network-enabled retries. The first sandbox run could not
resolve isolated build dependencies: five cases failed/errored and one wheel
case skipped; all six pass when rerun with network, without source changes.
Eight optional real publication-tool cases remain unexecuted locally because
Pandoc/Biber/the portable JabRef distribution are absent. No full-publication
tool qualification is inferred. Ruff, indexes and strict Sphinx pass. Exact-head
CI and the required installed/real receiving/public gates remain separately owned
by #134; detailed local outcomes and source hashes are retained in its receipt.
