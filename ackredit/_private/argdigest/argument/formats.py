"""The `formats` argument: the report formats to write."""

from __future__ import annotations

from ...smonitor.exceptions import ArgumentError


def digest_formats(formats, caller=None):
    """the report formats to write, and never a single string.

    A string is a sequence, so `dump("reports", formats="bibtex")` used to be
    iterated character by character: six formats were asked for, one per character.
    """
    # `dump(path)` leaves it unset, which means the default list. The guide puts
    # that kind of optionality in the digester rather than in a bypass.
    if formats is None:
        return None

    if isinstance(formats, str):
        raise ArgumentError(
            extra={
                "caller": caller or "dump",
                "argument": "formats",
                "value": formats,
                "reason": "is a single string, and a string is iterated by character",
                "expected": "A list of format names; ackredit.available_formats() lists them.",
            }
        )
    if formats is None or not hasattr(formats, "__iter__"):
        raise ArgumentError(
            extra={
                "caller": caller or "dump",
                "argument": "formats",
                "value": formats,
                "reason": "is not a sequence",
                "expected": "A list of format names; ackredit.available_formats() lists them.",
            }
        )
    return list(formats)
