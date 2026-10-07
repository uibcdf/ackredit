---
summary: Defer 1.0 and pause feature development when stabilization depends on consumer adoption.
issue: uibcdf/ackredit#126
status: resolved
opened: 2026-10-06
closed: 2026-10-07
severity: medium
verification: inspected
area: [release, api, packaging, documentation]
guard:
normative: devguide/decisions.md
blocked_by: []
supersedes: []
---

# Pre-1.0 stabilization and consumer-adoption pause

## What

On 2026-10-07 the maintainer chose to continue **pre-1.0 releases**, because
Ackredit needs stabilization and dogfooding. The maintainer further specified
that development should pause when only stability remains, to give the other
MolSysSuite and MOLI components time to adopt Ackredit. Consumer owners supply
actual-use experience before general 1.x delivery is reconsidered.
The earlier 1.0.0 recommendation was not accepted. The completed post-0.11.0
scope below remains available for a future minor delivery; **0.12.0 is a possible
next version**, not an operative selection or publication authorization.

The inspected preparation baseline is
`535b2ae68a19b247f72f1064744af250a85cd14d`. It is not a frozen release producer;
the eventual authorized candidate must include reviewed release inputs and
self-citation. The current publisher plan still describes completed 0.11.0.

## How

### Included development

| Delivery change | Owning evidence | Boundary to preserve |
| --- | --- | --- |
| Stable bounded recorder evidence, opt-in collection and explicitly requested workflow/CLI reporting | #114; [accepted evidence review](../recorder_evidence_contract_review.md) | Forward promise begins at the separately qualified delivering release; public 0.11.0 retains its original provisional classification. Unknown/empty declarations, diagnosed gaps and inert saved readers retain their meanings. |
| Standalone `validate_provider(module) -> dict` and dependency-free provider author example | #111–#113/#125; [validator implementation](../archive/standalone_provider_validation.md), [author guide](../../docs/content/user_guide/provider_authors.md) | Trusted imported ordinary module, detached merged declaration, original metadata/role order, fresh reads and E012 refusal; no Ackredit credit, registration, wrapper or scientific call. Selected producer lazy-loader effects are producer-owned. Empty role lists remain valid unspecified use. |
| Faithful BibTeX keys and shared deterministic fallback allocation | #109; [repair](../archive/bibtex_citation_keys.md) | Preserve valid original keys; resolve invalid/case-clashing/generated collisions without losing distinct citations or double-escaping imported LaTeX. |
| Deferred feature imports and separated startup discovery | #116; [startup study](../archive/startup_discovery_costs.md) | Core operation remains available without optional engines. Actual feature failures retain diagnostics; measured startup benefits do not imply every workflow is faster. |
| Bibliographic editor/name and CFF book-kind fidelity | #120; [publication guide](../../docs/content/user_guide/publication_tools.md) | Preserve original structured people/entities, metadata and software releases; selected styles may omit available fields. |
| Supported DOI resolver/label presentation | #121; [publication guide](../../docs/content/user_guide/publication_tools.md) | JSON/BibTeX originals remain unchanged; unsupported or ambiguous forms remain original. Equal same-ID records share, same-ID conflicts refuse and distinct IDs/releases stay distinct. |
| Reviewed dependency-route inputs and reusable receiving tools/evidence | #108/#110, #115–#119, #120–#123 | Distribution guards and cost/engine/manager measurements retain their separate identities and limits; these tools are not new runtime dependencies or universal interoperability promises. |

Existing portable attribution, sessions/scopes, provider observation/prepared
credits, composition/explanation, persistence, output/plugins and optional
operations retain the source decisions reviewed under #125. Their earlier public
promises retain their original release floors. The general 1.x signature/meaning
commitment is accepted in source but its public delivery is deferred; it is not
part of the next pre-1.0 delivery. Its existing major-change/two-minor deprecation
policy remains documented in [API stability](../../docs/content/about/stability.md).
Documentation and release notes must preserve these distinct boundaries without
retroactively changing public 0.11.0 or weakening accepted bounded promises.

### Maintainer disposition — 2026-10-07

