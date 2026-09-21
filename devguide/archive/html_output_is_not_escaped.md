---
summary: The notebook and dashboard renderers interpolated citation metadata into HTML without escaping it or validating the link.
issue: uibcdf/ackredit#25
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: high
verification: measured
area: [contrib, formats]
guard: tests/test_html_escaping.py
normative:
blocked_by: []
supersedes: []
---

# HTML output is not escaped

## What

`ackredit.summary()` builds the notebook table by interpolating citation metadata into
an HTML string. None of the six interpolated values was escaped, and the link was not
validated. Measured on `main` before the fix:

```html
<a href='javascript:alert(1)' target='_blank' ...><b>Surfaces &amp; Pockets <script>alert('xss')</script></b></a>
```

`title`, `authors`, `year`, the caller names and the `href` all reached the page raw. The
`href` is delimited by single quotes, so a `'` in a DOI ended the attribute and everything
after it was parsed as further attributes.

`ackredit/contrib/web_ui.py` renders the second HTML page through Flask. It was not
measured, because the defect there was different in kind: the page relied on Flask's
autoescaping default for a template with no filename, which Flask changed in 2.2, and
`flask` is declared here with no lower bound. Whether that page escaped depended on which
Flask the environment resolved.

## How

`ackredit/formats/_html.py`, the HTML counterpart of `_latex.py`:

- `escape` wraps `html.escape(..., quote=True)`, covering text content and attribute
  values with one function, so no call site can pick the weaker of the two;
- `safe_link` returns a URL only when its scheme is `http` or `https`, after removing the
  ASCII whitespace and control characters a browser removes before resolving a scheme.
  A rejected URL is not repaired and not replaced: the title renders as plain text, so
  the citation is still reported and only the link is withheld.

`jupyter.py` escapes every interpolated value and builds its link through `safe_link`.
`web_ui.py` no longer renders through Flask's default: the template moved to a module
constant and `_render_dashboard` renders it under an explicit
`jinja2.Environment(autoescape=True)`, which states the behaviour and makes it testable
without a server.

## Why

The ordinary half of this comes first. A citation title carrying `&`, `<` or `>` is
unremarkable — Ackredit's own shipped data cites *Computing in Science & Engineering* —
and it rendered wrong.

The other half is that the data is not Ackredit's. Titles and authors arrive from
Crossref, from DataCite, from the `CITATION.cff` of any installed third-party package and
from whatever a host library registered. `summary()` rendered those strings as markup in
the user's notebook.

This is the same class as the LaTeX escaping defect closed in #7 and #9, in the renderer
nobody had examined. `contrib/jupyter.py`, `contrib/web_ui.py`,
`contrib/duecredit_compat.py`, `core/standard_injections.py` and `formats/jsonfmt.py` had
no test file at all, and two of the other four held defects of their own (#26, #27).

## What was refuted

- **Escaping by provenance, as `_latex.py` does.** `_latex.py` must ask where a value came
  from, because `load_bibtex` yields LaTeX that is already escaped and re-escaping it
  would corrupt it. HTML has no such source: nothing in Ackredit produces markup that an
  item field could legitimately carry. Escaping is unconditional here, and the module says
  so rather than copying a distinction it does not need.
- **Escaping the URL instead of validating it.** Escaping `javascript:alert(1)` yields a
  well-formed attribute holding a live script. The scheme has to be checked; escaping does
  not substitute for it.
- **Pinning `flask>=2.2`.** It would have fixed the dashboard, and left the page's
  escaping stated in `pyproject.toml` rather than in the code that renders it, and
  untestable in an environment without Flask. Rendering explicitly is both stronger and
  checkable, and the test for it runs in the ordinary suite.
- **A blanket "strip tags" cleaner.** It destroys legitimate content — a title containing
  `<` — while pretending to be a security boundary. Escaping preserves the text exactly.

## Scope and exclusions

Covers the two HTML renderers. The non-HTML formats were already escaped or structurally
encoded (`bibtex`, `latex`, `csl-json`, `json`). The `json` format's own defect is #27 and
the shipped metadata's is #26; both were found in the same audit and are closed
separately.

## Acceptance criteria

- every field the notebook renderer interpolates is inert when hostile — met;
- a URL whose scheme cannot be followed is not linked, and the citation is still shown —
  met;
- the dashboard escapes independently of the Flask version — met;
- `tests/test_html_escaping.py` guards it: 19 of its 29 tests fail when the escaping is
  removed.
