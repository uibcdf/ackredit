---
summary: Review a bounded 1.0.0 delivery of completed post-0.11.0 development.
issue: uibcdf/ackredit#126
status: open
opened: 2026-10-06
closed:
severity: medium
verification: inspected
area: [release, api, packaging, documentation]
guard:
normative:
blocked_by: []
supersedes: []
---

# Next release scope and version recommendation

## What

Prepare a concrete delivery decision from development completed after public
0.11.0. Recommend **1.0.0**, subject to explicit maintainer authorization and
successful exact-candidate qualification. This record is a proposal, not an
operative version selection, release authorization or qualification receipt.

The inspected preparation baseline is
`535b2ae68a19b247f72f1064744af250a85cd14d`. It is not a frozen release producer;
the eventual authorized candidate must include reviewed release inputs and
self-citation. The current publisher plan still describes completed 0.11.0.

## How

### Included development

| Delivery change | Owning evidence | Boundary to preserve |
| --- | --- | --- |
| General stable API signature/meaning commitment through 1.x | #125; [API stability](../../docs/content/about/stability.md), [accepted adoption review](../archive/general_stability_review.md) | Begins at qualified public 1.0.0. Incompatible removal or meaning changes require a major release after at least two minor releases carrying deprecation and replacement guidance. Private implementation remains outside this contract. |
| Stable bounded recorder evidence, opt-in collection and explicitly requested workflow/CLI reporting | #114; [accepted evidence review](../recorder_evidence_contract_review.md) | Forward promise begins at the separately qualified delivering release; public 0.11.0 retains its original provisional classification. Unknown/empty declarations, diagnosed gaps and inert saved readers retain their meanings. |
| Standalone `validate_provider(module) -> dict` and dependency-free provider author example | #111–#113/#125; [validator implementation](../archive/standalone_provider_validation.md), [author guide](../../docs/content/user_guide/provider_authors.md) | Trusted imported ordinary module, detached merged declaration, original metadata/role order, fresh reads and E012 refusal; no Ackredit credit, registration, wrapper or scientific call. Selected producer lazy-loader effects are producer-owned. Empty role lists remain valid unspecified use. |
| Faithful BibTeX keys and shared deterministic fallback allocation | #109; [repair](../archive/bibtex_citation_keys.md) | Preserve valid original keys; resolve invalid/case-clashing/generated collisions without losing distinct citations or double-escaping imported LaTeX. |
| Deferred feature imports and separated startup discovery | #116; [startup study](../archive/startup_discovery_costs.md) | Core operation remains available without optional engines. Actual feature failures retain diagnostics; measured startup benefits do not imply every workflow is faster. |
| Bibliographic editor/name and CFF book-kind fidelity | #120; [publication guide](../../docs/content/user_guide/publication_tools.md) | Preserve original structured people/entities, metadata and software releases; selected styles may omit available fields. |
| Supported DOI resolver/label presentation | #121; [publication guide](../../docs/content/user_guide/publication_tools.md) | JSON/BibTeX originals remain unchanged; unsupported or ambiguous forms remain original. Equal same-ID records share, same-ID conflicts refuse and distinct IDs/releases stay distinct. |
| Reviewed dependency-route inputs and reusable receiving tools/evidence | #108/#110, #115–#119, #120–#123 | Distribution guards and cost/engine/manager measurements retain their separate identities and limits; these tools are not new runtime dependencies or universal interoperability promises. |

Existing portable attribution, sessions/scopes, provider observation/prepared
credits, composition/explanation, persistence, output/plugins and optional
operations are included in the general documented stability boundary reviewed
under #125. Their earlier public promises retain their original release floors.
Documentation and release notes must describe those boundaries together without
retroactively changing public 0.11.0.

### Version alternatives

**Recommended: 1.0.0.** Theme F is complete in source: every export has an
explicit stable decision, no provisional export remains, and #125 accepts the
general 1.x promise against actual adoption. Themes A–E have their recorded
foundation evidence. The [roadmap](../roadmap.md) defines 1.0 by that commitment,
not by completion of all future features or all clients. This proposal adds no
API removal or schema migration to earn the major number.

**Alternative: 0.12.0.** Deliver the same completed repairs and the accepted
bounded evidence/validator promises while postponing the general 1.x public
commitment. This remains valid if the maintainer chooses further pre-1.0
adoption. A new arbitrary feature or mandatory extra minor release is not
needed by the current stability rule. The operative version remains undecided.

### Compatibility and delivery inputs

Retain Python `>=3.11,<3.15`, routine Python 3.14 development and the existing
Linux x86-64/macOS arm64 × Python 3.11–3.14 qualification matrix. The package
remains pure Python/noarch. Keep declared floors `smonitor>=0.16.0`,
`depdigest>=0.11.0`, `argdigest>=0.13.0` and `pyyaml>=6`; #119's public
SMonitor 0.19.0 / ArgDigest 0.15.0 receiving evidence does not alone justify
raising floors. Resolve core providers through their actual Conda routes, with
normal Ackredit installation using `pip install --no-deps` where appropriate.

