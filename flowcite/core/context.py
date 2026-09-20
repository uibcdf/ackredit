from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional


class scope:
    """
    Context manager to mark a specific code block as a named scope.
    Usage:
        with flowcite.scope("my_algorithm"):
            flowcite.track_item("paper_id")
    """

    _current_scope: Optional[str] = None

    def __init__(self, name: str):
        self.name = name
        self._previous_scope: Optional[str] = None

    def __enter__(self):
        from .collector import track_target

        # Passing current scope as parent for the new scope
        track_target(self.name, parent=scope._current_scope)

        self._previous_scope = scope._current_scope
        scope._current_scope = self.name
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        scope._current_scope = self._previous_scope


def get_current_scope() -> Optional[str]:
    return scope._current_scope
