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

    def mark(target: str, walked: frozenset) -> None:
        if target in walked:
            return
        reached.add(target)
        for child in tree.get(target, {}).get("children", ()):
            mark(child, walked | {target})

    for entry in entries:
        mark(entry, frozenset())

    for target in sorted(tree):
        if target not in reached:
            entries.append(target)
            mark(target, frozenset())

    return entries


def render(used: dict[str, list[str]], items: dict[str, dict]) -> str:
    """
    Render a provenance tree showing why each item was cited.
    """
    tree = get_usage_tree()
    if not tree:
        return "No tracking information available."

    lines = ["# Citation Provenance Graph", ""]

    def walk(target: str, prefix: str, is_last: bool, walked: frozenset) -> None:
        connector = "└── " if is_last else "├── "

        if target in walked:
            # Where it came back to itself. Saying so keeps the recursion in the
            # report, which is part of why the citation happened, without
            # following it.
            lines.append(f"{prefix}{connector}{target} (above)")
            return

        lines.append(f"{prefix}{connector}{target}")

        new_prefix = prefix + ("    " if is_last else "│   ")

        target_data = tree.get(target, {"items": set(), "children": set()})

        # Sort items and children for consistent output
        target_items = sorted(target_data["items"])
        target_children = sorted(target_data["children"])

        total_elements = len(target_items) + len(target_children)

        for index, item_id in enumerate(target_items):
            item_is_last = index == total_elements - 1
            item_conn = "└── " if item_is_last else "├── "
            item_info = items.get(item_id, {"title": item_id})
            title = item_info.get("title", item_id)
            lines.append(f"{new_prefix}{item_conn}(Cite: {title})")

        for index, child in enumerate(target_children):
            child_is_last = index + len(target_items) == total_elements - 1
            walk(child, new_prefix, child_is_last, walked | {target})

    entries = _entry_points(tree)
    for index, entry in enumerate(entries):
        walk(entry, "", index == len(entries) - 1, frozenset())

    return "\n".join(lines)
