"""Detecting, from a function's source, which citations it would need.

Static analysis answers *what* a function would cite. It cannot answer *whether*
to cite it, because that depends on the function running. Ackredit's whole claim
is the second half:

    Instead of asking users to cite a whole library because they installed it,
    Ackredit records which algorithms, datasets and dependencies a run actually
    reached.

So the source is read once, when the function is wrapped, and nothing is
credited until the function is called.
"""

from __future__ import annotations

import ast
import inspect
import textwrap
from functools import wraps
from typing import Callable

from .._private.smonitor.emitter import warn
from .._private.smonitor.warnings import SourceInspectionWarning
from .context import scope


class CitationCallVisitor(ast.NodeVisitor):
    """
    AST Visitor that finds calls to functions/methods.
    """

    def __init__(self, targets: set[str]):
        self.targets = targets
        self.found: set[str] = set()

    def visit_Call(self, node: ast.Call):
        # We try to resolve the function name
        name = self._get_name(node.func)
        if name in self.targets:
            self.found.add(name)
        self.generic_visit(node)

    def _get_name(self, node: ast.AST) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            base = self._get_name(node.value)
            if base:
                return f"{base}.{node.attr}"
        return None


def inspect_function(func: Callable, targets: set[str]) -> set[str]:
    """
    Deeply inspect a function's source code to see if it calls any of the targets.
    """
    try:
        # A method, or any function nested in another scope, comes back carrying
        # the indentation of what encloses it, and ast.parse rejects that. Every
        # method was therefore invisible to detection, which is most of what a
        # scientific library has to cite.
        source = textwrap.dedent(inspect.getsource(func))
        tree = ast.parse(source)
        visitor = CitationCallVisitor(targets)
        visitor.visit(tree)
        return visitor.found
    except Exception as error:
        warn(
            SourceInspectionWarning(
                extra={
                    "function": getattr(func, "__qualname__", repr(func)),
                    "error_type": type(error).__name__,
                    "error": str(error),
                }
            )
        )
        return set()


def auto_track_calls(func: Callable, target_map: dict[str, str | list[str]]):
    """Credit the items a function's own source shows it needs, when it runs.

    The source is parsed once, here, to find which of ``target_map``'s names the
    function calls. The items for those names are credited on each call, inside a
    scope named after the function, so the provenance tree shows where they came
    from::

        def convert(item, to_form):
            mdtraj.load(item)

        convert = auto_track_calls(convert, {"mdtraj.load": "external:mdtraj"})

    Nothing is credited until ``convert`` is called. This used to record the
    credit while reading the source, so importing a module was enough to cite
    work it never did.

    **What it still cannot tell you.** Detection is per function, not per branch:
    a function that runs but takes a path that never reaches the detected call is
    credited anyway. That is the same coarseness as ``credit_bound=True`` on
    :func:`ackredit.scoped_usage`, and the same remedy applies — where the
    citations depend on the path taken, call :func:`ackredit.track_item` on the
    branch that needs them.

    If the source cannot be read, which happens for a function defined in a REPL
    or by a C extension, nothing is detected, ``ACKREDIT-W010`` reports why, and
    the function is returned unchanged.
    """
    found = inspect_function(func, set(target_map.keys()))
    if not found:
        return func

    items: list[str] = []
    for name in sorted(found):
        entry = target_map[name]
        items.extend([entry] if isinstance(entry, str) else entry)

    name = getattr(func, "__qualname__", None) or func.__name__

    @wraps(func)
    def wrapper(*args, **kwargs):
        from .collector import track_item

        with scope(name):
            for item_id in items:
                track_item(item_id, used_by=name)
            return func(*args, **kwargs)

    return wrapper
