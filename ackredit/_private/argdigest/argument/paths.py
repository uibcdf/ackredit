"""The `paths` argument: the session files to merge."""

from __future__ import annotations

from ...smonitor.exceptions import ArgumentError


def digest_paths(paths, caller=None):
    """the session files to merge, and never a single string.

    A string is a sequence, so `aggregate("session.json")` used to be
    iterated character by character: nothing merged, because each character is a path that does not exist and a missing file is skipped by design.
    """
    if isinstance(paths, str):
        raise ArgumentError(
            extra={
                "caller": caller or "aggregate",
                "argument": "paths",
                "value": paths,
                "reason": "is a single string, and a string is iterated by character",
                "expected": "A list of paths, such as ['run-1.json', 'run-2.json'].",
            }
        )
    if paths is None or not hasattr(paths, "__iter__"):
        raise ArgumentError(
            extra={
                "caller": caller or "aggregate",
                "argument": "paths",
                "value": paths,
                "reason": "is not a sequence",
                "expected": "A list of paths, such as ['run-1.json', 'run-2.json'].",
            }
        )
    return list(paths)
