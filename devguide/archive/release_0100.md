---
summary: Deliver the corrected 0.10.1 checkpoint with exact Conda qualification.
issue: uibcdf/ackredit#93
status: resolved
opened: 2026-10-04
closed: 2026-10-05
severity: medium
verification: reproduced
area: [packaging, integration]
guard:
normative: devtools/conda-build/release_plan.toml
blocked_by: []
supersedes: []
---

# Deliver Ackredit 0.10.0 and its additive 0.10.1 repair

## What

Diego authorized the next release checkpoint and canonical tag on 2026-10-04.
Deliver the current function-provider, prepared-credit and contextual-report
work in 0.10.0, followed by the self-citation correction in 0.10.1 under #94.
`observe_calls` and `prepare_credit` remain provisional; the
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

## 2026-10-04 first publication and correction

Original source `16c356d` passed 1,710 local tests, source CI/full matrix and
policies. Staging 37237182299, installed 37237527349 (eight cells), real receiving
37237527141 (48 tests), promotion 37237913352 and a clean public Python 3.14.7
installation pass. Ten downloaded native scientific artifact ZIP digests and
their contents verify; the independently reconstructed aggregate is identical.
Tag 0.10.0 preserves this original producer. Public facts remain in the retained
receipt, including the discovered self-citation defect.

The CFF still named 0.9.0; #94 adds the missing plan/runtime identity guards.
0.10.1 repeats all required source, installed, real-producer and public gates
against its own new immutable archive. Delivery remained active until that
corrected file was independently verified.

## Resolution (2026-10-05)

Original corrected producer `dd500842b6085111e01e62cfc243f68406eb8cc7` passes
source CI 37268373385, full source matrix 37268372798 and both policy lanes.
Final closure passes 1,714 local tests, Ruff, current indexes and strict Sphinx.
Staging 37268654191 builds `ackredit-0.10.1-py_0.tar.bz2` once,
SHA-256 `26e75a0780ad4e6abc2de55df90b29b4a2aa4e510d6b50fa54a5812ad929228e`.
Installed 37268949725 passes eight full-suite cells; real receiving 37268949118
passes 48 mandatory tests across eight cells. Native artifacts and reconstructed
scientific aggregate independently verify.

Promotion 37269544505 adds the public main label to that same file; the shared
verifier independently confirms its public label and solver index. Clean public
Linux/Python 3.14.7 confirms accurate CFF/runtime/distribution 0.10.1, portable and
provisional capabilities, CLI and `pip check`. Public Sabueso 0.12.0 passes 56
unchanged receiving tests and its source-trace/three-result/saved-reader example.
The immutable `0.10.1` tag identifies the original producer; editable development
metadata is refreshed separately. Original 0.10.0 bytes/tag are preserved.

The reviewed
[delivery receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/conda-build/receipts/ackredit_0.10.1_public_2026-10-05.json)
and maintained installation/release documentation satisfy the committed noarch
plan's source, exact-file and public acceptance criteria. Impact owners receive
the version/file/digest and bounded evidence. #84/#87, MolSysSuite #97 and MOLI
#46 remain open for contract review; there is no stable promotion, client release
certification, new consumer minimum or DOI/archival claim.

Impact handoff owners are MolSysSuite #97, MOLI #46, PyUnitWizard #94,
Sabueso #108, MolSysMT #292, MolSysViewer #152, TopoMT #94,
PharmacophoreMT #19 and ElastNetMT #20. Their issues retain pre-publication
notice and post-publication evidence separately from source adoption or
consumer-release qualification.
