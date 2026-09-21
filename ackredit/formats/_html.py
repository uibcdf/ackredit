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
escaped. That validation is not about HTML at all — the Markdown renderer needs
exactly the same answer — so it lives in ``_links.py`` and is re-exported here,
where it was written.
"""

from __future__ import annotations

import html

from ._links import safe_link


def escape(value: object) -> str:
    """Return *value* as HTML text, safe in content and in an attribute."""
    return html.escape(str(value), quote=True)


__all__ = ["escape", "safe_link"]
