---
summary: Measure and reduce portable capture overhead while preserving fidelity.
issue: uibcdf/ackredit#85
status: resolved
opened: 2026-10-04
closed: 2026-10-04
severity: medium
verification: measured
area: [core, performance]
guard: tests/test_attribution_capture.py::test_mutable_context_is_revalidated_on_repeated_credits_in_nested_captures
normative:
blocked_by: []
supersedes: []
---

# Portable capture overhead

## What

Measure portable and nested capture separately from the historically measured
plain tracking path, then remove redundant work without weakening validation.

## How

Use a repeatable benchmark with plain/contextual tracking, captures, snapshots
and rendering. `_Builder.item` currently evaluates `deepcopy(record)` in
`setdefault` even for an already stored record; each enclosing builder also
serializes the same normalized contextual use independently.

## Why

Metadata snapshots and repeated-credit capture are essential to fidelity, but
repeated copying and serialization are not. Measure before/after on the same
interpreter and machine, with repeated samples and source identities.

## What was refuted

Skipping observations after the first credit loses later independent captures.
Caching mutable registry records by identity hides conflicts and is unsafe.
Universal wall-clock CI thresholds confuse scheduler noise with regressions.

## Scope and exclusions

No public payload or call semantics change; no global profiler, background work
or DOI access. Synthetic timings do not qualify a scientific consumer release.

## Acceptance criteria

Repeatable before/after receipt; unchanged mutation/conflict, reused capture,
context-role and original-version behavior; measured scope and noise reported.

## Resolution

Already retained records are no longer deep-copied on every credit. One
normalized contextual key is shared across the workflow and enclosing captures.
Public tracking still validates and detaches mutable inputs on every call;
the selected guard mutates the same context object between repeated credits
and then injects a non-finite value. Both captures and the workflow retain
the two original distinct uses and refuse the invalid third observation.

The #84 provider observer prepares privately detached declarations once at
activation and passes them through the same normalized attribution/session
writers, including the existing journal writer. Repeated calls still enter
every active capture; registry contents and bibliographic identity conflicts
remain checked. It is not an identity cache over user-mutable metadata.

`devtools/benchmark_portable.py` measures plain/contextual tracking, capture,
nested capture, detachment, BibTeX and inactive/active function providers.
The receipt under `devtools/receipts/portable_capture_85_2026-10-04.json`
retains all samples, runtime file hashes and benchmark identity. The performance
page publishes scoped medians and spreads; historical scientific-workflow
measurements are not replaced by these synthetic repeated-credit results.
