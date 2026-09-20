from __future__ import annotations


def render(used: dict[str, list[str]], items: dict[str, dict]) -> str:
    if not used:
        return "No items were tracked in this session."
    parts: list[str] = []
    for item_id, used_by in used.items():
        item = items.get(item_id, {"title": item_id})
        title = item.get("title", item_id)
        year = item.get("year")
        s = title if not year else f"{title} ({year})"
        if used_by:
            s += f" [used by: {', '.join(used_by)}]"
        parts.append(s)
    return "\n".join(parts)
