from __future__ import annotations

import json

from ._names import csl_name


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
            "type": type_map.get(item.get("type", "other"), "document"),
            "title": item.get("title", ""),
        }

        # CSL wants family/given, and a `literal` says the name cannot be
        # decomposed. Emitting every author as a literal left a reference
        # manager unable to sort, abbreviate or apply a style — see `_names.py`
        # for which strings decompose and why the rest do not.
        authors = item.get("authors", [])
        if authors:
            csl_item["author"] = [csl_name(author) for author in authors]

        # Date handling
        year = item.get("year")
        if year:
            csl_item["issued"] = {"date-parts": [[int(year)]]}

        # Other fields
        if "doi" in item:
            csl_item["DOI"] = item["doi"]
        if "url" in item:
            csl_item["URL"] = item["url"]
        if "journal" in item:
            csl_item["container-title"] = item["journal"]
        if "note" in item:
            csl_item["note"] = item["note"]
        if "volume" in item:
            csl_item["volume"] = item["volume"]
        if "number" in item:
            csl_item["issue"] = item["number"]
        if "pages" in item:
            csl_item["page"] = item["pages"]
        if "version" in item:
            csl_item["version"] = item["version"]

        csl_items.append(csl_item)

    return json.dumps(csl_items, indent=2)
