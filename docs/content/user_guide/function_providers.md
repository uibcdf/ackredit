# Third-party function citation providers

This is a **provisional development capability**, owned by Ackredit #84 with
cross-component review in MolSysSuite #97. Public Ackredit 0.9.0 does not contain
`observe_calls`. Review with real producers and receivers is required before
the declaration protocol or observation API becomes stable. Existing portable
schema `ackredit.attribution@1` and released APIs retain their contracts.

## Declare citations without depending on Ackredit

A library can export an ordinary `__ackredit__` dictionary, possibly imported
from its own `_citations.py`. Declaration is offline and credits nothing. The
library requires no Ackredit dependency, decorator or import:

```python
__ackredit__ = {
    "schema": "ackredit.provider@1",
    "software": {"name": "Example", "version": "2.4.0"},
    "items": [
        {
            "id": "example:software:2.4.0",
            "type": "software",
            "title": "Example",
            "version": "2.4.0",
        },
        {
            "id": "example:paper",
            "type": "article",
            "title": "The method",
            "authors": ["Ruiz, Ana"],
            "year": 2025,
            "doi": "10.1234/example",
        },
    ],
    "functions": {
        "normalize": [
            {"item_id": "example:software:2.4.0", "roles": ["executed_software"]},
            {"item_id": "example:paper", "roles": ["software_description"]},
        ],
    },
}


def normalize(values):
    total = sum(values)
    return [value / total for value in values]
```

All schema fields are required. `software` contains exactly `name` and `version`,
both non-empty strings describing the **original producer**. `items` is a list
of JSON-compatible bibliographic objects with unique non-empty `id` strings.
Keep distinct software releases under distinct identifiers. `functions` maps
direct export names to non-empty lists of uses. Each use has exactly `item_id`
and `roles`, a list of non-empty role names; every used item is declared locally.
No DOI lookup, citation guessing or journal-specific rewrite occurs at runtime.

An individual function can instead carry `function.__ackredit__ = {"uses": [...]}`.
The references still resolve through the module's bibliography, and
`functions` may be empty. A library's own dependency-free decorator can attach
that attribute and **return the original function unchanged**. If both the
module and function declare the same export, their uses must agree. Roles such
as `executed_software`, `software_description`, `scientific_criterion` and
`reference_implementation` describe the use rather than modifying the article.

## Observe actual entries into selected functions

```python
import ackredit
import example

with ackredit.session("analysis"), ackredit.scope("pipeline"):
    with ackredit.observe_calls(example):
        with ackredit.capture("normalization") as result:
            values = example.normalize([1, 3])
    bibliography = result.attribution.report(format="bibtex")
    saved = result.attribution.to_json()
```

Importing or declaring the provider gives no credit. Only entry into the
selected function records its declared references. A branch that does not call
it records nothing. Independent captures each receive references reused from
earlier calls; the workflow retains their union. Each use identifies the
qualified export, software and original version, and the saved graph records
the enclosing pipeline scope. Detached readers render those saved records
without the producer installed or the current dependency versions substituted.

Sync functions preserve their return values and exceptions. Coroutine functions
record on **awaited execution**, not on creating a coroutine. Nested exports
retain their parent-child call scopes across `await`. Entry establishes that a
function was invoked, not that the scientific computation succeeded; references
already observed survive an exception. A host owns the interpretation of
partial or failed scientific results.

Pass ordinary imported module objects; custom module subclasses, including
lazy modules with special attribute handling, are refused in this first
implementation rather than patched with unverified restoration semantics.

## Cost and boundaries

Inactive producers are the original functions: no producer-side Ackredit code
or wrapper runs. Activation temporarily replaces selected module attributes.
Observation is enabled only in the activating context and its descendants;
unrelated threads/tasks can call the temporary wrapper without recording.
Nested/concurrent observers share a wrapper, and the last observer restores the
original export. An inherited observer stops recording when its owner exits.
There is no universal profiler, import sweep, background task or network access.

Activation validates and privately detaches declarations once, preparing
contextual reference keys. Actual calls still check registered bibliographic
contents and write through the same session, capture and journal machinery.
Prepared declarations are not mutable-identity caches; a later independent
capture still records reused references and conflicting captured identities
still receive diagnostics.

Use qualified calls such as `example.normalize(...)` **inside** the observation
block. Aliases obtained before activation keep the original callable and are
not observed. A wrapper retained after exit delegates without attribution.
This mechanism does not observe arbitrary native internal calls, descriptors,
class methods or subprocesses. Declared generators and async generators are
refused: recording their actual execution across yields needs a different,
reviewed lifecycle. Select a coarse scientific operation rather than wrapping
millions of inner-loop scalar calls. Timing depends on the number of citations,
captures and context size; see the [performance page](../about/performance.md).

Malformed/unknown declarations or conflicting identities raise catalog error
`ACKREDIT-E012` **before activation**, leaving exports and the registry intact.
Changes to declaration metadata during an active observation are not adopted.
If bibliography is replaced or recording otherwise fails, `ACKREDIT-W019`
reports an attribution gap and the scientific call continues; already observed
references may remain. Do not interpret that report as complete. Standard Python
warning filters still apply, including an explicitly selected error policy.
An export rebound by another actor is preserved on exit and diagnosed with
the same warning; Ackredit never overwrites that replacement to restore its own.

`enable_import_hooks` and `auto_track_calls` keep their separate, coarse
contracts. Combining them with this context can add package-level or static
credits; use the function observer alone when testing call-level precision.
