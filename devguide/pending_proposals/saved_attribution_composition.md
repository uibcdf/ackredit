---
summary: Compose shared bibliography without conflating independent original result graphs.
issue: uibcdf/ackredit#102
status: active
opened: 2026-10-05
closed:
severity: medium
verification: reproduced
area: [portability, reporting]
guard: tests/test_attribution_bundle.py
normative:
blocked_by: []
supersedes: []
---

# Saved attribution composition

## What

Roadmap theme I needs a reusable offline composition operation after the CLI
milestone #101. Scientific results can reuse references and target labels while
having independent contexts and graphs. Their original boundaries must survive.

## How

`compose_attributions` returns a detached `AttributionBundle`. Its separate
`ackredit.attribution_bundle@1` envelope contains complete original schema-1
members and caller-owned name/context. Preflight equal IDs against complete
bibliographic records; reject conflicts before returning. Shared bibliography
is exported once, while workflow/provenance reports retain per-member graphs.
The explicit CLI bundle mode uses the same provider-owned reader and renderers.

## Why

Unioning independent target-name graphs can create paths no result recorded.
Overwriting producer context or deduplicating entire input results also loses
evidence. A named bundle preserves inputs without crediting another calculation.

## What was refuted

Do not overwrite metadata, guess DOI equivalence, merge software releases,
rename original scientific targets, interpret input order as chronology, or
alter the released schema-1 structural meaning. No live-session aggregation,
producer import, lookup or new execution credit is needed.

## Scope and exclusions

Additive Ackredit tool/format and CLI. The new names have deliberately recorded
pre-1.0 stable intent; the already released portable promise is separate from
this unpublished envelope. Existing provisional names are not promoted. No
dependency, shared adoption requirement, client code/guide or release/tag change.

## Acceptance criteria

- Detached round trips retain each original name, context, bibliography, use
  and graph, including duplicate/reordered/empty inputs and shared graph edges.
- Equal IDs share references; conflicting metadata refuses the entire bundle,
  preserves originals and distinguishes software versions by explicit IDs.
- Workflow/reference numbering and offline fresh CLI/export are faithful.
- A real multi-result producer workflow is retained separately from frozen
  reader fixtures; source and normally installed checks retain actual identities.
- Relevant quality/reporting/documentation checks and exact-head CI pass;
  archive this record and close the implementation issue on completion.

## Source checkpoint — 2026-10-05

The chosen tool, separate envelope, shared-reference workflow renderer and
explicit CLI reader are implemented. Python 3.14.7 source checks pass 1,915
tests without skips; the focused composition/reader/format/API/diagnostic/
qualification selection passes 290. Ruff check/format, report indexes and
strict nitpicky Sphinx pass. Existing individual workflow tests retain their
meaning after factoring shared reference rendering into its owning module.

The installed receiving gate now requires eight passed cases and all three
composition proofs per supported cell. Clean candidate build, actual scientific
receiving and exact-head hosted qualification remain to execute before closing
this issue. These source results neither qualify a public artifact nor promote
the observer/prepared APIs.
