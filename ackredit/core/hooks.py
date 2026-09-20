from __future__ import annotations

import atexit
import sys
from importlib import metadata
from importlib.abc import MetaPathFinder
from importlib.util import find_spec
from pathlib import Path

from .._private.smonitor.emitter import warn
from .._private.smonitor.warnings import PackageMetadataWarning
from .collector import get_used_items, track_item
from .registry import Registry, register_item

_REMINDER_ENABLED = False


def _split_authors(value: str | None) -> list[str]:
    """Split the legacy metadata Author field into individual names.

    PEP 621 renders `authors` into one comma-separated string. Kept whole it
    becomes a single BibTeX name with many commas, which aborts bibtex.
    """
    if not value:
        return []
    return [name.strip() for name in value.split(",") if name.strip()]


def _exit_reminder():
    """
    Function called at exit to remind the user about collected citations.
    """
    used = get_used_items()
    if not used:
        return

    n_items = len(used)
    msg = (
        f"\n\033[94mℹ️  Ackredit: Your analysis utilized {n_items} components requiring citation.\033[0m\n"
        f"   Run `ackredit.report()` or `ackredit.summary()` to view the full list.\n"
    )
    # Print to stderr to avoid interfering with redirected stdout
    print(msg, file=sys.stderr)


def enable_auto_reminder():
    """
    Enable a polite reminder at the end of the Python session if citations were collected.
    """
    global _REMINDER_ENABLED
    if not _REMINDER_ENABLED:
        atexit.register(_exit_reminder)
        _REMINDER_ENABLED = True


class InjectionsFinder(MetaPathFinder):
    """
    A finder that triggers Ackredit tracking when a registered injection is imported.
    """

    def __init__(self):
        self._triggered = set()

    def find_spec(self, fullname, path, target=None):
        if fullname.startswith("ackredit"):
            return None

        # 0. Standard Injections
        from .standard_injections import STANDARD_INJECTIONS

        if fullname in STANDARD_INJECTIONS and fullname not in self._triggered:
            self._triggered.add(fullname)
            for item_data in STANDARD_INJECTIONS[fullname]:
                register_item(**item_data)
                track_item(item_data["id"], used_by=fullname)

        # 1. Manual Injections
        if fullname in Registry.injections and fullname not in self._triggered:
            self._triggered.add(fullname)
            item_ids = Registry.injections.get(fullname, [])
            for item_id in item_ids:
                track_item(item_id, used_by=fullname)

        # 2. Auto-discovery (only for top-level packages)
        elif "." not in fullname and fullname not in self._triggered:
            self._triggered.add(fullname)
            self._discover_and_register(fullname)

        # We return None so the normal import process continues
        return None

    def _discover_and_register(self, fullname: str):
        # Try to find package path
        spec = find_spec(fullname)
        if not spec or not spec.origin:
            return

        pkg_path = Path(spec.origin).parent

        # Look for CITATION.cff
        from .cff import find_and_parse_cff

        cff_data = find_and_parse_cff(pkg_path)

        if cff_data:
            item_id = f"discovered:{fullname}"
            register_item(
                id=item_id,
                type="software",
                title=cff_data.get("title", fullname),
                authors=cff_data.get("authors", []),
                doi=cff_data.get("doi"),
                url=cff_data.get("url"),
                note=cff_data.get("message"),
            )
            track_item(item_id, used_by=fullname)
        else:
            # Fallback: metadata discovery
            try:
                meta = metadata.metadata(fullname)
                if meta:
                    item_id = f"metadata:{fullname}"
                    register_item(
                        id=item_id,
                        type="software",
                        title=meta.get("Name", fullname),
                        authors=_split_authors(meta.get("Author")),
                        url=meta.get("Home-page") or meta.get("Project-URL"),
                        version=meta.get("Version"),
                    )
                    track_item(item_id, used_by=fullname)
            except metadata.PackageNotFoundError:
                warn(PackageMetadataWarning(extra={"package": fullname}))


_IMPORT_HOOKS_ENABLED = False


def enable_import_hooks():
    """
    Enable automatic citation tracking for third-party libraries via import hooks.
    """
    global _IMPORT_HOOKS_ENABLED
    if not _IMPORT_HOOKS_ENABLED:
        sys.meta_path.insert(0, InjectionsFinder())
        _IMPORT_HOOKS_ENABLED = True
