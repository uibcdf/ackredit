(User_Registration)=
# Registering Items

Before citations can be tracked, Ackredit needs to know about them. Items can be registered manually or loaded from existing BibTeX files.

## Manual Registration
You can register an item using {func}`ackredit.register_item`.

```python
import ackredit

ackredit.register_item(
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
import ackredit

ackredit.bind("my_library.analysis.run", ["paper:2024"])
ackredit.bound_items("my_library.analysis.run")
# -> ["paper:2024"]
```

A binding is a declaration of *potential* citations, so it credits nothing by
itself. Read declarations back with {func}`ackredit.bound_items`. See {ref}`User_Tracking` for how a run turns declarations into
actual citations, either explicitly with `track_item` or automatically with
`credit_bound=True`.

## Automatic DOI Enrichment
If you only have a DOI, Ackredit can automatically fetch the remaining metadata from **Crossref** or **DataCite**.

```python
import ackredit

# Register only with DOI
ackredit.register_item(id="paper: AF2", doi="10.1038/s41586-021-03819-2")

# Fetch metadata automatically
ackredit.enrich_all()
```
*Note: Metadata results are cached locally in `~/.cache/ackredit` to speed up future
sessions.* An answer is used for thirty days and then asked again, because a record that
said "in press" when it was cached would otherwise say so for ever. If that second request
does not come back, the answer already held is used rather than lost, so a run without a
network keeps its metadata. Deleting the directory forces everything to be asked again.

### Being a good client

Crossref and DataCite are free services shared by everyone, and they publish a rate limit
on every response. Ackredit waits between requests so that limit is respected, and adopts
whatever the service states rather than assuming.

Crossref offers a larger allowance to a client that gives a contact address — its "polite
pool", which doubles the rate. Ackredit does not do this by default, because the address
would be sent to a third party and it is yours to decide. Set it if you want it:

```bash
export ACKREDIT_CONTACT_EMAIL=you@example.org
```

The address goes into the `User-Agent` of requests Ackredit makes on your behalf, and
nowhere else. Without it, enrichment works at the smaller public-pool rate.

## Loading from BibTeX
For libraries with many references, you can load an entire `.bib` file directly.

```python
import ackredit
from pathlib import Path

bib_file = Path("my_library/citations.bib")
ackredit.load_bibtex(bib_file)
```
"
