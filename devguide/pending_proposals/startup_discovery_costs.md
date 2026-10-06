---
summary: Separate startup discovery costs and defer unused network and PDF imports.
issue: uibcdf/ackredit#116
status: active
opened: 2026-10-06
closed:
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
