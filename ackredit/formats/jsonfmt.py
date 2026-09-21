"""The machine-readable report.

This format existed to be parsed, and it emitted six fixed keys: it kept `note`,
which is usually null, and dropped the DOI, the authors, the journal and the
URL. A citation record without those cannot be used as one, which is the only
reason to ask for this format, and nothing said so — the call succeeded and the
output was well-formed JSON.

It now emits what the item carries. Keys beginning with an underscore are
Ackredit's own bookkeeping, such as the `_source` that tells the LaTeX escaper
where a field came from, and stay out of the report.
"""

from __future__ import annotations

import json


def render(used: dict[str, list[str]], items: dict[str, dict]) -> str:
    out = []
    for item_id, used_by in used.items():
        item = items.get(item_id, {"title": item_id})

        # The registry key is the identity, whatever the item says about itself.
        record: dict = {"id": item_id}
        record.update(
            {
                key: value
                for key, value in item.items()
                if key != "id" and not key.startswith("_")
            }
        )
        record["used_by"] = list(used_by)
        out.append(record)

    # A host may register a value this module cannot serialise — a date object
    # reaches `register_item` easily. Rendering it as text keeps the report,
    # which is worth more than refusing to produce one over one field.
    return json.dumps(out, indent=2, default=str, ensure_ascii=False)
