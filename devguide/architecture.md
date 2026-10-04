# Architecture

Ackredit separates bibliographic declarations, runtime observations and saved
attribution. A scientific client chooses which operation earned credit; Ackredit
records that observation and renders its references. It does not determine
whether the scientific result is correct or complete.

## Declarations and execution

`register_item` declares a bibliographic work: software, an article, a dataset
or another supported record. The private registry shares declarations within a
process. `bind` associates potential references with a named code target;
`bound_items` reads that declaration. Neither operation credits a calculation.

`track_item` records an observed use in the current session. A client places it
on the branch actually reached. `scope` and `scoped_usage` give observations
their enclosing target path; `credit_bound` explicitly credits a target's
declared references. Crediting every binding or observing an import is coarser
than instrumenting the executed branch. Import hooks and static call inspection
are opt-in discovery aids, not proof that every associated algorithm ran.

Provisional `observe_calls` adds a separate, explicit observation mechanism for
dependency-free third-party declarations. A selected module's `__ackredit__`
metadata (or function metadata referring to that bibliography) states the
references earned on entry to each declared function. Temporary wrappers
delegate untouched scientific arguments, results and exceptions; a context-local
observer lease controls credit and expiration. Original exports are restored
when the last lease exits. Pre-existing aliases, generators and native internal
calls are excluded. The [provider guide](../docs/content/user_guide/function_providers.md)
defines the provisional schema and failure boundaries; this is not suite policy.

Provisional `prepare_credit` (#87) exposes preparation of one explicit fixed
contextual use for hosts that credit a backend only after completed dispatch.
It reuses the same private prepared-reference writer as the function observer,
but creates no scientific call scope or proof of entry. Per-call registry
comparison and all current session/capture/journal writes remain in place.

A software reference and its description articles are separate bibliographic
works. Contextual uses carry roles and the executed software/version relationship;
a single article may describe multiple releases. Original metadata and context
are retained rather than inferred from the reader's current environment.

## Application sessions and calculation captures

Applications own `session(...)`. A `Session` holds observed items, targets and
their usage tree; a `ContextVar` selects the current one. The module functions
use a default session when no explicit session is entered. Context-local scope
and session selection isolate independently entered analyses and asynchronous
tasks; threads do not automatically inherit an application's context. Collector
updates within a shared session are serialized.

`capture(name, context=...)` observes a calculation without replacing that
session. Every enclosing capture in the same session receives the calculation's
references, including references that the workflow had already credited.
Subtracting before/after deduplicated session IDs cannot provide that behavior.
An explicitly isolated session is not implicitly merged into another capture.
Exceptions propagate and completed child observations remain; the client owns
the success/partial/failure interpretation of its scientific result.

`get_attribution()` snapshots the current workflow. Contextual and captured uses
retain the records observed when they were credited. Legacy plain credits resolve
their bibliography when the workflow snapshot is requested.

## Detached results and identifier journals

`Attribution` carries complete bibliographic records, contextual uses, original
producer context and the saved usage tree. Its `ackredit.attribution@1` schema
and supported operations ship in public Ackredit 0.9.0. Export creates detached
JSON data; a client's result schema decides where that payload is stored.
`Attribution.from_dict` and `Attribution.from_json` validate saved records without
registering references, crediting a new calculation, loading the original
scientific engines or enriching metadata. Conflicting observed metadata for one
ID and invalid/unknown schemas are diagnosed and refused.

The session journal is a different contract, `ackredit.session@1`: it persists
item IDs and target observations, not complete bibliographic records or contextual
uses. `aggregate` merges journal observations into the current session. It does
not reconstruct a portable bibliography that the journal never contained.
Use detached attribution alongside scientific results when fresh readers need
original records and versions; use journals for the documented session workflow.

```text
offline declarations --> process registry
                               |
executed branch --> current session --> workflow Attribution
                         |
                         +--> enclosing capture --> result Attribution
                         |
                         +--> optional journal (IDs and targets)

saved Attribution --> validate/detach --> render bibliography
                     (no new credit)
```

## Rendering and extensions

`report` renders the current session; `Attribution.report` renders saved records
through the same format machinery. Markdown, text, BibTeX, CSL-JSON, JSON,
provenance and LaTeX are implemented. Development source also offers an explicit
`workflow` report joining numbered bibliography, contextual uses and graph.
It preserves original versions/roles/context and distinguishes recorded uses
from invocation counts or scientific success. Shared graph targets expand once
while retaining every incoming edge; deep traversal uses explicit stacks.
`dump` writes outputs and may compile PDF
when the external tools are available. `export_to_duecredit` forwards the
current session's references to the optional DueCredit provider.

`register_format` and the `ackredit.formats` entry-point group extend rendering.
Citation packs use `ackredit.citations` and `load_plugins`; installed citation
plugins load on Ackredit import, while format plugins load when the format table
is consulted. These are provider behaviors, separate from a scientific host's
lazy optional boundary. A format registration cannot replace an existing name.
Renderer inputs detach nested data so a plugin cannot alter later reports.
The plugin contract and portable schema do not change for `workflow`.

## Component boundaries and compatibility

Optional MolSysSuite scientific clients keep offline declarations, defer provider
loading/registration until use and contribute to the application's session. They
preserve completed scientific results and host-owned provenance when the provider
is absent or fails, with host catalog diagnostics for failures. They do not
automatically enable hooks, inspection, enrichment, journals or reminders.
Applications such as Sabueso may explicitly require Ackredit; that client decision
does not change the optional integration profile for other hosts.

SMonitor owns diagnostic infrastructure, DepDigest optional dependency guards,
ArgDigest argument auditing and PyYAML CFF parsing. Ackredit owns bibliographic
records, observation/capture semantics and the portable attribution schema.
Clients own scientific methods, result/quantity serialization and released
integration claims. MolSysSuite owns common policy, admission and registered
guide synchronization.

The portable compatibility promise is bounded to the released schema and
reviewed operations; general API stability remains pre-1.0 intent. See
[API stability](../docs/content/about/stability.md), the
[portable contract](../docs/content/user_guide/portable_attribution.md),
[integration guide](https://github.com/uibcdf/ackredit/blob/main/standards/ACKREDIT_GUIDE.md)
and [roadmap](roadmap.md).
