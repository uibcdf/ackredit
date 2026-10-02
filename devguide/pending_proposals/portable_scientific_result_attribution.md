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
blocked_by: []
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

The issue and record stay partial while source/guide delivery, consumer review,
and published compatibility remain open. This is development-source evidence,
not a released-installation claim; release machinery remains uibcdf/ackredit#22.
