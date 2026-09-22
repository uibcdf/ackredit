from __future__ import annotations

import threading
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from .._private.argdigest import arg_digest
from .._private.smonitor.emitter import warn
from .._private.smonitor.exceptions import ArgumentError
from .._private.smonitor.warnings import (
    SessionLoadWarning,
    SessionMergeWarning,
    SessionSaveWarning,
)
from . import session
from .session import current_session


def _merge(state, stored, record=None) -> None:
    """Fold a read session into *state*, through the session's own writers.

    Going through `_record_item` and `_record_target` is what keeps the caller
    index and the ordered list from drifting: they have one writer, not three.

    *record* appends the merged events to an open journal, and is given
    ``(append, *arguments)`` exactly as `Collector._record` takes them. Without
    it the merge reached memory only, so a process that aggregated and then died
    lost everything it had merged, and a later run aggregating its journal
    received only what it had tracked itself.

    The writers return whether they changed anything, so merging a file twice
    appends nothing the second time.

    `enable_persistence` merges without a *record*, and must: what it reads is
    already in the file it is about to append to. That is also safe by
    construction, since the journal is not open when it merges.
    """
    for target in stored["used_targets"]:
        if state._record_target(target, None) and record:
            record(session.append_target, target, None)

    for item_id, callers in stored["used_items"].items():
        for caller in callers or [None]:
            if state._record_item(item_id, caller) and record:
                record(session.append_item, item_id, caller)

    for name, node in stored["usage_tree"].items():
        current = state.usage_tree.setdefault(name, {"items": set(), "children": set()})

        # What the loops above already recorded is in `current` by now, so these
        # differences are what only the tree carries: the parent-to-child links,
        # which no `used_targets` entry describes.
        for item_id in node["items"] - current["items"]:
            if state._record_item(item_id, name) and record:
                record(session.append_item, item_id, name)

        for child in node["children"] - current["children"]:
            if state._record_target(child, name) and record:
                record(session.append_target, child, name)


class _CollectorState(type):
    """Reads the current session's state through the names Collector always had.

    The state used to be class attributes, one set per interpreter. It belongs to
    a session now, but `Collector.used_items` is a published name and reads the
    same from outside; what changes is which session answers.
    """

    @property
    def used_targets(cls) -> set[str]:
        return current_session().used_targets

    @property
    def used_items(cls) -> Mapping[str, list[str]]:
        """Read-only, because the session indexes it.

        A list preserves the order callers appeared in and a set makes
        membership constant; `Session._record_item` writes both. Clearing or
        assigning through this view would leave the index describing entries
        that are gone, and the drift is silent — a caller already in the stale
        index is never re-added. A view turns that into an immediate error.
        Use `ackredit.current_session().clear()` to forget what was tracked.
        """
        return MappingProxyType(current_session().used_items)

    @property
    def usage_tree(cls) -> dict[str, dict[str, set[str]]]:
        return current_session().usage_tree

    @property
    def _persistence_path(cls) -> Path | None:
        return current_session().journal_path

    @property
    def _lock(cls) -> threading.RLock:
        return current_session()._lock


