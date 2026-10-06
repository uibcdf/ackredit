---
summary: Review bounded recorder evidence guarantees for an explicit stability decision.
issue: uibcdf/ackredit#114
status: partial
opened: 2026-10-06
closed:
verification: measured
area: [api, evidence, compatibility]
guard: tests/test_provider_lifecycle.py
normative:
blocked_by: []
supersedes: []
---

# Recorder evidence contract review

## What

Prepare the separate J/F product review of `AttributionEvidence`, opt-in capture
collection and explicitly requested integrated reports. The accepted provider
decision explicitly excludes these newer surfaces. All remain provisional until
the principal maintainer records acceptance, amendment or deferral.

## How

Review implementation, maintained guides, original #104/#105/#106/#107 receiving
receipts and current source guards. Add focused evidence-lifecycle guards and
retain an original hosted companion as a compatibility input. Publish the bounded
guarantees, exclusions, evidence and specific decision choices in a maintained
review document.

## Why

Successful tests establish implementation behavior; they cannot decide which
meanings future releases must preserve. Original-result associations, unknown
versus empty declarations, collector ownership and diagnostics need an explicit
promise independent of stable function observation or general 1.0 acceptance.

## What was refuted

The accepted provider decision and public 0.11.0 delivery do not promote recorder
evidence. An empty plane does not certify complete instrumentation or no failures.
Scientific failure or cancellation does not by itself diagnose a recording gap.
Additional recorder integration is not an automatic promotion prerequisite.

## Scope and exclusions

Review and supplementary qualification of the existing bounded contracts. No
runtime/schema change, new recorder, sibling source change, API reclassification
or new public release is implied. General 1.0 and client object boundaries remain
independent decisions. The issue stays open for the actual maintainer decision.

## Acceptance criteria

- A concrete review maps each proposed guarantee and exclusion to behavior,
  durable guards and exact original installed receiving scope.
- Supplementary guards establish evidence behavior for cancellation, warning
  filters, unawaited calls and delayed completed credits, including cleanup.
- A retained original hosted companion remains readable without the producer,
  new credits, diagnostics or network use; original reports and per-result
  declarations preserve their meanings.
- Applicable reporting/index, Ruff, documentation and exact-head controls pass.
- The principal maintainer explicitly accepts, amends or defers each reviewed
  surface; accepted classification/delivery work follows that concrete decision.

## Review outcome

The [maintained review](../recorder_evidence_contract_review.md) recommends
bounded acceptance of all three surfaces, mapping concrete guarantees to existing
and supplementary guards. Four evidence-enabled lifecycle variants and two
original hosted saved-reader cases pass within 149 selected Python 3.14.7 tests,
without skips or warnings. The original #106 native ZIP and saved JSON hashes
were verified before retaining the unmodified compatibility fixture. Runtime
implementation and provisional classification remain unchanged.

Analysis and selected qualification are complete. #114 remains open for the
principal-maintainer's acceptance, amendment or deferral; there is no inferred
approval, new release or broad-recorder obligation. Another 231 documented-API,
stability and reporting cases pass. Ruff 0.16.5 lint/format, generated indexes,
current suite repository conformance and strict Sphinx pass. Sphinx required
authorized network access for its Python inventory after sandbox DNS failed.
Exact published-head controls are recorded in the owning issue.
