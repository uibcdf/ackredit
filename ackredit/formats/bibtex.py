from __future__ import annotations


def render(used: dict[str, list[str]], items: dict[str, dict]) -> str:
    """
    Render used items in BibTeX format.
    Supports basic mapping from Ackredit types to BibTeX entry types.
    """
    if not used:
        return ""

    entries: list[str] = []

    # Mapping Ackredit types to BibTeX types
    type_map = {
        "article": "article",
        "software": "software",
        "repo": "misc",
        "web": "misc",
        "dataset": "dataset",
        "other": "misc",
    }

    for item_id in used:
        item = items.get(item_id)
        if not item:
            # If item not in registry, create a minimal misc entry
            item = {"title": item_id, "id": item_id}

        item_id = item.get("id", item_id)
        key = item_id.replace(":", "_").replace(" ", "_")

        fc_type = item.get("type", "other")
        bib_type = type_map.get(fc_type, "misc")

        fields: list[str] = []

        # Helper to add fields
        def add_field(bib_key: str, fc_key: str):
            val = item.get(fc_key)
            if val:
                if isinstance(val, list):
                    val = " and ".join(val)
                fields.append(f"  {bib_key} = {{{val}}}")

        add_field("title", "title")
        add_field("author", "authors")
        add_field("year", "year")
        add_field("doi", "doi")
        add_field("url", "url")
        add_field("note", "note")

        # Type specific additions
        if fc_type == "article":
            add_field("journal", "journal")
            add_field("volume", "volume")
            add_field("number", "number")
            add_field("pages", "pages")
        elif fc_type == "software" or fc_type == "repo":
            if "version" in item:
                add_field("version", "version")

        entry = f"@{bib_type}{{{key},\n" + ",\n".join(fields) + "\n}"
        entries.append(entry)

    return "\n\n".join(entries)
