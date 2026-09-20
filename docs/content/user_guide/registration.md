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
