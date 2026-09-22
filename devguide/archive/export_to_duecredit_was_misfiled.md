---
summary: export_to_duecredit was provisional for depending on another project, which never reached its contract.
issue: uibcdf/ackredit#56
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: low
verification: measured
area: [api, contrib]
guard: tests/test_duecredit_bridge.py
normative: docs/content/about/stability.md
blocked_by: []
supersedes: []
---

# export_to_duecredit was misfiled

## What

Its reason read "a bridge to another project's API, which we do not control". Checked
against the question the page asks — do we expect the name, its meaning or its signature to
change? — it does not hold.

- the signature is `export_to_duecredit()`, taking nothing;
- it returns nothing and has no `return` statement;
- the only exception it raises is `MissingDependencyError`, ours;
- a failure on one item raises `ACKREDIT-W013`, ours, and the export continues.

DueCredit does not appear in our contract anywhere. If it changes, we adapt inside the
function.

## Why

This is the misfiling corrected in `uibcdf/ackredit#49`, one name further: an open fact
about something we do not control, read as an expected change of shape. Found while
answering what the remaining provisional names would each need, which is the kind of
question that finds this.

`dependency_info` is not the same case and stays provisional: there the external shape
*is* our return value, since `dependency_info` is `return get_info("ackredit", format=...)`.

## What was refuted

- **Keeping it provisional because DueCredit might be abandoned.** Then we would remove it,
  and that is true of every optional integration: `compile_pdf` rests on a LaTeX
  distribution and is stable. A dependency that might disappear is not a shape we expect to
  change.

## Acceptance criteria

- the surface takes nothing, returns nothing and raises only Ackredit's own errors — met,
  asserted rather than argued;
- whatever DueCredit raises reaches the caller as `ACKREDIT-W013` — met;
- thirty-two stable and two provisional.
