from __future__ import annotations

import threading
from pathlib import Path

from .._private.smonitor.emitter import warn
from .._private.smonitor.warnings import (
    SessionLoadWarning,
    SessionMergeWarning,
    SessionSaveWarning,
)
from . import session


class Collector:
    # set of target names actually used
    used_targets: set[str] = set()
    # item_id -> list of targets that caused it
    used_items: dict[str, list[str]] = {}

    # Hierarchical tracking: target -> { 'items': set(), 'children': set() }
    usage_tree: dict[str, dict[str, set[str]]] = {}

    # Persistence. The session is a journal: one appended line per event, so the
    # cost of tracking one more item does not depend on how many came before.
    _persistence_path: Path | None = None
    _journal: int | None = None

    # Guards every compound read-modify-write on the structures above, and
    # serializes writes to the session file. Reentrant because credit_bound()
    # calls track_item() while already holding it.
    _lock = threading.RLock()

    @classmethod
    def enable_persistence(cls, path: str | Path) -> None:
        """Record every tracked event to *path*, and adopt what it already holds.

        The journal is appended to, so enabling persistence on a file another
        process is also writing is safe on a local filesystem rather than
        destructive. See `ackredit.core.session` for the guarantee and its limit.
        """
        with cls._lock:
            cls.close_persistence()
            target = Path(path)

            if target.exists():
                try:
                    state = session.read(target)
                    cls.used_targets.update(state["used_targets"])
                    for item, callers in state["used_items"].items():
                        known = cls.used_items.setdefault(item, [])
                        known.extend(c for c in callers if c not in known)
                    for name, node in state["usage_tree"].items():
                        current = cls.usage_tree.setdefault(
                            name, {"items": set(), "children": set()}
                        )
                        current["items"].update(node["items"])
                        current["children"].update(node["children"])
                except Exception as error:
                    warn(
                        SessionLoadWarning(
                            extra={
                                "path": str(target),
                                "error_type": type(error).__name__,
                                "error": str(error),
                            }
                        )
                    )

            try:
                cls._journal = session.open_journal(target)
                cls._persistence_path = target
            except OSError as error:
                warn(
                    SessionSaveWarning(
                        extra={
                            "path": str(target),
                            "error_type": type(error).__name__,
                            "error": str(error),
                        }
                    )
                )

    @classmethod
    def close_persistence(cls) -> None:
        """Close the journal, paying the single fsync that makes it durable
        against the machine failing rather than only the process."""
        with cls._lock:
            if cls._journal is not None:
                session.close_journal(cls._journal)
            cls._journal = None
            cls._persistence_path = None

    @classmethod
    def _record(cls, append, *arguments) -> None:
        """Append one event, if a journal is open. Callers already hold the lock.

        A failure here must not cost the caller their tracking, which lives in
        memory regardless, so it is reported and the journal is closed rather
        than retried on every subsequent event.
        """
        if cls._journal is None:
            return
        try:
            append(cls._journal, *arguments)
        except OSError as error:
            path = str(cls._persistence_path)
            cls.close_persistence()
            warn(
                SessionSaveWarning(
                    extra={
                        "path": path,
                        "error_type": type(error).__name__,
                        "error": str(error),
                    }
                )
            )

    @classmethod
    def track_target(cls, target: str, parent: str | None = None) -> None:
        with cls._lock:
            cls.used_targets.add(target)
            cls.usage_tree.setdefault(target, {"items": set(), "children": set()})
            if parent:
                cls.usage_tree.setdefault(parent, {"items": set(), "children": set()})
                cls.usage_tree[parent]["children"].add(target)
            cls._record(session.append_target, target, parent)

    @classmethod
    def track_item(cls, item_id: str, used_by: str | None = None) -> None:
        if used_by is None:
            from .context import get_current_scope

            used_by = get_current_scope()

        with cls._lock:
            cls.used_items.setdefault(item_id, [])
            if used_by is not None:
                if used_by not in cls.used_items[item_id]:
                    cls.used_items[item_id].append(used_by)

                # Update usage tree
                cls.usage_tree.setdefault(used_by, {"items": set(), "children": set()})
                cls.usage_tree[used_by]["items"].add(item_id)
            cls._record(session.append_item, item_id, used_by)

    @classmethod
    def credit_bound(cls, target: str) -> list[str]:
        """
        Credit every item bound to *target*, as if each had been tracked by it.

        This is the opt-in bridge between static registration and runtime
        tracking: :func:`ackredit.bind` declares what a target *may* require, and
        this records that those items were in fact used. It is never applied
        automatically, because deciding per code path is what separates Ackredit
        from a plain "function used, therefore cite everything" mapping.

        Returns the item ids that were credited.
        """
        from .registry import Registry

        with cls._lock:
            item_ids = Registry.bound_items(target)
            for item_id in item_ids:
                cls.track_item(item_id, used_by=target)
            return item_ids

    @classmethod
    def get_used_items(cls) -> dict[str, list[str]]:
        with cls._lock:
            return {item: list(callers) for item, callers in cls.used_items.items()}

    @classmethod
    def get_usage_tree(cls) -> dict[str, dict[str, set[str]]]:
        return cls.usage_tree

    @classmethod
    def aggregate(cls, paths: list[str | Path]) -> None:
        """
        Merge multiple saved session files into the current collector state.
        """
        with cls._lock:
            cls._aggregate_locked(paths)

    @classmethod
    def _aggregate_locked(cls, paths: list[str | Path]) -> None:
        """Fold each session file into the current state.

        Reads both a journal and the whole-document format written before
        journals existed, so a session saved by an earlier version still merges.
        """
        for path in paths:
            path = Path(path)
            if not path.exists():
                continue
            try:
                state = session.read(path)
            except Exception as error:
                warn(
                    SessionMergeWarning(
                        extra={
                            "path": str(path),
                            "reason": f"{type(error).__name__}: {error}",
                        }
                    )
                )
                continue

            cls.used_targets.update(state["used_targets"])
            for item_id, callers in state["used_items"].items():
                known = cls.used_items.setdefault(item_id, [])
                known.extend(caller for caller in callers if caller not in known)
            for name, node in state["usage_tree"].items():
                current = cls.usage_tree.setdefault(
                    name, {"items": set(), "children": set()}
                )
                current["items"].update(node["items"])
                current["children"].update(node["children"])


def close_persistence() -> None:
    """Close the session journal, paying its single fsync."""
    Collector.close_persistence()


def track_target(target: str, parent: str | None = None) -> None:
    Collector.track_target(target, parent=parent)


def track_item(item_id: str, used_by: str | None = None) -> None:
    Collector.track_item(item_id, used_by=used_by)


def credit_bound(target: str) -> list[str]:
    return Collector.credit_bound(target)


def get_used_items() -> dict[str, list[str]]:
    return Collector.get_used_items()


def get_usage_tree() -> dict[str, dict[str, set[str]]]:
    return Collector.get_usage_tree()
