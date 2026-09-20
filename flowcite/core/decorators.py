from __future__ import annotations

from functools import wraps

from .collector import track_target
from .context import get_current_scope


def scoped_usage(target: str):
    """
    Decorator to mark that this target (function/method) was used in the workflow.
    """

    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Passing current scope as parent for the target
            track_target(target, parent=get_current_scope())

            from .context import scope

            previous_scope = scope._current_scope
            scope._current_scope = target
            try:
                result = fn(*args, **kwargs)
            finally:
                scope._current_scope = previous_scope
            return result

        return wrapper

    return deco
