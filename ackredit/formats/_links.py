"""Whether a citation's link can be followed.

Escaping does not help here. ``javascript:alert(1)`` escapes into a perfectly
well-formed HTML attribute and a perfectly well-formed Markdown destination,
both holding a live script, so a link is *validated* instead: it is rendered as
a link only when its scheme can be followed without running anything.

The question is not about any one output format, which is why it is not in
either renderer. A rejected URL is never repaired and never swapped for
another; the caller renders the title as plain text, so the citation is still
reported and only the link is withheld.
"""

from __future__ import annotations

# Schemes a citation link may use. A DOI or a landing page is fetched over HTTP;
# anything else in this position is not a reference to a work.
_ALLOWED_SCHEMES = ("http://", "https://")

# Browsers strip ASCII whitespace and control characters from a URL before
# resolving its scheme, so "java\tscript:alert(1)" is a javascript: URL to them.
# They are removed here for the same reason, and only for the test.
_STRIPPED = {code: None for code in range(0x21)}
_STRIPPED[0x7F] = None


def safe_link(url: object) -> str | None:
    """Return *url* if it can be linked, or ``None`` if it must not be."""
    if not url:
        return None
    candidate = str(url)
    if not candidate.translate(_STRIPPED).lower().startswith(_ALLOWED_SCHEMES):
        return None
    return candidate
