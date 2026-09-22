"""The `path` argument: where a report or a session journal is written."""

from __future__ import annotations

import os
from pathlib import Path

from ...smonitor.exceptions import ArgumentError


def digest_path(path, caller=None):
    """A place on disk, returned as a `Path`.

    `enable_persistence(None)` and `dump(None)` used to raise a bare `TypeError`
    from inside `pathlib`, naming `__fspath__` rather than the argument.
    """
    if not isinstance(path, (str, os.PathLike)) or not str(path).strip():
        raise ArgumentError(
            extra={
                "caller": caller or "dump",
                "argument": "path",
                "value": path,
                "reason": "is not a path",
                "expected": "A path, as a string or a pathlib.Path.",
            }
        )
    return Path(path)