The preparation initially recommended 1.0.0 because theme F is complete in
source and #125 accepts the general 1.x promise. The maintainer instead chose
further stabilization and dogfooding before that delivery. Preserve #114/#125's
accepted source classifications; accepted intent and tests do not establish
sufficient habitual-use experience for the maintainer's release decision.

Continue with bounded pre-1.0 cycles. Select each delivery version from its
actual scope and qualification; do not declare a last pre-1.0 version, fixed
number of minor releases or arbitrary time period. Revisit 1.0 explicitly after
reviewing real-use evidence and feedback. Existing bounded compatibility promises
remain in force during those cycles; pre-1.0 is not permission to break them.

### Adoption pause and resumption

Finish this documentation checkpoint, then pause proactive feature development
on the current completed source scope. The inspected local bug queue is empty;
the only other open product issue is optional dashboard #58, explicitly outside
the priority scope. Source review/repairs are complete within their recorded
limits. This makes consumer adoption and observed stability the next phase;
it does not prove the absence of unknown defects or qualify a new release.

Keep adoption with the existing MolSysSuite/MOLI and consumer owners, through
#97/#46 and linked member issues. Do not start another Ackredit feature merely
to occupy the adoption period, require every unrelated component to import it,
or mandate a new workflow/owner on behalf of a consumer. The initial proposal
to prioritize a new PyUnitWizard dogfooding cycle was not selected; no first
habitual workflow has been claimed or executed under this decision.

Public 0.11.0 is already available for its delivered portable/provider contracts.
The standalone validator, later runtime repairs and accepted forward
evidence/validator promises still await a separately qualified minor delivery.
Consumers must not be told that those capabilities are in 0.11.0. If adoption
requires them, use the retained scope/gates below for an explicitly authorized
pre-1.0 delivery; source pins are separate development evidence, not public
dependency closure. This delivery work does not justify new unrelated features.

Resume focused Ackredit work for concrete owning adoption feedback, a
demonstrated defect or an explicit maintainer request. Keep failures in owning
issues with meaningful guards; revisit 1.0 with actual-use evidence and a new
release decision. The pause creates no scheduled polling, arbitrary waiting
period or claim that all consumers have adopted the provider. Pending CI stays
recorded with its exact head, owning issue and recovery route.

### Evidence for consumer-led dogfooding

When a consumer adopts Ackredit, retain evidence from its **owned habitual
workflow** rather than treating the existing receiving matrix as user adoption.
PyUnitWizard and Sabueso are existing receiving clients; their owners choose
the next actual workflow/input. The following outline is available for that
feedback, not a newly authorized consumer task. Synthetic publication fixtures
and automated scientific receiving cases remain useful guards, not a claim
of habitual use.

1. Identify the application/workflow owner, actual input and intended use of its
   references, saved results and reports. Record the installed Ackredit identity,
   exact file/digest or explicit editable revision, Python/platform and relevant
   producer/dependency versions. Keep development and public identities distinct.
2. Run the workflow in ordinary work, including repeat operations and the normal
   session/capture lifecycle. Retain completed scientific results and original
   references/roles/software versions. Observe unexpected citations, omissions,
   diagnostics and user effort. Entry evidence does not prove successful science;
   unrecorded use stays unknown. Do not manufacture failures in the habitual run
   or change a user's environment just to complete a checklist.
3. Save the actual detached result and inspect its intended workflow report and
   bibliography in a fresh reader without the original producer. Record input
   and saved-artifact hashes, expected versus observed references and whether
   reading creates any new execution credit. Use the existing public API/CLI and
   receiving tools, keeping original files intact. Inspect an actual publication
   route when this workflow needs it; the fixture studies remain separately bounded.
4. Compare cost and usability against the workflow's own baseline: startup,
   warmed calls, capture/session lifetime and saved reporting where relevant.
   Reuse owned `devtools/benchmark_lifecycle.py` or other applicable benchmark
   operations for investigation; a synthetic benchmark alone does not measure
   the application's full cost. Record sample/workload limits and scientific
   invariants. Optional provider absence/failure belongs in controlled receiving
   checks and must preserve the completed result.
5. File observed defects or missing capabilities in their owning repository,
   cross-link consumer evidence and add meaningful guards for the failure
   mechanism. Recheck the actual workflow against the corrected candidate and
   preserve both before/after identities. The workflow owner reviews remaining
   gaps before selecting the next pre-1.0 delivery scope.

