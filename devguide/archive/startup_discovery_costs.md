---
summary: Separate startup discovery costs and defer unused network and PDF imports.
issue: uibcdf/ackredit#116
status: resolved
opened: 2026-10-06
closed: 2026-10-06
severity: medium
verification: measured
area: [core, tooling, performance]
guard: tests/test_startup_imports.py
normative:
blocked_by: []
supersedes: []
---

# Startup discovery and feature imports

## What

The installed #115 baseline includes format-plugin discovery in the first report
and imports network/PDF support before either feature is requested.

## How

Extend the existing lifecycle tool with `--startup-only`: cold import, natural
first report, explicit format discovery, and repeated rendering for one and
1,000 references. Retain independent processes, timing/allocation samples,
loaded-source fingerprints and equality of repeated report contents.

Move standard-library networking imports into the existing `_fetch` owner and
PDF subprocess imports into `compile_pdf` after its missing-source check.
Preserve catalogs, retries, cached enrichment, public signatures, plugin
activation/reload and default ArgDigest validation. No reusable provider
operation is duplicated.

## Why

An exploratory `cProfile` run of the fixed installed baseline identifies
distribution entry-point enumeration and eager optional-feature import trees.
Profiler overhead makes these observations structural evidence, not latency
estimates. Compare unprofiled installed samples with the same provider wheels,
environment and installation path before claiming an improvement.

## What was refuted

Sharing a cached entry-point list across citation and format discovery can
freeze providers installed after import and affect explicit citation reload.
Do not introduce that behavior change as a startup optimization. Rendering is
not itself established as the source of the one-reference first-report cost.

## Scope and exclusions

Local Linux/Python 3.14 developer-wheel evidence. No public release, plugin-pack
size qualification, RSS measurement, dependency changes, scientific algorithm
changes, or complete roadmap L qualification.

## Acceptance criteria

Publish reproducible before/after raw installed samples, original wheel/file
identities and limits. Guard deferred imports in fresh processes and discovery
versus rendering stages. Run relevant network/PDF/plugin and argument contracts,
reporting/index checks, lint/format and applicable exact-head CI.

## Resolution and evidence

The source candidate is `45294c426486495fff8749388af941b2fa8c8a06`.
Only `core/registry.py`, `core/report.py` and the generated version differ
between the installed baseline and candidate package files. The four provider
wheels are unchanged. Original wheel/file verification and the identical other
distribution inventory are retained in
[`startup_installed_116_2026-10-06.json`](../../devtools/receipts/startup_installed_116_2026-10-06.json).
The [baseline](../../devtools/receipts/startup_before_116_2026-10-06.json) and
[candidate](../../devtools/receipts/startup_after_116_2026-10-06.json) keep
120 raw samples. Overlapping initial build/test trials were excluded and repeated
without concurrent task work. Their sequential cohort order still permits
machine drift; ranges and local scope remain explicit.

One-reference format discovery has candidate median 24.34 ms; the first workflow
render after explicit discovery has median 0.248 ms. With 1,000 references that
render takes 24.24 ms, so large reports have an independent cost. Cold import
has baseline/candidate medians 161.86/160.48 ms with overlapping ranges;
no reliable speedup follows. Traced allocation peak falls from 10.68 to 8.95 MiB.
The deferred imports still initialize on the first network/PDF operation.
The [profile](../../devtools/receipts/startup_profile_116_2026-10-06.json)
is exploratory instrumented evidence, kept separate from unprofiled timings.

DepDigest's `core/loader.py` was inspected: `LazyRegistry` uses the same standard
discovery and owns a different module-registry contract. This change extends
Ackredit's existing benchmark and feature owners rather than duplicating a
generic metadata-discovery tool. Real plugin packs and a separately owned
invalidation contract are the next investigation, not an implicit cache here.

Fresh-process guards distinguish Ackredit-owned import requests from imports
made by its providers. Ordinary reporting, fresh cached enrichment and missing
PDF-source diagnostics keep feature imports deferred. The installed candidate
passes 264 selected tests with `--receptor=llm`, including real BibTeX compilation,
network retry/cache, plugin conflict/reentry, validation and diagnostic guards.
The maintained [performance page](../../docs/content/about/performance.md)
records bounded numbers and reproduction. Exact-head hosted results are
synchronized in the owning issue after the final source checkpoint.

Another 314 disjoint documentation/report/guide tests pass locally. Ruff lint
and format, reporting indexes, dependency-route preflight, suite conformance
and strict Sphinx pass. Sphinx's first restricted-network attempt could not
download Python's inventory; the network-enabled strict rebuild succeeds.

### Hosted correction (2026-10-06)

The first hosted checkpoint `fad14af` passed docs and policies, but all five
test jobs failed the same `tests/test_pdf.py` case. That existing test patched
`report_module.shutil`, a private eager import removed by this change. The local
selection had covered PDF warnings and real BibTeX compilation but omitted this
file. It now patches the owning standard-library `shutil.which` directly, and
the three PDF cases join the selected installed validation. The runtime candidate
and its original measured wheel bytes are unchanged; final exact-head CI must
execute again. The original failed run is
[#37504900987](https://github.com/uibcdf/ackredit/actions/runs/37504900987).
