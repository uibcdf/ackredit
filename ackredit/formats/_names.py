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

CFF discovery retains explicit person/entity declarations alongside its display
strings. CSL uses them while they match the current list, so punctuation cannot
change a declared identity. Explicit list replacement keeps the generic path.
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


def _cff_name(entry: dict) -> dict | None:
    """Use declared identity; CFF particles stay part of the family name."""
    if literal := entry.get("name"):
        return {"literal": literal}
    name = {}
    if family := entry.get("family-names"):
        particle = entry.get("name-particle")
        name["family"] = f"{particle} {family}" if particle else family
    if given := entry.get("given-names"):
        name["given"] = given
    if not name:
        return None
    # Without a family name, a particle's placement cannot be reconstructed
    # as a structured CSL name. Keep all stated components without guessing.
    if entry.get("name-particle") and not family:
        return {
            "literal": " ".join(
                entry[field]
                for field in ("given-names", "name-particle", "name-suffix")
                if entry.get(field)
            )
        }
    if suffix := entry.get("name-suffix"):
        name["suffix"] = suffix
    return name


def cff_names(authors: Any, cff: Any) -> list[dict] | None:
    """Read matching detached CFF name declarations, without guessing identity.

    Source metadata is a hint about the original strings, not authority over a
    caller's current author/editor list. Generic names retain their old path.
    ORCID remains saved metadata, not an invented CSL name property.
    """
    if isinstance(cff, dict) and isinstance(authors, (list, tuple)):
        entries = cff.get("names")
        if (
            cff.get("text") == list(authors)
            and isinstance(entries, list)
            and len(entries) == len(authors)
            and all(
                isinstance(entry, dict)
                and all(isinstance(value, str) for value in entry.values())
                for entry in entries
            )
        ):
            names = [_cff_name(entry) for entry in entries]
            if all(names):
                return names
    return None


def csl_names(authors: Any, *, cff: Any = None) -> list[dict]:
    """Prefer matching CFF declarations; explicit list replacement still wins."""
    if names := cff_names(authors, cff):
        return names
    return [csl_name(author) for author in authors]


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
