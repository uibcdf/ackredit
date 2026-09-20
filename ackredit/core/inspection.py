from __future__ import annotations

import ast
import inspect
from typing import Callable

from .._private.smonitor.emitter import warn
from .._private.smonitor.warnings import SourceInspectionWarning


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
        source = inspect.getsource(func)
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
    """
    Decorator that inspects the decorated function and automatically tracks
    citations if certain external calls are detected in its source.
    """
    found = inspect_function(func, set(target_map.keys()))

    # This is a bit of a hybrid: we track if we FIND the call in the source.
    # Note: This is static analysis at definition time!
    for f in found:
        from .collector import track_item

        items = target_map[f]
        if isinstance(items, str):
            items = [items]
        for item_id in items:
            track_item(item_id, used_by=func.__name__)

    return func
