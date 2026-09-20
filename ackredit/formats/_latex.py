"""Shared LaTeX escaping for the renderers that produce LaTeX-bound text.

Both the BibTeX and the LaTeX renderer emit text that a TeX engine will read, so
the rule lives in one place rather than being approximated twice.

The rule is deliberately conservative. Citation metadata arrives as plain text —
Crossref titles, CITATION.cff fields, values a host library passed to
`register_item` — and a bare ampersand in "Computing in Science & Engineering"
must not end a table cell. But items can also arrive through `load_bibtex` from a
file that is already escaped, and a scientific title may legitimately carry
mathematics such as ``$\\alpha$-helix``.

So: escape the four characters that reliably break the text and mean nothing in
prose, and only where the author has not escaped them already. Structural
characters (``$ { } \\ ^ ~``) are left alone, because in this input they are far
more often intentional LaTeX than literal text.
"""

from __future__ import annotations

import re

# A special character, when it is not already preceded by a backslash.
_UNESCAPED = re.compile(r"(?<!\\)([&%#_])")


def escape(value: str) -> str:
    """Return *value* with unescaped LaTeX specials escaped, idempotently."""
    return _UNESCAPED.sub(r"\\\1", value)
