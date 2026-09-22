from __future__ import annotations

from functools import wraps

from .._private.argdigest import arg_digest
from .context import scope


@arg_digest()
def scoped_usage(target: str, credit_bound: bool = False):
    """
    Decorator to mark that this target (function/method) was used in the workflow.

    With ``credit_bound=True`` the items declared for *target* by
    :func:`ackredit.bind` are credited whenever the function runs. Use it when a
    function's citations do not depend on the code path taken, so the coarse case
    needs no bookkeeping inside the body::

        bind("topomt.detect", ["paper:base"])

        @scoped_usage("topomt.detect", credit_bound=True)
        def detect(mode="basic"):
            if mode == "advanced":
                track_item("paper:advanced")

    It stays off by default. Deciding what to credit per branch, with
    :func:`ackredit.track_item`, is what distinguishes Ackredit from a plain
    "function used, therefore cite everything" mapping, and enabling it silently
    would credit items a given run never needed.

    Decorating a function is exactly entering a :class:`ackredit.scope` named after
    the target, so this delegates rather than repeating that logic: the two must not
    drift, and the scope isolation belongs in one place.
    """

    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            with scope(target, credit_bound=credit_bound):
                return fn(*args, **kwargs)

        return wrapper

    return deco
