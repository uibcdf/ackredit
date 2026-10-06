---
summary: Measure normally installed plugin packs and guard their actual lifecycle.
issue: uibcdf/ackredit#117
status: active
opened: 2026-10-06
closed:
severity: medium
verification: inspected
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
