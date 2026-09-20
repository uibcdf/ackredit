---
title: Ackredit Developer Guide
version: 0.5.0
authors: [UIBCDF Development Team]
license: MIT
---

# Ackredit Developer Guide

## 1. Introduction

Ackredit helps you make your scientific library “self-citing”: every time users call specific functions or instantiate specific classes, Ackredit can record **what they should cite** — and it will only report the items that were **actually used** in that run.

This guide shows how to:
1. register citation items (static),
2. track actual usage (dynamic, including conditionals),
3. add injections for non-instrumented dependencies,
4. and generate reports in multiple formats.

---

## 2. Static Registration (what *could* be cited)

```python
from ackredit import registry

registry.register_item(
    id="topomt:2024:base-paper",
    type="article",
    title="TopoMT: a toolkit for macromolecular topography",
    authors=["Prada, D."],
    year=2024,
    note="Main description of the TopoMT approach.",
)

registry.register_item(
    id="topomt:github:repo",
    type="repo",
    title="TopoMT GitHub repository",
    url="https://github.com/uibcdf/topomt",
)

registry.bind(
    target="topomt.mouths.detect_mouths",
    items=["topomt:2024:base-paper", "topomt:github:repo"],
)
```

This says: “if someone uses `topomt.mouths.detect_mouths`, these are the items they might need to cite.”

Bindings are declarations, not credits. Read them back with `bound_items`:

```python
from ackredit import bound_items

bound_items("topomt.mouths.detect_mouths")
# -> ["topomt:2024:base-paper", "topomt:github:repo"]
```

---

## 3. Dynamic Tracking (what *was* cited)

Inside the function, decide which items apply:

```python
from ackredit import scoped_usage, track_item


@scoped_usage(target="topomt.mouths.detect_mouths")
def detect_mouths(surface, mode="basic"):
    # always cite the base paper
    track_item("topomt:2024:base-paper", used_by="topomt.mouths.detect_mouths")

    # only cite the advanced paper when the advanced branch is used
    if mode == "advanced":
        track_item("topomt:2025:advanced-mouths", used_by="topomt.mouths.detect_mouths")
```

This pattern (static + dynamic) goes beyond the typical “function → citations” mapping.

### When the citations are not conditional

If every run of a function needs the same items, repeating them inside the body is
noise. Pass `credit_bound=True` and the bound items are credited whenever the
function runs:

```python
from ackredit import bind, scoped_usage, track_item

bind(target="topomt.mouths.detect_mouths", items=["topomt:2024:base-paper"])


@scoped_usage(target="topomt.mouths.detect_mouths", credit_bound=True)
def detect_mouths(surface, mode="basic"):
    # the base paper is credited automatically
    if mode == "advanced":
        track_item("topomt:2025:advanced-mouths")
```

It is off by default on purpose: crediting bound items silently would report
citations a given run never needed, which is exactly what Ackredit exists to avoid.
The `scope` context manager takes the same option.

---

## 4. Injections for non-Ackredit libraries

If your library uses an external package that does **not** use Ackredit, you can still credit it:

```python
from ackredit import injections

# say your library uses mdtraj internally
injections.register(target_module="mdtraj", items=["external:mdtraj:paper"])
```

Ackredit can then mark that if `mdtraj` was imported or used, the corresponding item should appear in the final report — similar to DueCredit injections. citeturn0search1

---

## 5. Reporting in multiple formats

```python
import ackredit

# Markdown (notebooks, README-like)
print(ackredit.report(format="markdown"))

# Plain text (logs, CLI)
print(ackredit.report(format="text"))

# BibTeX (papers)
print(ackredit.report(format="bibtex"))

# JSON (further processing)
print(ackredit.report(format="json"))
```

You can also add your own renderer under `ackredit/formats/yourformat.py` and register it.

---

## 6. Optional dependency pattern

In your scientific library you can do:

```python
try:
    from ackredit import scoped_usage, track_item
except ImportError:
    # define no-ops so library works without ackredit
    def scoped_usage(target=None):
        def deco(fn):
            return fn

        return deco

    def track_item(*args, **kwargs):
        pass
```

This mirrors how DueCredit is often used — the host library does not break if the citation tool is absent. citeturn0search9

---

## 7. Future: DueCredit compatibility

To help users who already have workflows built around `duecredit`, Ackredit can provide:

- an exporter that returns Ackredit data shaped like DueCredit’s summary;
- or a small contrib module that, if `duecredit` is installed, calls its API to add Ackredit-collected items.

This keeps Ackredit independent but interoperable.

---

## 8. Minimal Working Example

```python
from ackredit import registry, scoped_usage, track_item

# 1) register items
registry.register_item(
    id="example:2024:paper", type="article", title="Example research article"
)
registry.bind(target="example.run", items=["example:2024:paper"])


# 2) runtime tracking
@scoped_usage(target="example.run")
def run(method="a"):
    track_item("example:2024:paper", used_by="example.run")
    if method == "b":
        track_item("example:2024:paper-b", used_by="example.run")
    print("Running analysis...")


# 3) run workflow
run()

# 4) report
import ackredit

print(ackredit.report(format="markdown"))
```

---

> **Ackredit** — inspired by DueCredit, extended for conditional, branch-aware scientific workflows.
