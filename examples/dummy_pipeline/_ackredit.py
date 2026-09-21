# This file is the template from standards/ACKREDIT_GUIDE.md, copied verbatim.
# tests/test_example_libraries.py asserts it is byte-identical to the guide, so
# the guide is not a snippet checked in isolation: it is a file two working
# libraries here actually use.

"""Ackredit integration for this library.

Ackredit is an optional dependency. This module must import cleanly and expose the
same names whether or not it is installed.
"""

try:
    import ackredit
    from ackredit import (
        add_injection,
        bind,
        bound_items,
        credit_bound,
        register_item,
        report,
        scope,
        scoped_usage,
        track_item,
    )

    ACKREDIT_INSTALLED = True

except ImportError:
    ACKREDIT_INSTALLED = False
    ackredit = None

    def register_item(**item):
        pass

    def bind(target, items):
        pass

    def bound_items(target):
        return []

    def add_injection(target_module, items):
        pass

    def credit_bound(target):
        return []

    def track_item(item_id, used_by=None):
        pass

    def scoped_usage(target, credit_bound=False):
        def deco(fn):
            return fn

        return deco

    class scope:
        def __init__(self, name, credit_bound=False):
            self.name = name

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

    def report(format="markdown", **kwargs):
        return "Ackredit is not installed."