class Collector(metaclass=_CollectorState):
    @staticmethod
    def session():
        """The session these classmethods are acting on."""
        return current_session()

    @classmethod
    def enable_persistence(cls, path: str | Path) -> None:
        """Record every tracked event to *path*, and adopt what it already holds.

        The journal is appended to, so enabling persistence on a file another
        process is also writing is safe on a local filesystem rather than
        destructive. See `ackredit.core.session` for the guarantee and its limit.
        """
        state = current_session()
        with state._lock:
            cls.close_persistence()
            target = Path(path)

            if target.exists():
                try:
                    _merge(state, session.read(target))
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
                state._journal = session.open_journal(target)
                state.journal_path = target
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
        state = current_session()
        with state._lock:
            if state._journal is not None:
                session.close_journal(state._journal)
            state._journal = None
            state.journal_path = None

    @classmethod
    def _record(cls, state, append, *arguments) -> None:
        """Append one event, if a journal is open. Callers hold the session lock.

        A failure here must not cost the caller their tracking, which lives in
        memory regardless, so it is reported and the journal is closed rather
        than retried on every subsequent event.
        """
        if state._journal is None:
            return
        try:
            append(state._journal, *arguments)
        except OSError as error:
            path = str(state.journal_path)
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
        state = current_session()
        with state._lock:
            if state._record_target(target, parent):
                cls._record(state, session.append_target, target, parent)

    @classmethod
    def track_item(cls, item_id: str, used_by: str | None = None) -> None:
        if used_by is None:
            from .context import get_current_scope

            used_by = get_current_scope()

        state = current_session()
        with state._lock:
            if state._record_item(item_id, used_by):
                cls._record(state, session.append_item, item_id, used_by)

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

        state = current_session()
        with state._lock:
            item_ids = Registry.bound_items(target)
            for item_id in item_ids:
                cls.track_item(item_id, used_by=target)
            return item_ids

    @classmethod
    def get_used_items(cls) -> dict[str, list[str]]:
        state = current_session()
        with state._lock:
            return {item: list(callers) for item, callers in state.used_items.items()}

    @classmethod
    def get_usage_tree(cls) -> dict[str, dict[str, set[str]]]:
        return current_session().usage_tree

    @classmethod
    def aggregate(cls, paths: list[str | Path]) -> None:
        """
        Merge multiple saved session files into the current collector state.
        """
        state = current_session()
        with state._lock:
            cls._aggregate_locked(paths)

    @classmethod
    def _aggregate_locked(cls, paths: list[str | Path]) -> None:
        """Fold each session file into the current state.

        Reads both a journal and the whole-document format written before
        journals existed, so a session saved by an earlier version still merges.
        """
        state = current_session()
        for path in paths:
            path = Path(path)
            if not path.exists():
                continue
            try:
                stored = session.read(path)
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

            _merge(
                state,
                stored,
                lambda append, *arguments: cls._record(state, append, *arguments),
            )


@arg_digest()
def enable_persistence(path: str | Path) -> None:
    """Record every tracked event to *path*, and adopt what it already holds."""
    Collector.enable_persistence(path)


def close_persistence() -> None:
    """Close the session journal, paying its single fsync."""
    Collector.close_persistence()


@arg_digest()
def aggregate(paths: list[str | Path]) -> None:
    """Merge saved session files into what this run has tracked."""
    Collector.aggregate(paths)


def _a_name(value, caller: str, argument: str) -> str:
    """The check the tracking path can afford.

    `@arg_digest` costs 11.71 µs against the 1.02 µs `track_item` takes, which
    is the number `docs/content/about/performance.md` publishes and the reason
    this path is not decorated. An `isinstance` is what fits, and it covers what
    was measured: `track_item(None)` put `{None: []}` in the report.
    """
    if not isinstance(value, str) or not value.strip():
        raise ArgumentError(
            extra={
                "caller": caller,
                "argument": argument,
                "value": value,
                "reason": "is not a name",
                "expected": "A name, such as 'mylib:paper:2024'."
                if argument == "item_id"
                else "A name, such as 'mylib.basic.convert'.",
            }
        )
    return value


def track_target(target: str, parent: str | None = None) -> None:
    Collector.track_target(_a_name(target, "track_target", "target"), parent=parent)


def track_item(item_id: str, used_by: str | None = None) -> None:
    Collector.track_item(_a_name(item_id, "track_item", "item_id"), used_by=used_by)


def credit_bound(target: str) -> list[str]:
    return Collector.credit_bound(target)


def get_used_items() -> dict[str, list[str]]:
    return Collector.get_used_items()


def get_usage_tree() -> dict[str, dict[str, set[str]]]:
    return Collector.get_usage_tree()
