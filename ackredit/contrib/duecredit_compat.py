from __future__ import annotations

import logging

from ..core.collector import get_used_items
from ..core.registry import Registry

logger = logging.getLogger(__name__)


def export_to_duecredit():
    """
    Forward all citations collected by Ackredit to DueCredit (if installed).
    This allows interoperability between the two systems.
    """
    try:
        import duecredit
        from duecredit.entries import BibTeX, Doi
    except ImportError:
        logger.debug("duecredit not installed. Skipping export.")
        return

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
        except Exception as e:
            logger.warning(f"Failed to export citation {item_id} to duecredit: {e}")
