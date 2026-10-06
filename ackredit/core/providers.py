"""Opt-in observation of dependency-free, explicitly selected function exports."""

from __future__ import annotations

import inspect
import json
import threading
from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
from functools import wraps
from types import ModuleType

from smonitor import signal

from .._private.smonitor.emitter import warn
from .._private.smonitor.exceptions import ProviderDeclarationError
from .._private.smonitor.warnings import ProviderObservationWarning
from .attribution import (
    _json_copy,
    _note_provider_evidence,
    _provider_evidence_receivers,
)
from .collector import _track_prepared_item
from .context import scope
from .registry import Registry

_lock = threading.RLock()
_patches = {}
_observers: ContextVar[tuple] = ContextVar("ackredit_call_observers", default=())
_SCHEMA = "ackredit.provider@1"


def _selected_targets():
    """Selected exports in this context, including an already active observer."""
    return sorted(
        {
            binding.target
            for run in _observers.get()
            if run._active
            for binding in run._bindings
        }
    )


def _refuse(module, reason):
    raise ProviderDeclarationError(extra={"provider": module, "reason": reason})


def _name(value, module, field):
    if not isinstance(value, str) or not value.strip():
        _refuse(module, f"{field} must be a non-empty string")
    return value


def _function_uses(function, module, export):
    metadata = getattr(function, "__ackredit__", None)
    if metadata is None:
        return None
    try:
        metadata = _json_copy(metadata, "read function provider")
    except ValueError as error:
        _refuse(module, str(error))
    if not isinstance(metadata, dict) or set(metadata) != {"uses"}:
        _refuse(module, f"{export} metadata needs only uses")
    return metadata["uses"]


def _read(module):
    """Detach and validate every declaration before changing any module export."""
    if type(module) is not ModuleType:
        _refuse(
            type(module).__name__, "pass an already imported ordinary module object"
        )
    name = module.__name__
    try:
        data = _json_copy(vars(module).get("__ackredit__"), "read provider")
    except ValueError as error:
        _refuse(name, str(error))
    if (
        not isinstance(data, dict)
        or set(data) != {"schema", "software", "items", "functions"}
        or data["schema"] != _SCHEMA
    ):
        _refuse(name, f"expected a complete {_SCHEMA} declaration")
    software = data["software"]
    if not isinstance(software, dict) or set(software) != {"name", "version"}:
        _refuse(name, "software needs name and original version")
    context = {
        "software": _name(software["name"], name, "software name"),
        "version": _name(software["version"], name, "software version"),
    }
    records = {}
    if not isinstance(data["items"], list):
        _refuse(name, "items must be a list of bibliographic objects")
    for record in data["items"]:
        if not isinstance(record, dict):
            _refuse(name, "each item must be a bibliographic object")
        item_id = _name(record.get("id"), name, "item id")
        if item_id in records:
            _refuse(name, f"duplicate item id {item_id!r}")
        records[item_id] = record
    declarations = data["functions"]
    if not isinstance(declarations, dict):
        _refuse(name, "functions must map direct export names to reference uses")
    declarations = dict(declarations)
    for export, function in vars(module).copy().items():
        if not (inspect.isfunction(function) or inspect.isbuiltin(function)):
            continue
        uses = _function_uses(function, name, export)
        if uses is not None:
            if export in declarations and declarations[export] != uses:
                _refuse(name, f"conflicting declarations for {export}")
            declarations[export] = uses
    plans = []
    for export, uses in declarations.items():
        _name(export, name, "function export")
        if not isinstance(uses, list) or not uses:
            _refuse(name, f"{export} needs a non-empty reference use list")
        normalized = []
        for use in uses:
            if not isinstance(use, dict) or set(use) != {"item_id", "roles"}:
                _refuse(name, f"{export} uses need item_id and roles")
            item_id = _name(use["item_id"], name, "used item id")
            if item_id not in records:
                _refuse(name, f"{export} refers to undeclared {item_id!r}")
            if not isinstance(use["roles"], list):
                _refuse(name, f"{export} roles must be a list")
            roles = sorted({_name(role, name, "role") for role in use["roles"]})
            normalized.append((item_id, roles))
        if export in vars(module):
            function = vars(module)[export]
        else:
            # A selected ordinary module may expose PEP 562 lazy exports. Resolve
            # only its explicit declarations, never discover names through dir().
            try:
                function = getattr(module, export)
            except Exception as error:
                _refuse(
                    name, f"cannot resolve {export}: {type(error).__name__}: {error}"
                )
        if not (inspect.isfunction(function) or inspect.isbuiltin(function)):
            _refuse(name, f"{export} is not a direct function export")
        metadata_uses = _function_uses(function, name, export)
        if metadata_uses is not None and metadata_uses != uses:
            _refuse(name, f"conflicting declarations for {export}")
        if inspect.isgeneratorfunction(function) or inspect.isasyncgenfunction(
            function
        ):
            _refuse(name, f"{export} yields; generator observation is unsupported")
        plans.append((module, export, function, normalized, context, records))
    data["functions"] = declarations
    return plans, records, data


