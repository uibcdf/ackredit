---
summary: aggregate merged saved sessions into memory and never into the journal, so the file held less than the report.
issue: uibcdf/ackredit#39
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: high
verification: measured
area: [core, persistence]
guard: tests/test_aggregation.py
normative: docs/content/about/stability.md
blocked_by: []
supersedes: []
---

# Aggregated citations never reach the journal

## What

`_merge` wrote through `Session.record_item` and `record_target` directly, while
`Collector.track_item` and `track_target` write through the same methods *and* append the
event. Only the second pair journalled. Measured before the fix:

```
in memory after aggregating : ['a:1', 'b:1']
runB.json on disk           : ['b:1']
```

`report()` showed both. The file showed one, silently, and the file is what outlives the
process.

## How

`_merge` takes a `record` callback, given `(append, *arguments)` exactly as
`Collector._record` takes them, and `aggregate` passes one. The writers already return
whether they changed anything, so merging a file twice appends nothing the second time.

The parent-to-child links needed care. They live only in the usage tree — no `used_targets`
entry describes them — and the old merge updated those sets wholesale. The loops now take
the difference against what the earlier loops already recorded, so the links are journalled
and nothing is written twice.

`enable_persistence` merges without a `record`, and must: what it reads is already in the
file it is about to append to.

## Why

Aggregation is the multi-run story this library advertises: N jobs each write a journal, a
final step merges them and reports. Two ways that lost work.

The aggregating process is the natural place to enable persistence, being the step that
owns the combined record. Killed or crashed, everything merged was gone, although the
integration guide promises that no citation is lost when a script crashes.

Worse, a later run aggregating *that* journal received only what the process had tracked
itself, so merged citations disappeared one level down with nothing to indicate it.

## What was refuted

- **Leaving it, on the reading that a journal records what this run tracked.** The session
  is what `report()` renders, and a file that cannot reproduce the report is the surprise.
  The docstring of `enable_persistence` already says it records every tracked event and
  adopts what the file holds.
- **Journalling the adoption inside `enable_persistence` for symmetry.** It would write a
  file's contents back into itself. It is currently a no-op rather than a bug, because the
  journal is not open when the adoption merges — measured: passing a `record` there changes
  nothing. That is safety by construction, and the guard holds the outcome, so a future
  reordering that opened the journal first is caught. Verified by making exactly that
  change and watching the test fail.
- **Recording the merge as one event.** The journal's whole property is that a line is one
  state change, replayable and deduplicable; a compound event would need a second reader.

## Also settled

`aggregate` was classified provisional as "the least exercised part of the design, and how
it should behave across machines is open". It is exercised now, and the cross-machine
question is decided rather than open: `devguide/roadmap.md` records that multi-process
sharing beyond a local filesystem will not be attempted, and `devguide/status.md` states
the remedy, which is one journal per process merged here. It is stable.

## Scope and exclusions

Covers what aggregation does to the journal. The rest of `aggregate` was probed in the same
pass and is sound: merging is idempotent, caller order is preserved, the tree merges
faithfully, a missing file is skipped by design, and an unreadable file or a directory
raises `ACKREDIT-W003` and continues.

## Acceptance criteria

- the file holds what the report holds, including the provenance tree — met;
- a later run aggregating that journal receives everything — met;
- merging the same file twice appends nothing — met;
- enabling persistence on an existing file does not duplicate its contents — met;
- `tests/test_aggregation.py` guards it: 3 of its 7 tests fail when the merge stops being
  journalled, and 1 fails on the reordering that would duplicate a file into itself.
