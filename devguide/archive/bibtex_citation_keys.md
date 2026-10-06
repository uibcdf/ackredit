---
summary: Preserve valid citation keys and allocate distinct BibTeX and LaTeX keys.
issue: uibcdf/ackredit#109
status: resolved
opened: 2026-10-06
closed: 2026-10-06
severity: high
verification: reproduced
area: [formats, reporting]
guard: tests/test_cite_keys.py
normative:
blocked_by: []
supersedes: []
---

# Preserve original citation keys and resolve generated-key collisions

## What

The released renderer rewrites colons and underscores to hyphens. Distinct
references such as `Smith_2020`, `Smith:2020` and `Smith-2020` collapse, and
exporting an imported bibliography renames keys used by the manuscript.
Authorless discovered references also receive indistinguishable `dis` labels
under `plainnat`, rather than their software titles.

## How

The reviewed local patch preserves valid ASCII keys, allocates fallbacks for
invalid or case-clashing IDs and shares the allocator between BibTeX and LaTeX.
Further review reproduced a second-generation collision: the fallback for
`a b` can itself be a valid original ID, whose regenerated key can collide with
another original. A truncated hash alone also cannot guarantee uniqueness.
Matching with `$` admitted a trailing newline as a valid key.

The implementation reserves all nonclashing valid originals first and assigns
remaining IDs in sorted order, adding numeric suffixes when needed. Full-string
validation rejects newlines. Mapping is independent of input order. Generated
authorless records get an escaped title in BibTeX's `key` field; imported LaTeX
fields keep their existing provenance and escaping rules.

## Why

An unresolved or collapsed citation loses attribution in the final manuscript.
`tests/test_cite_keys.py` checks imported-key preservation, case-fold uniqueness,
forced hash collisions, reserved and second-generation keys, input permutations,
newline rejection and agreement between both report formats. Three added
regressions failed before the allocation repair. All 87 focused format tests
then passed on Python 3.14.7, including actual BibTeX and multi-pass PDF compilation.
The complete local suite passed 6,207 tests without skips, failures or warnings
in 79.22 seconds. Its complete Pytest Receptor event stream records 6,207
distinct call node IDs and integrity SHA-256
`7471338859a51e158bfd4a98f428b15c3093228686809676508b2cbf5e4eb9e6`.
Ruff check/format, generated report indexes, notebook JSON/source preservation
and a fresh warnings-as-errors Sphinx build also pass. The owning issue retains
the subsequent published head and CI links; local validation does not certify
a new release artifact or the unrelated dependencies in the shared environment.

## What was refuted

Replacing every separator does not preserve reference-manager keys. A short
digest reduces collision frequency but is not a uniqueness guarantee. Citation
key syntax and the printed authorless label need separate handling; valid
underscores need not be removed to make natbib compile.

## Scope and exclusions

This is development after public 0.11.0; its original artifact, digest and tag
are unchanged. No new release, provider contract or saved attribution schema
is introduced. Arbitrary bibliography styles and reference-manager products
need their own qualification; the executed compilation uses `plainnat`.
The existing workflow notebook changes update outputs and execution timestamps;
its source cells are unchanged.

## Acceptance criteria

- Valid nonclashing original keys survive import/export unchanged.
- Every distinct used ID gets a unique key under BibTeX's case-insensitive comparison,
  including forced hash collisions and reserved generated keys.
- BibTeX entries and LaTeX citations agree; real compilation resolves the citations
  and prints meaningful authorless labels.
- Applicable source, documentation, reporting and exact-head CI gates pass;
  archive this record and close the owning issue with their evidence.
