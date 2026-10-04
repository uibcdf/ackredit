---
summary: Observe executed third-party functions through dependency-free declarations.
issue: uibcdf/ackredit#84
status: partial
opened: 2026-10-04
closed:
severity: medium
verification: reproduced
area: [core, integration]
guard: tests/test_function_providers.py::test_normally_installed_provider_and_reader_outside_checkout
normative:
blocked_by: [uibcdf/molsyssuite#97, uibcdf/moli#46]
supersedes: []
---

# Dependency-free function citation providers

## What

Let third-party software declare its bibliography and references for individual
functions without importing Ackredit. Observe actual selected function entries
only within an explicit application context.

## How

A versioned module `__ackredit__` dictionary supplies bibliographic items,
original software/version and reference roles. Functions may carry metadata
attributes without wrapping themselves. The observer reuses scopes, tracking,
sessions and portable capture rather than creating a second attribution system.

## Why

`auto_track_calls` intentionally credits statically discovered calls even in
untaken branches. Import hooks establish package-level credit. Neither proves
that a particular dependency function ran. Provider declarations can give both
software and description articles and avoid guessing citations from names.

## What was refuted

Automatic import sweeps, mandatory provider dependencies and universal profiling
are outside this implementation. Existing coarse APIs retain their contracts.

## Scope and exclusions

Direct exports of explicitly selected, already imported modules; synchronous
functions and awaited coroutine functions. Pre-activation aliases, generators,
descriptors, native internal calls and child processes are excluded. The new
surface is provisional until provider and receiving review, not suite policy.

## Acceptance criteria

Normally installed dependency-free producer; no credit on declaration or
untaken branches; reused references in independent captures; original versions,
roles and pipeline graph preserved after serialization; exception propagation,
restoration and concurrent-context isolation. Document limits and measure costs.

## Implemented development boundary

`observe_calls` and the provisional `ackredit.provider@1` schema implement the
bounded proposal. The installed test builds both Ackredit and a dependency-free
producer normally, blocks Ackredit during producer use, then captures actual
calls and restores saved records in a separate producer-blocked reader.
Behavioral guards cover untaken branches, software/article roles, two versions
sharing an article, nested captures/observers, unrelated threads, concurrent
tasks, expired inherited leases, original exception propagation, declaration
conflicts, registry replacement, tracking failures and export rebinding.

Declarations are normalized/detached at activation, and their contextual keys
are prepared once. Actual entries still go through the shared session/capture
and journal writers on every invocation. Registry contents and captured
identities are compared, not cached by mutable identity. Unsupported custom
module subclasses are refused before mutation as well as generators.

MolSysSuite #97 records the shared-provider impact before publication. Real
producer/receiving review and promotion or removal of the provisional API
remain open; the installed fixture is not evidence of scientific adoption.

## Hosted installation correction

Initial exact-source CI 37203629536 passed lint, docs and Linux 3.11/3.12, but
the new receiving test failed on Linux 3.13/3.14 and macOS 3.14. GH Run Receptor
identified the single failed test; its retained macOS log at lines 681–690
identifies `BackendUnavailable: Cannot import 'setuptools.build_meta'`.
The minimal runtime test environments legitimately omit build backends.

The receiving test now uses normal pip build isolation for both packages,
honoring their declared `[build-system]` requirements rather than requiring
incidental setuptools/versioningit installations in the runtime interpreter.
`--no-deps` remains: scientific runtime dependencies are supplied by the test
environment. No runtime environment/tooling policy change or skip is introduced.
The public 0.9.0 artifact and provider implementation are unchanged by this
test-only correction; the final hosted execution will be linked in the issue.

The durable receiving guard creates a fresh build interpreter without inherited
site-packages and verifies Versioningit is absent there. Normal pip installs
both packages into the target directory with their isolated build requirements;
the consumer interpreter supplies its existing runtime dependency foundation.
This recreates the minimal-builder precondition locally and prevents accidental
reliance on the maintainer environment's build tools.
