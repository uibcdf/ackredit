# Generating Reports

Once your workflow has finished, FlowCite provides multiple ways to view and export the collected citations.

## Jupyter Notebook Summary
In a notebook, you can see a stylized HTML table with clickable links.

```python
import flowcite

flowcite.summary()
```

## Standard Formats
Use `report(format=...)` to get a string in any of these formats:
*   `markdown` (Rich markdown with links)
*   `bibtex` (Standard BibTeX file content)
*   `csl-json` (For Zotero, Mendeley, and EndNote)
*   `provenance` (Hierarchical tree showing *why* each item was cited)
*   `latex` (A complete, compilable LaTeX document)

## Consolidating Results (`dump`)
Save multiple formats at once to a directory.

```python
import flowcite

flowcite.dump("my_citations", formats=["markdown", "bibtex", "provenance", "latex"])
```

### Automatic PDF Generation
If you have `pdflatex` installed, FlowCite can compile the LaTeX report into a PDF automatically.

```python
flowcite.dump("my_citations", build_pdf=True)
```

## Collaborative Workflows (Aggregation)
If you run analysis in a parallel cluster, you can merge multiple session files into one.

```python
import flowcite

flowcite.aggregate(["node1.json", "node2.json", "node3.json"])
print(flowcite.report())
```