@signal(tags=["ackredit", "provider", "validation"])
def validate_provider(module: ModuleType) -> dict:
    """Validate one imported provider without activating observation.

    Return a detached ``ackredit.provider@1`` declaration containing original
    software identity, all local items and merged module/function uses. Role
    order and duplicates are retained so function metadata continues to agree.
    Invalid declarations raise catalog error ``ACKREDIT-E012`` (a ValueError).

    This provisional API neither records uses, registers bibliography, patches
    exports nor checks conflicts with the current registry. Explicit lazy
    exports may invoke the producer's loader; unrelated exports are not swept.
    Pass a trusted ordinary module object, not an import name or subclass.
    """
    with _lock:
        _, _, declaration = _read(module)
    return declaration


class _Patch:
    def __init__(self, module, export, original, uses, context, records, *, registered):
        self.module = module
        self.export = export
        self.original = original
        self.uses = uses
        self.context = context
        self.records = records
        self._registered = {item_id: registered[item_id] for item_id, _ in uses}
        self.target = f"{module.__name__}.{export}"
        self._evidence_source = f"{module.__name__}.__ackredit__.items"
        self.leases = 0
        self._credits = [
            (
                records[item_id],
                roles,
                json.dumps(
                    dict(
                        item_id=item_id,
                        used_by=self.target,
                        roles=roles,
                        context=context,
                    ),
                    sort_keys=True,
                ),
            )
            for item_id, roles in uses
        ]

        if inspect.iscoroutinefunction(original):

            @wraps(original)
            async def wrapped(*args, **kwargs):
                if not self.enabled():
                    return await original(*args, **kwargs)
                with self.entry():
                    return await original(*args, **kwargs)
        else:

            @wraps(original)
            def wrapped(*args, **kwargs):
                if not self.enabled():
                    return original(*args, **kwargs)
                with self.entry():
                    return original(*args, **kwargs)

        self.wrapped = wrapped

    def enabled(self):
        return any(run._active and self in run._bindings for run in _observers.get())

    @contextmanager
    def entry(self):
        active_scope = scope(self.target)
        receivers = _provider_evidence_receivers()
        try:
            # Never attach a replacement bibliography to the original producer
            # version. Check all references before recording any of this call.
            for item_id, _ in self.uses:
                if Registry.items.get(item_id) != self._registered[item_id]:
                    _refuse(self.module.__name__, f"reference {item_id!r} was replaced")
            active_scope.__enter__()
            for record, roles, key in self._credits:
                _track_prepared_item(record, self.target, roles, self.context, key)
                if receivers:
                    _note_provider_evidence(
                        receivers,
                        self.target,
                        record=record,
                        source=self._evidence_source,
                    )
        except Exception as error:
            active_scope.__exit__(None, None, None)
            diagnostic = ProviderObservationWarning(
                extra={
                    "target": self.target,
                    "operation": "record call",
                    "error_type": type(error).__name__,
                    "error": str(error),
                }
            )
            if receivers:
                _note_provider_evidence(receivers, self.target, diagnostic=diagnostic)
            warn(diagnostic)
            # Scientific exceptions are outside the diagnostic catch. A failed
            # observation must never be mistaken for a scientific call failure.
            yield
        else:
            try:
                yield
            finally:
                active_scope.__exit__(None, None, None)


