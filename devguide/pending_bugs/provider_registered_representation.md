---
summary: Function observation rejects JSON-equivalent pre-existing tuple metadata.
issue: uibcdf/ackredit#92
status: active
opened: 2026-10-04
closed:
severity: medium
verification: reproduced
area: [core, integration]
guard: tests/test_function_providers.py::test_registered_tuple_metadata_matches_public_observation
normative:
blocked_by: []
supersedes: []
---

# Registered provider representation

## What

On `de209ca`, pre-registering a reference through public `register_item` with
tuple authors makes `observe_calls` reject the equivalent provider JSON list
with E012. Ordinary contextual tracking and provisional `prepare_credit` accept
these fields. Three new regression cases reproduce the observer's refusal.

## How

At activation compare the registered bibliography's normalized portable value
with the provider declaration. Preserve accepted existing registrations and
separately detach their raw representation for per-invocation replacement checks.
Use normalized declarations for portable capture. New references register only
after every selected provider and conflict passes preflight.

## Why

Provider interoperability cannot depend on whether an application previously
used a tuple or JSON list for the same bibliography. Fixing it by rewriting
registered data would change caller-owned state and undermine prepared credits.

## What was refuted

Identity caches and JSON conversion on every scientific call are unnecessary.
The existing prepared-credit guard already distinguishes registered and portable
representations; observation needs that distinction too. Genuine metadata
changes and non-portable registry data remain E012 before activation, while
replacement/deletion during observation remains W019 and preserves science.

## Scope and exclusions

Ackredit observer activation and frozen runtime comparisons only. No schema,
dependency, sibling source change, stable promotion, tag or release. Reuse the
existing real PyUnitWizard report gate with valid pre-existing tuple registration.

## Acceptance criteria

Public contextual tracking and observation produce equal portable captures.
Existing raw registered values/objects survive activation, nesting and reuse.
Changed/deleted references still diagnose a gap without affecting the calculation;
real conflicts/non-portable records are refused before exports or registry mutate.
Relevant full source gates and the exact installed eight-cell receiving bundle pass.

## Local correction evidence

The first new test run fails three tuple/replacement cases with the reproduced
E012. After the repair, observed portable captures equal public contextual
tracking across independent sessions, nested observers and reused calls.
The original registered object and tuple authors remain unchanged. Guards also
exercise in-place nested-author changes and replacement/deletion diagnostics.
Instrumented provider normalization happens at activation and never again for
reused calls or the diagnosed gap. Existing conflict and atomic-preflight tests
remain green. Full Python 3.14.7 source gates pass 1,698 tests without skips,
Ruff, indexes and strict Sphinx. Hosted exact-source/installed evidence follows.
