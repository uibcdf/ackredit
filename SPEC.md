---
title: Ackredit Technical Specification
version: 0.5.0
authors: [UIBCDF Development Team]
license: MIT
---

# Ackredit Technical Specification

## 1. Scope

Ackredit provides runtime-aware citation tracking for scientific workflows.
It is inspired by the goals of **DueCredit** but focuses on explicit per-branch tracking, broader item types, and notebook-friendly reporting.

---

## 2. Core Concepts

1. **Item** — a structured piece of crediting information (paper, repo, website, dataset, software).
2. **Binding** — a declaration that a code entity (function/class/module) *may* require certain items.
3. **Tracking** — a runtime event that says “this item was actually used in this run.”
4. **Injection** — a binding for a module/package that is not Ackredit-aware (DueCredit-style).

---

## 3. Data Structures

```python
from typing import TypedDict, Literal


class CitationItem(TypedDict, total=False):
    id: str
    type: Literal["article", "software", "repo", "web", "dataset", "other"]
    title: str
    authors: list[str]
    year: int
    doi: str
    url: str
    note: str
    how_to_cite: str


# registry: static info
class Registry:
    items: dict[str, CitationItem] = {}
    bindings: dict[str, list[str]] = {}  # target -> [item_id, ...]
    injections: dict[str, list[str]] = {}  # external module -> [item_id, ...]

    @classmethod
    def register_item(cls, **item): ...
    @classmethod
    def bind(cls, target: str, items: list[str]): ...
    @classmethod
    def bound_items(cls, target: str) -> list[str]: ...
    @classmethod
    def add_injection(cls, target_module: str, items: list[str]): ...
```

`bind` declares what a target *may* require; `bound_items` reads those declarations
back. Bindings are never credited on their own — see section 5.

---

## 4. Collector

```python
class Collector:
    used_targets: set[str] = set()
    used_items: dict[str, list[str]] = {}  # item_id -> [used_by targets]

    @classmethod
    def track_target(cls, target: str):
        cls.used_targets.add(target)

    @classmethod
    def track_item(cls, item_id: str, used_by: str | None = None):
        cls.used_items.setdefault(item_id, [])
        if used_by and used_by not in cls.used_items[item_id]:
            cls.used_items[item_id].append(used_by)
```

Collector may also, on import of an injected module, mark the corresponding items.

---

## 5. Decorators (Runtime Layer)

```python
from .core import Collector
from .core import Registry


def scoped_usage(target: str, credit_bound: bool = False):
    """Mark that this target was used in this workflow."""

    def deco(fn):
        def wrapper(*args, **kwargs):
            Collector.track_target(target)
            if credit_bound:
                Collector.credit_bound(target)
            return fn(*args, **kwargs)

        return wrapper

    return deco


def track_item(item_id: str, used_by: str | None = None):
    """Mark that this specific item must be credited in this run."""
    Collector.track_item(item_id, used_by=used_by)
```

Developers can call `track_item(...)` inside conditional branches — this is the key difference vs a pure “function used → all citations” approach.

`credit_bound` is the opt-in bridge back to the coarse mapping: when a target's
citations do not depend on the code path taken, `bind` alone carries them and the
function body needs no bookkeeping. It is off by default, because enabling it
silently would credit items a given run never needed and erase the distinction
above. The same option exists on the `scope` context manager, and
`Collector.credit_bound(target)` applies it directly.

---

## 6. Reporting

```python
def report(format: str = "markdown") -> str:
    # gather used items
    used = Collector.used_items
    # fetch item definitions
    from .core import Registry

    items = Registry.items
    if format == "markdown":
        from .formats.markdown import render

        return render(used, items)
    elif format == "bibtex":
        from .formats.bibtex import render

        return render(used, items)
    elif format == "json":
        from .formats.jsonfmt import render

        return render(used, items)
    else:
        from .formats.text import render

        return render(used, items)
```

---

## 7. Optional Dependency Behavior

- If `ackredit` is **not installed**, host libraries should wrap imports in `try/except ImportError` and define no-op shims for `scoped_usage` and `track_item`.
- If `ackredit` **is installed**, the decorated functions will actually record usage.
- This mirrors the optional pattern used by DueCredit.

---

## 8. DueCredit Interoperability (Future)

- Provide an exporter:

```python
def export_duecredit_json():
    """Return Ackredit-collected items in a structure compatible with duecredit summary."""
    ...
```

- Or provide a compatibility layer in `contrib/duecredit_compat.py` that, if `duecredit` is installed, forwards Ackredit’s collected items into DueCredit’s reporting engine.

---

## 9. Security / Performance

- All tracking is in-memory and per-process.
- No external calls are required.
- Registry can be imported at package init time.
- The current scope is held in a `ContextVar`, so scopes are isolated per thread and
  per asyncio task. Concurrent workflows cannot cross-attribute citations, and a scope
  cannot leak to whatever runs next in the same worker.
- The collector guards its compound updates with a reentrant lock, and writes the
  session file atomically, so a reader or a crash never observes a partial document.

---

> Ackredit is inspired by DueCredit but optimized for conditional, branch-based scientific workflows.
