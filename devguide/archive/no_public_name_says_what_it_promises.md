---
summary: __all__ stated what was public and nothing stated what was kept, so seven untested names sat beside the ones the library is built on.
issue: uibcdf/ackredit#31
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: medium
verification: measured
area: [api, documentation, testing]
guard: tests/test_api_stability.py
normative: docs/content/about/stability.md
blocked_by: []
supersedes: []
---

# No public name says what it promises

## What

Roadmap theme F. 1.0.0 means the public API is stable and we commit to not breaking it,
and nothing said which names that covered.

`__all__` has 33 names and states only that they are public. A reader could not tell
`report` — 106 test mentions, 30 in the documentation, its shape decided twice in
`devguide/decisions.md` — from `serve_ui`, whose own docstring calls it "a conceptual stub
for the 0.4.0 release".

Measured across the surface: **seven public names had no test at all** — `compile_pdf`,
`dependency_info`, `enable_auto_reminder`, `enrich_all`, `export_to_duecredit`,
`load_plugins` and `serve_ui`.

## How

`docs/content/about/stability.md` classifies every name, seventeen stable and sixteen
provisional, with a reason for each provisional one. `tests/test_api_stability.py` holds
the page to `__all__` in both directions and refuses a stable name no test exercises.

The seven are exercised in `tests/test_optional_surface.py`. They are the part of the
surface that reaches outside — a system binary, a network, a third party's API, another
package's entry points — and what they must do is Ackredit's core promise: a missing
optional dependency produces a catalog diagnostic naming what to install, never a bare
`ImportError` and never a silent no-op.

The deprecation policy is on the same page. A stable name is removed only in a major
release, after at least two minor releases carrying a deprecation code that names the
replacement; two rather than one, so a user who skips a release still meets it. Changing
what a name does follows the same route as removing it.

Decisions 12 to 14 record the three entries that had stood under "Pending Decisions" since
the beginning and that the implementation settled long ago.

## Why

A commitment made by default is not a commitment. Without this, 1.0.0 would have frozen
whatever happened to be exported on the day it was tagged, including a stub, a bridge to
another project's API, and five names nothing ran.

## What was refuted

- **Adding the deprecation catalog code now.** The policy names an SMonitor code, and
  adding `ACKREDIT-W014` in advance was the obvious next step. It is the same proposal
  refused in `devguide/archive/shipped_citation_data_is_not_true.md`: schema added for a
  case nobody has is how it drifts from the code meant to use it. A deprecation adds its
  code with the path that emits it, as every other code here was added.
- **Marking the seven provisional without testing them.** It is the same word for a
  different thing. Provisional is a judgement about a name whose behaviour is known;
  applied to a name nobody has run, it only records that nobody looked.
- **Keeping the classification in the devguide.** It is a promise to users, so it belongs
  where users read it. The devguide records the decision behind it.
- **Marking `track_target` provisional on its thin coverage.** Three test mentions and one
  documentation line is thin, and decision 10 examined the name against seven public
  functions and kept it deliberately. Thin use is not an undecided shape.

## Incidental findings, fixed here

- **`enrich_all`'s own test reached Crossref while asserting that it did not.** The
  registry still held items other files had registered, DOIs included. It takes
  `clean_registry` now.
- **`enable_import_hooks` has no counterpart.** It inserts a finder into `sys.meta_path`
  and nothing removes it, so after `tests/test_hooks.py` ran, every later `find_spec` in
  the suite went through discovery and emitted diagnostics for modules no test chose. The
  suite restores `sys.meta_path` itself, and the missing counterpart is now part of why
  that name is provisional. The suite emits **no warnings at all** after both, where it
  emitted six.

## Scope and exclusions

Covers the classification, the policy and the evidence behind them. It does not make the
commitment: that happens when 1.0.0 is tagged, and until then a provisional name may still
change without ceremony.

Theme F is not finished. Sixteen provisional names must each be promoted or removed, the
extension point for output formats is an open decision this work opened rather than
closed, and reviewing the decisions against what adoption taught waits on theme C.

## Acceptance criteria

- every name in `__all__` classified, with a reason for each provisional one — met;
- no name classified that is not public, and none listed twice — met;
- no stable name unexercised — met, and the guard was verified by declaring an
  unexercised name stable and watching it fail;
- a deprecation policy stating what a removal requires and how long it is announced —
  met;
- the three long-standing pending decisions recorded — met, decisions 12 to 14.
