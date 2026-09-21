"""Escaping for the renderers that produce LaTeX-bound text.

A citation field is one of two things, and the code knows which:

- **plain text**, which is what a Crossref title, a `CITATION.cff` field, package
  metadata or a `register_item` call contains. Every LaTeX special in it is a
  literal character and must be escaped;
- **LaTeX already**, which is what `load_bibtex` parses out of a `.bib` file. It
  is escaped the way its author intended and must be left exactly as written.

Deciding per character which of the two a string is cannot be done. `$\\alpha$` and
"Cost in $ per sample" are both prose containing a dollar sign, and only their
provenance separates them. Items carry that provenance in `_source`, so this
module never guesses.
"""

from __future__ import annotations

import re

LATEX_SOURCE = "bibtex"

# Applied in a single pass. Replacing them one after another would re-escape the
# braces that \textbackslash{} itself introduces, turning "C:\path" into
# "C:\textbackslash\{\}path".
_REPLACEMENTS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}

_SPECIAL = re.compile("[" + re.escape("".join(_REPLACEMENTS)) + "]")

# A value this module produced. Recognising it keeps escaping idempotent, so a
# field that passes through two renderers is not escaped twice.
_ALREADY_ESCAPED = re.compile(
    r"\\(?:[&%$#_{}]|textbackslash\{\}|textasciitilde\{\}|textasciicircum\{\})"
)


def escape(value: str, *, latex_source: bool = False) -> str:
    """Return *value* ready for a TeX engine.

    With ``latex_source=True`` the value is returned unchanged: it came from a
    ``.bib`` file and is already in the form its author wrote.
    """
    if latex_source:
        return value

    pieces = []
    position = 0
    for match in _ALREADY_ESCAPED.finditer(value):
        pieces.append(_escape_plain(value[position : match.start()]))
        pieces.append(match.group())
        position = match.end()
    pieces.append(_escape_plain(value[position:]))
    return "".join(pieces)


def _escape_plain(text: str) -> str:
    return _SPECIAL.sub(lambda match: _REPLACEMENTS[match.group()], text)


def is_latex_source(item: dict | None) -> bool:
    """Whether this item's fields are LaTeX as written rather than plain text."""
    return bool(item) and item.get("_source") == LATEX_SOURCE
