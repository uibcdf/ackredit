"""Escaping for the renderers that produce HTML.

Ackredit renders citation metadata into a notebook and into a local dashboard.
That metadata is not Ackredit's: titles and authors arrive from Crossref, from
DataCite, from the ``CITATION.cff`` of any installed package and from whatever a
host library passed to ``register_item``. None of it is markup, and all of it
must reach the page as the characters it is.

Unlike LaTeX, HTML needs no provenance rule here. There is no path by which an
item field is HTML already: ``load_bibtex`` produces LaTeX, not markup, so every
value this module sees is text and every value is escaped.

Two contexts, because they are not the same. Text content is safe once ``&``,
``<`` and ``>`` are replaced; an attribute value also ends at the quote that
delimits it. :func:`escape` is given both, since escaping the quotes in text
content costs nothing and removes the chance of using the wrong one.

A URL is a third thing. Escaping ``javascript:alert(1)`` produces a perfectly
well-formed attribute holding a live script, so a link is *validated*, not
escaped: :func:`safe_link` returns a URL only when its scheme can be followed
without running anything.
"""

from __future__ import annotations

import html

# Schemes a citation link may use. A DOI or a landing page is fetched over HTTP;
# anything else in this position is not a reference to a work.
_ALLOWED_SCHEMES = ("http://", "https://")

# Browsers strip ASCII whitespace and control characters from a URL before
# resolving its scheme, so "java\tscript:alert(1)" is a javascript: URL to them.
# They are removed here for the same reason, and only for the test.
_STRIPPED = {code: None for code in range(0x21)}
_STRIPPED[0x7F] = None


def escape(value: object) -> str:
    """Return *value* as HTML text, safe in content and in an attribute."""
    return html.escape(str(value), quote=True)


def safe_link(url: object) -> str | None:
    """Return *url* if it can be linked, or ``None`` if it must not be.

    A rejected URL is not repaired and not silently swapped for another: the
    caller renders the title as plain text, so the citation is still shown and
    only the link is withheld.
    """
    if not url:
        return None
    candidate = str(url)
    if not candidate.translate(_STRIPPED).lower().startswith(_ALLOWED_SCHEMES):
        return None
    return candidate
