from __future__ import annotations

from ..core.collector import get_usage_tree


def render(used: dict[str, list[str]], items: dict[str, dict]) -> str:
    """
    Render a provenance tree showing why each item was cited.
    """
    tree = get_usage_tree()
    if not tree:
        return "No tracking information available."

    # Identify root targets (those that are not children of any other target)
    all_children = set()
    for data in tree.values():
        all_children.update(data["children"])

    roots = [t for t in tree if t not in all_children]

    lines = ["# Citation Provenance Graph", ""]

    def walk(target: str, prefix: str = "", is_last: bool = True):
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{target}")

        new_prefix = prefix + ("    " if is_last else "│   ")

        target_data = tree.get(target, {"items": set(), "children": list()})

        # Sort items and children for consistent output
        target_items = sorted(list(target_data["items"]))
        target_children = sorted(list(target_data["children"]))

        total_elements = len(target_items) + len(target_children)

        for i, item_id in enumerate(target_items):
            item_is_last = i == total_elements - 1
            item_conn = "└── " if item_is_last else "├── "
            item_info = items.get(item_id, {"title": item_id})
            title = item_info.get("title", item_id)
            lines.append(f"{new_prefix}{item_conn}(Cite: {title})")

        for i, child in enumerate(target_children):
            child_is_last = i + len(target_items) == total_elements - 1
            walk(child, new_prefix, child_is_last)

    for i, root in enumerate(sorted(roots)):
        walk(root, is_last=(i == len(roots) - 1))

    return "\n".join(lines)