| Evidence to retain in #126 or a linked owning issue | Current state |
| --- | --- |
| Real workflow owner, actual input and intended output/report route | Consumer-owned; no new first route selected here. |
| Installed/source identity, dependency versions and environment boundary | Existing receipts are background; bind the actual dogfooding run separately. |
| Completed scientific result and expected versus observed references/roles/versions | Not yet observed in the new habitual-use cycle. |
| Actual saved result, fresh-reader report, original hashes and no-new-credit check | Existing automated guards are background; retain actual-run evidence. |
| Workload cost, friction, owning feedback and corrected-run comparison | Collect observed facts; do not infer a successful cycle from green CI. |

Before reconsidering 1.0, review those actual-use outcomes, resolved/remaining
issues affecting the intended stable meanings, and any necessary changes within
the accepted compatibility rules. A general release still requires its separate
maintainer decision and all exact-candidate gates. This does not make every
future feature, sibling issue or client release a new blanket prerequisite.

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
alongside source acceptance of the outstanding public promises. Pre-1.0
deliveries can make these changes available and receive real-use feedback before
the general public stability commitment. Preserve the differences between source
review, controlled receiving, habitual dogfooding and exact-file qualification.

## What was refuted

Neither #114 nor #125 selected a release version or authorized publication.
Completing the source stability inventory does not require immediate 1.0;
the maintainer has chosen more actual-use evidence. Passing automated receiving
tests does not prove that the library has been used in habitual work.
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

- The maintainer's pre-1.0 direction, retained inclusion map and compatibility
  boundary are durable here and linked from current resumption guidance.
- Each proposed public promise retains its source acceptance and delivery floor;
  exact-candidate gates, original-file identity and currently missing evidence
  are explicit. Preparation receives applicable reporting/link/documentation and
  exact-head development CI checks.
- The accepted pause condition and consumer-owned adoption route are recorded
  in decision 22 and current guidance. Close #126 as a planning disposition,
  not as completion of dogfooding, consumer adoption or a release.
- Future real-use feedback is tracked by its owning issue and may reuse the
  evidence outline above. The maintainer records the operative pre-1.0 version
  and release authorization before candidate inputs or qualification change;
  publication must be explicitly covered or separately approved.

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

## Disposition validation — 2026-10-07

The accepted pre-1.0/adoption-pause documentation passes the same 262 selected
tests with Pytest Receptor, without skips/warnings, plus Ruff lint/format,
generated indexes, whitespace, nine relative archived-scope links and a fresh
strict Sphinx build. Module-based local conformance passes against the available
policy 1.0 checkout. These counts describe overlapping preparation checks on
different documentation inputs, not additional scientific qualification.

The prior documentation head `f9b77ea9952561b87c9d7bb7656048acd972f4a7` still has
six successful CI jobs and queued macOS/Python 3.14 in run 37578322269 at this
inspection; GH Run Receptor reports `PENDING` with native exit 3. Its policies
had already passed. The final disposition head and its observed CI/policy
outcomes are recorded in #126, including any missing evidence and recovery.
Closing this planning record does not clear pending CI or qualify a candidate.

## Subsequent delivery authorization — 2026-10-07

After reviewing the difference between completed source and public 0.11.0, the
maintainer explicitly authorized closing **0.12.0** for stabilization under
[Ackredit #127](https://github.com/uibcdf/ackredit/issues/127). This is a new
delivery instruction following the planning decision above, not a rewrite of
its original authorization boundary. The active release record owns candidate
inputs, qualification and conditional publication. Finish that minor delivery,
then resume the accepted feature-development pause for consumer adoption.

## Subsequent completed delivery — 2026-10-07

The separately authorized #127 delivery is complete in qualified public 0.12.0.
Its [archived record](release_0120.md) and [public receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/conda-build/receipts/ackredit_0.12.0_public_2026-10-07.json) preserve
original producer/file, all required gates and public installation evidence.
This completion does not rewrite the planning authorization above. Resume the
accepted feature pause for consumer adoption and habitual use; general 1.x,
client synchronization and client releases remain separate outcomes.
