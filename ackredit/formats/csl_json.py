"""The report a reference manager reads.

CSL-JSON is a schema, so unlike BibTeX nothing can simply be passed through: a
processor has no use for a key it does not define. The mapping below is
therefore bounded and explicit, and it used to be much shorter than the schema
allows — a book arrived at Zotero with no publisher, no ISBN and no series,
which is a reference the manager cannot format.
"""

from __future__ import annotations

import json

from ._names import csl_name

# Ackredit's key to CSL's field, for values that are plain text.
_DIRECT = {
    "doi": "DOI",
    "url": "URL",
    "note": "note",
    "volume": "volume",
    "number": "issue",
    "pages": "page",
    "version": "version",
    "isbn": "ISBN",
    "issn": "ISSN",
    "edition": "edition",
    "series": "collection-title",
    "abstract": "abstract",
    "language": "language",
    "chapter": "chapter-number",
    "address": "publisher-place",
}

# One CSL field that several of Ackredit's keys can fill. The first key present
# wins: a thesis names its school and a report its institution, and CSL puts
# both where a book puts its publisher.
_FALLBACKS = {
    "container-title": ("journal", "booktitle"),
    "publisher": ("publisher", "school", "institution"),
}


# The entry type a `.bib` file used, in CSL's vocabulary. Ackredit's own six
# types flatten `@book` and `@phdthesis` alike into `other`, and a manager that
# is told a book is a "document" cannot format it as a book. `uibcdf/ackredit#43`
# kept the original; this reads it.
_FROM_BIBTEX = {
    "article": "article-journal",
    "book": "book",
    "booklet": "pamphlet",
    "conference": "paper-conference",
    "inproceedings": "paper-conference",
    "proceedings": "book",
    "incollection": "chapter",
    "inbook": "chapter",
    "manual": "book",
    "mastersthesis": "thesis",
    "phdthesis": "thesis",
    "techreport": "report",
    "unpublished": "manuscript",
    "misc": "document",
}


def _issued(year: object) -> dict | None:
    """The `issued` date, or a literal when the year is not one.

    `ACKREDIT-W009` documents that a biblatex date range and "in press" reach a
    renderer legitimately, and its hint promises at worst that the value is
    rendered unchanged. This one raised `ValueError` instead. CSL has a literal
    date for exactly this, so the value arrives as what it is.
    """
    text = str(year).strip()
    if not text:
        return None
    try:
        return {"date-parts": [[int(text)]]}
    except ValueError:
        return {"literal": text}


def render(used: dict[str, list[str]], items: dict[str, dict]) -> str:
    """
    Render used items in CSL-JSON format.
    This is the standard format for Zotero, Mendeley, and others.
    """
    if not used:
        return "[]"

    csl_items = []

    # Mapping Ackredit types to CSL types
    # Reference: https://docs.citationstyles.org/en/stable/specification.html#appendix-iii-types
    type_map = {
        "article": "article-journal",
        "software": "software",
        "repo": "webpage",
        "web": "webpage",
        "dataset": "dataset",
        "other": "document",
    }

    for item_id in used:
        item = items.get(item_id)
        if not item:
            item = {"title": item_id, "id": item_id}

        csl_item = {
            "id": item.get("id", item_id),
            # What the entry said it was, where that is known; otherwise what
            # Ackredit's own vocabulary can say.
            "type": _FROM_BIBTEX.get(
                item.get("_bibtex_type", ""),
                type_map.get(item.get("type", "other"), "document"),
            ),
            "title": item.get("title", ""),
        }

        # CSL wants family/given, and a `literal` says the name cannot be
        # decomposed. Emitting every author as a literal left a reference
        # manager unable to sort, abbreviate or apply a style — see `_names.py`
        # for which strings decompose and why the rest do not.
        authors = item.get("authors", [])
        if authors:
            csl_item["author"] = [csl_name(author) for author in authors]

        if year := item.get("year"):
            if issued := _issued(year):
                csl_item["issued"] = issued

        if editors := item.get("editors") or item.get("editor"):
            if isinstance(editors, str):
                editors = [editors]
            csl_item["editor"] = [csl_name(editor) for editor in editors]

        for fc_key, csl_key in _DIRECT.items():
            if value := item.get(fc_key):
                csl_item[csl_key] = value

        for csl_key, fc_keys in _FALLBACKS.items():
            for fc_key in fc_keys:
                if value := item.get(fc_key):
                    csl_item[csl_key] = value
                    break

        csl_items.append(csl_item)

    return json.dumps(csl_items, indent=2)
