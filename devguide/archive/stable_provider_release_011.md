---
summary: Deliver 0.11.0 with accepted provider contracts and exact-file public qualification.
issue: uibcdf/ackredit#107
status: resolved
opened: 2026-10-06
closed: 2026-10-06
verification: measured
area: [release, packaging, integration]
guard: tests/test_release_citation.py::test_self_citation_matches_committed_release_candidate
normative:
blocked_by: []
supersedes: []
---

# Stable-provider release 0.11.0

## What

Deliver the maintainer-authorized next release checkpoint as 0.11.0, including
accepted stable `prepare_credit`, `observe_calls` and `ackredit.provider@1`
contracts under #84/#87 and reviewed post-0.10.1 features. Stable-provider public
compatibility begins only after this release's exact archive is qualified and
verified publicly. Evidence representation, collection and integrated reporting
remain provisional under their separate review.

## How

Commit the staged noarch plan, matching root/packaged CFF version/date, required
resources and release scope. Execute the exact producer's ordinary CI, full
Linux/macOS arm64 × Python 3.11–3.14 source matrix and both policy controls.
Use the existing immutable shared publisher pins to build one file once and
retain its original producer, filename and SHA-256. Stage and qualify that same
archive through the full installed matrix and real PyUnitWizard/independent
reader matrix, retaining the original 0.9.0 fallback. Promote without rebuilding
and verify public labels/index and a clean public installation. Register the
immutable version tag at the original producer and refresh editable metadata.

## Why

0.11.0 delivers visible CLI, composition, explanation and opt-in recorder-evidence
features alongside metadata fidelity and measured repeated-use improvements
(#95–#106). A minor checkpoint fits that scope. The accepted contract in
[the provider review](../function_provider_contract_review.md) supplies bounded
forward compatibility without converting general pre-1.0 intent into a global
stability claim. #84/#87 remain partial until stable public delivery is verified.

## What is measured and what is assumed

Prior source, installed development, public 0.10.1 and real-producer receipts
support the design and implementation review. They do not qualify new 0.11.0
archive bytes. Source, artifact-installed, real receiving and public-registry
claims remain separate; retain complete zero-skip receptor events and exact
original identities. Human primary-worktree BibTeX/LaTeX/notebook edits are
excluded by working in the clean owned worktree.

## What was refuted

Rebuilding during promotion, substituting editable/source smoke for exact-file
installed qualification, relabeling old public contracts as stable and requiring
every client to adopt observation are outside the accepted delivery.

## Scope and exclusions

The current source implementation, staged pure-Python noarch profile and
existing supported matrix. No sibling implementation changes, implicit observer,
new engine requirement, API promotion of evidence surfaces or retroactive tag/
artifact mutation. Central guide distribution, consumer runtime adoption and
consumer releases retain their own owners. Shared publisher failures are
reported upstream with original runs/receipts.

## Acceptance criteria

- Reviewed staged plan, original CFF metadata and packaged resources match 0.11.0.
- All declared exact-source gates execute successfully.
- One inspected archive is staged; its original source/name/digest are retained.
- All eight full installed cells and all eight real receiving cells pass without
  skipped/partial substitutes against that same file; independent readers retain
  original bibliography/versions, scopes, evidence and released-provider fallback.
- Exact-file promotion and independent public label/index checks succeed; a clean
  public installation passes provenance, portable/provider/CLI use and pip check.
- Retain durable public receipts, original-producer version tag, truthful public
  documentation and #84/#87 closure; notify receiving/coordinating owner issues.

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
