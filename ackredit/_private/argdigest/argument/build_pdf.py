"""The `build_pdf` argument: whether to run a TeX engine after writing."""

from __future__ import annotations

from ...smonitor.exceptions import ArgumentError


def digest_build_pdf(build_pdf, caller=None):
    """A decision, not a value that happens to be truthy.

    `dump(path, build_pdf="no")` is true, which is the opposite of what it says.
    """
    if not isinstance(build_pdf, bool):
        raise ArgumentError(
            extra={
                "caller": caller or "dump",
                "argument": "build_pdf",
                "value": build_pdf,
                "reason": "is not True or False",
                "expected": "True or False.",
            }
        )
    return build_pdf
