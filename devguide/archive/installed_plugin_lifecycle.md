---
summary: Measure normally installed plugin packs and guard their actual lifecycle.
issue: uibcdf/ackredit#117
status: resolved
opened: 2026-10-06
closed: 2026-10-06
severity: medium
verification: measured
area: [tooling, integration, performance]
guard: tests/test_installed_plugins.py
normative:
blocked_by: []
supersedes: []
---

# Installed plugin lifecycle and scaling

## What

The #115/#116 measurements have no installed Ackredit plugin packs, and existing
citation/format tests substitute entry-point objects. Measure actual normally
installed distributions before designing a shared discovery cache.

## How

`devtools/benchmark_plugins.py` builds controlled fixture packages through the
standard setuptools backend and installs their wheels normally in disposable
environments. Reuse `benchmark_lifecycle` for minimal cold workers, named stages,
raw summaries and loaded-source identities; reuse `qualification_bundle` for
original wheel/file verification. No new runtime plugin implementation.

Separate pack count (zero, one, ten) from references per pack (one, 100, 1,000).
Cold import and warm operations use independent fresh processes. Measure explicit
citation reload, first/repeated format discovery, independent captures, requested
reports and detached export/read, with timing and allocations separated.

## Why

Automatic citation plugins must declare without recording use. Format plugins
must activate on first demand and tolerate reentry. Failed plugins and name
conflicts must retain catalog warnings and working neighbors. New distributions
installed after import must remain visible to first format discovery and explicit
citation reload. Each capture must retain its own original references.

## What was refuted

The dependency-free function-provider example serves a different observation
contract and has no citation/format entry points. A scan of local suite packaging
declarations found no packages providing these groups. Controlled installable
fixtures establish distribution/lifecycle evidence, not third-party scientific
workload coverage or external published adoption.

## Scope and exclusions

Ackredit-owned tooling, normal installed fixtures and bounded local measurements.
No runtime cache, public release, changed plugin lifecycle, clean dependency
closure, arbitrary graph qualification, RSS, scientific equivalence claim or
complete roadmap L closure.

## Acceptance criteria

Retain original wheel/source identities, raw timing/allocation samples and actual
installed origins. Exercise independent captures and a plugin-free detached
reader. Add installed guards for failures, conflicts, reentry, late installation
and optional Ackredit absence. Run relevant tool/plugin/attribution contracts,
governance/lint/docs checks and inspect applicable exact-head CI.

## Resolution and evidence

Tool source `778132006bfa` extends the existing lifecycle/qualification owners;
the Ackredit runtime remains original wheel candidate `45294c4`, with fixed
normal SMonitor/ArgDigest/DepDigest wheels. Every package file and origin is
verified. Original fixture sources, wheel bytes, environments and saved results
remain in the disposable study directory; their immutable hashes/file maps and
100 raw cold/operation samples are preserved in
[`installed_plugins_117_2026-10-06.json`](../../devtools/receipts/installed_plugins_117_2026-10-06.json).
Timing and allocations are separate, case order alternates, and source/tool
fingerprints remain fixed. All worker stderr fields are empty. The maintained
[performance page](../../docs/content/about/performance.md) contains ranges,
reproduction and limits.

First format discovery has medians of 23.17–27.08 ms across five variants.
Cold import ranges overlap for one and ten small packs; one 1,000-reference
pack instead takes median 173.41 ms, versus 132.20 ms for one reference.
These environment-local controls do not establish a speedup over #116 or an
external client's overhead. Original fixture-version notes survive both reused
captures and a separate reader without any plugin installation or execution
credit. No public plugin cache or runtime lifecycle change is made.

Four normally installed guards cover first requested format activation/reentry,
diagnosed broken plugins and conflicts with surviving neighbors, late normal
installation before first format demand, explicit citation reload and dedup,
optional Ackredit absence and measured report/capture integrity. Initial import
diagnostics are observed through SMonitor's public `MemoryHandler`, without
assuming default event retention or replacing its bootstrap warning hooks.
Both the routine source lane and fixed normally installed runtime lane pass
135 selected pytest cases with `--receptor=llm` and no skips/warnings.
Another 314 documentation/report/guide tests pass; that selection shares the
one reporting-protocol guard with the contract lane. Ruff, generated indexes,
pinned dependency-route preflight, suite conformance and strict Sphinx pass.

The missing standalone grouped-discovery operation is handed to
[DepDigest #31](https://github.com/uibcdf/depdigest/issues/31), with measured
consumer impact and late-provider constraints. This is a single-consumer
proposal for owner triage, not an adopted shared contract or provider source
change. The pre-handoff suite refresh preserved Ackredit's one intentional local
checkpoint ahead of origin; DepDigest was clean and synchronized. Provider and
consumer use their registered cross-component labels. This bounded measurement
can close independently of that future operation and the larger roadmap.

Exact-head hosted results are synchronized in the owning issue after the final
source checkpoint; public Ackredit 0.11.0 is unchanged.
