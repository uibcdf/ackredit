---
summary: Two processes sharing a session file silently discarded most of their citations.
issue: uibcdf/ackredit#8
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: high
verification: reproduced
area: [persistence, reporting]
guard: tests/test_session_sharing.py
normative:
blocked_by: []
supersedes: []
---

# A session file shared between processes silently loses most of its citations

## What

`Collector._save_state` replaces the whole document on every write. Two processes given
the same path therefore do not merge: the last writer wins and the other's citations are
gone. `os.replace` keeps every write atomic, so the file is never corrupt — it is valid
JSON with plausible content and more than half the data missing.

## How

Four processes, sixty items each, all pointed at one path:

```
items expected : 240
in the file    : 106
LOST           : 134  (55%)
JSON valid     : yes
processes whose data survives: ['p0', 'p2']   (2 of 4)
```

The documented pattern already gives the right answer:

```
one file per process, then aggregate -> 240/240, all four represented
```

## Why

This is the failure mode a citation tracker must not have: the report is confident and
wrong. `status.md` offers a multi-session aggregator for HPC clusters, which is exactly
where a user runs one script under several ranks and gives them a single session path
because it looks like the obvious thing to do.

## What was refuted

File locking was considered and rejected. The per-process plus `aggregate` design is
already correct and verified; locking would add a cross-platform dependency to make a
discouraged pattern work slightly less badly, and would still serialize writers that have
no reason to contend. The missing piece was never coordination, it was noticing.

Reading the file back before each write to identify the other writer was also rejected:
saves happen on every `track_item`, and parsing the document each time to detect a rare
mistake is the wrong trade. Comparing this process's own last `stat` costs one syscall.

## Scope and exclusions

Covers detection and documentation of the shared-path mistake. Excludes making concurrent
shared-path writes safe, which is explicitly not planned.

## Acceptance criteria

Met by the commit closing this record:

- `ACKREDIT-W014` names the path and the way out, emitted once rather than per write;
- detection compares the stat of this process's own last write, reading nothing;
- no diagnostic on the supported pattern, verified with four real processes writing
  their own files;
- tracking continues after the warning, so the diagnostic costs the caller nothing;
- the user guide documents per-process files and `aggregate`;
- `tests/test_session_sharing.py` covers all of it, verified by removing the detection,
  which fails two of its tests.
