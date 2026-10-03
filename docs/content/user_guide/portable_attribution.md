# Portable attribution contract

The first reviewed portable contract is assigned to the **0.9.0 candidate**.
This identifies the intended first release, not an already published package.
Earlier immutable tags do not provide this API. Distribution and clean public
consumer installation are tracked separately in Ackredit #22 and #80.

Applications own `session(...)`. Within it, `capture(name="capture", *,
context=None)` observes one calculation without replacing that session. A
capture can be entered once; its `attribution` property returns an independently
owned snapshot during or after the block. Nested captures in the same session
receive child observations, including references reused in earlier results.
Exceptions propagate and already recorded credits remain. The application must
determine whether the scientific calculation succeeded; a partial capture does
not make that claim. Thread/async session and context boundaries keep their
existing semantics; work in another session is not implicitly merged.

`get_attribution()` snapshots the current workflow. `track_item` retains its
existing positional arguments and accepts keyword-only `roles=()` and
`context=None`. Roles are caller-defined, nonempty strings, deduplicated and
sorted; they are not a closed enumeration. Context is a detached JSON object.
Software versions belong in the original software record and use/producer
context. A shared article can describe several software versions without
changing its bibliography. Conflicting observed records for one identifier are
refused with `ACKREDIT-E011`; use distinct IDs for distinct software releases.

`Attribution(payload)`, `Attribution.from_dict(payload)` and
`Attribution.from_json(content)` validate and detach records. `to_dict()`
returns a new copy; `to_json()` returns JSON; `report(format="markdown",
**options)` uses the existing format registry. Reading, copying and rendering
never register items, credit a new calculation, import original engines or
query a DOI. The original authors, identifiers and producer versions remain
in the saved record even when the reader uses newer libraries.

## Schema 1

`ackredit.attribution@1` has exactly these top-level fields:

| Field | Contract |
| --- | --- |
| `schema` | Literal `ackredit.attribution@1`. |
| `name` | Nonempty capture/workflow name. |
| `context` | JSON object carrying original producer context. |
| `items` | Bibliographic objects with unique, nonempty `id`; original metadata is retained. |
| `uses` | Objects with exactly `item_id`, nullable `used_by`, `roles` and `context`; every item ID resolves in `items`. |
| `usage_tree` | Target-name mapping to objects with exactly `items` and `children` lists; all links resolve to records or nodes. |

JSON object keys must be strings and numbers must be finite. Empty collections
are valid. Bibliographic metadata and context are extensible JSON objects;
scientific result and quantity schemas remain client-owned. Schema validation
does not claim that a cited work exists or that a graph proves scientific success.
Malformed records, dangling references and unknown schema IDs are diagnosed
with `ACKREDIT-E010`. Readers refuse additional structural fields rather than
guessing a newer interpretation.

The released schema 1 remains readable by later Ackredit releases. Structural
or meaning changes introduce a new schema ID and retain the existing reader.
Byte formatting, JSON whitespace and object-key order are not promised. Clients
compare the decoded data and keep host-specific wrappers outside this payload.

## Evidence and client ownership

PyUnitWizard #92 exercises real Pint/unyt conversions, software-only and
software-plus-article records, reuse, enclosing workflows, original versions,
absence/failure and saved readers. Sabueso #108 exercises its application-owned
session, reused knowledge resources, detached packet records and saved readers.
Their activation policies remain client-owned; optional MolSysSuite hosts keep
working when Ackredit is unavailable.

`tests/data/attribution_v1_pyunitwizard.json` is a frozen record from a real
PyUnitWizard 0.27.0 / unyt 3.1.0 conversion. The regression suite reads it in a
fresh process without the producer or either unit engine and checks unchanged
bibliography/version data without credit. It complements the executed capture,
conflict, isolation and integration-guide tests.