Hosts retain optional Ackredit operation: absence or diagnosed provider failure
must preserve completed science. Keep original attribution/provider/evidence
schema identifiers and explicit default opt-in behavior. Canonical guide
synchronization and runtime client adoption remain independent, owned by
[MolSysSuite #97](https://github.com/uibcdf/molsyssuite/issues/97) and
[MOLI #46](https://github.com/uibcdf/moli/issues/46).

### Qualification sequence after release authorization

Use the existing [packaging route](../../devtools/conda-build/README.md) and
owned tools rather than a new task-specific publisher or evidence parser.

1. Record the authorized version/scope here and in #126. Review and commit
   `devtools/conda-build/release_plan.toml`, self-citation, candidate release
   notes and applicable resource/contract assertions. Recommend the existing
   **staged** route because accepted new public promises and a new export need
   exact-file receiving before promotion. Bind a full original producer SHA.
2. Execute ordinary CI, the full eight-cell source/installed-wheel matrix and
   both policy workflows for that exact source. Preserve required tests,
   warnings, skips and native exit statuses; a backlog probe is not the full
   matrix. Inspect hosted runs through GH Run Receptor.
3. Build one noarch archive once with the pinned shared staged builder. Inspect
   version, resources and self-citation; retain original filename, producer and
   SHA-256. Install that same archive outside source in all eight cells through
   `test_staged_conda_package.yaml`, executing its full installed tests and
   before/after provenance checks. A selected source test or development wheel
   does not qualify this archive.
4. Execute `function_provider_receiving.yaml` in its Conda profile against that
   original archive and the pinned real PyUnitWizard producer. Require all eight
   cells and the independent aggregate, without skipped mandatory science.
   The current nine cases per cell cover original references/roles/graphs,
   failures, prepared credits, detached readers, composition, provider absence,
   released fallback and actual provider evidence. Full installed contract tests
   separately cover the standalone validator; the existing receiving matrix does
   not by itself prove that new operation.
5. From an isolated installation of the same archive, rerun the bounded saved
   publication fixtures through `devtools/check_publication_tools.py`, both
   `devtools/check_biblatex.py` styles and `devtools/check_jabref.py`, using the
   reviewed external distributions and fresh output directories. Bind original
   input hashes, tool versions, native outcomes and candidate identity; preserve
   warnings, originals and no-new-credit assertions. Execute the installed
   dependency-free example and validator/empty-role path as well. Missing an
   engine cannot count as completing its designated gate. Keep historical
   #120–#123 receipts unmodified and limit renewed claims to executed routes.
6. Once all applicable gates pass and publication is authorized, promote the
   exact SHA-256 through the existing shared verifier. Verify public main-label
   and solver-index records, then perform a clean public Linux/Python 3.14
   installation with runtime/distribution/citation identity, CLI, saved and
   provider/evidence/validator behavior, optional absence and dependency closure.
   Keep any read-only verification retry separate from promotion.
7. Register the immutable version tag at the original producer after verified
   delivery, retain the public receipt and effective promise floors, and hand
   off guide/version/file/digest evidence to the existing owners. GitHub Release,
   Zenodo archival, central classification and client releases retain separately
   observed outcomes; the package's major version proves none of them alone.

No candidate archive, full release matrix, candidate publication-engine rerun,
staging, promotion or clean public installation has been executed for this
proposed version. Existing development CI and the #121 wheel used by later
studies are preparatory evidence, not transferable release qualification.

## Why

The work since 0.11.0 contains useful runtime repairs and a new accepted export,
alongside source acceptance of the outstanding public promises. A concrete
delivery can make those changes available without creating another feature
cycle. Separating original development evidence from exact-file delivery keeps
the general 1.0 decision meaningful and the published artifact immutable.

## What was refuted

Neither #114 nor #125 selected a release version or authorized publication.
Public SMonitor/ArgDigest availability does not require waiting for all sibling
improvements, and their tested newer versions do not automatically change
Ackredit's minimums. Theme M's bounded completed studies do not certify every
manager, style or candidate artifact. General stability acceptance does not
waive installed qualification or establish central mature/admitted status.

## Scope and exclusions

This proposal selects no operative version and changes no runtime, dependency,
schema, publisher plan, historical receipt or synchronized consumer copy.
It does not add acknowledgements: #124 requires an owned real use case to reopen
that scope. Dashboard #58, wider performance workloads, unqualified publication
routes, DepDigest #31, SMonitor #36 and platform/client adoption retain their
owners and explicit limits; they are not blanket prerequisites for this delivery.

## Acceptance criteria

- A reviewed inclusion map, version recommendation/alternative and compatibility
  boundary are durable here and linked from current resumption guidance.
- Each proposed public promise retains its source acceptance and delivery floor;
  exact-candidate gates, original-file identity and currently missing evidence
  are explicit. Preparation receives applicable reporting/link/documentation and
  exact-head development CI checks.
- The maintainer records the operative version and release authorization before
  changing candidate inputs or executing the qualification sequence. Keep #126
  open for that decision; archive this proposal only after its disposition,
  with a normative decision or successor delivery issue. Publication must be
  explicitly covered by that authorization or separately approved.

## Preparation validation — 2026-10-06

Python 3.14.7 in the existing isolated editable validation environment passes
262 selected reporting, devguide-claim, documented-API, stability, documentation
configuration and integration-guide cases using Pytest Receptor, without skips
or warnings. Ruff lint/format, generated indexes, whitespace and all eleven
relative links in this scope pass. A fresh strict Sphinx HTML build passes.
Local module-based suite conformance passes against the available policy 1.0
checkout; the published head's remote policy workflow checks its separately
pinned release. Consumed synchronized guides, runtime/candidate inputs and
historical receipts are unchanged.

These are preparation checks, not the complete source or installed release
matrices. Exact-head development CI/policy run identities and outcomes belong
in #126 after the documentation checkpoint is pushed. They do not substitute
for any proposed candidate qualification or publication gate.
