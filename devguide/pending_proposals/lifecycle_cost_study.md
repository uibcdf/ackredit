---
summary: Measure lifecycle costs and scaling before selecting further optimizations.
issue: uibcdf/ackredit#115
status: partial
opened: 2026-10-06
closed:
severity: medium
verification: measured
area: [tooling, performance]
guard: tests/test_benchmark_lifecycle.py
normative:
blocked_by: []
supersedes: []
---

# Lifecycle cost study

## What

Roadmap L starts with a bounded lifecycle measurement. Existing portable and
provenance tools retain their repeated-operation contracts and historical samples.

## How

Use `devtools/benchmark_lifecycle.py` with fresh interpreters outside the checkout,
separate timing/allocation samples, and fingerprints of actual loaded packages.
Pair ordinary and instrumented real PyUnitWizard conversions with exact numerical,
unit and original-reference checks. Do not change scientific provider code.

The tool now rejects a study if a loaded package's source fingerprint or version
changes between samples. Each process also receives an independent directory:
journal files cannot leak into another sample. Cold-import measurement starts
before importing the benchmark's metadata/reporting machinery; timing excludes
tracemalloc and allocation runs are separate.

## Why

Repeated-credit benchmarks exclude import, activation, first use and memory.
Choose future optimizations from measured stages rather than adding independent
historical percentages or inferring an external user's installed cost.

The fixed-source study completed 24 cases with seven timing and three separate
allocation samples each. Every scientific mode/sample preserves exact meter to
centimeter values, units and original credited versions; every journal and
detached snapshot passes its round-trip guard. All worker stderr fields are empty.
The raw evidence is retained in
[`lifecycle_cost_115_2026-10-06.json`](../../devtools/receipts/lifecycle_cost_115_2026-10-06.json),
with original source/file identities in
[`lifecycle_sources_115_2026-10-06.json`](../../devtools/receipts/lifecycle_sources_115_2026-10-06.json).
The unchanged portable tool is repeated in the same fixed-source environment;
[`lifecycle_portable_115_2026-10-06.json`](../../devtools/receipts/lifecycle_portable_115_2026-10-06.json)
retains its own raw samples and narrower warmed-operation scope. Bounded tables
and limits live in [the maintained performance page](../../docs/content/about/performance.md).

Local guards: 234 selected pytest cases pass with `--receptor=llm` against the
fixed sources, including eight lifecycle-tool guards. Ruff, reporting/index
checks and the pinned shared dependency-route check pass. This evidence covers
tool/contract changes, not public installed-release qualification.

## What was refuted

The existing tools do not already measure the complete lifecycle. A new generic
benchmark framework or runtime dependency is unnecessary: these are Ackredit-owned
workloads composed with standard-library process and allocation tools.

The initial completed trial was unsuitable as a fixed-source comparison:
SMonitor's editable source had five distinct fingerprints while its declared version stayed
the same. Actual fingerprints detected this; version strings alone would not.
It is not published as the performance baseline. Earlier journal-isolation and
backend-credit assumptions failed their controls and produced no successful
study receipt. Backend-only conversion credits Pint; public observation also
credits PyUnitWizard.

## Scope and exclusions

Local Linux/Python 3.14 evidence; no release, runtime optimization, dependency
change, clean Conda installation qualification, RSS measurement or plugin pack
size sweep. Source and installed identities are separate facts.

The principal maintainer confirmed concurrent SMonitor development on 2026-10-06.
The repeated study uses fixed temporary copies of Ackredit, SMonitor, DepDigest,
ArgDigest and PyUnitWizard, preserving original repositories and their human work.
Those copies represent development source, not released installed distributions.
Numbers remain a provisional reference until the selected SMonitor work is ready.
Do not choose or claim an optimization from mixed-source timings.

## Acceptance criteria

Retain reproducible raw samples and actual identities for named lifecycle stages,
scaling dimensions and scientific controls. Guard sample isolation and retained
references, publish results with variation and limits, and leave unfinished
roadmap L work explicitly visible.

The remaining checkpoint is to select the final SMonitor source/version and
repeat the affected import, activation and scientific controls with fixed
identities before selecting an optimization. Keep #115 open for that evidence;
the broader installed-closure and plugin-pack study remains roadmap L work.
