# Explain recorded attribution

Development under Ackredit #103 adds `explain_attribution` and the `explanation`
report format. They describe the evidence a saved result actually contains.
They are not included in the current public 0.10.1 package.

```python
import ackredit

saved = ackredit.Attribution.from_dict(
    {
        "schema": "ackredit.attribution@1",
        "name": "example result",
        "context": {},
        "items": [{"id": "example:reference"}],
        "uses": [],
        "usage_tree": {},
    }
)
view = ackredit.explain_attribution(saved)
assert view["results"][0]["instrumentation_scope"] == "not_recorded"
print(saved.report(format="explanation"))
```

The view states its version as `ackredit.attribution_explanation@1`, the source
schema and input name. `results` keeps each original result's name/context,
counts, reference evidence and graph targets without direct references. Its
overview reports input-record and shared-reference counts. Reused inputs,
independent graph boundaries and empty results remain separate.

Counts describe raw recorded use records and distinct contextual uses, not
invocations. A different original use context is distinct evidence; an exactly
repeated use is counted once in the distinct count. References list their
recorded caller labels, roles and unscoped uses. The tool never interprets an
entry role as completed backend dispatch or scientific success.

`fields_absent` checks key presence for `type`, `title`, `authors`, and also
`version` for an explicitly typed software record. Present empty/null fields
remain present: this is a description of saved shape, not value validation,
mandatory citation requirements or a completeness rating. `metadata_fields`
lists supplied keys other than the identifier. Neither field supplies a
verification of the cited work.

A supplied `version` is copied exactly and shown as its recorded JSON value;
it is never replaced by the reader's installed version. Missing and supplied
null values remain distinguishable through field presence.

## What remains unknown

The original portable schemas do not define instrumentation boundaries,
metadata origins or diagnosed recording gaps. The tool states those facts as
`not_recorded`, including for empty or apparently comprehensive results. A DOI,
URL, arbitrary extra field or caller-owned context cannot establish their
meaning. The caller's context is retained without granting it authority over
the separate descriptive fields.

No references recorded does not prove that no citable work was used. A reference
without contextual uses is not necessarily unused. An enclosing graph node with
no direct citations is not automatically an attribution failure. There is no
global coverage percentage, missing-call inference or assertion of successful
recording, bibliographic truth or scientific completion.

Later roadmap J work must decide an explicit evidence representation and
collection contract before reports can make stronger claims. This tool neither
hides new structure inside released schema 1 nor changes the caller's payload.

## Bundles, current sessions and CLI

```python
bundle = ackredit.compose_attributions([saved, saved], name="batch")
batch_view = ackredit.explain_attribution(bundle)
assert batch_view["counts"] == {"input_records": 2, "shared_references": 1}
print(bundle.report(format="explanation"))
```

Use `ackredit.report(format="explanation")` for a detached snapshot of the
current session. Existing format selection also supports `dump` and saved
CLI input:

```bash
ackredit report result.json --input-format attribution --format explanation
ackredit report batch.json --input-format bundle --format explanation -o report.md
```

Saved reading/explanation never imports the producer or scientific engines,
queries metadata services, records new credits or changes the original. The
returned view is detached, so editing its dictionaries cannot affect later
explanations. It is a descriptive output, not a replacement attribution payload
accepted by `Attribution.from_dict`.

The new tool has deliberately recorded pre-1.0 stable intent for this bounded
operation. The released individual-record compatibility promise and the
provisional observer/prepared APIs retain their existing status. Existing
default workflow and bibliographic formats are unchanged.
