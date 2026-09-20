# FlowCite Integration Guide

This guide explains how to integrate **FlowCite** into a host library (e.g., `molsysmt`) following the **MolSysSuite** standards.

## 1. Centralization File: `_flowcite.py`

Every host library should have a `_flowcite.py` file in its main package directory to centralize FlowCite's configuration and handle it as an optional dependency.

Since version 0.3.0, FlowCite supports **Auto-Discovery** and **Import Hooks**. We recommend enabling these in your centralization file if you want to automatically track third-party dependencies.

### Template for `_flowcite.py`:

```python
try:
    from flowcite import registry, scoped_usage, track_item, report

    FLOWCITE_INSTALLED = True
except ImportError:
    FLOWCITE_INSTALLED = False

    # No-op shims
    def registry_register_item(*args, **kwargs):
        pass

    def registry_bind(*args, **kwargs):
        pass

    def scoped_usage(target=None):
        def deco(fn):
            return fn

        return deco

    def track_item(*args, **kwargs):
        pass

    def report(*args, **kwargs):
        return "FlowCite not installed."


# Exporting clean names for the host library
if FLOWCITE_INSTALLED:
    register_item = registry.register_item
    bind = registry.bind
else:
    register_item = registry_register_item
    bind = registry_bind
```

## 2. Static Registration

In your host library's `__init__.py` or a dedicated setup file, register your items and bindings using the centralized `_flowcite.py`:

```python
from ._flowcite import register_item, bind

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
from .._flowcite import scoped_usage, track_item


@scoped_usage(target="molsysmt.basic.convert")
def convert(item, to_form):
    track_item("molsysmt:paper:2024")
    # implementation...
```

## 4. Reporting

Expose a reporting function for the end user:

```python
from ._flowcite import report


def cite(format="markdown"):
    return report(format=format)
```

## 5. Advanced Features (since 0.3.0)

### Auto-Discovery of Dependencies
If your library uses external packages (like `numpy` or `mdtraj`) and you want FlowCite to track them automatically, add this to your initialization:
```python
if FLOWCITE_INSTALLED:
    flowcite.enable_import_hooks()
```

### Session Persistence
For long-running scientific workflows, you can ensure no citation is lost even if the script crashes:
```python
if FLOWCITE_INSTALLED:
    flowcite.enable_persistence("flowcite_session.json")
```

By following this pattern, the host library remains functional even if FlowCite is not installed, while providing full citation support for users who have it.
