---
title: FlowCite Developer Guide
version: 0.5.0
authors: [UIBCDF Development Team]
license: MIT
---

# FlowCite Developer Guide

## 1. Introduction

FlowCite helps you make your scientific library “self-citing”: every time users call specific functions or instantiate specific classes, FlowCite can record **what they should cite** — and it will only report the items that were **actually used** in that run.

This guide shows how to:
1. register citation items (static),
2. track actual usage (dynamic, including conditionals),
3. add injections for non-instrumented dependencies,
4. and generate reports in multiple formats.

---

## 2. Static Registration (what *could* be cited)

```python
from flowcite import registry

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

---

## 3. Dynamic Tracking (what *was* cited)

Inside the function, decide which items apply:

```python
from flowcite import scoped_usage, track_item


@scoped_usage(target="topomt.mouths.detect_mouths")
def detect_mouths(surface, mode="basic"):
    # always cite the base paper
    track_item("topomt:2024:base-paper", used_by="topomt.mouths.detect_mouths")

    # only cite the advanced paper when the advanced branch is used
    if mode == "advanced":
        track_item("topomt:2025:advanced-mouths", used_by="topomt.mouths.detect_mouths")
```

This pattern (static + dynamic) comes from your requirement and goes beyond the typical “function → citations” mapping.

---

## 4. Injections for non-FlowCite libraries

If your library uses an external package that does **not** use FlowCite, you can still credit it:

```python
from flowcite import injections

# say your library uses mdtraj internally
injections.register(target_module="mdtraj", items=["external:mdtraj:paper"])
```

FlowCite can then mark that if `mdtraj` was imported or used, the corresponding item should appear in the final report — similar to DueCredit injections. citeturn0search1

---

## 5. Reporting in multiple formats

```python
import flowcite

# Markdown (notebooks, README-like)
print(flowcite.report(format="markdown"))

# Plain text (logs, CLI)
print(flowcite.report(format="text"))

# BibTeX (papers)
print(flowcite.report(format="bibtex"))

# JSON (further processing)
print(flowcite.report(format="json"))
```

You can also add your own renderer under `flowcite/formats/yourformat.py` and register it.

---

## 6. Optional dependency pattern

In your scientific library you can do:

```python
try:
    from flowcite import scoped_usage, track_item
except ImportError:
    # define no-ops so library works without flowcite
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

To help users who already have workflows built around `duecredit`, FlowCite can provide:

- an exporter that returns FlowCite data shaped like DueCredit’s summary;
- or a small contrib module that, if `duecredit` is installed, calls its API to add FlowCite-collected items.

This keeps FlowCite independent but interoperable.

---

## 8. Minimal Working Example

```python
from flowcite import registry, scoped_usage, track_item

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
import flowcite

print(flowcite.report(format="markdown"))
```

---

> **FlowCite** — inspired by DueCredit, extended for conditional, branch-aware scientific workflows.
