---
summary: A typo in a format name silently produced plain text, written to a file named for neither.
issue: uibcdf/ackredit#15
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: high
verification: reproduced
area: [formats, api]
guard: tests/test_report_formats.py
normative:
blocked_by: []
supersedes: []
---

# An unknown report format silently returns a different one

## What

`report`'s dispatch ended in `# default fallback / return text.render(...)`, so any name it
did not recognise produced plain text. Through `dump`, the same name also missed the
extension map and the file was written as `.txt`.

## How

```python
report(format="bibtext")   -> 'A Title (2024)'    # plain text
report(format="BibTeX")    -> 'A Title (2024)'    # the format's own spelling
report(format="yaml")      -> 'A Title (2024)'    # a format that does not exist
```

```python
dump(directory, formats=["bibtext"])
```
```
files written: ['ackredit_report.txt']
```

## Why

The failure is silent and the output is plausible: a plain-text citation list looks like a
report, so nothing prompts anyone to check. It surfaces when a `.bib` is handed to a TeX
engine, or not at all. `BibTeX` failing is worse than a typo failing, because it is the
spelling the format's own documentation uses.

There was also no way to ask which formats existed: the valid names lived in a chain of
`if` statements, and `dump`'s extension map listed a slightly different set, so the two
could disagree about what existed.

## What was refuted

Accepting case-insensitive names was rejected as the fix. It would have made `BibTeX` work
and left `bibtext` silently wrong, which is the actual defect; refusing what is not
recognised covers both, and the message names the alternatives.

Keeping a fallback for forward compatibility was also rejected: a caller asking for a
format a future version will add is better served by an error naming today's formats than
by a file that looks right and is not.

## Scope and exclusions

Covers dispatch, the format inventory and the refusal. Excludes whether `format` should be
a string at all, which belongs with the other 1.0 shape questions.

## Acceptance criteria

Met by the commit closing this record:

- one table maps each format to both its renderer and its extension, so the two cannot
  disagree;
- an unrecognised name raises `UnknownFormatError` (`ACKREDIT-E004`), which is also a
  `ValueError`, naming what to use instead;
- `csl` still resolves to `csl-json`, because it was published;
- `available_formats()` is exported and documented;
- `dump` refuses the same names `report` refuses, instead of writing a `.txt`;
- `tests/test_report_formats.py` covers all of it, verified by restoring the fallback,
  which fails seven of its tests.
