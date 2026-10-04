---
summary: Reconcile conceptual architecture and current status with public portable attribution.
issue: uibcdf/ackredit#83
status: resolved
opened: 2026-10-04
closed: 2026-10-04
severity: medium
verification: measured
area: [docs, architecture]
guard: tests/test_devguide_claims.py::test_conceptual_site_uses_the_canonical_source
normative:
blocked_by: []
supersedes: []
---

# Conceptual documentation after public delivery

## What

At source `04015022d0e13a33ce6631bdc10d62ea10aefa74`, current status still
reports no public distribution, no real adoption and a non-blocking Python 3.14
lane. The conceptual site duplicates a superseded dependency pillar; the
architecture omits sessions and portable capture. Stability and integration
guidance call the delivered 0.9.0 contract a candidate, while the portable
contract page correctly identifies the public release. DueCredit export exists
but its explanatory pages call it planned.

## How

Reuse canonical conceptual sources in the Sphinx site. Explain declarations,
session observations, per-result capture, detached bibliography, rendering and
the separate identifier journal. Reconcile current statements against the
public delivery receipt, metadata, workflows and executed contract tests. Append
dated supersession notes to historical decisions rather than rewriting them.

## Why

Readers must distinguish missing functionality from obsolete documentation.
The remaining roadmap C/F gates concern released receiving adoption and the
final general API review; public provider delivery and Python 3.14 qualification
are already complete. Neither those results nor a guide sync establishes
central admission or a scientific client's release.

## What was refuted

This is not a missing capture implementation, a need to remove core dependencies,
an unimplemented DueCredit bridge or authorization to announce 1.0. The reviewed
portable schema and operations already ship in the immutable public 0.9.0 file.

## Scope and exclusions

Provider documentation only. Preserve historical observations, human work and
all runtime/API/package identities. No scientific consumer implementation is
changed. Publish the corrected canonical guide before a central registered
synchronization request; do not overwrite locally edited consumer guides.

## Acceptance criteria

The current status and conceptual site describe the implemented architecture and
public contract accurately. The site reuses the canonical conceptual sources,
API/guide examples and metadata checks pass, strict Sphinx builds succeed and
the canonical guide is committed/published. Cross-link a central request for
registered guide delivery and retain remaining consumer/admission/1.0 gates.


## Resolution and verification — 2026-10-04

The conceptual site now includes canonical `devguide/vision.md` and
`devguide/architecture.md`. The addressable guard verifies the exact include
routes and refuses a parallel copied body: it protects the divergence mechanism
that left the old zero-dependency promise on the site. Existing dependency-count
and naming checks hold the canonical vision to actual metadata. This guard
checks source authority, not the scientific truth of every prose statement.

The architecture explains declarations, application sessions, calculation
captures, contextual software/article roles, detached original bibliography,
identifier journals, renderers/plugins and provider/client responsibilities.
Status, interoperability and stability now describe the delivered 0.9.0 portable
contract. Historical global-session, persistence, Python and publication
checkpoints retain their text with dated supersession references. The roadmap
keeps receiving releases, central admission and the final general API review
open; no new runtime feature or 1.0 release is inferred.

Local Python 3.14 validation passes 1,562 tests without skips, including 257
focused documentation/API/portable/guide cases. Ruff lint and format, reporting
indexes and diff checks pass. Strict Sphinx builds pass consecutively. An
explicit rendered-HTML inspection confirms canonical dependency and capture
content and existing local link targets on the five conceptual/status/decision
pages; code/examples and API classification retain their existing guards.

The corrected canonical guide's SHA-256 is
`dab9d96a897f0e229837ffeda2a7277029a344cace6530a79ac55e5a90d3e529`.
[MolSysSuite #96](https://github.com/uibcdf/molsyssuite/issues/96) owns the
registered six-client delivery request and review of its older provider-status
reference. The exact published provider source will be handed off there after
push. Initial #68/#71 policy/registration decisions are not reopened.

The bounded central working-state probe found dirty/behind clients, including
modified or untracked consumer guides. They were explicitly preserved; no
consumer guide was overwritten and no scientific sibling implementation was
edited. Source publication, guide distribution, runtime adoption and public
consumer releases remain separate outcomes. Ackredit-local documentation is
resolved; owner-controlled distribution remains tracked centrally.

## Admission evidence update (2026-10-04)

After this closure, Liliana published Ackredit adoption `8c743b3`, updating
the caller to immutable `policy-v1.5.6` and the verified four-minor badge.
That frozen central registry records Ackredit's Python transition as
`admitted`. Current status, roadmap and the dated decision update now reflect
this owner-controlled admission. The earlier pending-admission statements
describe their observed checkpoint; MolSysSuite #51 remains open for other
members and guide distribution #96 remains separately owned.
