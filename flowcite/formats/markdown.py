from __future__ import annotations


def render(used: dict[str, list[str]], items: dict[str, dict]) -> str:
    """
    Render used items in a rich Markdown format.
    Includes clickable titles (via DOI or URL) and formatted author lists.
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

        title = item.get("title", item_id)
        year = item.get("year")
        authors = item.get("authors", [])
        doi = item.get("doi")
        url = item.get("url")
        note = item.get("note")

        # Link construction
        link = f"https://doi.org/{doi}" if doi else url

        display_title = f"**{title}**"
        if link:
            display_title = f"[{display_title}]({link})"

        line = f"- {display_title}"
        if year:
            line += f" ({year})"
        lines.append(line)

        if authors:
            if isinstance(authors, list):
                authors_str = ", ".join(authors)
            else:
                authors_str = str(authors)
            lines.append(f"  - Authors: {authors_str}")

        if used_by:
            lines.append(f"  - Used by: {', '.join(used_by)}")

        if note:
            lines.append(f"  - Note: {note}")

        lines.append("")

    return "\n".join(lines).strip() + "\n"
