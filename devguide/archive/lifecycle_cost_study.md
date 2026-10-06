---
summary: Measure lifecycle costs and scaling before selecting further optimizations.
issue: uibcdf/ackredit#115
status: resolved
opened: 2026-10-06
closed: 2026-10-06
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

## Resolution — installed source follow-up, 2026-10-06

The maintainer confirmed completed SMonitor/ArgDigest improvements. The selected
clean sources are SMonitor `6feac9728cc35d57cbc92f284d7040d7f04cb35b` and ArgDigest
`5e7925ddcd14922d00647d39b6a97eed2499bc23`; both exact-head provider CIs passed
and were inspected with gh-run-receptor. The remaining producers are Ackredit
`b8f7100388f2a7d598c4d0c86fe034cad008fa60`, DepDigest `0568f9a` and PyUnitWizard
`2ab37a5`. Build each once in clean temporary clones and install their five wheels
normally in an isolated environment. `qualification_bundle.wheel_record` and
`verify_installed` bind every shipped file, wheel digest and runtime/distribution
version; those identities still match after measurements.

The repeated study has 34 cases and 340 total subprocess samples. Ten additional
scientific cases request SMonitor's metadata-only scope explicitly. All scientific
outputs retain their exact values, units, original references/versions and value
digests; saved snapshots/journals round-trip. All package fingerprints are fixed
and worker stderr is empty. Evidence:

- `devtools/receipts/lifecycle_followup_115_2026-10-06.json`;
- `devtools/receipts/lifecycle_installed_115_2026-10-06.json`;
- `devtools/receipts/lifecycle_portable_followup_115_2026-10-06.json`.

Cold import is 173.26 ms (151.22–191.88 ms), with 10.69 MiB peak Python allocations.
First workflow rendering of one reference is 25.01 ms; 1,000-reference snapshot,
JSON export and workflow rendering are 20.21, 2.38 and 49.16 ms. Default captured
Pint conversions cost 100.81/171.64 µs for one/100,000 values; the explicit
restricted scope gives 110.20/183.83 µs. These successful calls do not construct
costly failure payloads, and show policy enforcement cost rather than error-path
savings. This is not an isolated speedup comparison against the earlier source
snapshot, which also differs in versions and installation layout.

ArgDigest's explicit selector stays at its compatible default in Ackredit:
argument digesters, normalization, binding and refusal contracts remain active.
Its `False` selector is not adopted as a public validation bypass. New diagnostic
policy is caller-owned and opt-in; it is not applied globally by this tool or
added to Ackredit's public product contract. Successful receiving checks do not
prove every provider's native-error payload respects the scope.

Local receiving validation passes 243 selected cases, including the nine lifecycle
tool guards and Ackredit argument/diagnostic/evidence/lifecycle contracts. The guard
refuses mutable source identities and leaked journal state, separates cold import
from benchmark machinery and tracemalloc, preserves independent results/raw
variation, and requires actual scientific cases for requested scoped diagnostics.
The disjoint reporting/documentation/integration-guide selection passes another
160 cases. Ruff, strict Sphinx, reporting/index and the pinned dependency-route
checks pass; no dependency route or workflow was changed.

The first measurement checkpoint is resolved. Scientific dependencies still
inherit the maintained Conda environment; this is one local installed development
lane, not public delivery or full platform qualification. Profile first-report
format discovery and cold initialization next, preserving current validation and
diagnostic defaults. Real plugin packs, independent graph shapes, external-user
dependency closure and broader platforms remain roadmap L scope.
