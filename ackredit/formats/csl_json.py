"""The report a reference manager reads.

CSL-JSON is a schema, so unlike BibTeX nothing can simply be passed through: a
processor has no use for a key it does not define. The mapping below is
therefore bounded and explicit, and it used to be much shorter than the schema
allows — a book arrived at Zotero with no publisher, no ISBN and no series,
which is a reference the manager cannot format.
"""

from __future__ import annotations

import json

from .._private.dates import calendar_date_parts
from ._links import doi_name
from ._names import csl_names

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
    "page-count": "number-of-pages",
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

# CFF uses a separate vocabulary. Keep its original kind in the saved record,
# and map only kinds whose meaning is unambiguous in CSL 1.0.2. In particular,
# a complete dictionary is not necessarily a dictionary entry, and an event is
# not a paper presented at that event. Unmapped kinds remain documents.
_FROM_CFF = {
    "book": "book",
    "edited-work": "book",
    "proceedings": "book",
    "manual": "report",
    "report": "report",
    "thesis": "thesis",
    "conference-paper": "paper-conference",
    "magazine-article": "article-magazine",
    "newspaper-article": "article-newspaper",
    "pamphlet": "pamphlet",
    "patent": "patent",
    "personal-communication": "personal_communication",
    "blog": "post-weblog",
    "map": "map",
    "unpublished": "manuscript",
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


def _publication_date(item: dict) -> dict | None:
    """Use original precision without combining contradictory date components.

    Explicit year/month take precedence over conflicting full dates. Consistent
    publication dates add precision, with release dates used only when no
    publication date is stated. Textual years keep their historical literal
    meaning. Missing/invalid months never invent date parts.
    """
    year = item.get("year")
    issued = _issued(year) if year is not None else None
    month = None
    raw_month = item.get("month")
    if issued and "date-parts" in issued and raw_month is not None:
        try:
            candidate = int(str(raw_month).strip())
        except ValueError:
            candidate = 0
        if 1 <= candidate <= 12:
            month = candidate
            issued["date-parts"][0].append(month)

    for field in ("date-published", "date-released"):
        if (raw := item.get(field)) is None or not (text := str(raw).strip()):
            continue
        parts = calendar_date_parts(text)
        if issued:
            if "date-parts" not in issued:
                return issued
            if parts and parts[0] == issued["date-parts"][0][0]:
                if raw_month is None or month == parts[1]:
                    return {"date-parts": [parts]}
            return issued
        return {"date-parts": [parts]} if parts else {"literal": text}
    return issued


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
                _FROM_CFF.get(
                    item.get("_cff_type", ""),
                    type_map.get(item.get("type", "other"), "document"),
                ),
            ),
            "title": item.get("title", ""),
        }

        # CSL wants family/given, and a `literal` says the name cannot be
        # decomposed. Emitting every author as a literal left a reference
        # manager unable to sort, abbreviate or apply a style — see `_names.py`
        # for which strings decompose and why the rest do not.
        authors = item.get("authors", [])
        if authors:
            csl_item["author"] = csl_names(authors, cff=item.get("_cff_authors"))

        if issued := _publication_date(item):
            csl_item["issued"] = issued

        if editors := item.get("editors") or item.get("editor"):
            if isinstance(editors, str):
                editors = [editors]
            csl_item["editor"] = csl_names(editors, cff=item.get("_cff_editors"))

        for fc_key, csl_key in _DIRECT.items():
            if value := item.get(fc_key):
                csl_item[csl_key] = doi_name(value) if fc_key == "doi" else value

        for csl_key, fc_keys in _FALLBACKS.items():
            for fc_key in fc_keys:
                if value := item.get(fc_key):
                    csl_item[csl_key] = value
                    break

        csl_items.append(csl_item)

    return json.dumps(csl_items, indent=2)
