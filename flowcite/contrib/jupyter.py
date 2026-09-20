from __future__ import annotations
from ..core.collector import get_used_items
from ..core.registry import Registry

class CitationsHTML:
    """
    Object that implements _repr_html_ for rich display in Jupyter Notebooks.
    """
    def __init__(self, used: dict[str, list[str]], items: dict[str, dict]):
        self.used = used
        self.items = items

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
            "<tbody>"
        ]

        for item_id, used_by in self.used.items():
            item = self.items.get(item_id, {"title": item_id})
            title = item.get("title", item_id)
            year = item.get("year", "")
            authors = item.get("authors", [])
            if isinstance(authors, list):
                authors = ", ".join(authors)
            
            doi = item.get("doi")
            url = item.get("url")
            
            # Format Title & Link
            link = None
            if doi:
                link = f"https://doi.org/{doi}"
            elif url:
                link = url
            
            display_title = f"<b>{title}</b>"
            if link:
                display_title = f"<a href='{link}' target='_blank' style='text-decoration: none; color: #007bff;'>{display_title}</a>"
            
            details = []
            if authors:
                details.append(f"<i>{authors}</i>")
            if year:
                details.append(f"({year})")
            
            html.append("<tr style='border-bottom: 1px solid #eee;'>")
            html.append(f"<td style='padding: 8px;'>{display_title}</td>")
            html.append(f"<td style='padding: 8px; font-size: 0.9em;'>{'<br>'.join(details)}</td>")
            html.append(f"<td style='padding: 8px; font-size: 0.8em; color: #666;'>{', '.join(used_by) if used_by else '-'}</td>")
            html.append("</tr>")

        html.append("</tbody></table></div>")
        return "".join(html)

def summary():
    """
    Returns a rich HTML representation of the tracked citations.
    Usage in a notebook:
        flowcite.summary()
    """
    return CitationsHTML(get_used_items(), Registry.items)
