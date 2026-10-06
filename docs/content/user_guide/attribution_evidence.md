# Explicit recorder evidence

The development `AttributionEvidence` API is **provisional**. It saves explicit
recorder declarations alongside a complete `Attribution` or `AttributionBundle`.
It does not collect those declarations automatically. Existing saved attribution
continues to use its original contract and remains separately readable.

```python
from ackredit import AttributionEvidence

# result is an existing detached Attribution from the producer's calculation.
evidence = AttributionEvidence.from_attribution(
    result,
    results=[
        {
            "metadata_origins": None,
            "observation_scope": [
                {
                    "boundary": "engine.convert",
                    "mechanism": "provider_observer",
                    "status": "selected",
                    "recorder": "application:1.2",
                }
            ],
            "recording_gaps": None,
        }
    ],
)
saved = evidence.to_json()
restored = AttributionEvidence.from_json(saved)
print(restored.report())
assert restored.attribution.to_dict() == result.to_dict()
```

There is exactly one `results` entry per original result: one for a single
attribution, one per member for a bundle. Position identifies the original
occurrence, including reused members and repeated names. Reordering the originals
requires reordering their evidence too. An empty bundle has no entries. Omitting
`results` creates three unknown planes per original.

Each entry needs exactly these three planes:

| Plane | Declaration fields | Interpretation |
| --- | --- | --- |
| `metadata_origins` | `item_id`, `fields`, `method`, `source`, `recorder` | Source declared for specific retained bibliographic fields. |
| `observation_scope` | `boundary`, `mechanism`, `status`, `recorder` | Declared instrumentation selection or exclusion at a named boundary. |
| `recording_gaps` | `boundary`, `diagnostic_owner`, `diagnostic_code`, `recorder` | An already diagnosed recording problem, attributed to its diagnostic owner. |

A plane is `null` when unrecorded, or a list of declarations. An explicitly
empty list means no declarations were supplied; it never certifies complete
recording. Gap declarations can exist when observation scope is unknown. Boundary
names need not appear in the recorded graph: unsupported and unobserved functions
can legitimately have no graph node.

Origin methods are `explicit_declaration`, `provider_declaration`, `citation_file`,
`bibtex_file`, `plugin`, `doi_enrichment` or `fallback`. Each declaration needs a
non-empty list of unique fields actually present in its original item. Multiple
sources may describe the same field; the reader does not select a winner or
invent a chronology. Sources are inert locators and are never opened. Origin
describes metadata, not evidence that software executed or a citation is correct.

Observation mechanisms are `explicit_credit`, `provider_observer`, `import_hook`,
`static_inspection` or `host_integration`. Status is `selected`, `unsupported` or
`unobserved`. `selected` declares a boundary selected for instrumentation; it does
not establish that a call occurred, succeeded or was captured. Recorder identity
is supplied by the producer; accepting the declaration does not independently
verify it. Gaps preserve diagnostic identities without emitting that diagnostic
again, deciding scientific completion or guessing which reference was lost.

`explain()` returns `ackredit.attribution_evidence_explanation@1`: the existing
[descriptive attribution view](attribution_explanation.md) and the separate
recorder declarations, plus explicit interpretation limits. Original schema-1
scope remains unknown in that descriptive view. The companion is the separate
contract carrying the stronger declarations. `report("explanation")` renders both.
Other formats render the original and stay byte-identical; `report("json")`
exports bibliography, while `to_json()` retains the complete companion.

```bash
ackredit report saved-evidence.json --input-format evidence -f explanation
```

CLI selection is explicit; default session input and original attribution/bundle
readers retain their contracts. Saved evidence can be explained offline, without
the scientific producer, engines, network services or new live-session credits.
Unknown structures and invalid declarations are refused through `ACKREDIT-E016`;
embedded original-contract errors retain their own diagnostic identities.

## Collect provider-recorder evidence during a calculation

The development capture extension is also **provisional**:

```python
import ackredit

# provider is an already imported module with valid __ackredit__ declarations.
with ackredit.capture("calculation", record_evidence=True) as run:
    with ackredit.observe_calls(provider):
        answer = provider.calculate(inputs)

saved = run.evidence.to_json()
assert run.evidence.attribution.to_dict() == run.attribution.to_dict()
print(run.evidence.report())
```

Observer activation and capture entry both preserve selected boundaries when
those contexts overlap. A capture started inside an existing observer gets its
selected boundaries too. Untaken functions can appear in that selection; this
is not a statement that they ran. Successfully credited provider items retain
all original fields' source as `provider_declaration`, naming the detached
`module.__ackredit__.items` declaration read at activation. Later mutation of
that module's metadata cannot substitute its new bibliography or original version.

If recording fails partway through a call, the companion keeps origins for
references already successfully credited and the owning `ACKREDIT-W019` gap.
Completed scientific results and original scientific exceptions keep the existing
observer behavior. A scientific exception does not become a recording gap.
Export restoration diagnostics enter the companion only while its capture is
still active. Saved reading never emits those earlier diagnostics again.

The recorder identity includes Ackredit's original runtime version. Facts are
bounded per selected boundary, reference/source and boundary/diagnostic identity;
repeated calls do not create invocation counters or endless duplicate events.
Reused references still enter every opted-in enclosing capture. Separate
sessions, unselected task contexts and already closed captures remain isolated.

Default captures allocate no evidence collector. Their `.evidence` property
returns a companion with unknown planes. Even an opted-in capture retains unknown
planes when no provider observer overlaps. Plain explicit credits, import hooks,
discovery, DOI enrichment, pre-activation aliases and refused generators do not
acquire guessed origins or invented scope through this extension. Broader recorder
integration remains pending. `run.attribution` and existing workflow/bibliography
reports retain their original contracts; `.evidence` is the explicitly requested
companion carrying these extra bounded facts.
