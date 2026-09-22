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
from .injections import mark_import, mark_loaded
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
    """Say, once, that this run used work worth citing.

    This is a `print` rather than an SMonitor code on purpose. The catalog
    carries diagnostics — something went wrong and here is what and why — and a
    host filters, escalates and reports them as such. This is not one: nothing
    failed, and routing a courtesy at the end of a run through the warning
    machinery would let a host's warning configuration turn it into an error.
    """
    used = get_used_items()
    if not used:
        return

    count = len(used)
    if count == 1:
        headline = "Ackredit: this run used 1 work that asks to be cited."
        detail = (
            "ackredit.report() lists it; ackredit.summary() shows it in a notebook."
        )
    else:
        headline = f"Ackredit: this run used {count} works that ask to be cited."
        detail = (
            "ackredit.report() lists them; ackredit.summary() shows them in a notebook."
        )

    # Colour only for a terminal. Written unconditionally, the escapes land as
    # literal ^[[94m in every redirected log, batch job and CI record.
    if _is_a_terminal(sys.stderr):
        headline = f"\033[94m{headline}\033[0m"

    # stderr, so a redirected stdout carrying real output is left alone.
    print(f"\n{headline}\n   {detail}\n", file=sys.stderr)


def _is_a_terminal(stream) -> bool:
    """Whether *stream* is a terminal, for a stream that may not say."""
    try:
        return bool(stream.isatty())
    except (AttributeError, ValueError):
        # A closed stream raises ValueError; a substitute may have no isatty.
        return False


def enable_auto_reminder():
    """
    Enable a polite reminder at the end of the Python session if citations were collected.
    """
    global _REMINDER_ENABLED
    if not _REMINDER_ENABLED:
        atexit.register(_exit_reminder)
        _REMINDER_ENABLED = True


def disable_auto_reminder():
    """Undo :func:`enable_auto_reminder`, leaving the process as it was.

    Enabling was process-wide and could not be undone, so a notebook user who
    called it to try it had changed the interpreter for as long as it lived.
    Calling this without having enabled anything, or twice, does nothing.
    """
    global _REMINDER_ENABLED
    atexit.unregister(_exit_reminder)
    _REMINDER_ENABLED = False


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
            mark_import(fullname)
            return None

        # Everything below describes a distribution, not one of its modules.
        if "." in fullname:
            return None

        # The standard library ships with Python and is cited as Python, not
        # module by module. Discovery found nothing for it and said so, once
        # per module, private C extensions included, advising the user to
        # register `_decimal` by hand (`uibcdf/ackredit#70`). An injection on
        # one is still honoured above: that is a person deciding.
        if fullname in sys.stdlib_module_names or fullname.startswith("_sysconfigdata"):
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
        # Everything discovery needs, loaded before the finder can see an
        # import. `cff` imports yaml at module level, and with the finder
        # already installed that import reached the finder while `cff` was
        # still executing its own line — so the first hooked import of any
        # package raised ImportError. A lazy import inside the discovery path
        # is the whole cause, and loading them here is the whole fix. The cost
        # is paid only by a process that asked for discovery.
        from importlib import metadata  # noqa: F401

        from . import cff  # noqa: F401

        sys.meta_path.insert(0, InjectionsFinder())
        _IMPORT_HOOKS_ENABLED = True

        # A declared injection whose module is already loaded will never be
        # imported again, so the finder cannot see it. Discovery is not swept
        # the same way: an empty notebook kernel has already loaded 32
        # packages, and crediting them would build the report from what the
        # process contains rather than what the workflow used.
        mark_loaded()


def disable_import_hooks():
    """Remove the finder :func:`enable_import_hooks` installed.

    Every Ackredit finder goes, not just the first, so the process is left as it
    was however many were inserted. Imports that already happened keep whatever
    they credited; this stops the watching, it does not undo the crediting.

    Calling this without having enabled anything, or twice, does nothing.
    """
    global _IMPORT_HOOKS_ENABLED
    sys.meta_path[:] = [
        finder for finder in sys.meta_path if not isinstance(finder, InjectionsFinder)
    ]
    _IMPORT_HOOKS_ENABLED = False
