---
summary: Persistence rewrote the whole document on every item, making a run O(n squared).
issue: uibcdf/ackredit#17
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: high
verification: reproduced
area: [persistence, performance]
guard: tests/test_persistence_cost.py
normative: devguide/decisions.md
blocked_by: []
supersedes: []
---

# Session persistence is O(n squared) and unusable at the scale it advertises

## What

`_save_state` serialised and rewrote the entire session document on every `track_item`,
so the cost of tracking one more item grew with how many had been tracked already.

## How

```
in memory                    100 items      1.4 µs/item
in memory                 10 000 items      1.4 µs/item      flat

with persistence             100 items    1 199 µs/item
with persistence             500 items    2 281 µs/item
with persistence           1 000 items    2 958 µs/item      growing
```

One thousand items took three seconds and wrote about 23 MiB to produce a 48 KiB file.

The per-event cost had two independent parts:

```
serialise the whole document (39 KiB)        410 µs     grows with n
write it without fsync                       136 µs     grows with n
temp file + fsync + os.replace (current)   1 186 µs
append one line to a journal                  35 µs     constant
append one line + fsync                      982 µs
```

## Why

`devguide/status.md` offered a multi-session aggregator for HPC clusters and the
integration guide recommended persistence for long-running workflows. Those are the runs
that track thousands of items, and they were the ones this made slowest. A tracker that
measurably slows the science it is attached to gets switched off, and a tracker that is
off records nothing.

## What was refuted

Four alternatives were measured over 2 000 events before choosing:

| backend | per event | vs previous |
| --- | ---: | ---: |
| whole document + fsync | 2 071 µs | 1× |
| SQLite WAL, commit per event | 910 µs | 2.3× |
| SQLite WAL, commit every 100 | 6.4 µs | 322× |
| JSONL journal, fsync on close | 3.2 µs | 654× |
| memory only, written once | 1.1 µs | 1 842× |

**SQLite was evaluated seriously and refused.** Its advantage is not speed but concurrent
writers, queryability and integrity, with no dependency. Against it: its locking is
documented as unreliable on network filesystems, and HPC scratch is typically NFS or
Lustre, so its headline advantage is weakest exactly where it would be wanted; it is twice
the per-event cost of a journal; a `.db` cannot be read or grepped by a person looking at a
failed run; and a table needs migrations where an append-only journal of typed events
absorbs a new field without changing a reader.

**Memory-only was refused** because it abandons the documented guarantee that no citation
is lost when a script crashes.

**Per-event `fsync` was refused.** It costs a flat ~950 µs and protects only against the
machine failing; an ordinary write already survives the process dying, which is the
promise actually made. It is paid once, on close.

## Scope and exclusions

Covers the on-disk form, its reading, and merging. Excludes compression: 94% on this data
is real but belongs at archival or compaction, not on a hot append.

## Acceptance criteria

Met by the commit closing this record:

- 6.6 µs per item and flat from 100 to 5 000, where the previous design reached 2 958 and
  kept rising;
- a session written by an earlier version still loads, and still merges;
- an interrupted run keeps every complete event, with a torn final line skipped rather
  than discarding the journal;
- `ACKREDIT-W014` is retired: four processes sharing one journal now keep all 240 items,
  where the document format kept 106, so the warning reported a loss that can no longer
  happen;
- `tests/test_persistence_cost.py` asserts the ratio rather than a time, so it means the
  same on a loaded runner. Verified by restoring a full-document write, which fails it
  with "60.5 µs/item at 200 became 444.1 µs at 2000".
