---
summary: Half the citation entries Ackredit ships listed a truncation as an author, one named a paper that does not exist, and the guide taught the same.
issue: uibcdf/ackredit#26
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: high
verification: measured
area: [core, documentation, integration]
guard: tests/test_standard_injections.py
normative:
blocked_by: []
supersedes: []
---

# Shipped citation data is not true

## What

`ackredit/core/standard_injections.py` holds the citation metadata Ackredit injects for
packages it knows. Three of its six entries listed `"et al."` as an author name, so the
rendered bibliography was:

```bibtex
author = {Harris, C. R. and et al.}
```

A `.bst` style reads a name-shaped string as a person: surname `al.`, given name `et`.
The printed bibliography credits "C. R. Harris and E. al.".

The audit widened once the data was read against its sources:

- `molsysmt:paper:2024` named an article titled "MolSysMT: A modern tool for molecular
  systems analysis", dated 2024, authored by "Diego". MolSysMT's own `CITATION.cff` asks
  to be cited as **software** titled "MolSysMT", by Prada-Gracia and Moreno-Vargas,
  through `10.5281/zenodo.1298752`. The shipped entry was a work that does not exist.
- `argdigest:github` credited "UIBCDF Development Team"; ArgDigest's `CITATION.cff` names
  both authors. `pyunitwizard:github` credited the same placeholder; its `pyproject.toml`
  declares "UIBCDF Lab".
- `standards/ACKREDIT_GUIDE.md`, the document distributed to every host library, taught
  the defect in its worked example: `authors=["Diego", "et al."]`. `ROADMAP.md` taught it
  too.
- `docs/content/about/citation.md` asked users to cite Ackredit as "Prada, D. et al." for
  a work with exactly two named authors, hiding one of them, with a title and a year that
  `CITATION.cff` does not say.

## How

Nothing here was written from memory. The three papers were read from Crossref by DOI and
the file was generated from that response; the MolSysSuite entries were read from each
library's own `CITATION.cff`, or from its `pyproject.toml` where it ships none.

Author lists are now complete: NumPy's 26, Matplotlib's 1. SciPy's record lists 34 named
authors, then the collective author "SciPy 1.0 Contributors", then that collective
expanded into its 77 members; the list kept here ends at the collective, which is the
paper's author list as the publisher records it. Where it ends is read from the record —
the position of the entry with no family name — and asserted by the generator, not chosen.

The guide gained a fifth non-negotiable rule and a sentence on copying fields from the
work's own record. The citation page was rewritten to agree with `CITATION.cff`.

## Why

Ackredit exists so that credit is accurate. Shipping a citation that credits a person who
does not exist, or a paper that was never written, is the failure this library is built to
prevent, committed by the library itself. It is worse than shipping nothing, because a
user has no reason to doubt it and carries it into a manuscript.

The guide made it structural rather than local: five host libraries are told to copy that
example.

`core/standard_injections.py` had no test file, like the four other modules audited in the
same pass (#25, #27).

## What was refuted

- **Adding a truncation marker to the item schema**, so a renderer could emit BibTeX's
  `and others`. It was the first fix considered and it was not needed: every shipped list
  is complete once read from its source, and where a list is genuinely long the decision
  to abbreviate belongs to the bibliography style, which already makes it. A host that
  needs BibTeX's `and others` can pass that keyword, because the renderer joins authors
  with ` and `. Adding schema for a case nobody has is how the data drifts from its
  sources again.
- **Shipping SciPy's full 112-entry list.** It is Crossref's expansion of the collective
  author, not a second author list; ending at the collective is what the publisher
  records and what SciPy's own citation asks for.
- **Dropping the MolSysSuite entries and relying on discovery.** Correct in direction and
  blocked in practice: a standard injection marks the package as handled, so the
  package's own `CITATION.cff` is never read. That is a defect in the mechanism rather
  than the data, filed as #28. Until it is fixed these entries are what a user gets, so
  they were corrected rather than removed; afterwards they remain the fallback for a
  `CITATION.cff` that cannot be read.
- **A test asserting the shipped entries equal the sibling `CITATION.cff` files.** It
  would need those repositories checked out beside this one and would fail in CI for a
  reason that is not a defect here.

## Scope and exclusions

Covers the shipped data, the guide, the roadmap example and Ackredit's own citation page.
The precedence between an injection and a discovered `CITATION.cff` is #28. PyUnitWizard
ships no `CITATION.cff` at all, which is reported to that component rather than worked
around here.

## Acceptance criteria

- no shipped author is a truncation, and every shipped item carries a type a renderer
  maps, a place it was published and a way to reach it — met;
- the MolSysMT entry is the software MolSysMT asks to be cited as — met;
- no example anywhere in the repository writes a truncation into an author list, so
  nothing copying an example inherits the defect — met, enforced across every `.py`,
  `.md` and `.rst` outside the archive;
- Ackredit's citation page names every author its `CITATION.cff` names —
  `tests/test_self_citation.py`;
- `tests/test_standard_injections.py` guards it: 191 tests, failing when a truncation is
  reintroduced.
