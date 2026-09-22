"""The `target_module` argument: the import name of a package whose use should be credited."""

from __future__ import annotations

from ...smonitor.exceptions import ArgumentError


def digest_target_module(target_module, caller=None):
    """the import name of a package whose use should be credited. It is matched against what is imported, so it has to be the import name."""
    if (
        target_module is None
        or not isinstance(target_module, str)
        or not target_module.strip()
    ):
        raise ArgumentError(
            extra={
                "caller": caller or "add_injection",
                "argument": "target_module",
                "value": target_module,
                "reason": "is not a name",
                "expected": "An import name such as 'numpy'.",
            }
        )
    return target_module
