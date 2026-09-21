---
summary: The advertised json report emitted six fixed keys, dropping the DOI, the authors, the journal and the URL.
issue: uibcdf/ackredit#27
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: medium
verification: measured
area: [formats, documentation]
guard: tests/test_json_format.py
normative:
blocked_by: []
supersedes: []
---

# The json format is not a citation

## What

`json` is returned by `ackredit.available_formats()`. `formats/jsonfmt.py` built a fixed
six-key record per item and discarded the rest. For an item registered with a DOI,
authors, a journal and a URL, the whole output was:

```json
{ "id": "a:1", "title": "T", "year": 2024, "used_by": ["run"], "note": null, "type": "article" }
```

It kept `note`, which is usually null, and dropped the DOI. The call succeeded, the output
was valid JSON, and nothing indicated that a parser had just been handed a citation record
with nothing to identify the work by.

The format was also documented nowhere. `docs/content/user_guide/reporting.md` listed five
formats while `available_formats()` returned seven; `json` and `text` existed, worked, and
were named on no page. Nothing pointed at `json`, which is why nobody looked at it.

## How

The renderer emits what the item carries, keyed by the registry id, with `used_by` for
provenance. Keys beginning with an underscore are Ackredit's own bookkeeping — `_source`
tells the LaTeX escaper where a field came from — and stay out.

`json.dumps` is given `default=str`. A host can register a value this module cannot
serialise, a `datetime.date` most easily, and losing the entire report over one field is
worse than rendering that field as the text it prints as.

The documentation page now lists all seven, and a test holds it to `available_formats()`.

## Why

This is the shape of #15: a call that succeeds while returning something other than what
was asked for. There the name was wrong and the report was a different format; here the
format is right and the content is not a citation. In both cases the failure is silent,
and silence is what makes it expensive — the output looks fine until someone tries to use
it.

`formats/jsonfmt.py` had no test file, like the four other modules audited in the same
pass (#25, #26).

## What was refuted

- **Making `json` an alias of `csl-json`.** They answer different questions. CSL-JSON is a
  schema for reference managers and cannot carry `used_by`, which is the provenance this
  library exists to produce. A caller writing its own tooling wants the registered fields
  and who reached them.
- **Raising on a value that cannot be serialised.** It would replace a lossy report with
  no report, for a field that renders faithfully as text.
- **A fixed schema with every known field, nulls included.** It reintroduces the defect
  for the next field added, which is how the six keys came to be fixed in the first place.

## Scope and exclusions

Covers the `json` renderer and the documented format list. The other renderers legitimately
select fields, because a BibTeX entry has no `used_by` and a `.bst` style has no field for
it.

## Acceptance criteria

- every field a registered item carries survives into the `json` report — met;
- internal keys do not leak — met;
- the documented format list and `available_formats()` agree — met,
  `tests/test_report_formats.py`;
- `tests/test_json_format.py` guards it: 7 of its 16 tests fail when the fixed six keys
  are restored.
