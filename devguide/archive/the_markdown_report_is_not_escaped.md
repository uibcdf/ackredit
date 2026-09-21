---
summary: The default report format interpolated citation metadata into Markdown without escaping it or validating the link.
issue: uibcdf/ackredit#37
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: high
verification: measured
area: [formats]
guard: tests/test_markdown_escaping.py
normative:
blocked_by: []
supersedes: []
---

# The Markdown report is not escaped

## What

`report()` returns Markdown by default, and `standards/ACKREDIT_GUIDE.md` tells every host
library to expose `cite(format="markdown")`. It is the first output almost every user sees.
Nothing in it was escaped and no link was validated. Measured before the fix:

```
- [**Pockets [see note]**](https://doi.org/10.1/x)      the ] closes the link text early
- [**Rate *k* and 2*3**](https://doi.org/10.1/z)        emphasis where the author wrote an asterisk
- [**A Title**](javascript:alert(1))                    a live link
- [**A Title**](https://e.org/a(b)c)                    unbalanced parentheses break the destination
```

`<` and `>` reached the output too, and Markdown passes raw HTML through, so `<script>` in
a title is the defect `uibcdf/ackredit#25` closed for the notebook renderer, here in the
format that is the default. A `note` taken from a `CITATION.cff` folded scalar carries
newlines, and a newline inside a list item ends the list.

## How

`ackredit/formats/_markdown.py`, beside `_latex.py` and `_html.py`. `escape` collapses
whitespace and backslash-escapes the characters that change rendering; `destination` writes
a URL so a parser reads all of it.

`safe_link` moved to `ackredit/formats/_links.py`. Validating a scheme is not an HTML
question — escaping `javascript:alert(1)` yields a well-formed Markdown destination holding
a live script exactly as it yields a well-formed HTML attribute — so it now sits where both
renderers reach it, and is re-exported from `_html.py`, where it was written.

## Why

This is the third renderer in the family: LaTeX in `uibcdf/ackredit#7` and `#9`, HTML in
`#25`. Both of those were found by looking. This one was never looked at because its output
reads plausibly — a broken link still looks like a line of a bibliography.

The values are not Ackredit's. Titles and authors arrive from Crossref, from DataCite, from
the `CITATION.cff` of any installed package, and from whatever a host registered.

## What was refuted

- **Escaping `&`.** It would put a visible backslash in front of every "Computing in
  Science & Engineering" in any renderer that is not CommonMark, which is a cost paid on
  the common case; unescaped, it only misreads a title that already contains something
  shaped like `&amp;`.
- **Escaping `~`.** A single tilde is ordinary in scientific prose — "~10 nm" — and GFM
  strikethrough needs a pair.
- **Leaving `_` alone because CommonMark does not emphasise intraword underscores.** True
  for CommonMark and false for the older renderers a report also lands in, and the position
  of the underscore is not knowable from the value alone.
- **Wrapping every destination in `<...>`.** Uniform and noisy; the angle-bracket form is
  used only when the destination contains a parenthesis or whitespace.
- **Escaping the link rather than validating it.** Same refusal as `#25`, for the same
  reason.

## Scope and exclusions

Covers the Markdown renderer. The plain-text renderer produces no markup and needs no
escaping. Escaping targets CommonMark, which is what GitHub, Jupyter, VS Code and the tools
a report is pasted into implement.

## Acceptance criteria

- every interpolated field is inert when hostile — met;
- brackets, asterisks, backticks and angle brackets survive as themselves — met;
- a newline in a note does not end the list — met;
- a URL whose scheme cannot be followed is not linked, and the citation is still
  reported — met;
- a destination containing parentheses or spaces is read whole, including one built from a
  DOI that contains them — met;
- `tests/test_markdown_escaping.py` guards it: 18 of its 28 tests fail when the escaping
  is removed.
