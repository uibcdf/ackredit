---
summary: BibTeX output was written verbatim, producing a subtly wrong compiled bibliography.
issue: uibcdf/ackredit#7
status: resolved
opened: 2026-09-20
closed: 2026-09-20
severity: high
verification: reproduced
area: [formats, reporting]
guard: tests/test_latex_escaping.py
normative:
blocked_by: []
supersedes: []
---

# BibTeX output does not escape LaTeX special characters

## What

`formats/bibtex.py` wrote field values verbatim while `formats/latex.py` escaped its own.
Four independent causes made the compiled bibliography wrong, each found by fixing the
previous one and recompiling.

## How

```python
register_item(id="amp:1", type="article", title="Surfaces & Pockets", year=2024)
track_item("amp:1")
dump(directory, build_pdf=True)
```

Compiled output before the fix:

```
list:          • Surfaces & Pockets (?)     <- the \citep reference does not resolve
bibliography:  Surfaces pockets. 2024.      <- the ampersand dropped, the title mangled
```

The full chain of causes:

1. unescaped `& % # _` in every emitted field;
2. a second, partial escaping rule in `latex.py`;
3. citation keys containing underscores. With no author, natbib prints the key as the
   label, where a bare underscore is read in math mode and aborts the run;
4. the whole comma-separated metadata `Author` field inserted as a single name, which
   BibTeX rejects with `Too many commas in name 1` and exit status 2.

## Why

The affected fields are titles, journals, notes and author names: what a scientific
citation is made of. An ampersand is ordinary in journal names, and "Computing in Science
& Engineering" is in Ackredit's own standard injections. A tool that produces a subtly
wrong bibliography is worse than one that refuses, because the error is carried into a
manuscript. The `.bib` is also handed to DueCredit, so the corruption propagated.

## What was refuted

An initial claim that the PDF came out with no bibliography at all was wrong, and is
corrected here: `pdflatex` runs under `-interaction=nonstopmode`, recovers, and produces
a PDF whose bibliography is present but corrupted. That is the more dangerous outcome,
not the milder one.

Escaping every LaTeX special was also rejected. Items loaded through `load_bibtex` arrive
already escaped, and scientific titles legitimately carry mathematics such as
`$\alpha$-helix`. The rule escapes only `& % # _`, and only where not already escaped,
which makes it idempotent.

## Scope and exclusions

Covers what the BibTeX and LaTeX renderers emit. Excludes the `@software` and `@dataset`
entry types, which `plainnat.bst` does not define; bibtex warns and continues, and
choosing a style or mapping those types is a separate question.

## Acceptance criteria

Met by commit `89d71e2`:

- both renderers share `ackredit/formats/_latex.py`, whose escaping is idempotent and
  preserves intentional LaTeX;
- citation keys use hyphens, so they are safe as printed natbib labels;
- discovery splits comma-separated metadata author strings, and the renderer
  brace-protects any name BibTeX still could not parse;
- `tests/test_latex_escaping.py` covers all four, verified by reverting the escaper,
  which fails seven of them;
- the test suite emits no diagnostics at all, where before `test_pdf_compilation` passed
  while reporting a failed compilation.
