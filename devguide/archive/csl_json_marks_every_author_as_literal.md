---
summary: Every author reached a reference manager as a literal, declaring a name that could be decomposed to be indecomposable.
issue: uibcdf/ackredit#38
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: medium
verification: measured
area: [formats]
guard: tests/test_csl_names.py
normative:
blocked_by: []
supersedes: []
---

# CSL-JSON marks every author as literal

## What

`ackredit/formats/csl_json.py` emitted every author as a literal:

```json
[{"literal": "Harris, Charles R."}, {"literal": "Millman, K. Jarrod"}]
```

CSL-JSON exists for reference managers, and `literal` tells them the name cannot be
decomposed. Zotero, Mendeley and EndNote then cannot sort by surname, cannot abbreviate to
"Harris, C. R.", and cannot apply a journal's name style. The one format whose purpose is
to be machine-readable handed over names no machine could work with.

The reason sat in a comment beside it — "Ackredit currently stores authors as strings" —
and the strings are in `Family, Given` form: what the CFF reader produces, what the shipped
data uses, and what a `.bib` file carries. The claim that the name was irreducible was one
we could disprove ourselves.

## How

`ackredit/formats/_names.py`. One comma with both parts present decomposes into `family`
and `given`; everything else stays `literal`.

## Why

Both halves are the point. A name that decomposes should, because that is what the format
is for. A name that does not must not be forced: "Travis E. Oliphant" split at the last
space is a guess, and "SciPy 1.0 Contributors" split that way becomes the given name
"SciPy 1.0" of a family called "Contributors" — inventing a person, which is the defect
`uibcdf/ackredit#26` closed in the shipped data.

That is the same discipline `_latex.py` follows: structure what can be proven and never
guess. The guard checks both directions, and fails both when everything is made literal
again and when the last space is used to split.

## What was refuted

- **Splitting "Given Family" at the last space.** It is what most of the world's author
  strings look like and it cannot be distinguished from an organisation, a mononym or a
  compound surname. Verified as a failing case rather than argued.
- **Mapping BibTeX's two-comma form, "von Last, Jr, First", to CSL's `suffix`.** Defined
  for a `.bib` file and nowhere else; a two-comma string from Crossref or a `CITATION.cff`
  is more likely noise than a suffix. Items do carry provenance in `_source`, so this could
  be revisited for BibTeX-sourced names alone if a real one appears.
- **Cleaning a trailing comma into a family-only name.** `{"family": "Harris"}` is valid
  CSL and it invents structure out of what is a data error. The literal carries the string
  as registered, so the error stays visible to the person who can fix it.
- **Splitting on the last comma rather than the first.** Identical for one comma and
  wrong for the ambiguous cases, which are the ones that matter.

## Scope and exclusions

Covers author names in CSL-JSON. BibTeX keeps its own handling, which brace-protects a name
with more commas than its three-part form allows.

## Acceptance criteria

- a `Family, Given` name decomposes, and putting the parts back gives the string that was
  registered — met, including particles and non-ASCII given names;
- a mononym, an organisation, a collective author and an over-punctuated string stay
  literal — met;
- order and count survive a mixed list — met;
- every author in the shipped citation data becomes a usable name — met;
- `tests/test_csl_names.py` fails both when names are made literal again and when they are
  split at the last space.
