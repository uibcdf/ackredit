"""Detached bibliography and contextual use, independent of session deduplication."""

from __future__ import annotations

import json
import math
import threading
from contextvars import ContextVar
from copy import deepcopy
from typing import Any, Mapping, Sequence

from .._private.smonitor.exceptions import AttributionConflictError, AttributionError

_SCHEMA = "ackredit.attribution@1"
_captures: ContextVar[tuple[capture, ...]] = ContextVar("ackredit_captures", default=())


def _invalid(operation: str, reason: str) -> None:
    raise AttributionError(extra={"operation": operation, "reason": reason})


def _json_copy(value: Any, operation: str) -> Any:
    """A JSON value, without silently stringifying keys or losing non-finite data."""

    def check(node):
        if isinstance(node, dict):
            if any(not isinstance(key, str) for key in node):
                _invalid(operation, "JSON object keys must be strings")
            for child in node.values():
                check(child)
        elif isinstance(node, (list, tuple)):
            for child in node:
                check(child)
        elif isinstance(node, float) and not math.isfinite(node):
            _invalid(operation, "JSON numbers must be finite")

    try:
        check(value)
        return json.loads(json.dumps(value, allow_nan=False))
    except (TypeError, ValueError, RecursionError) as error:
        if isinstance(error, AttributionError):
            raise
        _invalid(operation, f"not a JSON value: {error}")


