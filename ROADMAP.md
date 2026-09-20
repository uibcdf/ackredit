---
title: FlowCite — Workflow-Aware Citation & Acknowledgement Library
version: 0.5.0
authors: [UIBCDF Development Team]
license: MIT
---

# FlowCite — Workflow-Aware Citation & Acknowledgement Library

## 1. Project Definition

**FlowCite** is a lightweight library to be embedded in scientific Python packages (TopoMT, MolSysMT, etc.) so that users can obtain, at the end of a workflow, an accurate list of **citations, software acknowledgements, repositories, and web resources** corresponding to the functionality they actually used.

FlowCite is conceptually in the same family as **DueCredit** (automatic, usage-based citation collection) but:

- it makes the distinction between **static registration** and **dynamic tracking per code path** explicit;
- it broadens the notion of “item” (papers, repos, websites, datasets, notes);
- it aims for **notebook-friendly** reporting in addition to text/BibTeX;
- it is designed to be an **optional dependency** for the host library;
- and it plans for **interoperability** with existing DueCredit-based reporting.

---

## 2. Objectives

1. **Static registration, dynamic tracking**
   - Developers register the *potential* items for each function/class.
   - During runtime, code paths explicitly call `track_item(...)` to mark what was *actually used*.

2. **Injections (DueCredit-inspired)**
   - Allow registering items for 3rd-party libraries that are **not** FlowCite-aware.
   - Useful when a host package wants to credit its dependencies even if they don’t ship FlowCite hooks.

3. **Optional dependency model**
   - Host libraries should work even if FlowCite is not installed.
   - FlowCite should no-op gracefully in that case.

4. **Multiple output formats**
   - Markdown and plain text for notebooks/scripts.
   - BibTeX/CSL-like stubs to integrate with publication workflows.
   - JSON for programmatic post-processing.

5. **Compatibility / future interoperability with DueCredit**
   - Provide mappings or exporters so FlowCite-collected items can be rendered in a format expected by a DueCredit-based reporter.

---

## 3. Package Structure

```text
flowcite/
  __init__.py
  core/
    registry.py        # static item and binding registration
    collector.py       # runtime usage and item tracking
    decorators.py      # @scoped_usage, track_item
    report.py          # dispatch to formats
    injections.py      # register injections for external libs
    context.py
  formats/
    markdown.py
    text.py
    bibtex.py
    jsonfmt.py
  contrib/
    jupyter.py         # pretty display in notebooks
    duecredit_compat.py # future: export to duecredit-like format
tests/
docs/
```

---

## 4. Example Workflow

**1) Developer registers items and binds them**

```python
from flowcite import registry

registry.register_item(
    id="topomt:2024:concavity",
    type="article",
    title="Unified topographic analysis of macromolecular surfaces",
    authors=["Prada, D.", "et al."],
    year=2024,
    doi="10.1234/topomt.2024.001",
    note="Core method for concavity/convexity classification.",
)

registry.bind(target="topomt.features.detect_pockets", items=["topomt:2024:concavity"])
```

**2) Developer optionally defines an injection for a 3rd-party tool**

```python
from flowcite import injections

injections.register(target_module="mdtraj", items=["external:mdtraj:paper"])
```

**3) At runtime, the function decides which item applies**

```python
from flowcite import scoped_usage, track_item


@scoped_usage(target="topomt.features.detect_pockets")
def detect_pockets(surface, mode="basic"):
    track_item("topomt:2024:concavity")
    if mode == "advanced":
        track_item("topomt:2025:deep-mouths")
```

**4) User asks for report**

```python
import flowcite

print(flowcite.report(format="markdown"))
```

---

## 5. Roadmap

| Phase | Goals | Deliverables |
|:------|:------|:-------------|
| **v0.1 (done in design)** | Core concepts (registry + collector + report) | Prototype |
| **v0.2 (this doc)** | Add injections, optional dependency behavior, multi-format output | Updated core + formats |
| **v0.3** | Jupyter integration + JSON export + basic DueCredit compatibility | `contrib/` modules |
| **v0.4** | Plugin discovery for external libs | Auto-registration |
| **v1.0** | Stable API + docs + PyPI/conda-forge | CI/CD, tests |

---

## 6. Tagline

> **FlowCite** — trace what you used, cite what matters.
