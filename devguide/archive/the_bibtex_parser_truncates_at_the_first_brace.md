---
summary: A non-greedy regex cut every field at its first inner brace, so a loaded .bib file was re-emitted with braces that do not balance.
issue: uibcdf/ackredit#42
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: high
verification: measured
area: [core, formats]
guard: tests/test_bibtex_parsing.py
normative:
blocked_by: []
supersedes: []
---

# The BibTeX parser truncates at the first brace

## What

Fields were read with `(\w+)\s*=\s*(\{.*?\}|".*?"|[^,]+)`. The braced branch is non-greedy,
so it stopped at the first closing brace:

```
title  = {The {DNA} helix}           ->  'The {DNA'
title  = {Analysis with {MolSysMT}}  ->  'Analysis with {MolSysMT'
title  = {{A Fully Protected Title}} ->  '{A Fully Protected Title'
author = {{The SciPy Community}}     ->  '{The SciPy Community'
```

Brace protection is not an edge case. It is what stops a bibliography style lowercasing an
acronym or a proper noun, and every reference manager emits it.

The output was then **invalid BibTeX**, not merely wrong:

```bibtex
@article{rt,
  title = {Analysis with {MolSysMT},
```

The braces do not balance, so a file exported from Zotero, loaded by Ackredit and written
back would not compile. `_source = "bibtex"` passes these fields through unescaped, which
is correct, and is also why nothing downstream repaired it.

`and` separates authors at brace depth zero, and splitting on `\s+and\s+` anywhere broke
`{Smith and Sons}` — the kind of name braces exist to protect.

## How

Fields are read by scanning: a braced value to its balanced closing brace, a quoted value
to a quote at depth zero, a bare value to the next comma. The inner braces are kept,
because they are part of the citation. Whitespace inside a value is collapsed, the way a
TeX engine reads it, so a field spanning lines becomes one line.

Authors split only at depth zero.

The entry-level scan already counted depth correctly, and dropped an entry it could not
close without saying so. That is the same silent loss one level up, so it now raises
`ACKREDIT-W016` and keeps the entries before it.

## Why

The severity is in the round trip. Every other defect closed this week produced a wrong
report; this one produced a file that a TeX engine refuses, from input a user did not write
and cannot be blamed for.

It also had to be run to be found. `\{.*?\}` reads as "a braced value", and the entry-level
loop beside it counts depth properly, so the file looks like it handles braces.

## What was refuted

- **Making the regex greedy.** `\{.*\}` runs to the *last* closing brace in the body, so
  one field swallows the rest of the entry. Neither direction of laziness is right, because
  the language is nested and a regular expression cannot count.
- **Stripping the inner braces once parsed.** They are semantic: `{DNA}` without them is
  lowercased by most styles. Keeping them also makes the round trip exact.
- **Repairing unbalanced output in the renderer.** It would paper over a parser that lost
  data, and the renderer has no way to know what was lost.
- **Dropping an unterminated entry silently, as before.** A truncated file is the realistic
  cause, and quietly returning fewer citations than the file contains is the failure this
  library exists to prevent.

## Also fixed

`ackredit/core/registry.py` carried `\&` in a docstring — an invalid escape sequence,
written into the previous commit. Python reports that **when a module is compiled**, so it
appeared once and then the cached bytecode answered and it was never seen again. It would
have reached a user on their first import. `tests/test_packaging.py` now compiles every
shipped module with `SyntaxWarning` as an error, which is the class rather than the
instance.

## Scope and exclusions

Covers reading a `.bib` file. `@book` loads as type `other` and re-emits as `@misc`, which
is a second round-trip loss in the type vocabulary rather than the value parser, and is
not this report.

## Acceptance criteria

- a protected word does not truncate its field, at any nesting depth, and the fields after
  it are still read — met;
- the inner braces are kept — met;
- what Ackredit writes back has balanced braces — met, asserted by counting;
- `and` inside braces does not separate names — met;
- an unterminated entry is reported and the entries before it survive — met;
- `tests/test_bibtex_parsing.py` guards it: 9 of its 21 tests fail when the regex returns,
  and 1 when authors split anywhere.