def _name(value: Any, operation: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _invalid(operation, "a non-empty string is required")
    return value


def _context(value: Any, operation: str) -> dict:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        _invalid(operation, "context must be a JSON object")
    return _json_copy(dict(value), operation)


def _roles(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        _invalid("track reference roles", "roles must be a list or tuple of names")
    return sorted({_name(role, "track reference roles") for role in value})


class _Builder:
    def __init__(self):
        self.records: dict[str, dict] = {}
        self.uses: list[dict] = []
        self.seen: set[str] = set()
        self.tree: dict[str, dict[str, set[str]]] = {}

    def check_record(self, record: dict) -> None:
        previous = self.records.get(record["id"])
        if previous is not None and previous != record:
            raise AttributionConflictError(extra={"item_id": record["id"]})

    def item(
        self,
        record: dict,
        caller: str | None,
        roles: list[str],
        context: dict,
        *,
        key: str | None = None,
    ) -> None:
        if key is None:
            key = json.dumps(
                dict(
                    item_id=record["id"], used_by=caller, roles=roles, context=context
                ),
                sort_keys=True,
            )
        # Every writer's bibliography has already been checked by the observer.
        # Deduplicate only this builder: a new capture still needs its own use.
        if key in self.seen:
            return
        if record["id"] not in self.records:
            self.records[record["id"]] = deepcopy(record)
        self.seen.add(key)
        self.uses.append(
            deepcopy(
                dict(item_id=record["id"], used_by=caller, roles=roles, context=context)
            )
        )
        if caller is not None:
            self.target(caller, None)
            self.tree[caller]["items"].add(record["id"])

    def target(self, target: str, parent: str | None) -> None:
        if target not in self.tree:
            self.tree[target] = {"items": set(), "children": set()}
        if parent is not None:
            if parent not in self.tree:
                self.tree[parent] = {"items": set(), "children": set()}
            self.tree[parent]["children"].add(target)

    def payload(self, name: str, context: dict) -> dict:
        return dict(
            schema=_SCHEMA,
            name=name,
            context=deepcopy(context),
            items=deepcopy(list(self.records.values())),
            uses=deepcopy(self.uses),
            usage_tree={
                target: {key: sorted(values) for key, values in node.items()}
                for target, node in self.tree.items()
            },
        )


class Attribution:
    """A detached, versioned bibliography and its contextual uses.

    Read with :meth:`from_dict` or :meth:`from_json`, write with :meth:`to_dict`
    or :meth:`to_json`, and render with :meth:`report`. These operations never
    register records, credit calculations, load scientific backends or enrich DOIs.
    Original producer versions belong in capture/use context or software records.
    """

    def __init__(self, payload: Mapping[str, Any]):
        if not isinstance(payload, Mapping):
            _invalid("read attribution", "the payload must be a JSON object")
        data = _json_copy(dict(payload), "read attribution")
        required = {"schema", "name", "context", "items", "uses", "usage_tree"}
        if set(data) != required or data["schema"] != _SCHEMA:
            _invalid("read attribution", f"expected the complete {_SCHEMA} payload")
        _name(data["name"], "read attribution name")
        if not isinstance(data["context"], dict):
            _invalid("read attribution", "context must be a JSON object")
        if not isinstance(data["items"], list) or not isinstance(data["uses"], list):
            _invalid("read attribution", "items and uses must be lists")
        ids = set()
        for item in data["items"]:
            if not isinstance(item, dict):
                _invalid(
                    "read attribution", "each bibliographic item must be an object"
                )
            item_id = _name(item.get("id"), "read bibliographic id")
            if item_id in ids:
                _invalid("read attribution", "bibliographic ids must be unique")
            ids.add(item_id)
        for use in data["uses"]:
            if not isinstance(use, dict) or set(use) != {
                "item_id",
                "used_by",
                "roles",
                "context",
            }:
                _invalid(
                    "read attribution",
                    "a use needs item_id, used_by, roles and context",
                )
            if _name(use["item_id"], "read attribution item id") not in ids:
                _invalid(
                    "read attribution", "each use must refer to a bibliographic item"
                )
            if use["used_by"] is not None:
                _name(use["used_by"], "read attribution caller")
            use["roles"] = _roles(use["roles"])
            if not isinstance(use["context"], dict):
                _invalid("read attribution", "use context must be a JSON object")
        tree = data["usage_tree"]
        if not isinstance(tree, dict):
            _invalid("read attribution", "usage_tree must be an object")
        for target, node in tree.items():
            _name(target, "read attribution target")
            if not isinstance(node, dict) or set(node) != {"items", "children"}:
                _invalid("read attribution", "a tree node needs items and children")
            for field in ("items", "children"):
                if not isinstance(node[field], list):
                    _invalid("read attribution", "tree links must be lists")
                for name in node[field]:
                    _name(name, "read attribution tree link")
                    if name not in (ids if field == "items" else tree):
                        _invalid(
                            "read attribution", "tree links must have a record or node"
                        )
        self._payload = data

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> Attribution:
        """Validate and detach a saved payload, without crediting its uses."""
        if not isinstance(payload, Mapping):
            _invalid("read attribution", "the payload must be a JSON object")
        return cls(payload)

    @classmethod
    def from_json(cls, content: str) -> Attribution:
        """Read the versioned JSON representation without tracking anything."""
        try:
            data = json.loads(content)
        except (TypeError, ValueError, RecursionError) as error:
            _invalid("read attribution JSON", str(error))
        return cls.from_dict(data)

    def to_dict(self) -> dict[str, Any]:
        """Return a fresh JSON-compatible copy, including original use context."""
        return deepcopy(self._payload)

    def to_json(self) -> str:
        """Serialize without filesystem or network side effects."""
        return json.dumps(self._payload, ensure_ascii=False, allow_nan=False, indent=2)

    def report(self, format: str = "markdown", **options: Any) -> str:
        """Render saved records through Ackredit's existing format registry.

        Bibliographic reports describe the cited works; :meth:`to_dict` retains
        the separate contextual roles. A provenance report uses the saved graph.
        The workflow format combines original bibliography, contextual uses and
        that graph without claiming scientific success or invocation counts.
        """
        from .report import _render_records

        _name(format, "render attribution format")
        used = {item["id"]: [] for item in self._payload["items"]}
        for use in self._payload["uses"]:
            caller = use["used_by"]
            if caller is not None and caller not in used[use["item_id"]]:
                used[use["item_id"]].append(caller)
        items = {item["id"]: deepcopy(item) for item in self._payload["items"]}
        return _render_records(
            format,
            used,
            items,
            self._payload["usage_tree"],
            options,
            attribution=self._payload,
        )


class capture:
    """Capture one calculation while contributing to the current workflow.

    Unlike a session, this does not replace the application's tracking state.
    Reused credits enter every enclosing capture in the same session, even when
    the session has deduplicated them. ``attribution`` returns a detached snapshot
    during or after the block. Exceptions propagate; credits already made remain.
    A capture instance may be entered only once. Context is a detached JSON object.
    """

    def __init__(
        self, name: str = "capture", *, context: Mapping[str, Any] | None = None
    ):
        self.name = _name(name, "start capture")
        self._context = _context(context, "start capture context")
        self._builder = _Builder()
        self._lock = threading.RLock()
        self._state = None
        self._token = None
        self._active = False
        self._entered = False

    def __enter__(self) -> capture:
        from .session import current_session

        if self._entered:
            _invalid("start capture", "a capture instance may be entered only once")
        self._entered = self._active = True
        self._state = current_session()
        self._token = _captures.set((*_captures.get(), self))
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        with self._lock:
            self._active = False
        _captures.reset(self._token)
        return False

    @property
    def attribution(self) -> Attribution:
        """A detached bibliography, retaining this calculation's own references."""
        with self._lock:
            return Attribution(self._builder.payload(self.name, self._context))


def _observe_item(
    state, item_id: str, caller: str | None, roles: Sequence[str], context
) -> None:
    """Called under the session lock before crediting; the plain path is cheap."""
    active = [run for run in _captures.get() if run._active and run._state is state]
    if (
        not active
        and roles == ()
        and context is None
        and state._attribution_builder is None
    ):
        return
    from .registry import Registry

    record = _json_copy(
        Registry.items.get(item_id, {"id": item_id, "title": item_id}),
        "capture bibliography",
    )
    if record.get("id") != item_id:
        _invalid("capture bibliography", "the record id differs from its tracked id")
    roles = _roles(roles)
    context = _context(context, "track reference context")
    if caller is not None:
        _name(caller, "track reference caller")
    _observe_prepared_item(state, record, caller, roles, context, active=active)


def _observe_prepared_item(
    state, record, caller, roles, context, *, active=None, key=None
):
    """Write a detached, validated observation under the caller's session lock.

    Only internal provider declarations can supply a precomputed key: they are
    normalized and detached at activation, never memoized from mutable inputs.
    Public tracking always normalizes its record/context before coming here.
    """
    if active is None:
        active = [run for run in _captures.get() if run._active and run._state is state]
    if state._attribution_builder is None:
        state._attribution_builder = _Builder()
    state._attribution_builder.check_record(record)
    for run in active:
        with run._lock:
            run._builder.check_record(record)
    # The normalized observation is identical for the workflow and all captures.
    # Reuse its key only for this call; mutable declarations are still validated
    # and compared on every observation, including repeated session credits.
    if key is None:
        key = json.dumps(
            dict(item_id=record["id"], used_by=caller, roles=roles, context=context),
            sort_keys=True,
        )
    state._attribution_builder.item(record, caller, roles, context, key=key)
    for run in active:
        with run._lock:
            if run._active:
                run._builder.item(record, caller, roles, context, key=key)


def _observe_target(state, target: str, parent: str | None) -> None:
    for run in _captures.get():
        with run._lock:
            if run._active and run._state is state:
                run._builder.target(target, parent)


def get_attribution() -> Attribution:
    """Snapshot the current workflow, including contextual credit when provided.

    Contextual/captured records keep the metadata observed at use. Legacy plain
    credits resolve their records when this snapshot is requested. Journals of
    identifiers remain a separate persistence contract.
    """
    from .registry import Registry
    from .session import current_session

    state = current_session()
    with state._lock:
        builder = (
            deepcopy(state._attribution_builder)
            if state._attribution_builder
            else _Builder()
        )
        for item_id, callers in state.used_items.items():
            record = builder.records.get(
                item_id, Registry.items.get(item_id, {"id": item_id, "title": item_id})
            )
            for caller in callers or [None]:
                if not any(
                    use["item_id"] == item_id and use["used_by"] == caller
                    for use in builder.uses
                ):
                    builder.item(record, caller, [], {})
        builder.tree = deepcopy(state.usage_tree)
        return Attribution(builder.payload(state.name, {}))
