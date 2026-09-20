from __future__ import annotations

import json


def render(used: dict[str, list[str]], items: dict[str, dict]) -> str:
    out = []
    for item_id, used_by in used.items():
        item = items.get(item_id, {"title": item_id})
        out.append(
            {
                "id": item_id,
                "title": item.get("title"),
                "year": item.get("year"),
                "used_by": used_by,
                "note": item.get("note"),
                "type": item.get("type"),
            }
        )
    return json.dumps(out, indent=2)
