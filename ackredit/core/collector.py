from __future__ import annotations

import json
import os
import tempfile
import threading
from pathlib import Path

from .._private.smonitor.emitter import warn, warn_once
from .._private.smonitor.warnings import (
    SessionLoadWarning,
    SessionMergeWarning,
    SessionSaveWarning,
    SessionSharedWarning,
)


class Collector:
    # set of target names actually used
    used_targets: set[str] = set()
    # item_id -> list of targets that caused it
    used_items: dict[str, list[str]] = {}

    # Hierarchical tracking: target -> { 'items': set(), 'children': set() }
    usage_tree: dict[str, dict[str, set[str]]] = {}

    # Persistence
    _persistence_path: Path | None = None

    # Stat of this process's own last write. Every save replaces the whole
    # document, so if the file changed underneath us another writer is racing us
    # and one of the two sets of citations is being discarded. Comparing a stat
    # costs one syscall and reads nothing.
    _persistence_stamp: tuple[int, int] | None = None

    # Guards every compound read-modify-write on the structures above, and
    # serializes writes to the session file. Reentrant because credit_bound()
    # calls track_item() while already holding it.
    _lock = threading.RLock()

    @classmethod
    def enable_persistence(cls, path: str | Path) -> None:
        with cls._lock:
            cls._persistence_path = Path(path)
            cls._persistence_stamp = None
            # Load existing if present
            if not cls._persistence_path.exists():
                return
            try:
                data = json.loads(cls._persistence_path.read_text())
                cls.used_targets.update(data.get("used_targets", []))
                cls.used_items.update(data.get("used_items", {}))
                # Conversion back to sets for usage_tree
                for target, content in data.get("usage_tree", {}).items():
                    cls.usage_tree[target] = {
                        "items": set(content.get("items", [])),
                        "children": set(content.get("children", [])),
                    }
            except Exception as error:
                warn(
                    SessionLoadWarning(
                        extra={
                            "path": str(cls._persistence_path),
                            "error_type": type(error).__name__,
                            "error": str(error),
                        }
                    )
                )

    @classmethod
    def _save_state(cls) -> None:
        """Write the session file atomically, so a reader or a crash never sees
        a half-written document. Callers already hold the lock."""
        if not cls._persistence_path:
            return

        # Convert sets to lists for JSON
        tree_serializable = {}
        for target, content in cls.usage_tree.items():
            tree_serializable[target] = {
                "items": list(content["items"]),
                "children": list(content["children"]),
            }

        data = {
            "used_targets": list(cls.used_targets),
            "used_items": cls.used_items,
            "usage_tree": tree_serializable,
        }

        path = cls._persistence_path
        cls._warn_if_another_writer(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(
            dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp"
        )
        try:
            with os.fdopen(descriptor, "w") as handle:
                json.dump(data, handle, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
            cls._persistence_stamp = cls._stamp(path)
        except Exception as error:
            Path(temporary).unlink(missing_ok=True)
            warn(
                SessionSaveWarning(
                    extra={
                        "path": str(path),
                        "error_type": type(error).__name__,
                        "error": str(error),
                    }
                )
            )

    @staticmethod
    def _stamp(path: Path) -> tuple[int, int] | None:
        try:
            status = path.stat()
        except OSError:
            return None
        return (status.st_mtime_ns, status.st_size)

    @classmethod
    def _warn_if_another_writer(cls, path: Path) -> None:
        """Report a session file that someone else is also replacing.

        Each write replaces the whole document, so two processes sharing a path
        do not merge: the last one wins and the other's citations disappear,
        leaving a file that is perfectly valid and quietly incomplete.
        """
        if cls._persistence_stamp is None:
            return
        if cls._stamp(path) == cls._persistence_stamp:
            return
        warn_once(SessionSharedWarning(extra={"path": str(path)}))

    @classmethod
    def track_target(cls, target: str, parent: str | None = None) -> None:
        with cls._lock:
            cls.used_targets.add(target)
            cls.usage_tree.setdefault(target, {"items": set(), "children": set()})
            if parent:
                cls.usage_tree.setdefault(parent, {"items": set(), "children": set()})
                cls.usage_tree[parent]["children"].add(target)
            cls._save_state()

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
            cls._save_state()

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
        for path in paths:
            path = Path(path)
            if not path.exists():
                continue
            try:
                data = json.loads(path.read_text())
                cls.used_targets.update(data.get("used_targets", []))

                # Merge used_items
                new_items = data.get("used_items", {})
                for item_id, callers in new_items.items():
                    cls.used_items.setdefault(item_id, [])
                    for c in callers:
                        if c not in cls.used_items[item_id]:
                            cls.used_items[item_id].append(c)

                # Merge usage_tree
                new_tree = data.get("usage_tree", {})
                for target, content in new_tree.items():
                    cls.usage_tree.setdefault(
                        target, {"items": set(), "children": set()}
                    )
                    cls.usage_tree[target]["items"].update(content.get("items", []))
                    cls.usage_tree[target]["children"].update(
                        content.get("children", [])
                    )
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
        cls._save_state()


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
