"""The `file_path` argument: the `.bib` file to read."""

from __future__ import annotations

import os
from pathlib import Path

from ...smonitor.exceptions import ArgumentError


def digest_file_path(file_path, caller=None):
    """A place on disk, returned as a `Path`. Whether it exists is the caller's
    to report, with the code that says what was expected there."""
    if not isinstance(file_path, (str, os.PathLike)) or not str(file_path).strip():
        raise ArgumentError(
            extra={
                "caller": caller or "load_bibtex",
                "argument": "file_path",
                "value": file_path,
                "reason": "is not a path",
                "expected": "A path, as a string or a pathlib.Path.",
            }
        )
    return Path(file_path)
