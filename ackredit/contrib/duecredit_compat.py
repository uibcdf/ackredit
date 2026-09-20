from __future__ import annotations

from depdigest import dep_digest

from .._private.smonitor.emitter import warn
from .._private.smonitor.warnings import DueCreditExportWarning
from ..core.collector import get_used_items
from ..core.registry import Registry


@dep_digest("duecredit")
def export_to_duecredit():
    """
    Forward all citations collected by Ackredit to DueCredit (if installed).
    This allows interoperability between the two systems.
    """
    import duecredit
    from duecredit.entries import BibTeX, Doi

    used = get_used_items()
    items = Registry.items

    # We use our BibTeX renderer to feed duecredit
    from ..formats import bibtex

    for item_id in used:
        item = items.get(item_id)
        if not item:
            continue

        description = item.get("title", item_id)
        path = "ackredit." + item_id

        try:
            if "doi" in item:
                # Use Doi entry if available, it's cleaner for duecredit
                duecredit.due.cite(Doi(item["doi"]), description=description, path=path)
            else:
                # Fallback to BibTeX
                single_item_used = {item_id: used[item_id]}
                bib_str = bibtex.render(single_item_used, items)
                duecredit.due.cite(BibTeX(bib_str), description=description, path=path)
        except Exception as error:
            warn(
                DueCreditExportWarning(
                    extra={
                        "item_id": item_id,
                        "error_type": type(error).__name__,
                        "error": str(error),
                    }
                )
            )
