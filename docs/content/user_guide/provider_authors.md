# Publish a dependency-free citation provider

Expose bibliographic metadata alongside your library's ordinary functions.
The library keeps working without Ackredit; the caller chooses whether to
observe it. `ackredit.provider@1` and `observe_calls` have a stable bounded
contract in public Ackredit **>=0.11.0**. The
[full protocol](function_providers.md) specifies validation and lifecycle limits.

## Start from the installable example

The maintained [Citation Example package](https://github.com/uibcdf/ackredit/tree/main/examples/citation_provider)
has no runtime dependencies. From a repository checkout:

```bash
python -m pip install ./examples/citation_provider
python -c 'import citation_provider; print(citation_provider.normalize([1, 3]))'
```

This produces `[0.25, 0.75]` with Ackredit absent. Copy the package structure
into your own project and replace its fictional references, DOI, software name
and version. Keep Ackredit optional and install it separately in your author
validation or client environment using the [supported route](../about/installation.md).

## Declare references for each direct export

Add a module-level `__ackredit__` dictionary, optionally imported from your
library's own citation module. It requires no Ackredit import or decorator:

```python
__ackredit__ = {
    "schema": "ackredit.provider@1",
    "software": {"name": "My Library", "version": "2.4.0"},
    "items": [
        {
            "id": "my-library:software:2.4.0",
            "type": "software",
            "title": "My Library",
            "version": "2.4.0",
        },
        {"id": "my-library:method", "type": "article", "title": "My method"},
    ],
    "functions": {
        "normalize": [
            {"item_id": "my-library:software:2.4.0", "roles": ["executed_software"]},
            {"item_id": "my-library:method", "roles": ["software_description"]},
        ],
    },
}
```

Define `normalize` as an ordinary direct module export. Use non-empty original
software name/version strings, JSON-compatible bibliography and unique item
IDs. Give different software releases different IDs. Supply verified authors,
year, DOI and other bibliographic fields where applicable; validation checks
structure and references, not whether a paper exists or supports your method.

Each use refers to an item declared locally and has a list of role names.
The list may be empty when no role is declared; each supplied name must be a
non-empty string. An empty list does not infer a relationship.
`executed_software` describes software execution; `software_description`
describes a paper about that software. Use `scientific_criterion` or
`reference_implementation` only when that is the actual relationship. Declaring
unused references gives no credit. Static per-function uses apply on every
observed entry: branch-specific references need distinct declared functions
called by the chosen branch, or a caller-owned explicit credit decision.

Alternatively attach `normalize.__ackredit__ = {"uses": [...]}`. Keep those
references in the module's `items`; `functions` can be empty. Your own decorator
may attach metadata and return the original function unchanged. Module and
function declarations for the same export must agree. List lazy exports in
`functions`, since metadata on an unresolved function cannot be discovered.

## Validate in your author environment

With development Ackredit after public 0.11.0, use the accepted bounded source API:

```python
import ackredit
import citation_provider

declaration = ackredit.validate_provider(citation_provider)
assert declaration["schema"] == "ackredit.provider@1"
```

Pass an already imported ordinary trusted module. The returned declaration is
detached and includes module/function metadata. Invalid declarations raise
`ValueError` with catalog code `ACKREDIT-E012`; validation records no uses,
registers no bibliography, installs no wrappers and performs no DOI lookup.
Selected lazy loaders may import code or populate the producer's cache; their
side effects are not rolled back. Validation does not detect conflicts with
the caller's current bibliography registry. Public **0.11.0 lacks this API**
and validates declarations when `observe_calls` is activated.
Standalone validation was promoted under #125 on 2026-10-06; its forward public
compatibility promise starts with a separately qualified delivering release,
selected as 0.12.0 under #127 and still awaiting public qualification.
See [API stability](../about/stability.md).

## Let the client observe actual calls

```python
import ackredit
import citation_provider

with ackredit.observe_calls(citation_provider), ackredit.capture("analysis") as run:
    values = citation_provider.normalize([1, 3])
saved = run.attribution.to_json()
```

Use qualified module calls inside the block. Aliases taken before activation
retain the original callable and earn no observed credit. Coroutines earn credit
on awaited entry; declared generators, methods/descriptors and native internal
calls are outside this bounded mechanism. Entry records an invocation, even if
the computation later fails. Saved attribution keeps the original producer
version and renders without that producer installed.
