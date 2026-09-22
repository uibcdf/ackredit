"""The `items` argument: the citation ids a target may require."""

from __future__ import annotations

from ...smonitor.exceptions import ArgumentError


def digest_items(items, caller=None):
    """the citation ids a target may require, and never a single string.

    A string is a sequence, so `bind("mylib.convert", "paper:2024")` used to be
    iterated character by character: eight citations were bound, one per character.
    """
    if isinstance(items, str):
        raise ArgumentError(
            extra={
                "caller": caller or "bind",
                "argument": "items",
                "value": items,
                "reason": "is a single string, and a string is iterated by character",
                "expected": "A list of item ids, such as ['mylib:paper:2024'].",
            }
        )
    if items is None or not hasattr(items, "__iter__"):
        raise ArgumentError(
            extra={
                "caller": caller or "bind",
                "argument": "items",
                "value": items,
                "reason": "is not a sequence",
                "expected": "A list of item ids, such as ['mylib:paper:2024'].",
            }
        )
    return list(items)
