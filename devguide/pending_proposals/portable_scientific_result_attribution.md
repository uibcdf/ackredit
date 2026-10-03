---
summary: Provide portable individual-result attribution with enclosing workflow credit.
issue: uibcdf/ackredit#75
status: partial
opened: 2026-10-01
closed:
severity: medium
verification: reproduced
area: [compatibility, provenance]
guard: tests/test_attribution_capture.py
normative:
blocked_by: [uibcdf/molsyssuite#88, uibcdf/molsyssuite#89]
supersedes: []
---

# Portable attribution for scientific results

## What

Support individual scientific result bibliography while also contributing to an
enclosing workflow. MolSysSuite adopted the bounded optional client profile under
uibcdf/molsyssuite#68; the portable provider contract remains owned here.

## How

Agree and implement supported capture/export/import carrying bibliography,
contextual roles and original producer versions. The canonical
`standards/ACKREDIT_GUIDE.md` now documents deferred loading, public registration,
scope and tracking, detached host-owned result records and application-owned
sessions. Existing eager/demo templates remain available with explicit scope.

## Why

Consumer uibcdf/molsysmt#27 publishes pilot evidence at
`e21f03d9992b87af2cc9285211adee888462be41`. Journals contain IDs, not complete
bibliography; isolated sessions do not imply enclosing-session propagation.
Deduplicated session subtraction loses references reused by individual results.
The pilot uses supported public operations and a local result schema; its measured
provider was editable/dirty, so it does not certify a published installation.

## What was refuted

Do not promote the pilot schema to a provider format, read private registries,
duplicate renderers or claim that journal persistence supplies portable capture.
An installed flag or mocked success alone does not prove actual provider credit.

## Scope and exclusions

Provider API, its tests and canonical guidance. Scientific detector implementation,
client branch merges and public releases remain separate. Provider implementation,
canonical publication, guide delivery and consumer adoption are distinct gates.

## Acceptance criteria

- Two analyses retain exact individual records, including references reused by both.
- An enclosing workflow receives both analyses' observations.
- A fresh reader retains bibliography and original versions without new credit.
- Roles distinguish criterion, adapted implementation and executed software.
- Real-provider tests cover absence/failure, detached ownership and lazy imports.
- Supported capture/export/import requires no per-occurrence instrumentation or
  implicit DOI lookup; canonical examples use that supported contract when ready.

## Implemented development contract (2026-10-02)

The provisional public names are `capture`, `Attribution` and `get_attribution`.
The provider-owned `ackredit.attribution@1` payload separates full bibliographic
`items` from contextual `uses`, retaining a saved `usage_tree`, capture `name`
and producer `context`. `track_item` accepts keyword-only `roles` and JSON
`context`; existing calls and identifier journals retain their contracts.

Capture observes reused credits beside the application's session, including
enclosing/nested captures in the same session. Detached export/import and
reporting do not register records or credit another calculation. Original
versions belong to software records and producer/use context; a shared article
can describe several executed dependency versions without changing its record.
Conflicting observed metadata for one ID is refused with `ACKREDIT-E011`;
malformed/unsupported portable payloads use `ACKREDIT-E010`.

Roles are use-level conventions: `scientific_criterion`,
`reference_implementation`, `executed_software`, and `software_description`.
The PyUnitWizard consumer in uibcdf/pyunitwizard#92 uses real Pint/unyt operations
to verify software-only, article-only and combined declarations. Pint software
metadata identifies its repository and executed version; no unit-library Pint
article DOI is fabricated. unyt additionally cites `10.21105/joss.00809`.

PyUnitWizard attribution is explicitly enabled with `with puw.attribution():`.
Normal conversions remain provider-free; active tracking has a measured fixed
cost of about 200–240 us per completed array dispatch on the test machine, so
the pilot is bounded rather than imposed on every ordinary conversion.

## Validation and remaining delivery

Python 3.13.14, source `2e9f509` plus this work, with pre-existing human BibTeX,
LaTeX, notebook and citation-test edits preserved byte-for-byte. Full local
pytest, Ruff and devguide gates pass; the documentation builds with one external
intersphinx-inventory warning. The capture/schema guard exercises exact reused
records, JSON refusal, conflicts, nesting, sessions, async isolation, detachment
and fresh-reader reports. The canonical portable guide example is executed by
`tests/test_integration_guide.py`.

PyUnitWizard's full suite has 656 passing tests and one documented NaN/JSON skip;
its own report includes numerical parity, empty arrays, genuine absence,
provider load/register/track failures, opt-in context restoration and async
isolation, an inert QuantityRecord paired with original bibliography, and a
reproducible cost benchmark. QuantityRecord's existing reader may load Pint to
verify its descriptor; bibliography reading itself loads neither Pint nor unyt
and neither read credits a new calculation.

MolSysMT adoption is requested through uibcdf/molsysmt#292, complementing
uibcdf/molsysmt#27;
no MolSysMT implementation is edited by this work. Central registration and
six-client guide distribution are tracked in uibcdf/molsyssuite#71. The registry
addition is prepared, preserving unrelated central edits; its synchronizer
requires committed, published canonical source before writing copies.

The issue and record stay partial while consumer review and published
compatibility remain open. This is development-source evidence,
not a released-installation claim; release machinery remains uibcdf/ackredit#22.

Independent qualification of the isolated source plus the workflow-reader
import fix passes 1,505 tests. That fix is separately owned by
uibcdf/ackredit#77: subprocesses must resolve the checkout under test rather than
an editable installation from another worktree. The committed notebook is
correct and unchanged; the maintainer's original files remain byte-identical.

## Published source and guide delivery (2026-10-02)

Commits `4228444` (portable attribution and canonical guide) and `4577c83`
(workflow-reader qualification) are published on Ackredit `origin/main`.
The central registered synchronizer passed source/destination preflight and
copied `ACKREDIT_GUIDE.md` to PyUnitWizard, MolSysMT, MolSysViewer, TopoMT,
PharmacophoreMT and ElastNetMT. Its subsequent check reports all six copies
current. Central registry publication remains tracked in uibcdf/molsyssuite#71;
guide delivery does not establish runtime adoption or a package release.

## Reviewed contract and candidate (2026-10-03)

The maintainer authorized contract stabilization and preparation of distribution.
`Attribution`, `capture` and `get_attribution` are classified stable with their
existing semantics; the first reviewed release is assigned to candidate 0.9.0.
`docs/content/user_guide/portable_attribution.md` defines operations, detached
ownership, role/context extensibility, failure behavior and schema-1 compatibility.
Later readers retain released schema 1; structural/meaning changes use another ID.
This bounded promise applies across 0.9.x and 1.x and does not make a public
distribution claim or change host activation policies.

The frozen real PyUnitWizard 0.27.0/unyt 3.1.0 record is guarded by
`tests/test_attribution_contract.py`: saved data retain original bibliography,
versions and ownership in a fresh reader without producer/engines/network/credit.
The capture and canonical-example guards remain in force. Fresh source-provider
integration passes 17 PyUnitWizard tests at `e766b7c` and 14 Sabueso tests at
`62a019d`, with no consumer code edits. These are consumer source tests, not
public installation receipts. Sphinx `-W` passes the full contract documentation.

The provider contract decision is complete in source. Keep this record partial
until candidate delivery and receiving-consumer installed compatibility are
recorded; those delivery gates remain coordinated with #22/#80. No 0.9.0 tag or
public artifact is claimed before the exact candidate is qualified and released.


## Published qualification and consumer guide handoff (2026-10-03)

The accepted contract is published in `840aab3`. Its four required hosted
workflows pass, including all eight Python 3.11–3.14 full-matrix test cells.
The canonical guide SHA-256 is
`24615e3a8894c7cba67fc92fd0323369e725c3bd88096df9eda9311ab8890ff5`.
All six local consumer copies match after the guarded central synchronization.
PyUnitWizard publishes the guide and updated #92 record in `dbafcc5`; focused
integration/reporting checks pass 26 tests and Ruff/index gates pass.

Owner publication handoffs are uibcdf/molsysmt#292,
uibcdf/molsysviewer#152, uibcdf/topomt#91, uibcdf/pharmacophoremt#19 and
uibcdf/elastnetmt#20. These reports request generated guide publication and
keep runtime adoption/public dependency floors separate. No runtime changes or
pushes were made in those five components. Central registration remains
uibcdf/molsyssuite#71; PyUnitWizard's relationship is still a prepared registry
proposal rather than claimed central-main adoption.

The first staged artifact cannot yet be qualified: run `37109889925` fails
before production/upload at the shared host-build executable boundary, reported
in uibcdf/action-build-and-upload-conda-packages#46 and recorded under #22.
The accepted source API and source-consumer tests remain valid; no installed
0.9.0 receiving-consumer or public artifact claim is made.


## Installed local Conda diagnostic (2026-10-03)

The #22 provider diagnosis now includes a real local 0.9.0 noarch artifact
installed normally on Python 3.14.7. Its exact digest, source and public core
providers are recorded in that report. The installed detached reader preserves
the frozen real PyUnitWizard/unyt bibliography and versions; reused capture
also passes. This is stronger than a source-only probe but remains local
integration evidence: no registry upload or receiving-consumer release is
claimed. Provider action #46/#47 and shared adoption MolSysSuite #78 precede
the hosted staged-file qualification. The accepted contract remains unchanged.


## Installed receiving-consumer diagnostic (2026-10-03)

The exact local noarch Ackredit artifact recorded under #22 is now tested with
an independently installed PyUnitWizard wheel built from published source
`dbafcc5d21604ce7c94e0cb645937d9233cf061c`:
`pyunitwizard-0.27.0+40.gdbafcc5-py3-none-any.whl`, SHA-256
`29720d6ab7d61a9233ce31cebdb3c3836cad7a645fc92d84b33ae6f498cdb6ff`.
The provider file remains `ackredit-0.9.0-py_0.tar.bz2`, SHA-256
`99e6f9b9f0a3b0a22c66e476230dddabd2ba0017c59beb3253fbadc781d665c6`.

All 17 existing PyUnitWizard backend-attribution tests pass on Python 3.14.7,
without skips, from a copied unchanged test module outside either checkout.
The selected runtime packages all resolve under the fresh environment's
site-packages, with no editable install: Pint 0.26.1, unyt 3.1.0, SMonitor
0.18.0, DepDigest 0.12.0, ArgDigest 0.13.0 and public Pytest Receptor 1.2.0.
`pip check` passes. The tests exercise software-only, article-only and combined
bibliography, reused references and enclosing workflows, numerical results,
true provider absence/failure, opt-in isolation and saved-result fresh readers.

This is installed compatibility between identified local candidate files,
not a public PyUnitWizard or Ackredit release claim. The existing owned guard
remains `uibcdf/pyunitwizard`'s
`tests/integration/test_backend_attribution.py`; it is not duplicated here.
The stronger receiver evidence is retained while the hosted staged-file matrix,
central provider adoption and separate public-promotion decision remain open.

## Hosted staging and Sabueso receiver qualification (2026-10-03)

The accepted portable source now has an actual hosted, verified staging file:
provider source `598abf993a2409c025de5e912acd7eb45a257ebd`, producer
`37136075066`, filename `ackredit-0.9.0-py_0.tar.bz2`, SHA-256
`37661090f6ad19a74b8155d8a4d4b4a068c9099f4ceba0743b3abfe887e97fe1`.
Its upload receipt is verified and an independent staging download matches.

Sabueso prepared source `7352cf4437dca6d0249c3af9777ad123926d2f31` is built
as `sabueso-0.11.0+17.g7352cf4.dirty-py3-none-any.whl`, SHA-256
`646cc731fbdb1765a8a84b4f4cdb7fdd90c914a6e859fb80a153e9e11659a191`.
The local build dirties Sabueso's tracked build output, not its runtime source;
all 348 packaged Python source modules, excluding generated version metadata,
are byte-identical to the stated commit, with no extra modules. This wheel is
a receiving source candidate, not a released Sabueso 0.12.0 file.

Four fresh Linux prefixes normally install the exact Ackredit staging
coordinate and public runtime dependencies on Python 3.11.16, 3.12.14, 3.13.15
and 3.14.7. The unchanged Sabueso acquisition/attribution modules run outside
both checkouts and pass 36 tests per minor with no skips. The public HsTIM
workflow checks original source intake, two result bibliographies, reused
credits, the enclosing workflow union and saved readers without new credit.
Pip check, installed Conda digest, provider distribution/runtime versions and
non-editable prefix/site-packages origins pass in each environment.

This provides real same-file receiver compatibility across the supported
minors. The required hosted Linux/macOS-arm64 matrix is still rejected before
execution by the helper/descriptor mismatch in uibcdf/molsyssuite#89. Its
repair is proposed in central PR #90; the corrected qualification caller for
an existing producer/file remains #88. Preserve the registered artifact and
its producer identity. Public delivery and a published dependency floor must
wait for the required hosted gate and already authorized promotion, followed
by clean normal public-channel installation. Sabueso #108 receives the precise
staging handoff and retains its own release blocker.
