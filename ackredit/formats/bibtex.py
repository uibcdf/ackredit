from __future__ import annotations

from ._latex import escape, is_latex_source

# The fields whose BibTeX name differs from Ackredit's, in the order a reader
# expects them. Everything else the item carries follows, alphabetically.
_ORDERED = [
    ("author", "authors"),
    ("year", "year"),
    ("doi", "doi"),
    ("url", "url"),
    ("note", "note"),
    ("journal", "journal"),
]

# Ackredit's own keys, which are not bibliographic fields.
_NOT_A_FIELD = {"id", "type", "title", "authors", "how_to_cite"} | {
    fc_key for _, fc_key in _ORDERED
}


def _bibtex_name(name: str) -> str:
    """Brace-protect a name BibTeX cannot parse.

    BibTeX's three-part form is "von Last, Jr, First", so two commas are valid and
    only a third is an error that aborts the run. Double braces make the whole
    string one literal name, the standard idiom for corporate and irregular names,
    at the cost of its sorting key and initials — so it is used only when BibTeX
    genuinely cannot read the name.
    """
    return f"{{{name}}}" if name.count(",") > 2 else name


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

    # Ackredit's types mapped onto BibTeX's own vocabulary. `@software` and
    # `@dataset` come from biblatex and are not defined by a BibTeX style, so a
    # BibTeX run warns and falls back to a default layout, losing the distinction
    # entirely. Emitting `@misc` and carrying the kind in `howpublished` keeps it,
    # renders it to the reader, and compiles without warnings under any style.
    type_map = {
        "article": "article",
        "software": "misc",
        "repo": "misc",
        "web": "misc",
        "dataset": "misc",
        "other": "misc",
    }

    # What `howpublished` should say for a type that BibTeX has no entry for.
    kind_map = {
        "software": "Software",
        "dataset": "Dataset",
        "repo": "Software repository",
        "web": "Web resource",
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

        latex_source = is_latex_source(item)

        fc_type = item.get("type", "other")
        # An item read from a .bib file is written back as the entry it was.
        bib_type = item.get("_bibtex_type") or type_map.get(fc_type, "misc")

        fields: list[str] = []

        # Helper to add fields
        def add_field(bib_key: str, fc_key: str):
            val = item.get(fc_key)
            if not val:
                return

            # A TeX engine reads these values; a bare '&' in a journal name
            # silently mangles the compiled bibliography. An item parsed from a
            # .bib file is already LaTeX and is passed through untouched.
            #
            # Brace protection is applied after escaping, never before: its
            # braces are BibTeX syntax rather than content, and escaping them
            # would turn the protection into a literal pair of characters.
            if isinstance(val, list):
                parts = [escape(str(part), latex_source=latex_source) for part in val]
                if fc_key == "authors":
                    parts = [_bibtex_name(part) for part in parts]
                escaped = " and ".join(parts)
            else:
                escaped = escape(str(val), latex_source=latex_source)

            fields.append(f"  {bib_key} = {{{escaped}}}")

        add_field("title", "title")

        # Name the kind BibTeX cannot express in its entry type — but not when
        # the entry already says what it is, which it does for anything read
        # from a .bib file.
        if not item.get("_bibtex_type") and (kind := kind_map.get(fc_type)):
            fields.append(f"  howpublished = {{{kind}}}")

        for bib_key, fc_key in _ORDERED:
            add_field(bib_key, fc_key)

        # Whatever else the item carries. A fixed list dropped the publisher of
        # a book, the pages of a conference paper and the school of a thesis,
        # although the parser had stored all three. A .bst style ignores a field
        # it does not know, so carrying one costs nothing and dropping one costs
        # the bibliography.
        for fc_key in sorted(item):
            if fc_key in _NOT_A_FIELD or fc_key.startswith("_"):
                continue
            add_field(fc_key, fc_key)

        entry = f"@{bib_type}{{{key},\n" + ",\n".join(fields) + "\n}"
        entries.append(entry)

    return "\n\n".join(entries)