class observe_calls:
    """Observe declared exports of already imported modules.

    ``with observe_calls(module): module.function(...)`` records references only
    when a declared function is entered (or its coroutine is awaited). Producers
    declare offline ``__ackredit__`` metadata without depending on Ackredit.
    Observation is context-local, nests, and restores original exports on exit.
    Aliases taken before activation and generator functions are not supported.
    Each instance can be entered once. See the third-party provider guide for
    the schema, failure diagnostics and boundaries; this is not a global profiler.
    """

    def __init__(self, *modules):
        self._modules = modules
        self._bindings = set()
        self._active = False
        self._entered = False
        self._token = None

    def __enter__(self):
        if self._entered or not self._modules:
            _refuse("observer", "provide modules and enter each observer only once")
        plans = []
        records = {}
        unique = []
        for module in self._modules:
            if type(module) is not ModuleType:
                _refuse(
                    type(module).__name__,
                    "pass an already imported ordinary module object",
                )
            if module not in unique:
                unique.append(module)
        with _lock:
            # Read exports and manage leases under the same lock: concurrent
            # activation/exit must not capture an already expired wrapper.
            for module in unique:
                selected, declared, _ = _read(module)
                plans.extend(selected)
                for item_id, record in declared.items():
                    if item_id in records and records[item_id] != record:
                        _refuse(module.__name__, f"conflicting reference {item_id!r}")
                    records[item_id] = record
            registered = {}
            for item_id, record in records.items():
                if item_id in Registry.items:
                    current = Registry.items[item_id]
                    try:
                        portable = _json_copy(
                            current, "read registered provider reference"
                        )
                    except ValueError as error:
                        _refuse("observer", str(error))
                    if portable != record:
                        _refuse(
                            "observer", f"conflicting registered reference {item_id!r}"
                        )
                    # Accepted registrations retain their original representation.
                    # Actual calls compare this detached raw snapshot, without JSON.
                    registered[item_id] = deepcopy(current)
                else:
                    registered[item_id] = deepcopy(record)
            bindings = []
            for plan in plans:
                module, export, function, uses, context, declared = plan
                existing = _patches.get((module, export))
                if existing is not None:
                    if function is not existing.wrapped or (
                        uses,
                        context,
                        declared,
                    ) != (existing.uses, existing.context, existing.records):
                        _refuse(
                            module.__name__, f"active declaration changed for {export}"
                        )
                    bindings.append(existing)
                else:
                    bindings.append(_Patch(*plan, registered=registered))
            # All declarations and conflicts pass before the first mutation.
            Registry.items.update(
                deepcopy(
                    {
                        item_id: record
                        for item_id, record in records.items()
                        if item_id not in Registry.items
                    }
                )
            )
            self._bindings = set(bindings)
            for binding in self._bindings:
                binding.leases += 1
                _patches[(binding.module, binding.export)] = binding
                setattr(binding.module, binding.export, binding.wrapped)
            self._entered = self._active = True
            self._token = _observers.set((*_observers.get(), self))
        receivers = _provider_evidence_receivers()
        if receivers:
            for binding in sorted(self._bindings, key=lambda binding: binding.target):
                _note_provider_evidence(receivers, binding.target)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        changed = []
        with _lock:
            self._active = False
            _observers.reset(self._token)
            for binding in self._bindings:
                binding.leases -= 1
                if binding.leases == 0:
                    del _patches[(binding.module, binding.export)]
                    if vars(binding.module).get(binding.export) is binding.wrapped:
                        setattr(binding.module, binding.export, binding.original)
                    else:
                        changed.append(binding)
        for binding in changed:
            diagnostic = ProviderObservationWarning(
                extra={
                    "target": binding.target,
                    "operation": "restore export",
                    "error_type": "ExportRebound",
                    "error": "the export changed during observation; its replacement is preserved",
                }
            )
            _note_provider_evidence(
                _provider_evidence_receivers(), binding.target, diagnostic=diagnostic
            )
            warn(diagnostic)
        return False
