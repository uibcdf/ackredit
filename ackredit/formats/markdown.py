from __future__ import annotations

from ._markdown import destination, escape, safe_link


def render(used: dict[str, list[str]], items: dict[str, dict]) -> str:
    """Render the tracked items as Markdown, with linked titles.

    Every interpolated value is escaped and every link is validated. The values
    are not Ackredit's: they arrive from Crossref, from DataCite, from the
    `CITATION.cff` of any installed package and from whatever a host registered.
    """
    lines: list[str] = ["# Workflow Citations and Acknowledgements", ""]

    if not used:
        lines.append("_No items were tracked in this session._")
        return "\n".join(lines)

    for item_id, used_by in used.items():
        item = items.get(item_id)
        if not item:
            # Fallback if item is not registered
            item = {"title": item_id, "id": item_id}

        title = escape(item.get("title", item_id))
        year = item.get("year")
        authors = item.get("authors", [])
        note = item.get("note")

        # A DOI builds its own https link; a url is taken as given, so it is the
        # one that has to prove it can be followed safely.
        doi = item.get("doi")
        link = f"https://doi.org/{doi}" if doi else safe_link(item.get("url"))

        display_title = f"**{title}**"
        if link:
            display_title = f"[{display_title}]({destination(link)})"

        line = f"- {display_title}"
        if year:
            line += f" ({escape(year)})"
        lines.append(line)

        if authors:
            if isinstance(authors, list):
                authors_str = ", ".join(escape(author) for author in authors)
            else:
                authors_str = escape(authors)
            lines.append(f"  - Authors: {authors_str}")

        if used_by:
            lines.append(f"  - Used by: {', '.join(escape(name) for name in used_by)}")

        if note:
            lines.append(f"  - Note: {escape(note)}")

        lines.append("")

    return "\n".join(lines).strip() + "\n"
