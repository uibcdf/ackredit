---
summary: Prepare fixed contextual credits for repeated scientific dispatch.
issue: uibcdf/ackredit#87
status: resolved
opened: 2026-10-04
closed: 2026-10-06
verification: reproduced
area: [core, performance, integration]
guard: tests/test_prepared_credit.py::test_prepared_credit_is_detached_and_reused_in_independent_captures
normative:
blocked_by: []
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

## Registered representation guard

A final compatibility check reproduced a false replacement diagnosis for a
registered author tuple: portable JSON converts tuples to lists, so comparing
the raw registry to the JSON-normalized capture record is not valid. Preparation
now privately detaches the original representation for registry comparison and
separately normalizes the portable record. Registry data is not rewritten.
`test_registered_tuple_metadata_matches_public_portable_tracking` proves the
prepared result is identical to public contextual tracking while retaining the
registered tuple. Changed/deleted bibliography still receives E010.
The final local gate passes 1,636 tests without skips; Ruff and report indexes
remain clean. This is a representation fix, not a protocol or release change.

## Coupled receiving checkpoint (2026-10-04)

The installed development gate in `devguide/receiving_validation.md` exercises
prepared backend credit on the real PyUnitWizard source pin and normally
installs the original Ackredit 0.9.0 API in a separate process to test the
fallback without `prepare_credit`. Both routes retain references in independent
reused captures. Five receiving tests pass locally on Python 3.14.7; the
eight-cell hosted run remains pending at this pre-publication checkpoint and
will be linked in the issue. Fixed archive/resource hashes and the aggregate
zero-skip check prevent substituting editable/source smoke for installed evidence.
The 0.9.0 baseline is source-built and does not replace its public Conda file.

The first exact-source hosted qualification, `357083e` / run 37216812721, passes
all eight installed receiving cells, including the normally installed original
0.9.0 fallback, and its aggregate. All 40 tests pass with no skips/deselections;
downloaded archive, resource and event evidence verifies independently locally.
The separate ordinary-CI test precondition discovered in #88 remains a distinct
checkpoint, not a prepared-credit runtime failure or API promotion.

Final corrected source `fc00a6c` passes exact-source CI 37217509058 and coupled
receiving run 37217520167: eight installed cells, 40 tests, no skips/deselections
and a successful aggregate. Complete downloaded event artifacts and identical
candidate files verify independently locally. The reviewed source/hash/version,
reference-role, graph and fallback evidence is retained in
`devtools/receipts/function_provider_matrix_2026-10-04.json`. #88 is resolved;
the provisional prepared-credit decision still needs provider/receiver review.

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

## Concrete stability/release handoff (2026-10-04)

The independent central receiving review confirms the exact original pilot,
including genuine released-provider fallback. The current proposed bounded
contract and remaining release/maintainer decisions are in
[`../function_provider_contract_review.md`](../function_provider_contract_review.md).
Prepared credit's detached registered/portable representation distinction also
informs the observer-specific repair #92; this factory's runtime is unchanged.
The proposal keeps function entry and host-chosen completed credit separate,
and does not promote the API, select a tag or change the public portable minimum.

Observer correction #92 is qualified independently at `1a5dd45` with full CI
37230213187 and the eight-cell/48-test receiving matrix 37230225286, including
the real original-provider fallback. Reviewed evidence is retained in
`devtools/receipts/provider_registered_representation_matrix_2026-10-04.json`.
This factory's implementation remains unchanged; schema/API decisions stay open.

## Explicit provisional decision and lifecycle guards (2026-10-05)

The principal-maintainer decision retained centrally at MolSysSuite
`05f866ab7f17af6b046e89befa014460d5d13160` keeps this callable provisional;
the bounded experimental PyUnitWizard pilot is accepted. Public 0.10.1 delivery
under #93/#94 does not stabilize it. The maintained contract review records
separate exit criteria: callable stability can be decided independently of the
observer, declaration schema and shared client adoption.

`tests/test_provider_lifecycle.py` proves a single prepared callable serves four
thread-local sessions and eight independent reused captures per thread. Delayed
execution cannot mutate an expired inherited capture; the later capture and
workflow receive the credit. Concurrent scientific cancellation/failure earns
only function-entry references until the host actually invokes completed credit.
All five lifecycle guards pass against the original normally installed public
0.10.1 archive with shared provenance verification before/after tests; the
bounded receipt is `devtools/receipts/provider_lifecycle_2026-10-05.json`.
No runtime, dependency, portable schema, public file or stability promise changes.

## Repeated writer allocation checkpoint (2026-10-05)

