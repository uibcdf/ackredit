---
summary: Reconcile developer guidance and complete the 0.12.0 adoption-pause checkpoint.
issue: uibcdf/ackredit#129
status: resolved
opened: 2026-10-07
closed: 2026-10-07
severity: medium
verification: measured
area: [docs, workflow, reporting]
guard: tests/test_devguide_claims.py::test_conceptual_site_uses_the_canonical_source
normative: AGENTS.md#local-gates; MOLSYSSUITE_GUIDE.md#direct-pushes-and-validation-checkpoints
blocked_by: []
supersedes: []
---

# Developer-guide review before the adoption pause

## What

The maintainer requested a developer-guide completeness/checkpoint review before
ending the 0.12.0 session and pausing proactive development for MolSysSuite/MOLI
adoption. At `887b81c525ff9b285150b2d801c557321b4d48fa`, the active workflow still
prescribes routine Python 3.13, a three-minor range, complete tests for every
change and an unqualified direct-main/no-reviewer route. Architecture omits the
delivered validator/evidence boundary; some operative prose describes published
capabilities as future development. The checkpoint omits the pending closeout
run and exact canonical-guide handoff identity.

## How

Reconcile owned current guidance against metadata, maintained environments,
root instructions, accepted suite policy and verified release receipts.
Distinguish historical development evidence from current public contracts.
Record actionable CI resumption, guide identities, adoption owners and the
accepted pause/reopen conditions. Preserve historical decisions and archived
source/file identities; consumer copies remain centrally synchronized.

## Why

A new session must not choose an obsolete interpreter, launch unnecessary full
science for prose, assume unrestricted direct pushes, repeat publication or
start deferred features merely because a historical milestone says "next".

## What was refuted

The release is already qualified and public; this review is not a new candidate
or feature cycle. Empty local queues do not prove completed consumer adoption or
green CI. Original closeout CI 37600532162 still has six successful jobs and
queued macOS/Python 3.14 at the initial inspection; GH Run Receptor reports
`PENDING`/exit 3. That fact does not invalidate the original producer's completed
source/full-installed/real receiving/public qualification.

## Scope and exclusions

Owned developer documentation, reporting record and indexes only. No production
or test changes, dependency/metadata/recipe changes, archive rebuild, copied-guide
repair, client adoption or general 1.x publication. Existing regression guards
and normative contributor policies supply the applicable checks; no new test
duplicates prose. The canonical conceptual-site guard protects reuse of the
updated architecture rather than reviving an independent stale site copy.

## Acceptance criteria

- Workflow matches routine Python 3.14, supported 3.11–3.14 and scoped validation.
- Checkpoint provides verified release/guide identities, observed CI, owning
  follow-up and practical resumption without relying on chat history.
- Active guidance distinguishes shipped APIs, historical evidence and deferred
  product/adoption work; no new feature is required before the pause.
- Applicable reporting/index/link/API/guide and strict documentation checks pass.
- Publish an unskipped documentation checkpoint, record exact-head CI truthfully,
  archive this completed review and retain any queued checks with their owner.

## Completed review — 2026-10-07

Reviewed all current developer-guide entry points, conceptual/workflow guidance,
status/roadmap/decisions, provider/evidence contracts, receiving procedure,
reporting protocol and queue/archive indexes. Historical reports remain evidence
for their own dated source; this review does not repeat their scientific studies.

- Workflow now matches Python 3.14, the four-minor source range, maintained Conda
  environments, scoped gates, receptors and authorized contributor routes.
- Architecture describes delivered composition/workflow, standalone validation
  and opt-in evidence with distinct public floors and producer-owned effects.
- Current status/roadmap distinguish shipped contracts from historical provisional
  checkpoints and wider deferred work. README links the evidence review and
  explains why empty queues do not establish external adoption.
- Checkpoint retains original 0.12.0 source/file/digest, delivered guide source/hash,
  observed CI and commands, owner notice links, pause/reopen conditions and useful
  actual-use feedback. It does not require new features or an arbitrary waiting
  period before adoption can start.

Applicable Python 3.14 checks pass **278 tests without skips**, Ruff lint/format,
report indexes, **262 developer-guide relative links**, pinned `policy-v1.5.6`
conformance and strict Sphinx. The first fresh Sphinx build found three newly
introduced relative JSON-receipt URLs that the included web pages could not
resolve; canonical repository URLs repair them and the strict rebuild passes.
No test or production behavior changed; existing conceptual-site regression
checks protect canonical-source reuse, and accepted root/suite contributor
rules remain the authority for Python, validation and authorization.

Retained local evidence:

- Pytest Receptor events SHA-256: `3235ab5ab62d039755e8be15024bf39f6c3defb5de6050b78a21ab309c257e0a`; complete and integrity-valid, outcome `PASS`.
- Strict final Sphinx log SHA-256: `a24f0b999f6ef93d43623a6d0ea76f46c714b02cf99df99e0990744f13317dd1`.
- Five external synchronized guides and the owned delivered integration guide
  remain byte-identical to release closeout `887b81c525ff9b285150b2d801c557321b4d48fa`.
  Original tag/archive, dependencies, recipe, scientific inputs and old receipts
  are unchanged.

The final documentation commit and its exact-head hosted results are recorded
in #129. Original release-closeout CI 37600532162 still has queued macOS/Python
3.14 at this inspection, with six jobs and both policies passed. Closing this
review does not clear that queued evidence. Inspect the existing run with GH Run
Receptor and record its terminal outcome in #127; inspect this review's head and
record its outcome in #129. No release gate or source rebuild follows from a
pending documentation runner.

There is no outstanding local implementation requirement before the adoption
pause. Optional dashboard #58, acknowledgement deferral #124, wider roadmap
ideas and consumer synchronization/adoption remain explicitly scoped and owned.
Pause proactive features; resume for concrete owning feedback, a demonstrated
defect or an explicit maintainer request. Automated receiving is not habitual
use, completed guide synchronization or a consumer release.
