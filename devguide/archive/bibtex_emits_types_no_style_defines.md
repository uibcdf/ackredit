---
summary: The BibTeX renderer emitted biblatex entry types that a BibTeX style cannot render.
issue: uibcdf/ackredit#10
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: low
verification: reproduced
area: [formats]
guard: tests/test_bibtex.py
normative:
blocked_by: []
supersedes: []
---

# BibTeX output used entry types no BibTeX style defines

## What

`@software` and `@dataset` are biblatex's, not BibTeX's. Ackredit generates its LaTeX with
`natbib` and `plainnat`, so every compilation warned and fell back to a default layout,
losing the distinction the type was there to express.

## How

```
Warning--entry type for "software-1" isn't style-file defined
Warning--entry type for "dataset-1" isn't style-file defined
```

Rendered, both came out indistinguishable from any other `misc` entry.

## Why

Small on its own, but it warned on every run, which is noise that hides a real warning,
and it silently discarded information a reader would want: whether the thing being cited
is software, a dataset or a paper.

## What was refuted

Switching the generated document to biblatex was considered and rejected: it would raise
the system requirement from `pdflatex` and `bibtex`, which Ackredit already documents, to
`biber` as well, for no gain a `howpublished` field does not provide.

## Acceptance criteria

Met by the commit closing this record, verified against a real BibTeX run:

- every emitted entry type is one BibTeX defines, so a compilation produces no
  "isn't style-file defined" warning;
- the kind survives in `howpublished` and is rendered to the reader:
  "A software entry. Software, 2024e.";
- `tests/test_bibtex.py` covers all six of Ackredit's types.
