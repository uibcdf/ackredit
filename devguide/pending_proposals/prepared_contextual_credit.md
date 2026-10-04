---
summary: Prepare fixed contextual credits for repeated scientific dispatch.
issue: uibcdf/ackredit#87
status: partial
opened: 2026-10-04
closed:
verification: reproduced
area: [core, performance, integration]
guard: tests/test_prepared_credit.py::test_prepared_credit_is_detached_and_reused_in_independent_captures
normative:
blocked_by: [uibcdf/molsyssuite#97, uibcdf/moli#46]
supersedes: []
---

# Prepared contextual credit

## What

Provide an explicit, provisional `prepare_credit` factory for a fixed use of an
already registered reference. Repeated scientific dispatch can avoid repeating
declaration digestion and JSON preparation while retaining faithful independent
captures and the original producer's bibliography and version.

## How

`prepare_credit(item_id, used_by, *, roles=(), context=None)` validates and
privately detaches a registered record, role list and JSON context, prepares its
canonical use key and returns a zero-argument callable. Preparation credits
nothing. Each invocation checks the current registry against the frozen record
and writes through the existing locked session/capture/journal path. A replaced
or deleted reference raises catalog E010 before credit; the host can diagnose
that attribution gap through its existing optional-provider boundary.

This is explicit host-owned credit earned after an operation completes. It does
not prove entry into a function or create a call scope; `observe_calls` retains
that separate contract. Inputs changing after preparation do not change the
prepared use. Prepare a new callable when the intended use changes.

## Why

The real PyUnitWizard pilot, uibcdf/pyunitwizard#94, measured approximately
215 microseconds additional cost per small Pint conversion in its existing
completed-backend attribution path. A profiler identified repeated public
registration/argument digestion and JSON preparation as substantial costs.
The fixed declarations already prepared by `observe_calls` demonstrated the
shared internal writer needed by explicit completed-dispatch credit.

## What is measured and what is assumed

Seven test-first checks failed because the API was absent; implemented guards
exercise detached mutable inputs, independent sessions and nested result
captures, repeated references, persistence through the existing journal,
replacement/deletion and invalid/unknown declarations.

The owning real-producer record and raw before/after measurements are in
uibcdf/pyunitwizard#94. Synthetic prepared-entry cost alone does not demonstrate
real scientific workflow performance. Measurements exclude initial preparation,
imports and setup and retain versions and source fingerprints.

The first real small Pint result capture falls from 272.34 to 96.75 µs;
combined public-function/backend capture falls from 302.02 to 114.79 µs. For
100,000 values the corresponding medians are 338.81 to 165.85 µs and 379.25 to
183.55 µs. The ordinary control drifts from 48.95 to 47.33 µs for one value.
These are local total conversion timings, not a universal percentage or an
isolated-core cost. The raw seven samples and source SHA-256 values are retained
in the two `devtools/receipts/function_provider_94*2026-10-04.json` files owned
by PyUnitWizard #94. Captured backend attribution still adds about 49 µs above
the ordinary small conversion; the remaining cost is explicit.

The expanded local Ackredit gate passes 1,635 tests without skips on Python
3.14.7, with Ruff, report-index and strict Sphinx checks. The PyUnitWizard gate
passes 633 tests, with ten declared optional/sibling-dependent skips and one
existing deprecated-import warning. Provider/receiver protocol review remains
open rather than treating local gate success as a stable API decision.

## What was refuted

Repeated session-ID deduplication cannot supply reused references to independent
captures. Skipping public validation on mutable input identities is unsafe.
Accessing private Ackredit writers from a client would create an unsupported
cross-repository dependency. Removing scientific diagnostics to improve timing
would violate the integration contract.

## Scope and exclusions

One fixed explicit credit for an already registered item and a fixed caller.
No runtime dependency, background work, network lookup, schema change, universal
profiler, release or stable API commitment is added.

## Acceptance criteria

- Preparation is inert and all public inputs are validated and detached.
- Every invocation reaches the current session and every current capture.
- Replaced/deleted bibliography is diagnosed before it can be credited.
- Persistence retains the existing writer and independently reusable metadata.
- Real PyUnitWizard measurements show the cost change with numerical parity,
  original versions, reference roles, pipeline graph and released-provider fallback.
- Provider/receiver review resolves this provisional surface before 1.0.

## Dependencies and risks

Review is linked with uibcdf/ackredit#84, uibcdf/molsyssuite#97 and
uibcdf/moli#46. Public Ackredit 0.9.0 does not expose this factory; PyUnitWizard
retains its stable portable-call fallback when the capability is absent.
