from __future__ import annotations

from .collector import track_item
from .registry import Registry, add_injection


def register(target_module: str, items: list[str]) -> None:
    """
    Register items that should be credited if target_module is used/imported.
    """
    add_injection(target_module, items)


def mark_import(module_name: str) -> None:
    """
    Can be called by a small import hook to credit injected modules.
    """
    item_ids = Registry.injections.get(module_name, [])
    for item_id in item_ids:
        track_item(item_id, used_by=module_name)


# This leaves the door open for a future import hook, or for a host library to call
# flowcite.core.injections.mark_import("mdtraj") directly when it detects that use.
