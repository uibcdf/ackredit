"""The `target` argument: a named unit of code, such as a qualified function name."""

from __future__ import annotations

from ...smonitor.exceptions import ArgumentError


def digest_target(target, caller=None):
    """a named unit of code, such as a qualified function name. It is what a citation is attributed to, so an empty one attributes nothing."""
    if target is None or not isinstance(target, str) or not target.strip():
        raise ArgumentError(
            extra={
                "caller": caller or "bind",
                "argument": "target",
                "value": target,
                "reason": "is not a name",
                "expected": "A name such as 'molsysmt.basic.convert'.",
            }
        )
    return target
