---
summary: Character-level guessing left two escaping holes and invented authors who do not exist.
issue: uibcdf/ackredit#9
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: high
verification: reproduced
area: [formats, discovery]
guard: tests/test_latex_escaping.py
normative:
blocked_by: []
supersedes: []
---

# Citation rendering guesses at the character level and invents authors

## What

The fix for `uibcdf/ackredit#7` decided per character whether text was prose or LaTeX.
That cannot be decided per character, and it left two holes and introduced a third defect
worse than the one it closed.

1. `hooks._split_authors` split the metadata `Author` field on commas. `"Prada, Diego"`
   became two authors; `"Smith, J., Doe, A."` became four.
2. `_bibtex_name` brace-protected any name with two commas, but `von Last, Jr, First` is
   BibTeX's own three-part form and is valid. Protecting it costs the author their sorting
   key and initials.
3. `escape` left `$ { } \ ^ ~` alone, reasoning they are more often intentional
   mathematics. An unpaired `$` never is: `"Cost in $ per sample"` opens math mode and
   aborts the compilation, the exact failure #7 was opened for.

## How

```python
_split_authors("Prada, Diego")              -> ['Prada', 'Diego']
_bibtex_name("van der Berg, Jr, Johannes")  -> "{van der Berg, Jr, Johannes}"
escape("Cost in $ per sample")               -> "Cost in $ per sample"
```

## Why

Inventing an author is worse than the mangled title it was introduced to fix. Attribution
is the product, and a citation crediting people who do not exist is a false record carried
into a manuscript.

## What was refuted

Tuning the heuristics was rejected. `$\alpha$-helix` and `Cost in $ per unit` are both
prose containing a dollar sign, and no rule over characters separates them. The code does
not need to guess: a Crossref title, a `CITATION.cff` field or a `register_item` call is
plain text, and what `load_bibtex` parses is already LaTeX. Items now carry that in
`_source`, and escaping asks rather than infers.

The same applies to authorship. `Author-email` carries `Name <email>` pairs whose
separator is unambiguous and is used whenever present. `Author` is free text, split only
when every part carries a space — which no `Last, First` pair does — and otherwise kept
whole. Every failure of that rule is conservative: one literal name, brace-protected at
render time if BibTeX cannot read it, never a person who does not exist.

Sequential character replacement was also refuted while implementing it: replacing `\`
with `\textbackslash{}` and then escaping braces turned `C:\path` into
`C:\textbackslash\{\}path`. Escaping now runs in a single pass. Brace protection is
applied after escaping, never before, because its braces are BibTeX syntax rather than
content.

## Scope and exclusions

Covers what the BibTeX and LaTeX renderers emit and how authorship is read from package
metadata. Excludes `@software` and `@dataset`, which `plainnat.bst` does not define.

## Acceptance criteria

Met by the commit closing this record, and verified end to end against a real TeX engine
with every hard case in one document — no warnings, and each rendering correct:

```
Diego Prada. Surfaces & pockets. Computing in Science & Engineering, 2024.
Johannes van der Berg, Jr. Cost in $ per sample at 50% yield. 2025.
A Person, B Person, C Person, D Person. snake_case_tool ~ v2 ^ beta.
Ana Ruiz and Luis Gómez. A {curly} #hashtag title. 2026.
```

- provenance decides escaping, and a `.bib` file survives a round trip untouched;
- the `_source` marker reaches no output format;
- `von Last, Jr, First` is parsed by BibTeX rather than protected;
- authorship is read from `Author-email` when present, and free text is split only when
  it cannot invent a person.
