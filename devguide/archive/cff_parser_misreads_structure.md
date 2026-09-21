---
summary: A regex-based CITATION.cff reader dropped entity authors, merged preferred-citation and missed canonical DOIs.
issue: uibcdf/ackredit#10
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: high
verification: reproduced
area: [discovery, formats]
guard: tests/test_cff.py
normative: devguide/decisions.md
blocked_by: []
supersedes: []
---

# The CITATION.cff parser drops entity authors and merges preferred-citation

## What

`parse_cff` matched regular expressions against lines, so it had no model of the
document. On three constructs the specification documents it did not fail — it returned a
confident wrong answer.

## How

```yaml
authors:
  - name: "The Research Consortium"      # entity author, silently dropped
  - family-names: Ruiz
    given-names: Ana
```

```yaml
preferred-citation:                       # "cite this paper, not this software"
  title: The Paper Describing MyTool
  authors:
    - family-names: Gomez                 # merged into the software's authors
      given-names: Luis
```

```yaml
identifiers:
  - type: doi
    value: 10.5281/zenodo.123456          # canonical DOI form, never found
```

The merge is the worst of the three: the result credited a list belonging to neither the
software nor the paper, and produced precisely the citation the file asked not to receive.

## Why

Auto-discovery is what makes Ackredit useful without configuration, and CITATION.cff is
where a project states how it wants to be cited. Dropping an institutional author
under-credits the bodies least able to notice; merging two author lists credits people for
work they did not do.

## What was refuted

Tightening the patterns was rejected. No expression over lines can know whether an
`authors:` block belongs to the root mapping or to `preferred-citation`; the information
is in the indentation, which the approach discards.

Keeping the hand-rolled reader as a fallback when PyYAML is absent was also rejected. It
would make a citation depend on which environment produced it, which is worse for output
that enters the scientific record than a dependency is.

## Scope and exclusions

Covers reading the file. Excludes validating it against the CFF schema, and excludes the
`type` field of a `preferred-citation`, which Ackredit does not yet map onto its own
types.

## Acceptance criteria

Met by the commit closing this record:

- `pyyaml` is a declared dependency and the document is parsed as YAML;
- an entity author is credited by its `name`;
- `preferred-citation` replaces rather than merges, falling back to the root document
  only for fields it does not state;
- the DOI is read from `identifiers` as well as from a top-level `doi`;
- verified against the real `CITATION.cff` of four sibling repositories, including
  MolSysMT, whose Zenodo DOI was previously not found;
- `tests/test_cff.py` covers each case, and a malformed file is still reported as
  `ACKREDIT-W004` rather than swallowed.
