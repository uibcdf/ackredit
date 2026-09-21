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
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable

SCHEMA = "ackredit.session@1"

# Event kinds. Short keys because every tracked item writes one line.
ITEM = "i"
TARGET = "t"


def open_journal(path: Path) -> int:
    """Open *path* for appending, creating it and its directory if needed."""
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
