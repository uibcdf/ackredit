from __future__ import annotations

from functools import wraps

from .collector import track_target
from .context import get_current_scope


def scoped_usage(target: str, credit_bound: bool = False):
    """
    Decorator to mark that this target (function/method) was used in the workflow.

    With ``credit_bound=True`` the items declared for *target* by
    :func:`flowcite.bind` are credited whenever the function runs. Use it when a
    function's citations do not depend on the code path taken, so the coarse case
    needs no bookkeeping inside the body::

        bind("topomt.detect", ["paper:base"])

        @scoped_usage("topomt.detect", credit_bound=True)
        def detect(mode="basic"):
            if mode == "advanced":
                track_item("paper:advanced")

    It stays off by default. Deciding what to credit per branch, with
    :func:`flowcite.track_item`, is what distinguishes FlowCite from a plain
    "function used, therefore cite everything" mapping, and enabling it silently
    would credit items a given run never needed.
    """

    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Passing current scope as parent for the target
            track_target(target, parent=get_current_scope())

            if credit_bound:
                from .collector import Collector

                Collector.credit_bound(target)

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
