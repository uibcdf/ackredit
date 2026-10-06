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

## Next work, in order

1. **Complete the distribution-input review, #108.** Read the
   [active record](https://github.com/uibcdf/ackredit/blob/main/devguide/pending_proposals/distribution_adoption_runtime_review.md)
   and [owning issue](https://github.com/uibcdf/ackredit/issues/108).
   Inspect existing shared operations before adding one. Review metadata,
   recipe, all maintained runtime environments and actual CI/source routes,
   including names, floors/ceilings and Python bounds. Classify build-only and
   inapplicable routes. If a reusable check is missing for multiple members,
   report it in [MolSysSuite #45](https://github.com/uibcdf/molsyssuite/issues/45)
   before duplicating logic. Add relevant negative guards in the owning tool.
   This formal adoption review does not reopen the completed release or request
   another artifact, upload or scientific suite on every internal push.
2. **Expose standalone provider validation, then third-party author tooling
   (roadmap G).** Open focused Ackredit issues before implementation. Reuse the
   parser/preflight owned by `ackredit/core/providers.py`; choose the public
   signature/result and stability boundary first. Validation must remain offline
   and inert: no use credit, wrappers or bibliography registration. Supply an
   independently installable dependency-free producer example and a concise
   author guide for software/article references and per-function declarations.
3. **Review the separate evidence contracts (roadmap J/F).** Decide schema and
   per-original association, unknown versus empty meanings, collection/failure
   guarantees and integrated rendering with receiving evidence. Record explicit
   acceptance, amendment or deferral; do not infer it from successful provider
   delivery. Additional recorders require concrete ownership/use cases, not an
   automatic expansion to every recorder.
4. **Continue the wider roadmap with owning issues.** K needs platform/client
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
- The primary checkout contains nine preserved human files: BibTeX/LaTeX
  implementation and tests, self-citation tests, the workflow notebook and
  untracked `tests/test_cite_keys.py`. Review `git status` and preserve them;
  use a clean owned worktree for independent work. Never reset them to make a
  test pass. The clean release branch is `feat/portable-contract-release-75`;
  its temporary path may be removed when no longer useful.
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

No new implementation is started by this checkpoint. At resumption, inspect
current local/remote state and owner replies before selecting the next change.
