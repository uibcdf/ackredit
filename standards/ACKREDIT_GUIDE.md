# Ackredit Integration Guide

This guide explains how to integrate **Ackredit** into a host library (e.g., `molsysmt`) following the **MolSysSuite** standards.

## 1. Centralization File: `_ackredit.py`

Every host library should have a `_ackredit.py` file in its main package directory to centralize Ackredit's configuration and handle it as an optional dependency.

The single rule this file exists to enforce: **the host keeps working when Ackredit is absent**. Every name it exports must therefore have a fallback with the *same signature* as the real one, or the host will break precisely in the case the pattern was meant to protect.

### Template for `_ackredit.py`:

```python
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
```

Note what the fallbacks return: `bound_items` and `credit_bound` return an empty list, not `None`, so host code that iterates their result behaves identically in both modes. `scope` is a class, because it is used as a context manager.

## 2. Static Registration

In your host library's `__init__.py` or a dedicated setup file, register your items and bindings using the centralized `_ackredit.py`:

```python
from ._ackredit import bind, register_item

register_item(
    id="molsysmt:paper:2024",
    type="article",
    title="MolSysMT: A modern library for molecular systems analysis",
    authors=["Diego", "et al."],
    year=2024,
)

bind(target="molsysmt.basic.convert", items=["molsysmt:paper:2024"])
```

## 3. Dynamic Tracking

Use the decorators and tracking functions in your modules:

```python
from .._ackredit import scoped_usage, track_item


@scoped_usage(target="molsysmt.basic.convert")
def convert(item, to_form):
    track_item("molsysmt:paper:2024")
    # implementation...
```

`bind` declares what a target *may* require; it credits nothing on its own. When a function's citations do not depend on the code path taken, let the binding carry them instead of repeating the ids in the body:

```python
from .._ackredit import scoped_usage, track_item


@scoped_usage(target="molsysmt.basic.convert", credit_bound=True)
def convert(item, to_form, method="default"):
    # the bound items are credited on every call
    if method == "experimental":
        track_item("molsysmt:paper:2026:experimental")
```

## 4. Reporting

Expose a reporting function for the end user:

```python
from ._ackredit import report


def cite(format="markdown"):
    return report(format=format)
```

## 5. Advanced Features

These call the module directly, which is why the template imports `ackredit` as well as the individual names. Guard them with `ACKREDIT_INSTALLED`, because the fallback binds `ackredit` to `None`.

### Auto-Discovery of Dependencies

If your library uses external packages (like `numpy` or `mdtraj`) and you want Ackredit to track them automatically, add this to your initialization:

```python
from ._ackredit import ACKREDIT_INSTALLED, ackredit

if ACKREDIT_INSTALLED:
    ackredit.enable_import_hooks()
```

### Session Persistence

For long-running scientific workflows, you can ensure no citation is lost even if the script crashes:

```python
from ._ackredit import ACKREDIT_INSTALLED, ackredit

if ACKREDIT_INSTALLED:
    ackredit.enable_persistence("ackredit_session.json")
```

## 6. Check that the integration is live

The `try`/`except ImportError` above is deliberately silent, so a host with Ackredit installed but mis-integrated looks exactly like a host without it: everything succeeds and nothing is ever recorded.

Do not let that state pass unnoticed. Expose the flag, and assert it where it matters:

```python
from ._ackredit import ACKREDIT_INSTALLED


# in the host's test suite, when ackredit is a test dependency
def test_ackredit_integration_is_active():
    assert ACKREDIT_INSTALLED
```

If `ACKREDIT_INSTALLED` is `False` while `pip show ackredit` succeeds, the import in `_ackredit.py` is raising `ImportError` for some other reason and being swallowed. Reproduce it by importing the names outside the `try` block.

By following this pattern, the host library remains functional even if Ackredit is not installed, while providing full citation support for users who have it.
