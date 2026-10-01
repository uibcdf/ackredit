---
summary: Provide portable individual-result attribution with enclosing workflow credit.
issue: uibcdf/ackredit#75
status: partial
opened: 2026-10-01
closed:
severity: medium
verification: inspected
area: [compatibility, provenance]
guard:
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
client branch merges and public releases remain separate. Guide delivery is partial
progress, not portable API implementation or adoption in every member.

## Acceptance criteria

- Two analyses retain exact individual records, including references reused by both.
- An enclosing workflow receives both analyses' observations.
- A fresh reader retains bibliography and original versions without new credit.
- Roles distinguish criterion, adapted implementation and executed software.
- Real-provider tests cover absence/failure, detached ownership and lazy imports.
- Supported capture/export/import requires no per-occurrence instrumentation or
  implicit DOI lookup; canonical examples use that supported contract when ready.
