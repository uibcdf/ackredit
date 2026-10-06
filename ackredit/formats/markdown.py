from __future__ import annotations

from ._links import doi_link
from ._markdown import destination, escape, safe_link
from ._names import author_list


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
        lines.extend(_reference_lines(item_id, items.get(item_id), used_by))
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def _reference_lines(item_id, item, used_by):
    """Shared bibliography presentation; every external text/link is escaped."""
    item = item or {"title": item_id, "id": item_id}
    title = escape(item.get("title", item_id))
    year = item.get("year")
    authors = item.get("authors", [])
    note = item.get("note")

    doi = item.get("doi")
    link = doi_link(doi) if doi else safe_link(item.get("url"))
    display_title = f"**{title}**"
    if link:
        display_title = f"[{display_title}]({destination(link)})"
    line = f"- {display_title}"
    if year:
        line += f" ({escape(year)})"
    lines = [line]

    if authors:
        lines.append(f"  - Authors: {author_list(authors, escape)}")
    if used_by:
        lines.append(f"  - Used by: {', '.join(escape(name) for name in used_by)}")
    if note:
        lines.append(f"  - Note: {escape(note)}")
    return lines
