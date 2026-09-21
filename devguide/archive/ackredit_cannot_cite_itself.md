---
summary: A citation tracker that shipped no CITATION.cff and could not be found by its own discovery.
issue: uibcdf/ackredit#21
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: medium
verification: reproduced
area: [packaging, discovery]
guard: tests/test_self_citation.py
normative: devguide/roadmap.md
blocked_by: []
supersedes: []
---

# Ackredit ships no CITATION.cff and cannot discover itself

## What

Ackredit reads `CITATION.cff` to learn how a package wants to be cited, and shipped none
of its own. Its package metadata named no author beyond "UIBCDF Development Team", with no
contact and no identifier, while the repository's contributors are two people whose ORCIDs
are already published by sibling components.

## How

```python
>>> find_and_parse_cff(Path(ackredit.__file__).parent)
None
```

## Why

Roadmap theme B, and the smallest of the six, but the only defect in the library that is
also an argument against it: a citation tracker that cannot be cited has not finished
making its own case, and the path it failed is the one it asks every other project to
support.

## What was refuted

**Shipping the file only at the repository root** was the first attempt and it was wrong,
which the check caught. `find_and_parse_cff` looks in the package directory and its
parent; under an editable install the parent is the repository root, so discovery
succeeded from a checkout and the built wheel carried nothing. Verified by inspecting the
wheel, and then by installing it into a clean virtual environment, where the package
resolves under `site-packages` and discovery now returns the real authors.

That is the general lesson worth keeping: an editable install hides exactly the packaging
defects a packaging test exists to find, which is also what `uibcdf/ackredit#2` was.

**Removing `version:` from the file** to avoid a hand-written release number was
considered, since `uibcdf/ackredit#20` had just removed the other one. It was kept: a
citation without a version is less useful than one that has to stay current, and a test
compares it against the latest tag instead.

## Scope and exclusions

Covers the file, the metadata that must agree with it, and the packaging that carries it.
The Zenodo question raised beside it in the roadmap is answered by
`devguide/zenodo_policy.md` rather than here: incubating components use `optional`, and
an explicit applicability review is triggered by preparing a public release. A Git tag is
not that, so the review belongs to roadmap theme A.

## Acceptance criteria

Met by the commit closing this record:

- `CITATION.cff` names both authors with their ORCIDs and affiliation, in the form the
  sibling components use;
- `pyproject.toml` names the same people, asserted equal rather than trusted;
- the file travels inside the package, and a test inspects the built wheel rather than
  the checkout;
- Ackredit discovers Ackredit, end to end through register, track and render;
- the two copies — repository root for GitHub, package directory for discovery — are
  asserted identical.
