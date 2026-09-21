---
summary: track_item tested caller membership against a list, so an item reached from many call sites got slower with every one.
issue: uibcdf/ackredit#19
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: high
verification: reproduced
area: [core, performance]
guard: tests/test_persistence_cost.py
normative:
blocked_by: []
supersedes: []
---

# track_item is quadratic in the number of callers of one item

## What

`used_by not in state.used_items[item_id]` scanned a list, so crediting one more caller
cost more the more callers that item already had.

## How

```
one item, many distinct callers        many items, one caller
   500 callers    4.3 µs/call             500 items   1.3 µs/call
 2 000 callers   12.7 µs/call           2 000 items   1.3 µs/call
 8 000 callers   47.4 µs/call           8 000 items   1.4 µs/call
```

Found while measuring the session work in `uibcdf/ackredit#18`, where a `track_item`
took 98 µs instead of the expected 1.3 because the benchmark credited one item from
20 000 distinct callers.

## Why

This is the realistic shape rather than the pathological one. The items credited most
often are the central ones — a library's own paper, a numerical method, a reference
dataset — and they are reached from many call sites; `used_by` is a qualified function
name, so every distinct site is another entry to scan. Ackredit's own thread-safety test
produces 2 400 callers for a single item without trying.

It is the same defect removed from persistence in `uibcdf/ackredit#17`, in a second
place: a per-event cost that depends on how much has already been recorded.

## What was refuted

**Replacing the list with a set** was rejected: reports show the order callers appeared
in, and a set does not keep it.

**Keeping the index beside the list in the collector** was rejected as written, because
three places built `used_items` — tracking, aggregating and loading a session — and an
index maintained in three places is an index that drifts. All three now go through
`Session.record_item`, which is the only writer of both structures.

That drift is not hypothetical: the first attempt left the test fixtures clearing
`Collector.used_items` directly, which emptied the list and not the index, and the next
credit was silently dropped because the stale index already contained that caller.
`Collector.used_items` is therefore a read-only view now, so reaching in fails loudly
instead of corrupting quietly, and `Session.clear()` is the supported way to forget.

## Scope and exclusions

Covers crediting and the structures behind it. A consequence worth recording: the journal
now stores state changes rather than calls, so crediting the same pair in a loop writes
one line instead of one per iteration.

## Acceptance criteria

Met by the commit closing this record:

- 1.8 µs per credit at 500 callers and 2.1 µs at 20 000, where it was 4.3 and rising past
  47 at 8 000;
- the order callers appeared in is preserved, without duplicates;
- `Session.record_item` and `record_target` are the only writers, used by tracking,
  aggregation and session loading alike;
- 5 000 identical credits write two journal lines, the schema and one event;
- `tests/test_persistence_cost.py` asserts a ratio rather than a time. Verified by
  restoring the list scan, which fails it with "4.4 µs/call with 500 callers became
  39.7 µs with 5 000".
