---
summary: Deliver 0.10.0 with exact Conda and real-producer qualification.
issue: uibcdf/ackredit#93
status: active
opened: 2026-10-04
closed:
severity: medium
verification: reproduced
area: [packaging, integration]
guard:
normative: devtools/conda-build/release_plan.toml
blocked_by: []
supersedes: []
---

# Deliver Ackredit 0.10.0

## What

Diego authorized the next release checkpoint and canonical tag on 2026-10-04.
Deliver the current function-provider, prepared-credit and contextual-report
work in 0.10.0. `observe_calls` and `prepare_credit` remain provisional; the
review and adoption decisions in #84/#87, MolSysSuite #97 and MOLI #46 stay open.
The portable `ackredit.attribution@1` contract and its 0.9.0 minimum are retained.

## How

The committed staged noarch plan declares executed source CI, full matrix and
policies, followed by the complete installed suite on Linux/macOS arm64 and
Python 3.11–3.14. The existing real PyUnitWizard receiving lane gains an explicit
Conda profile: the pinned shared verifier installs and checks the exact staged
file before and after science. Only the producer and released fallback are built
as wheels; no candidate wheel can replace the Conda archive. All six receiving
tests execute in each cell, with original references, roles, versions, independent
reader/report, absence and original 0.9.0 fallback receipts retained.

The shared provider remains authoritative for archive inspection, installation,
Conda provenance, exact-file promotion and public index verification. Ackredit
only binds its scientific receipts to that verifier's successful identity.

## Why

Development wheel receipts prove the implementation but cannot qualify different
Conda bytes. Shipping provisional capabilities is distinct from promoting them
to stable contracts or requiring adoption in clients. No host gains an Ackredit
dependency through this release. PyUnitWizard stays at source
`33fec8a627505a4f5426babe87e8e85438105041`; no sibling source changes are needed.

## What was refuted

- Waiting for stable promotion is unnecessary for an explicitly provisional
  pre-1.0 release; it would conflate delivery with the pending contract decision.
- Rebuilding public 0.9.0 or creating its tag again is neither needed nor allowed.
- A wheel candidate, a skipped receiving test or one successful platform cannot
  establish qualification of the exact Conda file.

## Scope and exclusions

Ackredit delivery and owner evidence only. No stable API promotion, shared
adoption requirement, consumer release certification or Zenodo archival claim.
The synchronized guide copies and human work in the principal checkout are
preserved. The canonical integration guide retains its released portable scope.

## Acceptance criteria

- Required executed gates at the exact producer and one staged noarch archive.
- Eight full installed cells and eight real-producer cells against that same
  filename/digest, without skipped receiving tests.
- Label-only promotion and independently verified public availability and clean
  public installation, CLI and dependency closure.
- Immutable tag at the original producer; public receipt, installation/release
  documentation and handoffs in the linked owner issues.
- Archive this record only when delivery is complete; #84/#87 remain partial.
