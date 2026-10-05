---
summary: CFF person and entity identity is lost during CSL name export.
issue: uibcdf/ackredit#98
status: resolved
opened: 2026-10-05
closed: 2026-10-05
severity: medium
verification: reproduced
area: [metadata, reporting]
guard: tests/test_cff_name_identity.py::test_discovered_names_survive_a_producer_free_saved_reader
normative:
blocked_by: []
supersedes: []
---

# CFF name identity

## What

CFF explicitly distinguishes people and entities, but its parser flattens both
into strings. CSL reconstructs identity from punctuation: an entity named
`Research Unit, Example University` becomes an invented person, and a declared
person with family `Smith, Jr.` and given `John` becomes a literal. Explicit
single-component personal names, particles and suffixes lose their structure.

## How

Retain bounded source-name metadata alongside legacy author/editor strings.
Export declared CSL names only while that source metadata still matches the
current list; explicit replacement retains authority. Typed preferred works
keep their own names and untyped fallback keeps its established behavior.

## Why

These references reach citation managers and manuscripts. Punctuation cannot
recover a distinction the producer already supplied. Reproduced at `bcbb6d8`
on Python 3.14.7 with CFF parsing followed by CSL rendering. The primary source
is the [CFF 1.2.0 schema guide](https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md).

## What was refuted

Guessing entity/person identity from commas or spaces is unnecessary when CFF
states it. A source hint cannot override a replaced author/editor list. Do not
guess whether a name particle has CSL dropping semantics or invent fields for
original name identifiers.

## Scope and exclusions

CFF parsing, detached source-name metadata and CSL export. Preserve the current
human-readable author/editor strings and generic CSL string/object handling.
Human BibTeX/LaTeX edits, PyUnitWizard #111, provider API stabilization, new core
dependencies, schema identifiers and release selection are outside this work.

## Acceptance criteria

- Person/entity declarations, single-component names, commas, particles and
  suffixes retain their meaning in CSL authors/editors.
- Preferred works and explicit caller replacements retain their authority.
- Discovery, capture and detached offline reading retain original name metadata
  without producer imports, network access or new execution credit.
- Run the applicable code, report-index, documentation and exact-head CI gates.

## Resolution and evidence

The parser retains detached, bounded `_cff_authors`/`_cff_editors` source hints
alongside unchanged legacy display strings. The shared name helper consumes
them only when their original text list still matches the current list. Entity
names stay literal; explicit personal components, including a single component
or embedded comma, stay structured. Suffixes reach CSL `suffix`. Particles stay
part of the family name without guessed dropping semantics; without a family,
the available components stay literal. Original ORCID values remain saved
metadata rather than unsupported CSL name fields. Untyped partial preferred
works retain independent author/editor fallbacks; typed works own their names.

The 22 guards run against normal installations of exact original `bcbb6d8` and
the candidate files outside both checkouts, using the shared installed-test
runner at MolSysSuite `c3e2b9b3dabf3d1c65349c389a23048957bea21a`. Its same-interpreter
guard checks actual Ackredit imports before/after pytest. The original fails
17 cases and passes five; the candidate passes all 22 without skips. Relevant
installed bytes match expected source, runtime/distribution versions match,
scientific support dependencies are identical, and both prefixes pass `pip check`.

The selected saved-reader guard protects the full failure mechanism: discovered
entity/person declarations survive capture/serialization, then CSL export in a
new process retains an entity with a comma and a person's suffix without loading
the producer, connecting to the network or crediting new execution. It also
retains original name identifier metadata and unchanged saved data.

The broader CFF/CSL selection passes 149 tests; the final Python 3.14.7 local
gate passes 1,815 tests without skips. Ruff, format, report indexes and strict
Sphinx pass. Exact identities, runtime/test hashes and complete Pytest Receptor
outcomes are retained in `devtools/receipts/cff_name_identity_98_2026-10-05.json`.
This is local normal-install evidence, not a new hosted installed matrix or
public artifact. Shared-provider impact is tracked in MolSysSuite #103.

An initial receiving prefix inherited an inconsistent shared development
environment (PyUnitWizard 0.28 requiring ArgDigest >=0.14 while the editable
ArgDigest was based on 0.13); the final receipt uses coherent public dependencies
instead. That environmental finding was reported in PyUnitWizard #111, without
changing sibling source. The shared environment subsequently passes `pip check`
again; full local tests run there. A full `/tmp` filesystem interrupted setup;
one prior owned Conda cache was relocated to the workspace's ignored build
directory with its old path preserved by a symlink. No cache or artifact bytes
were discarded. After space recovery, the final installed checks complete.

No human BibTeX/LaTeX work, provider API stability decision, core dependency,
portable schema, client minimum, synchronized guide or public archive changes.
