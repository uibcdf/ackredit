---
summary: Five 1.0 API questions decided: two changed, three kept with the reason written down.
issue: uibcdf/ackredit#16
status: resolved
opened: 2026-09-21
closed: 2026-09-21
verification: reproduced
area: [api]
guard: tests/test_session_isolation.py
normative: devguide/decisions.md
blocked_by: []
supersedes: []
---

# Shape of the public API for 1.0

## What

Five questions about the shape of the public surface, opened for discussion rather than
implementation, with the incubating window as the reason to settle them now.

## How

Measuring the current cost first changed the order. It also found the only item with
demonstrated harm, which was not on the original list.

```
in memory                    100 items      1.4 µs/item      flat
with persistence             100 items    1 199 µs/item
with persistence           1 000 items    2 958 µs/item      growing
```

## Why

Ackredit was registered as a suite component the same week host libraries are expected to
integrate it. Each of these becomes expensive once `molsysmt` and `topomt` depend on it,
and is cheap while it is incubating.

## What was decided

**Changed.**

1. *Persistence* — `uibcdf/ackredit#17`. The session is a journal. Four backends were
   measured before choosing, and SQLite was refused with reasons rather than dismissed.
2. *One global per interpreter* — `uibcdf/ackredit#18`. Tracking belongs to a `Session`
   reached through a `ContextVar`; declarations stay shared.

**Kept, with the reason recorded in `devguide/decisions.md`.**

3. *`dump` compiling the PDF.* The argument for separating it was that unrelated failures
   were mixed, and that stopped being true when `ACKREDIT-W011` and `W012` began
   explaining a missing binary. `compile_pdf` is already exported for anyone wanting the
   steps apart.
4. *`format` as a string.* Command lines, configuration files and JSON all carry strings.
   The real defect was an unknown name silently producing a different format, closed in
   `uibcdf/ackredit#15`.
5. *The `target` vocabulary.* See below.

## What was refuted

The naming question was the one this record exists to correct. `track_target` reads as a
pair with `track_item` without being one, and renaming it was proposed and agreed.

The evidence refused it. `target` already means "a named unit of code" in seven public
functions — `bind`, `bound_items`, `credit_bound`, `scoped_usage`, `add_injection`,
`auto_track_calls` and `track_target` — so the name is consistent with all of them and a
rename would break that coherence to fix something else.

What was actually missing was documentation. In the user-facing docs `bind` had 13
mentions, `credit_bound` 11, `bound_items` 6, and `track_target` none: nothing anywhere
said what distinguishes an item from a target. That is now written, and the API is
untouched.

## Scope and exclusions

Covers the five questions raised. Two smaller defects found while measuring were filed
and closed separately: `uibcdf/ackredit#15` and `#19`.

## Acceptance criteria

- each of the five has a decision recorded in `devguide/decisions.md`, including the
  three kept as they are;
- the two changes are implemented, guarded and archived under their own issues;
- the distinction between an item and a target is documented.
