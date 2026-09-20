from __future__ import annotations

from contextvars import ContextVar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from contextvars import Token
    from typing import Optional

# The current scope is per-context, not per-process. A thread, and an asyncio task,
# each start from the default, so concurrent workflows cannot overwrite each other's
# attribution or leak a scope to whatever runs next.
_current_scope: ContextVar[Optional[str]] = ContextVar(
    "ackredit_current_scope", default=None
)


class scope:
    """
    Context manager to mark a specific code block as a named scope.

    Usage::

        with ackredit.scope("my_algorithm"):
            ackredit.track_item("paper_id")

    With ``credit_bound=True`` the items declared for the scope name by
    :func:`ackredit.bind` are credited on entry, mirroring the option of
    :func:`ackredit.scoped_usage` for blocks that are not whole functions.

    Scopes nest, and are isolated per thread and per asyncio task.
    """

    def __init__(self, name: str, credit_bound: bool = False):
        self.name = name
        self.credit_bound = credit_bound
        self._token: Optional[Token] = None

    def __enter__(self):
        from .collector import Collector, track_target

        # Passing current scope as parent for the new scope
        track_target(self.name, parent=_current_scope.get())

        if self.credit_bound:
            Collector.credit_bound(self.name)

        self._token = _current_scope.set(self.name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._token is not None:
            _current_scope.reset(self._token)
            self._token = None
        return False


def get_current_scope() -> Optional[str]:
    return _current_scope.get()
