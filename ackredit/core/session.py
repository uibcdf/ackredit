"""The on-disk form of a tracking session.

A session used to be a document rewritten in full on every tracked item, which
made a run cost O(n squared): one thousand items took three seconds and wrote
23 MiB to produce a 48 KiB file, in the mode advertised for HPC clusters.

It is a journal now. Each event is one line, appended. Appending is constant
whatever the session already holds, and what a reader wants — the state — is the
journal folded back.

Durability. Each line is written and flushed, so it has left this process before
the call returns and survives the interpreter dying, which is the guarantee
`standards/ACKREDIT_GUIDE.md` makes. `fsync` is called when the session closes,
not per event: it costs about 950 microseconds and protects only against the
machine failing, which is not a promise Ackredit makes.

Concurrency. POSIX makes an `O_APPEND` write below `PIPE_BUF` atomic, and these
lines are far below it, so several processes may write one journal without
losing or interleaving events. Measured with eight processes and 4000 events:
no loss, no corrupt line. That guarantee is a local-filesystem one; NFS does not
provide it, so a network filesystem still wants one journal per process, which
`aggregate` merges.

Reading one that is still being written is a different matter: the file can grow
between the stat and the read, so the last line may arrive partially. Nothing
before it ever does, and a closed journal has no partial line at all. `read`
skips an unparseable line rather than refusing the journal, which covers this
and covers the torn tail an interrupted run leaves.
"""

from __future__ import annotations

import json
import os
import threading
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, Optional

SCHEMA = "ackredit.session@1"

# Event kinds. Short keys because every tracked item writes one line.
ITEM = "i"
TARGET = "t"


