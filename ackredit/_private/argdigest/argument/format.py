"""The `format` argument: which rendering of a report is wanted."""

from __future__ import annotations

from ...smonitor.exceptions import ArgumentError


def digest_format(format, caller=None):
    """A format name.

    Only that it is a string. Which strings are names — including the empty one
    — is `report`'s to answer, because the list includes whatever a plugin
    registered and `ACKREDIT-E004` names them at the moment of the call. Two
    refusals for one condition is one too many.
    """
    if not isinstance(format, str):
        raise ArgumentError(
            extra={
                "caller": caller or "report",
                "argument": "format",
                "value": format,
                "reason": "is not a format name",
                "expected": "A name; ackredit.available_formats() lists them.",
            }
        )
    return format
