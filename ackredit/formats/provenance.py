"""The report that says *why* each item was cited.

The graph it draws is not a tree. Entering `scope("lib.fib")` inside itself
records the target as its own child, which is what a recursive function does,
and two functions that call each other record a cycle between them. The
renderer assumed a tree twice over: it started from the targets nobody calls, so
a pure cycle left it with nothing to draw, and it followed children without
remembering where it had been, so a cycle below a real root ran until Python
stopped it.

Both are ordinary in scientific code, and the first failed silently.
"""

from __future__ import annotations

from ..core.collector import get_usage_tree


def _entry_points(tree: dict) -> list[str]:
    """Where to start drawing.

    The targets nobody calls, and then whatever those cannot reach. A graph
    that is all cycle has no uncalled target at all, and used to be drawn as an
    empty report.
    """
    called = set()
    for node in tree.values():
        called.update(node["children"])

    entries = sorted(target for target in tree if target not in called)

    reached: set[str] = set()

    def mark(target: str) -> None:
        pending = [target]
        while pending:
            current = pending.pop()
            if current in reached:
                continue
            reached.add(current)
            pending.extend(tree.get(current, {}).get("children", ()))

    for entry in entries:
        mark(entry)

    for target in sorted(tree):
        if target not in reached:
            entries.append(target)
            mark(target)

    return entries


def render(used: dict[str, list[str]], items: dict[str, dict]) -> str:
    """
    Render a provenance tree showing why each item was cited.
    """
    return render_tree(get_usage_tree(), items)


def render_tree(tree: dict, items: dict) -> str:
    """Render an explicitly supplied graph, including a saved attribution graph."""
    if not tree:
        return "No tracking information available."

    lines = ["# Citation Provenance Graph", ""]

    expanded: set[str] = set()
    entries = _entry_points(tree)
    for index, entry in enumerate(entries):
        pending = [(entry, "", index == len(entries) - 1, False)]
        ancestors: set[str] = set()
        while pending:
            target, prefix, is_last, leaving = pending.pop()
            if leaving:
                ancestors.remove(target)
                continue
            connector = "└── " if is_last else "├── "
            if target in ancestors:
                lines.append(f"{prefix}{connector}{target} (above)")
                continue
            if target in expanded:
                lines.append(f"{prefix}{connector}{target} (shared; shown above)")
                continue
            lines.append(f"{prefix}{connector}{target}")
            expanded.add(target)
            ancestors.add(target)
            pending.append((target, prefix, is_last, True))
            new_prefix = prefix + ("    " if is_last else "│   ")
            node = tree.get(target, {"items": (), "children": ()})
            target_items = sorted(node["items"])
            target_children = sorted(node["children"])
            total_elements = len(target_items) + len(target_children)
            for item_index, item_id in enumerate(target_items):
                item_conn = "└── " if item_index == total_elements - 1 else "├── "
                title = items.get(item_id, {"title": item_id}).get("title", item_id)
                lines.append(f"{new_prefix}{item_conn}(Cite: {title})")
            for child_index in reversed(range(len(target_children))):
                child_is_last = child_index + len(target_items) == total_elements - 1
                pending.append(
                    (target_children[child_index], new_prefix, child_is_last, False)
                )

    return "\n".join(lines)