Implementation follow-up #97 reduces temporary use and graph allocations in
the shared writers without bypassing registry comparison or any capture's
conflict preflight. Newly entered captures still receive fixed reused uses;
repeated targets retain additional parents and the existing journal change
events. The portable benchmark now measures explicit prepared calls separately.
Normally installed Python 3.14 medians for prepared capture fall from 4.25 to
2.59 µs, and nested prepared capture from 5.85 to 3.53 µs. Three paired real
PyUnitWizard trials retain the scientific controls and full raw samples in
`devtools/receipts/repeated_attribution_97_2026-10-05.json`. Four unchanged
installed receiving guards pass against both original and candidate files.
These are bounded local observations, not a new hosted matrix or public artifact.
Producer-owned repeated declaration copies remain uibcdf/pyunitwizard#111.
The provisional review and its separate stability exit criteria remain open.

## Combined producer/writer receiving checkpoint (2026-10-05)

PyUnitWizard #111 is resolved in runtime `8cd205f` and closing source
`0e422d06b0af56e4dd2b43cafd00f059221eb405`. Ackredit #99 refreshes the
installed producer pin and guards both real warmed Pint/unyt conversions.
Ackredit source `cf21cc178720e106081699e9c91c49199aa24122` passes all eight
supported installed receiving cells, 56 mandatory tests without skips, in
run 37309592507. Version/value invalidation, original capture immutability,
diagnosed conflicts, graph/roles, original 0.9.0 fallback and offline readers
remain exercised. Downloaded ZIP/content/event identities verify independently;
the reviewed receipt is
`devtools/receipts/combined_prepared_receiving_99_2026-10-05.json`.
This removes the outstanding producer-copy dependency from development
qualification. It neither adds a cumulative timing claim nor publishes new
bytes or promotes the callable. The separate stability decision stays open.

## Accepted source promotion; public delivery pending (2026-10-06)

Diego explicitly accepted the proposed bounded stable contracts for
`prepare_credit`, `observe_calls` and `ackredit.provider@1` together
("ok, procede"). This supersedes the earlier provisional decision without
retroactively changing original public 0.10.0/0.10.1 releases. The maintained
[accepted contract](../function_provider_contract_review.md) gives the exact
signatures, entry versus host-chosen completion boundary, exclusions, diagnostics
and forward compatibility scope. Source classification, user guidance and the
canonical integration guide implement that decision. Newer evidence APIs remain
provisional for their own explicit review.

The issue stays **partial** until the qualified public release delivering the
promise is selected, staged, installed/received on the required eight cells,
promoted as the same exact file and verified publicly. The forward promise
begins at that delivery, retaining signatures/meanings across later patch/minor
releases (including pre-1.0 and 1.x) and applying the removal/deprecation policy
to incompatible changes. Later readers preserve `ackredit.provider@1`;
incompatible interpretation requires another identifier.

Existing source/lifecycle/real receiving evidence supports the acceptance; it
does not qualify an unbuilt new release. `tests/test_integration_guide.py`
executes the canonical declaration/observation/prepared examples, including a
producer without Ackredit and failed science that earns no completed credit.
MolSysSuite #97 and MOLI #46 receive this decision and the guide-delivery request;
central synchronization, shared adoption and client release remain separately
owned. No sibling guide is edited locally and no automatic observation is added.

## Public delivery and resolution (2026-10-06)

Public **0.11.0** delivers the accepted bounded contracts. Original producer/tag
`85deae594e65b2fd443d6ca9a7347eb2bda537e1`, archive `ackredit-0.11.0-py_0.tar.bz2` and SHA-256
`df8963ca2d286f50b19eb778e95c54c5ebb79c12fb55a6504e7c23daf5717d4f` are preserved from staging through promotion.
All declared source gates pass; installed run
[37429662858](https://github.com/uibcdf/ackredit/actions/runs/37429662858)
passes eight cells and real receiving run
[37429666506](https://github.com/uibcdf/ackredit/actions/runs/37429666506)
passes 72 mandatory tests without skips. Downloaded original artifact identities
and the receiving aggregate verify independently. Promotion
[37430816845](https://github.com/uibcdf/ackredit/actions/runs/37430816845),
public labels/index and clean public Linux/Python 3.14 provider/portable/CLI
checks and `pip check` pass. The [delivery receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/conda-build/receipts/ackredit_0.11.0_public_2026-10-06.json)
retains original identities and bounded evidence.

Stable-provider compatibility starts at `ackredit>=0.11.0`; the portable-only
minimum remains `>=0.9.0`. Original previous provisional releases are unchanged.
The registered guard protects this report's release metadata or bounded
provider/prepared behavior; exact-file native controls and receiving gates
protect installed provenance separately. Evidence APIs remain provisional.
Guide synchronization and client adoption/release retain their owners through
MolSysSuite #97 and MOLI #46. No sibling implementation is changed here.
