# Development checkpoint — 2026-10-06

Start here when resuming work. This is an operational handoff, not a new API
contract or a replacement for the [roadmap](roadmap.md), [status](status.md),
[decisions](decisions.md) and issue-backed queues. Refresh it when the working
state or next steps change.

## Completed and verified

Public **0.11.0** completes #84/#87/#107. The immutable tag points to original
producer `85deae594e65b2fd443d6ca9a7347eb2bda537e1`; later documentation commits
do not replace it. The original `ackredit-0.11.0-py_0.tar.bz2` has SHA-256
`df8963ca2d286f50b19eb778e95c54c5ebb79c12fb55a6504e7c23daf5717d4f`.

Required exact-source gates, eight Linux/macOS arm64 × Python 3.11–3.14
installed cells, 72 real PyUnitWizard receiving tests without skips, independent
artifact/aggregate verification, exact-file promotion and a clean public
Linux/Python 3.14 installation are complete. Public download bytes, installed
origins, citation/runtime/distribution identity, provider/prepared/portable use,
CLI and clean-environment `pip check` pass. Do not build or promote this release
again. [Installation](../docs/content/about/installation.md) links the public
file and runs; the
[delivery receipt](https://github.com/uibcdf/ackredit/blob/aae9ad98c89d162b946a65fa01603707db02359a/devtools/conda-build/receipts/ackredit_0.11.0_public_2026-10-06.json)
retains original identities, proofs and limits.

Closeout `aae9ad98c89d162b946a65fa01603707db02359a` passes all seven
[CI jobs](https://github.com/uibcdf/ackredit/actions/runs/37433598657),
[suite policy](https://github.com/uibcdf/ackredit/actions/runs/37433599205) and
[publication policy](https://github.com/uibcdf/ackredit/actions/runs/37433599278).
Local closeout passes 262 selected tests without skips, Ruff, indexes and strict
Sphinx. These results apply to those inputs; this checkpoint's subsequent
documentation-only commit receives its own applicable validation.

`prepare_credit`, `observe_calls` and `ackredit.provider@1` now have their
accepted bounded public compatibility promise from **`>=0.11.0`**. Portable-only
clients retain **`>=0.9.0`**. Earlier provisional releases are unchanged.
`AttributionEvidence`, opt-in capture evidence and integrated evidence reports
remain provisional. General 1.0 API commitment is still a separate decision.
See [the accepted provider review](function_provider_contract_review.md) and
[API stability](../docs/content/about/stability.md).

The final clone-cleanup request authorizes publication of the previously
preserved BibTeX/LaTeX changes, format tests and workflow notebook outputs.
Review added collision/newline guards and completed the source repair under
[Ackredit #109](https://github.com/uibcdf/ackredit/issues/109). This is development
after public 0.11.0; the release file and original producer remain unchanged.
Local Python 3.14.7 validation passes 6,207 tests without skips, Ruff and strict
Sphinx. The owning issue retains the published head and its applicable CI
evidence; the [archived repair](https://github.com/uibcdf/ackredit/blob/main/devguide/archive/bibtex_citation_keys.md)
records the scope.

## Completed development after 0.11.0

The distribution-input review #108 is implemented through accepted
[MolSysSuite #105](https://github.com/uibcdf/molsyssuite/pull/105) and integrated
[Ackredit #110](https://github.com/uibcdf/ackredit/pull/110). One recipe, five
environments and ten workflows use the pinned shared guard. The
[archived review](https://github.com/uibcdf/ackredit/blob/main/devguide/archive/distribution_adoption_runtime_review.md)
retains source/receipt evidence and limits. MolSysSuite #45 owns its separate
central adopted/readiness/access inventory update.

[Ackredit #111/#112](https://github.com/uibcdf/ackredit/pull/112) implements
provisional `validate_provider(module) -> dict` through the observer's parser,
without Ackredit credit, bibliography registration or export mutation. Explicit
lazy loaders retain their producer side effects. The
[archived implementation](https://github.com/uibcdf/ackredit/blob/main/devguide/archive/standalone_provider_validation.md)
records 24 guards and 2,122 local tests without skips/warnings; combined source
also passes all 16 routes and 303 selected tests. Required Ruff and strict docs
pass. The new export is absent from public 0.11.0; API promotion and future
artifact delivery remain separate.

Integrated development `7737d6ec7a477244f332e34080d26f1bc39822cc` passes all seven
[CI jobs](https://github.com/uibcdf/ackredit/actions/runs/37448899290),
[suite policy](https://github.com/uibcdf/ackredit/actions/runs/37448900271) and
[publication policy](https://github.com/uibcdf/ackredit/actions/runs/37448900303).
The subsequent documentation closeout receives its own applicable checks.

[Ackredit #113](https://github.com/uibcdf/ackredit/issues/113) completes the
[provider author guide](../docs/content/user_guide/provider_authors.md) and
`examples/citation_provider`. The former installed fixture is now the single
public example source, used by existing observer/evidence guards. It installs
with no runtime dependencies and computes with Ackredit imports blocked.
The installed guard also checks inert development validation, actual-call
software/article credit and detached reading without the producer. Local
Python 3.14.7 gates pass 389 selected tests without skips/warnings, Ruff,
indexes, all 16 dependency routes and strict Sphinx. The owning issue retains
the exact published head and its hosted controls. The
[archived record](https://github.com/uibcdf/ackredit/blob/main/devguide/archive/provider_author_guide.md)
keeps scope and evidence; the validator remains provisional and absent from
public 0.11.0.

## Next work, in order

1. **Record the evidence-contract decision (roadmap J/F, #114).** The
   [concrete review](recorder_evidence_contract_review.md) recommends bounded
   acceptance of representation, provider-observer collection and explicitly
   requested integrated reporting. It maps schema/per-original association,
   unknown/empty meanings, failure/ownership guarantees and exclusions to real
   saved receiving data and 149 selected tests, including six supplementary
   cases. The principal maintainer must explicitly accept, amend or defer each
   surface. Classification remains provisional until that decision; do not
   infer it from green tests. Accepted source guidance and a future delivering
   release need their own scoped work. Additional recorders require concrete
   owning use cases rather than automatic expansion.
2. **Continue the wider roadmap with owning issues.** K needs platform/client
   object-boundary decisions; L needs complete import/activation/runtime/memory/
   reporting cost measurements; M needs actual publication-tool/style round trips;
   N starts with accepting, deferring or excluding acknowledgements. The final
   general 1.0 review remains separate. #58's optional dashboard is not a priority
   or a dependency of these steps.

## External handoffs and constraints

| Owner | Remaining action | Boundary |
| --- | --- | --- |
| [MolSysSuite #97](https://github.com/uibcdf/molsyssuite/issues/97), [MOLI #46](https://github.com/uibcdf/moli/issues/46) | Synchronize the committed canonical `standards/ACKREDIT_GUIDE.md` through the registered consumer route; coordinate client adoption/object contracts | Canonical publication, copied-guide synchronization and runtime adoption are separate. Do not repair sibling copies locally. |
| [PyUnitWizard #94](https://github.com/uibcdf/pyunitwizard/issues/94#issuecomment-6012159851), [Sabueso #108](https://github.com/uibcdf/sabueso/issues/108#issuecomment-6012160193) | Review the delivered version/file/digest and bounded qualification evidence; client owners decide their required minimum and release qualification | A provider release does not certify a consumer release. |
| [MolSysSuite #82](https://github.com/uibcdf/molsyssuite/issues/82#issuecomment-6012041397) | Reconcile the current shared environment's unrelated scientific dependency conflicts | Ackredit's editable identity agrees and clean public installation passes; the current shared environment as a whole fails `pip check`. Do not silently downgrade other work's dependencies. |
| [MolSysSuite #104](https://github.com/uibcdf/molsyssuite/issues/104), [MOLI #61](https://github.com/uibcdf/moli/issues/61) | Adopt temporary-resource cleanup in component governance and applicable tools | `/tmp` may contain artifacts or evidence while needed. Delete them when no longer needed. There is no requirement to relocate necessary evidence outside `/tmp`. |

For MolSysMT and other siblings, use owning issues; do not change their sources.
PyUnitWizard changes are authorized only with its own required devguide/issue
records. Ackredit internal direct pushes are authorized; choose gates by scope
and finish with inspected applicable controls on the exact published head.

The release/guide handoff is already posted to
[MolSysSuite #97](https://github.com/uibcdf/molsyssuite/issues/97#issuecomment-6012159207)
and [MOLI #46](https://github.com/uibcdf/moli/issues/46#issuecomment-6012159535).
Guide adoption replies/commits are still separate owner evidence.

## Local resumption checks

- Routine development is Python 3.14 in `molsyssuite@uibcdf_3.14`, with Ackredit
  installed from its primary checkout using `pip install --no-deps --editable .`.
  Verify interpreter, import path and matching runtime/distribution versions
  at or above 0.11.0. A development suffix and dirty primary checkout are not
  the immutable release. Keep clean artifact tests separate.
- The formerly preserved nine human files are included in the authorized #109
  publication. The primary branch is `main`, tracking `origin/main` (the remote
  is named `origin`, not `upstream`). Verify a clean `git status` and matching
  local/remote heads at resumption. Historical local branch commits are already
  reachable remotely; their worktrees may still contain independent work.
  Never reset or discard such work to make a test pass.
- The read-only `/tmp` inventory found approximately 65.7 GiB total and 7.2 GiB
  in 298 Ackredit-prefixed directories at the recorded snapshot. Old release
  environments/caches and generated outputs are cleanup candidates, not proof
  that every path is obsolete. An old registered worktree has uncommitted work.
  Inventory files were `/tmp/ackredit011-tmp-inventory.json` and
  `/tmp/ackredit011-tmp-ackredit-inventory.tsv`; their continued existence is not
  required to resume. Recheck actual ownership, use and space before cleanup.
- Use the active queues for implementation reports; an empty bug queue does
  not mean the roadmap is complete. Update the report, guard and indexes when
  each issue changes lifecycle. Historical receipts describe their own inputs.
- Reuse applicable local evidence while its inputs/environment/scope remain
  unchanged. Documentation needs reporting/link/guide checks and strict build;
  executable changes need meaningful contract/behavior gates. Required source
  range remains Python 3.11–3.14, with installed Linux/macOS arm64 release gates.

The completed #108/#111/#113 work does not publish another release or accept
the remaining evidence contracts. At resumption, inspect current local/remote
state and owner replies, then resolve #114's explicit evidence-contract decision.