def open_journal(path: Path) -> int:
    """Open *path* for appending, creating it and its directory if needed.

    The schema line is written when the file is empty. Several processes opening
    a new journal at the same moment may each see it empty and each write one,
    which is harmless: a reader identifies the format from the first line and
    folds only lines carrying an event. Serialising this would need a lock
    across processes, which is a high price for a cosmetic duplicate.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    if os.fstat(descriptor).st_size == 0:
        _write_line(descriptor, {"schema": SCHEMA})
    return descriptor


def append_item(descriptor: int, item_id: str, used_by: str | None) -> None:
    event: Dict[str, Any] = {"e": ITEM, "i": item_id}
    if used_by is not None:
        event["b"] = used_by
    _write_line(descriptor, event)


def append_target(descriptor: int, target: str, parent: str | None) -> None:
    event: Dict[str, Any] = {"e": TARGET, "t": target}
    if parent is not None:
        event["p"] = parent
    _write_line(descriptor, event)


def close_journal(descriptor: int) -> None:
    """Flush to the device, then close. This is where fsync is paid, once."""
    try:
        os.fsync(descriptor)
    except OSError:
        # A journal on a filesystem that cannot sync is still written; the
        # events left this process when they were appended.
        pass
    os.close(descriptor)


def _write_line(descriptor: int, event: Dict[str, Any]) -> None:
    # One write call per line, so the append stays atomic.
    os.write(descriptor, (json.dumps(event, separators=(",", ":")) + "\n").encode())


def read(path: Path) -> Dict[str, Any]:
    """Fold a session file back into state.

    Reads a journal, and also the whole-document format written before this
    existed, so a session saved by an earlier version still loads.
    """
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return _empty()

    if SCHEMA not in text.split("\n", 1)[0]:
        return _from_document(json.loads(text))

    return _fold(text.splitlines())


def _empty() -> Dict[str, Any]:
    return {"used_targets": set(), "used_items": {}, "usage_tree": {}}


def _node() -> Dict[str, set]:
    return {"items": set(), "children": set()}


def _fold(lines: Iterable[str]) -> Dict[str, Any]:
    state = _empty()
    used_targets = state["used_targets"]
    used_items = state["used_items"]
    tree = state["usage_tree"]

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except ValueError:
            # A torn last line is what an interrupted run leaves behind. Every
            # complete event before it is still good, so the journal is read up
            # to the damage rather than discarded because of it.
            continue

        kind = event.get("e")
        if kind == ITEM:
            item_id = event["i"]
            callers = used_items.setdefault(item_id, [])
            used_by = event.get("b")
            if used_by is not None:
                if used_by not in callers:
                    callers.append(used_by)
                tree.setdefault(used_by, _node())["items"].add(item_id)
        elif kind == TARGET:
            target = event["t"]
            used_targets.add(target)
            tree.setdefault(target, _node())
            parent = event.get("p")
            if parent is not None:
                tree.setdefault(parent, _node())["children"].add(target)

    return state


def _from_document(data: Dict[str, Any]) -> Dict[str, Any]:
    """The pre-journal format: one document holding the whole state."""
    return {
        "used_targets": set(data.get("used_targets", [])),
        "used_items": {
            item: list(callers) for item, callers in data.get("used_items", {}).items()
        },
        "usage_tree": {
            target: {
                "items": set(content.get("items", [])),
                "children": set(content.get("children", [])),
            }
            for target, content in data.get("usage_tree", {}).items()
        },
    }


class Session:
    """What one run tracked, and where it is being journalled.

    Declarations live in `ackredit.core.registry.Registry` and are shared: a host
    library registers what it *could* cite once, at import. Observations live
    here and are per run: what was actually reached.

    **What this promises**, to a caller holding one from ``ackredit.session()``
    or :func:`ackredit.current_session`:

    - ``used_items``, item id to the names that credited it, in the order they
      appeared;
    - ``used_targets``, the targets that ran;
    - ``usage_tree``, which target led to which item and to which other target;
    - ``journal_path``, the file being written, or ``None``; read only, since
      `ackredit.enable_persistence` is what opens one;
    - ``name``, and ``clear()``, which forgets what was tracked and keeps the
      journal open.

    Everything else is machinery and is named with a leading underscore: the
    writers carry the rule that a caller holds the lock, and promising them
    would promise that rule too.
    """

    def __init__(self, name: str = "default"):
        self.name = name
        self.used_targets: set[str] = set()
        self.used_items: Dict[str, list[str]] = {}
        self.usage_tree: Dict[str, Dict[str, set]] = {}

        # An index over the lists in used_items. The list preserves the order
        # callers appeared in, which reports show; membership on it is linear,
        # and an item credited from many call sites made recording O(n squared).
        # `_record_item` is the only writer of both, so they cannot drift.
        self._callers: Dict[str, set] = {}

        self.journal_path: Optional[Path] = None
        self._journal: Optional[int] = None

        # Guards compound read-modify-write on the structures above. Reentrant
        # because credit_bound() tracks items while already holding it.
        self._lock = threading.RLock()

    def clear(self) -> None:
        """Forget what was tracked, keeping any journal open."""
        with self._lock:
            self.used_targets.clear()
            self.used_items.clear()
            self.usage_tree.clear()
            self._callers.clear()

    def _record_item(self, item_id: str, used_by: str | None) -> bool:
        """Credit *item_id*, optionally to *used_by*. Callers hold the lock.

        Returns whether this changed anything, so the journal records state
        changes rather than calls: crediting the same pair in a loop writes one
        line, not one per iteration.
        """
        changed = item_id not in self.used_items
        callers = self.used_items.setdefault(item_id, [])
        seen = self._callers.setdefault(item_id, set())

        if used_by is not None:
            if used_by not in seen:
                seen.add(used_by)
                callers.append(used_by)
                changed = True
            node = self.usage_tree.setdefault(
                used_by, {"items": set(), "children": set()}
            )
            node["items"].add(item_id)

        return changed

    def _record_target(self, target: str, parent: str | None) -> bool:
        """Record that *target* ran. Callers hold the lock."""
        changed = target not in self.used_targets
        self.used_targets.add(target)
        self.usage_tree.setdefault(target, {"items": set(), "children": set()})
        if parent:
            node = self.usage_tree.setdefault(
                parent, {"items": set(), "children": set()}
            )
            if target not in node["children"]:
                node["children"].add(target)
                changed = True
        return changed

    def __repr__(self) -> str:  # pragma: no cover - diagnostics only
        return (
            f"<ackredit.Session {self.name!r}: "
            f"{len(self.used_items)} items, {len(self.used_targets)} targets>"
        )


# The session the module-level functions act on. A ContextVar rather than a
# plain global, so a thread or an asyncio task that enters a session does not
# change what any other one sees — the same mechanism `scope` uses, and for the
# same reason.
_DEFAULT = Session("default")
_current: ContextVar[Session] = ContextVar("ackredit_session", default=_DEFAULT)


def current_session() -> Session:
    """The session the tracking functions are recording into."""
    return _current.get()


@contextmanager
def session(name: str = "session", inherit: bool = False) -> Iterator[Session]:
    """Track into a fresh session for the duration of the block.

    ``ackredit.report()`` inside the block describes only what happened inside
    it; outside, the enclosing session is untouched::

        with ackredit.session() as run:
            analyse(dataset)
            print(run_report := ackredit.report())

    With ``inherit=True`` the new session starts from a copy of what the
    enclosing one has tracked, for reporting on "everything so far plus this".

    Entering a session is context-local, so a thread or task that does not enter
    it keeps recording where it was.
    """
    fresh = Session(name)
    if inherit:
        enclosing = _current.get()
        with enclosing._lock:
            fresh.used_targets = set(enclosing.used_targets)
            fresh.used_items = {
                item: list(callers) for item, callers in enclosing.used_items.items()
            }
            fresh._callers = {
                item: set(callers) for item, callers in enclosing._callers.items()
            }
            fresh.usage_tree = {
                target: {
                    "items": set(node["items"]),
                    "children": set(node["children"]),
                }
                for target, node in enclosing.usage_tree.items()
            }

    token = _current.set(fresh)
    try:
        yield fresh
    finally:
        _current.reset(token)
        if fresh._journal is not None:
            close_journal(fresh._journal)
            fresh._journal = None
