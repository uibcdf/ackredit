# Release notes

## 0.11.0 — candidate under qualification

The maintainer-authorized checkpoint is tracked in
[Ackredit #107](https://github.com/uibcdf/ackredit/issues/107). It is not yet
publicly delivered. The exact staged archive must pass full source/installed
and real receiving matrices before promotion and clean public verification.

- Typed CFF `preferred-citation` works retain their own work category and
  bibliography during import discovery, saved attribution and export. Preferred
  articles no longer inherit software DOI/version or lose year, journal, volume,
  issue and page bounds. Page counts remain distinct from page ranges.
- Preferred works receive their own discovered identity and do not credit
  alternative shipped references. Root software/shipped-paper behavior and
  manual injection precedence remain available; root datasets retain their type.
- CSL-JSON exports original CFF book/report/thesis/conference and periodical
  types, available calendar-date precision and separate page counts. Explicit
  year/month conflicts are preserved without mixing date components; literal
  publication dates do not borrow a release year. Original metadata remains
  available to detached offline readers (#96).
- Repeated attribution avoids temporary graph/use allocations after a use is
  retained. Registry/conflict checks, independent captures, new parent links
  and journal replay remain active; installed real-producer timings are
  documented separately (#97).
- CFF person/entity declarations reach CSL authors and editors without guessing
  identity from punctuation. Original particles, suffixes and single-component
  names retain their available meaning; explicit author/editor replacement
  remains authoritative. Detached source-name metadata survives offline reading
  (#98).
- The CLI explicitly reads portable saved attribution/bundles/evidence and
  exports a chosen report without mutating the input or importing producers (#101).
- `AttributionBundle` / `compose_attributions` preserve independent original
  results, share only equal bibliographic records and refuse conflicts. Workflow
  graphs remain independent rather than becoming an invented combined pipeline (#102).
- `explain_attribution` describes saved uses and available scope/origin/gaps;
  unrecorded facts remain unknown, without a completeness score (#103).
- Provisional `AttributionEvidence` retains explicitly supplied recorder evidence
  separately from original attribution. `capture(record_evidence=True)` collects
  actual function-provider origins, observation boundaries and diagnosed gaps;
  other recorder origins remain unknown (#104/#105).
- Explicit `evidence.report("workflow", include_evidence=True)` and the CLI
  `--include-evidence` flag join those declarations with original references,
  uses and graphs. Default reports/payloads stay unchanged and readers create
  no new credits or replayed diagnostics (#106).

These corrections are tracked in [Ackredit #95](https://github.com/uibcdf/ackredit/issues/95)
and [#96](https://github.com/uibcdf/ackredit/issues/96); the writer optimization
is tracked in [#97](https://github.com/uibcdf/ackredit/issues/97). CFF name
identity is corrected in [#98](https://github.com/uibcdf/ackredit/issues/98).
They are development changes, not features of the already published 0.10.1
archive. The portable payload version and core dependencies remain unchanged.

On 2026-10-06 the principal maintainer accepted stable source contracts for
`prepare_credit`, `observe_calls` and `ackredit.provider@1` under #84/#87.
Preparation remains inert; invocation credits the current session/captures and
the host owns completion. Observation retains selected-export entry/awaited
execution, context-local leases, restoration, documented exclusions and W019
gaps. Incompatible declaration interpretations require a new schema identifier.
The forward compatibility promise is planned for verified public **0.11.0**;
**no new stable-provider public version is claimed yet**. See
[API stability](stability.md) and [function providers](../user_guide/function_providers.md).
Newer evidence representation, opt-in collection and integrated reporting remain
provisional pending their own explicit acceptance.

## 0.10.1 — corrected public checkpoint

Delivery is complete under [Ackredit #93](https://github.com/uibcdf/ackredit/issues/93).
0.10.0 delivered the features below, but its packaged self-citation still names
0.9.0. [Ackredit #94](https://github.com/uibcdf/ackredit/issues/94) corrects that
omission in additive 0.10.1 and binds the citation version to the candidate
before tagging and to the exact installed release. The original public 0.10.0
archive and tag remain unchanged. Corrected 0.10.1 passed its own source gates,
eight full installed cells and 48 real PyUnitWizard receiving tests before
promotion of the same noarch file. A fresh public Linux/Python 3.14 installation
verifies matching citation/runtime/distribution 0.10.1, the portable and
provisional capabilities, CLI and dependency closure. Public Sabueso 0.12.0
passes 56 receiving tests and its offline example there. Exact identities and
separate proofs are linked from [installation](installation.md).

## 0.10.0 — provisional capabilities

- Explicit `observe_calls` records entered declared exports, including awaited
  coroutine execution, with original software and article references. Libraries
  declare an offline `__ackredit__` dictionary without depending on Ackredit.
- `prepare_credit` prepares a fixed contextual credit for repeated operations;
  the host invokes it at its chosen completion boundary. PyUnitWizard provides
  the real optional producer and released-provider fallback pilot.
- The `workflow` report combines numbered references, original roles and software
  versions with the saved graph. A fresh reader renders it without importing the
  producer, contacting a service or crediting execution.
- Shared graph targets expand once; deep provenance graphs avoid recursive
  traversal. Report plugins receive detached nested bibliography. Equivalent
  registered tuple/list metadata is accepted without replacing the registration.

At this original release, `observe_calls`, `prepare_credit` and provider
declaration interpretation were **provisional**. Observation covers selected direct module exports, not existing
aliases, generators, native internal calls or subprocesses. Credits do not claim
invocation counts, scientific success or a complete execution trace. See
[function providers](../user_guide/function_providers.md) and
[API stability](stability.md).

The released portable `ackredit.attribution@1` contract remains unchanged. No new
core dependency, automatic observation or consumer minimum follows from these
additions. The original exact archive's installed matrix and real-producer
evidence are retained under #93; its self-citation limitation is recorded
separately under #94. Corrected evidence identifies the new 0.10.1 archive.
