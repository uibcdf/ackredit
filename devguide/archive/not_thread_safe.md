---
summary: Concurrent workflows cross-attributed citations and corrupted the session file.
issue: uibcdf/ackredit#5
status: resolved
opened: 2026-09-20
closed: 2026-09-20
severity: high
verification: reproduced
area: [core, concurrency, persistence]
guard: tests/test_thread_safety.py
normative:
blocked_by: []
supersedes: []
---

# Scope attribution and session persistence are not thread safe

## What

Two independent defects made Ackredit unusable from more than one thread.

`scope._current_scope` was a plain class attribute, shared by the whole process.
Concurrent workflows overwrote each other's current scope, so citations were attributed
to the wrong caller, and the scope leaked to whatever ran next in the same worker.

`Collector._save_state()` called `Path.write_text()` on every `track_item`, with no lock
and no atomic replace, so a reader or a crash found a truncated file.

## How

Five threads, each inside its own scope:

```
item_0: expected ['thread_0']  got ['thread_4']   WRONG
item_1: expected ['thread_1']  got []             WRONG
item_2: expected ['thread_2']  got ['thread_0']   WRONG
item_3: expected ['thread_3']  got ['thread_1']   WRONG
item_4: expected ['thread_4']  got ['thread_2']   WRONG
leaked scope after joins: 'thread_3' (expected None)
```

Eight threads tracking with persistence enabled, re-reading the file after each write:
**316 of 480 reads found truncated or invalid JSON.**

## Why

Attribution is the product. A tracker that credits the wrong caller is worse than one
that credits nothing, because the report looks complete. Persistence exists for
long-running and parallel workflows, and a crash-recovery file that is usually invalid
mid-run recovers nothing.

## What was refuted

A third suspicion did not hold. `track_item` does `if used_by not in list:
list.append(used_by)`, a check-then-act sequence. Thirty-two threads released from a
barrier, repeated twenty times, never produced a duplicate: on CPython 3.13 the GIL makes
those short sequences effectively atomic. It is recorded as **inspected, not reproduced**.
The lock covers it regardless, because the guarantee should not depend on an interpreter
detail.

Adding `pytest-timeout` was also rejected. The suite uses `pytest-cov` and `pytest-xdist`
and no component uses `pytest-timeout`, and more importantly it would have converted a
badly written test into a generic timeout rather than fixing it. Bounded rendezvous in
the tests themselves, plus `timeout-minutes` on the CI jobs as the suite already does,
cover the same risk without a new dependency.

## Scope and exclusions

Covers scope isolation, the collector's compound updates and the session file write.
Excludes multi-process safety: `Collector.aggregate` merges files written by separate
processes, and no file locking is attempted between them.

## Acceptance criteria

Met by commit `85dd59d`:

- the current scope lives in a `contextvars.ContextVar`, isolating threads and asyncio
  tasks without the caller opting in;
- `scoped_usage` delegates to the `scope` context manager instead of duplicating it, so
  the isolation has one implementation;
- the collector guards compound updates with a reentrant lock;
- the session file is written to a temporary file, fsynced and `os.replace`d into
  position, leaving no partial document and no leftover temporary;
- `tests/test_thread_safety.py` covers all of it and was verified by reverting each fix:
  the scope revert fails six tests, the write revert reports 126 corrupt reads;
- every rendezvous in those tests is bounded, so a regression fails in under a second
  instead of hanging. The first version of the tests did hang, which is how that
  requirement was discovered.
