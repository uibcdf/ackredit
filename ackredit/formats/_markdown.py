"""Escaping for the report Markdown, and destinations for its links.

`report()` returns Markdown by default and the integration guide tells every
host library to expose `cite(format="markdown")`, so this is the output almost
every user meets first. None of it was escaped: a `[` in a title closed the link
early, an asterisk became emphasis, and `<script>` reached a renderer that
passes raw HTML through — the defect `_html.py` exists for, in the format that
is the default.

**Escaping targets CommonMark**, which is what GitHub, Jupyter, VS Code and the
tools a report gets pasted into implement. A backslash before ASCII punctuation
is a literal character there, and that is the whole mechanism.

Which characters, and why not more. Escaped are the ones whose unescaped
behaviour is both likely and damaging: `\\` first of all, the emphasis pair `*`
and `_`, the link brackets `[` and `]`, the code span `` ` ``, and `<` and `>`,
which open raw HTML. Left alone are `&`, because escaping it would put a visible
backslash in front of every "Computing in Science & Engineering" for renderers
that are not CommonMark, while unescaped it only misreads a title that contains
something shaped like `&amp;`; and `~`, because a single tilde is ordinary in
scientific prose and strikethrough needs a pair.

Whitespace is collapsed, which is not cosmetic. A `CITATION.cff` folded scalar
carries newlines into the `message` that becomes an item's note, and a newline
inside a list item ends the list.
"""

from __future__ import annotations

import re

from ._links import safe_link

_SPECIAL = re.compile(r"[\\`*_\[\]<>]")
_WHITESPACE = re.compile(r"\s+")

# A destination stops at whitespace, and its parentheses must balance. Rather
# than count them, the angle-bracket form is used whenever either could bite.
_NEEDS_BRACKETS = re.compile(r"[()\s]")


def escape(value: object) -> str:
    """Return *value* as Markdown text: one line, and no markup."""
    text = _WHITESPACE.sub(" ", str(value)).strip()
    return _SPECIAL.sub(lambda match: "\\" + match.group(), text)


def destination(url: str) -> str:
    """Return *url* written so a Markdown parser reads all of it.

    `<...>` is the form that takes a destination containing spaces or
    parentheses. The angle brackets themselves cannot appear inside it, so those
    two characters are percent-encoded — which is what they must be in a URL
    anyway.
    """
    encoded = url.replace("<", "%3C").replace(">", "%3E")
    if _NEEDS_BRACKETS.search(encoded):
        return f"<{encoded}>"
    return encoded


__all__ = ["destination", "escape", "safe_link"]
