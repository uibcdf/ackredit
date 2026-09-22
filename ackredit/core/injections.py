"""Crediting what a host declared with :func:`ackredit.add_injection`.

An injection says: a process that imports this module cites these items. The
import hook in :mod:`ackredit.core.hooks` sees an import as it happens, but an
import of a module already in ``sys.modules`` never reaches a finder, so a
module loaded before the hook existed was never credited. That is ordinary — a
host imports mdtraj at the top of a submodule before its ``__init__`` enables
the hook — and since ``uibcdf/ackredit#62`` it is certain for numpy, which
Ackredit loads itself through ArgDigest (``uibcdf/ackredit#69``).

So an injection is credited whether its module arrived before the hook or after.
This is the one place that credits one, so the hook, enabling it, and declaring
an injection cannot disagree about what that means.
"""

from __future__ import annotations

import sys

from .collector import track_item
from .registry import Registry, add_injection


def register(target_module: str, items: list[str]) -> None:
    """
    Register items that should be credited if target_module is used/imported.
    """
    add_injection(target_module, items)


def mark_import(module_name: str) -> None:
    """Credit what was injected for *module_name*.

    Crediting twice is harmless: a run records each item once, with each name
    that used it once.
    """
    for item_id in Registry.injections.get(module_name, []):
        track_item(item_id, used_by=module_name)


def mark_loaded(module_name: str | None = None) -> None:
    """Credit the injections whose module is already imported.

    With a name, only that injection; without one, all of them. A module that
    has not been imported is left for the hook to see when it is.
    """
    targets = [module_name] if module_name else list(Registry.injections)
    for target in targets:
        if target in sys.modules:
            mark_import(target)
