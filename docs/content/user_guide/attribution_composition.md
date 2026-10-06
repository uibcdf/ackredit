# Compose saved result attribution

Development after public 0.10.1 provides `compose_attributions` and
`AttributionBundle`. They combine independently saved results with a shared
bibliography while preserving every original result's context, uses and graph.
These names have deliberate pre-1.0 stable intent; this unpublished envelope is
separate from the already released [schema-1 promise](portable_attribution.md).

```python
from pathlib import Path
import ackredit

results = [
    ackredit.Attribution.from_json(path.read_text(encoding="utf-8"))
    for path in (Path("first.json"), Path("second.json"))
]
bundle = ackredit.compose_attributions(
    results, name="Notebook results", context={"notebook": "analysis.ipynb"}
)
Path("attribution-bundle.json").write_text(bundle.to_json(), encoding="utf-8")
print(bundle.report(format="workflow"))
```

## What composition preserves

Each input must be an `Attribution` object; read saved mappings/JSON through its
validated readers first. Iterable inputs, including generators, are accepted.
Empty input and empty members are valid. Repeated inputs and repeated names
remain separate members; their order is presentation order, not chronology,
call counts or a claim about successful science.

`bundle.attributions` returns freshly detached originals. `to_dict()` returns
a fresh envelope; `from_dict()` and `from_json()` validate the complete envelope
and every member. Original capture names, producer versions, bibliographic
metadata, uses, roles, contexts and every graph edge remain available. The
bundle's own name/context does not overwrite any member's context. Bundles are
not implicitly nested or flattened into other bundles.

Equal bibliographic records with the same ID share one reference. Different
records for one ID raise `ACKREDIT-E011` before a bundle is returned; inputs
and the current session/registry remain unchanged. Distinct software releases
need distinct IDs. DOI spelling is not normalized to guess a shared identity,
and more complete metadata never silently replaces an original record.

Development follow-up [#121](https://github.com/uibcdf/ackredit/issues/121)
separates DOI presentation from this identity rule. Supported resolver/label
wrappers are stripped for CSL export and human DOI links, while original records
remain verbatim. Two originals with the same ID but different DOI spellings still
raise `ACKREDIT-E011`, even when their CSL exports would match. Equal records
under different IDs still produce different entries. Software releases sharing
one DOI retain their original IDs and versions; neither display projection nor
style formatting silently aliases them. See the
[publication-tool contract](publication_tools.md#doi-presentation-and-duplicate-identity).

Identical target labels can belong to independent results. Their graphs remain
separate: composition cannot make a path between two original graphs, rename
their scientific targets or manufacture parent/child observations.

## Report and export

`report()` defaults to `workflow`: one numbered reference list, followed by
each original result's contextual uses and graph using those shared numbers.
`provenance` retains a separately labelled graph for each input. Bibliographic
formats (`bibtex`, `csl-json`/`csl`, `json`, `markdown`, `text`, `latex`) use the
shared bibliography sorted by ID. Reordering inputs changes presentation order
of results, not their shared reference order. A format plugin receives shared
records and caller labels, with no fabricated combined graph; its inputs remain
detached. Workflow/provenance bundle reports accept no additional options.

```bash
ackredit report attribution-bundle.json --input-format bundle --format workflow
ackredit report attribution-bundle.json --input-format bundle --format bibtex --output references.bib
```

The input mode is explicit. Individual portable records use `--input-format
attribution`, and identifier sessions retain the default `session` mode.
Existing CLI output/error rules apply: UTF-8, nonzero catalog-diagnosed failures,
validation/rendering before output is opened, and no overwriting the input.
`--format json` exports shared bibliography, not the complete bundle; preserve
`to_json()` output to retain original members and their context/graphs.

Reading, copying, composing and built-in reporting need no original scientific
producer, unit engine, current registry or DOI lookup and earn no new credit.
Composition pays its explicit validation/detachment/reporting cost only when
requested; it adds no scientific tracking operation or dependency.

## Envelope

`ackredit.attribution_bundle@1` has exactly these top-level fields:

| Field | Contract |
| --- | --- |
| `schema` | Literal `ackredit.attribution_bundle@1`. |
| `name` | Nonempty bundle name. |
| `context` | Detached JSON object describing this bundle. |
| `attributions` | Ordered list of complete original `ackredit.attribution@1` records. |

Unknown structural fields or envelope versions are refused with `ACKREDIT-E015`.
Invalid original members retain their schema-1 diagnostics; names/JSON context
also retain the existing argument validation. JSON numbers must be finite.
Structural/meaning changes require a different envelope version. An older
reader of individual schema-1 records does not thereby understand a bundle;
the original members remain individually readable by that released reader.

Source qualification, public delivery and a client's adoption remain separate.
No library gains a required dependency, new result schema or stable-contract
promotion through this additive tool.
