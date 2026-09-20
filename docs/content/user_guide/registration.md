# Registering Items

Before citations can be tracked, FlowCite needs to know about them. Items can be registered manually or loaded from existing BibTeX files.

## Manual Registration
You can register an item using the `register_item` function.

```python
import flowcite

flowcite.register_item(
    id="paper:2024",
    type="article",
    title="An Amazing Scientific Paper",
    authors=["Smith, J.", "Doe, A."],
    year=2024,
    doi="10.1234/amazing.2024",
    journal="Nature Methods",
)
```

## Binding Items to Code

Registering an item says it exists. **Binding** says which code entity may require it:

```python
import flowcite

flowcite.bind("my_library.analysis.run", ["paper:2024"])
flowcite.bound_items("my_library.analysis.run")
# -> ["paper:2024"]
```

A binding is a declaration of *potential* citations, so it credits nothing by
itself. See [Tracking Usage](tracking.md) for how a run turns declarations into
actual citations, either explicitly with `track_item` or automatically with
`credit_bound=True`.

## Automatic DOI Enrichment
If you only have a DOI, FlowCite can automatically fetch the remaining metadata from **Crossref** or **DataCite**.

```python
import flowcite

# Register only with DOI
flowcite.register_item(id="paper: AF2", doi="10.1038/s41586-021-03819-2")

# Fetch metadata automatically
flowcite.enrich_all()
```
*Note: Metadata results are cached locally in `~/.cache/flowcite` to speed up future sessions.*

## Loading from BibTeX
For libraries with many references, you can load an entire `.bib` file directly.

```python
import flowcite
from pathlib import Path

bib_file = Path("my_library/citations.bib")
flowcite.load_bibtex(bib_file)
```
"
