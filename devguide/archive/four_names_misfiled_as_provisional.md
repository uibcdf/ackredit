---
summary: Four names were classified provisional for open behavioural questions rather than for any expected change of name, meaning or signature.
issue: uibcdf/ackredit#49
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: low
verification: asserted
area: [api, documentation]
guard: tests/test_api_stability.py
normative: docs/content/about/stability.md
blocked_by: []
supersedes: []
---

# Four names misfiled as provisional

## What

The page defines the levels by one question — do we expect the name, its meaning or its
signature to change? — and four names were filed against a different one: is anything about
this unsettled?

| name | recorded | what it is |
| --- | --- | --- |
| `enrich_all` | how long a cached answer keeps is open | internal behaviour; a later `max_age=` would be an addition |
| `auto_track_calls` | detection is per function, not per branch | decided: `devguide/roadmap.md` refuses per-branch precision |
| `enable_import_hooks` | "decided for now, not settled" | decision 13 settles it, and `uibcdf/ackredit#34` gave it a counterpart |
| `compile_pdf` | `@software` is undefined in common `.bst` styles | the content of the PDF, not the signature |

Twenty-three stable and thirteen provisional became twenty-seven and nine.

## How

The four are corrected, and the deprecation policy now says what a change of meaning is.
The promise is what counts, not the mechanism: giving a cache a freshness changes when a
request is made and not what `enrich_all` is for; making `track_item` credit at import
would change exactly what it is for, and is a removal however the name stays; adding an
optional argument is neither.

## Why

The rule was in the page and the line under it was not, so classifying leaned on a reading
of "provisional" that is wider than the page's own. Four names would have reached 1.0.0
without the commitment they deserve, and the list of provisional names is the measure of
how far theme F has to go — an inflated one makes the theme look further away than it is.

The nine that remain hold: `Session`, `Registry` and `Collector` have genuinely undecided
class surfaces with removal on the table; `register_format` promises the shape a renderer
is handed; `serve_ui` calls itself a stub; `dependency_info` and `export_to_duecredit` rest
on another project's contract; `summary` and `load_plugins` promise something nobody
outside has exercised.

## What was refuted

- **Keeping the four provisional until adoption.** It is a defensible caution and it is not
  what the level means here. "Provisional" says we expect a change; using it to mean "we
  have not seen it used" would put most of the surface there and say nothing.
- **Widening "stable" to mean settled in every respect.** No name would qualify. `report`
  has open questions about what its formats contain and is the most exercised name in the
  library.

## Acceptance criteria

- the four are stable with reasons that answer the page's question — met;
- the policy states what a change of meaning is — met;
- the counts are written in one place and checked against the table — met,
  `tests/test_api_stability.py`.
