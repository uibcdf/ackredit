from __future__ import annotations

from ._latex import escape


def _bibtex_name(name: str) -> str:
    """Brace-protect a name BibTeX cannot parse.

    BibTeX reads at most two commas in a name ("von Last, Jr, First"); more than
    that is an error that aborts the run. Double braces make the whole string one
    literal name, the standard idiom for corporate and irregular names.
    """
    return f"{{{name}}}" if name.count(",") > 1 else name


def _cite_key(item_id: str) -> str:
    """Return a citation key that is safe as a printed natbib label."""
    return item_id.replace(":", "-").replace(" ", "-").replace("_", "-")


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
        # A hyphen, not an underscore: when an entry has no author, natbib
        # derives the printed label from the key, and a bare underscore there is
        # read in math mode and aborts the compilation. Auto-discovered items
        # frequently have no author.
        key = _cite_key(item_id)

        fc_type = item.get("type", "other")
        bib_type = type_map.get(fc_type, "misc")

        fields: list[str] = []

        # Helper to add fields
        def add_field(bib_key: str, fc_key: str):
            val = item.get(fc_key)
            if val:
                if isinstance(val, list):
                    parts = [str(part) for part in val]
                    if fc_key == "authors":
                        parts = [_bibtex_name(part) for part in parts]
                    val = " and ".join(parts)
                # A TeX engine reads these values; a bare '&' in a journal name
                # silently mangles the compiled bibliography.
                fields.append(f"  {bib_key} = {{{escape(str(val))}}}")

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
