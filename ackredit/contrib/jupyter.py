from __future__ import annotations

from ..core.collector import get_used_items
from ..core.registry import Registry
from ..formats._html import escape, safe_link


class CitationsHTML:
    """What a run cited, rendered where it is shown.

    A notebook asks for `_repr_html_` and gets the table. Everywhere else —
    a REPL, a script, a log — printing this used to give the default object
    repr, so the call the guide offers a user showed them an address in memory.

    Its contract is those three: `_repr_html_` for a notebook, and `str()` and
    `repr()` for everywhere else. The text comes from the `text` renderer rather
    than a second implementation, so the two cannot disagree about what a run
    cited.
    """

    def __init__(self, used: dict[str, list[str]], items: dict[str, dict]):
        self.used = used
        self.items = items

    def __str__(self) -> str:
        from ..formats import text

        return text.render(self.used, self.items)

    # A display object is read, not reconstructed, so this is the same text.
    __repr__ = __str__

    def _repr_html_(self) -> str:
        if not self.used:
            return "<p><i>No items were tracked in this session.</i></p>"

        html = [
            "<div style='border: 1px solid #ddd; padding: 10px; border-radius: 5px; background-color: #f9f9f9;'>",
            "<h3 style='margin-top: 0;'>Workflow Citations & Acknowledgements</h3>",
            "<table style='width: 100%; border-collapse: collapse;'>",
            "<thead><tr style='border-bottom: 2px solid #ddd; text-align: left;'>",
            "<th style='padding: 8px;'>Item</th>",
            "<th style='padding: 8px;'>Details</th>",
            "<th style='padding: 8px;'>Used by</th>",
            "</tr></thead>",
            "<tbody>",
        ]

        for item_id, used_by in self.used.items():
            item = self.items.get(item_id, {"title": item_id})
            title = escape(item.get("title", item_id))
            year = item.get("year", "")
            authors = item.get("authors", [])
            if isinstance(authors, list):
                authors = ", ".join(str(author) for author in authors)

            # A DOI builds its own https link; a url is taken as given, so it is
            # the one that has to prove it can be followed safely.
            doi = item.get("doi")
            link = f"https://doi.org/{doi}" if doi else safe_link(item.get("url"))

            display_title = f"<b>{title}</b>"
            if link:
                display_title = (
                    f"<a href='{escape(link)}' target='_blank' "
                    f"style='text-decoration: none; color: #007bff;'>{display_title}</a>"
                )

            details = []
            if authors:
                details.append(f"<i>{escape(authors)}</i>")
            if year:
                details.append(f"({escape(year)})")

            callers = (
                ", ".join(escape(caller) for caller in used_by) if used_by else "-"
            )

            html.append("<tr style='border-bottom: 1px solid #eee;'>")
            html.append(f"<td style='padding: 8px;'>{display_title}</td>")
            html.append(
                f"<td style='padding: 8px; font-size: 0.9em;'>{'<br>'.join(details)}</td>"
            )
            html.append(
                f"<td style='padding: 8px; font-size: 0.8em; color: #666;'>{callers}</td>"
            )
            html.append("</tr>")

        html.append("</tbody></table></div>")
        return "".join(html)


def summary():
    """
    Returns a rich HTML representation of the tracked citations.

    Usage in a notebook::

        ackredit.summary()
    """
    return CitationsHTML(get_used_items(), Registry.items)
