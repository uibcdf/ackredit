"""The `directory` argument: the directory holding the LaTeX to compile."""

from __future__ import annotations

import os
from pathlib import Path

from ...smonitor.exceptions import ArgumentError


def digest_directory(directory, caller=None):
    """A place on disk, returned as a `Path`. Whether it exists is the caller's
    to report, with the code that says what was expected there."""
    if not isinstance(directory, (str, os.PathLike)) or not str(directory).strip():
        raise ArgumentError(
            extra={
                "caller": caller or "compile_pdf",
                "argument": "directory",
                "value": directory,
                "reason": "is not a path",
                "expected": "A path, as a string or a pathlib.Path.",
            }
        )
    return Path(directory)
