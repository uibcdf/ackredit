from __future__ import annotations

import atexit
import re
import sys
from importlib.abc import MetaPathFinder
from importlib.util import find_spec
from pathlib import Path

from .._private.smonitor.emitter import warn
from .._private.smonitor.warnings import PackageMetadataWarning
from .collector import get_used_items, track_item
from .registry import Registry, register_item

_REMINDER_ENABLED = False


# "Name <email>" pairs, whose separator is unambiguous because the address
# delimits each entry. This is what PEP 621 `authors` renders into.
_NAME_AND_EMAIL = re.compile(r"\s*([^<>,]+?)\s*<[^<>]*>\s*,?")


def _authors_from_metadata(meta) -> list[str]:
    """Read authorship without inventing any.

    `Author-email` carries `Name <email>` pairs and can be parsed exactly, so it
    is preferred whenever present. `Author` is free text where a comma may
    separate two people or may separate one person's surname from their given
    name, and the two cases are not distinguishable:

        "Ana Ruiz, Luis Gomez"   two people
        "Prada, Diego"           one person, written Last, First

    Splitting the second invents an author who does not exist, which is worse for
    a citation tool than a clumsy single entry. So `Author` is split only when
    every part carries a space, which no `Last, First` pair does, and is
    otherwise kept whole. A name BibTeX cannot parse is brace-protected at
    render time rather than guessed at here.
    """
    for field in ("Author-email", "Maintainer-email"):
        if raw := meta.get(field):
            if names := [name for name in _NAME_AND_EMAIL.findall(raw) if name]:
                return names

    raw = meta.get("Author") or meta.get("Maintainer")
    if not raw:
        return []
    return _split_authors(raw)


def _split_authors(value: str | None) -> list[str]:
    """Split a free-text author field only when doing so cannot invent a person."""
    if not value:
        return []
    parts = [part.strip() for part in value.split(",")]
    parts = [part for part in parts if part]
    if len(parts) > 1 and all(" " in part for part in parts):
        return parts
    return [value.strip()]


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
        """Credit *fullname* from the most authoritative source there is.

        The order is the point. A manual injection is a human integrating this
        library and saying what to credit, so it wins. After that the package's
        own `CITATION.cff` wins, because it is the project's own statement of
        how it wants to be cited, versioned and updated by the project itself.
        Ackredit's shipped table is a snapshot that can only go stale, so it is
        a fallback, and package metadata is the last resort.

        It used to run in the opposite order: a shipped entry marked the package
        as handled, so its `CITATION.cff` was never read. `import molsysmt`
        credited a MolSysMT paper that does not exist while the file saying what
        to cite sat unread in the same directory.
        """
        if fullname.startswith("ackredit") or fullname in self._triggered:
            return None

        # 1. What the host explicitly asked for.
        if fullname in Registry.injections:
            self._triggered.add(fullname)
            for item_id in Registry.injections[fullname]:
                track_item(item_id, used_by=fullname)
            return None

        # Everything below describes a distribution, not one of its modules.
        if "." in fullname:
            return None

        # Marked before the work, not after: the discovery below calls
        # find_spec, which reaches this finder again, and this is what stops it.
        self._triggered.add(fullname)
        self._record(fullname)

        # We return None so the normal import process continues
        return None

    def _record(self, fullname: str) -> None:
        from .standard_injections import STANDARD_INJECTIONS

        shipped = STANDARD_INJECTIONS.get(fullname, [])
        cff_data = self._read_citation_file(fullname)

        if cff_data is None:
            if shipped:
                self._register_all(shipped, fullname)
            else:
                self._register_from_metadata(fullname)
            return

        # The file describes the software, so it replaces a shipped entry for
        # the software and nothing else. A paper Ackredit ships alongside it is
        # a different work and still stands.
        entry = next((item for item in shipped if item.get("type") == "software"), {})
        item_id = entry.get("id", f"discovered:{fullname}")

        register_item(
            id=item_id,
            type="software",
            title=cff_data.get("title") or entry.get("title") or fullname,
            authors=cff_data.get("authors") or entry.get("authors", []),
            doi=cff_data.get("doi") or entry.get("doi"),
            url=cff_data.get("url") or entry.get("url"),
            version=cff_data.get("version"),
            note=cff_data.get("message"),
        )
        track_item(item_id, used_by=fullname)

        self._register_all([item for item in shipped if item is not entry], fullname)

    @staticmethod
    def _register_all(items, fullname: str) -> None:
        for item_data in items:
            register_item(**item_data)
            track_item(item_data["id"], used_by=fullname)

    @staticmethod
    def _read_citation_file(fullname: str) -> dict | None:
        """The package's own CITATION.cff, or None if it has none to read."""
        spec = find_spec(fullname)
        if not spec or not spec.origin:
            return None

        from .cff import find_and_parse_cff

        return find_and_parse_cff(Path(spec.origin).parent)

    @staticmethod
    def _register_from_metadata(fullname: str) -> None:
        """Last resort: what the installed distribution declares about itself.

        `importlib.metadata` is imported here rather than at module level: it
        pulls in email.message, zipfile and inspect, about half the cost of
        importing Ackredit, and this path only runs when import hooks are
        enabled.
        """
        from importlib import metadata

        try:
            meta = metadata.metadata(fullname)
        except metadata.PackageNotFoundError:
            warn(PackageMetadataWarning(extra={"package": fullname}))
            return

        if not meta:
            return

        item_id = f"metadata:{fullname}"
        register_item(
            id=item_id,
            type="software",
            title=meta.get("Name", fullname),
            authors=_authors_from_metadata(meta),
            url=meta.get("Home-page") or meta.get("Project-URL"),
            version=meta.get("Version"),
        )
        track_item(item_id, used_by=fullname)


_IMPORT_HOOKS_ENABLED = False


def enable_import_hooks():
    """
    Enable automatic citation tracking for third-party libraries via import hooks.
    """
    global _IMPORT_HOOKS_ENABLED
    if not _IMPORT_HOOKS_ENABLED:
        sys.meta_path.insert(0, InjectionsFinder())
        _IMPORT_HOOKS_ENABLED = True
