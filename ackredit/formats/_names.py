"""Turning an author string into a name a citation processor can work with.

Ackredit stores an author as one string, and CSL-JSON wants either a structured
name or a `literal` — a declaration that the string cannot be decomposed. Every
author was emitted as a literal, so Zotero, Mendeley and EndNote could not sort
by surname, could not abbreviate to "Harris, C. R.", and could not apply a
journal's name style. The one format whose purpose is to be machine-readable
handed over names no machine could use.

The strings are not opaque. `Family, Given` is what the `CITATION.cff` reader
produces, what the shipped citation data uses, and what a `.bib` file carries,
so one comma decomposes a name without guessing.

Everything else stays literal, and that is the point rather than a shortfall.
"Travis E. Oliphant" could be split at the last space, and "SciPy 1.0
Contributors" would become the given name "SciPy 1.0" of a family called
"Contributors". A literal name is merely less useful; an invented one is wrong,
and wrong is what this library exists to prevent.
"""

from __future__ import annotations

from typing import Any, Dict


def csl_name(author: Any) -> Dict[str, str]:
    """Return *author* as a CSL-JSON name object.

    Structured when the string is `Family, Given` with both parts present, and
    `literal` otherwise — a mononym, an organisation, or a string carrying more
    commas than that form accounts for.
    """
    if isinstance(author, dict):
        # Already a name object. A host that knows CSL may pass one, and
        # wrapping it in a literal would produce a name that is not a string.
        return author

    text = str(author).strip()
    if text.count(",") == 1:
        family, _, given = text.partition(",")
        family, given = family.strip(), given.strip()
        if family and given:
            return {"family": family, "given": given}

    return {"literal": text}


# Between authors in a list a person reads. A comma cannot do it: the names are
# `Family, Given`, so "Ruiz, Ana, Gómez, Luis" is two people or four, and no
# reader can undo it (`uibcdf/ackredit#67`). A semicolon is what bibliographies
# use for inverted names and is unambiguous whether a name is inverted or not.
AUTHOR_SEPARATOR = "; "


def author_text(author: Any) -> str:
    """One author as a person reads it.

    A CSL name object is accepted wherever a string is, so it is written the way
    its string form would be rather than as a dictionary.
    """
    if isinstance(author, dict):
        if author.get("literal"):
            return str(author["literal"])
        family = str(author.get("family", "")).strip()
        given = str(author.get("given", "")).strip()
        return f"{family}, {given}" if family and given else family or given
    return str(author).strip()


def author_list(authors: Any, escape=lambda text: text) -> str:
    """Every author of an item, escaped one by one and separated unambiguously.

    A single string is taken as already written by whoever registered it.
    """
    if not isinstance(authors, (list, tuple)):
        return escape(str(authors))
    return AUTHOR_SEPARATOR.join(escape(author_text(author)) for author in authors)
