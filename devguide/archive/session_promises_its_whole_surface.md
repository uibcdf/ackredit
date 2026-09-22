---
summary: Session exposed its writers and its lock alongside the mappings a caller wants, and its stated reason contradicted the same page.
issue: uibcdf/ackredit#52
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: low
verification: measured
area: [api]
guard: tests/test_session_contract.py
normative: docs/content/about/stability.md
blocked_by: []
supersedes: []
---

# Session promises its whole surface

## What

A session held through `with ackredit.session() as run:` exposed:

```
clear, journal_path, lock, name, record_item, record_target,
usage_tree, used_items, used_targets
```

`used_items`, `used_targets` and `usage_tree` are what a caller wants. `record_item` and
`record_target` are the writers the collector uses, and they carry the rule that a caller
holds the lock; `lock` is that lock. All were public names on a public class, promised by
accident.

Its recorded reason also said the journal was `ackredit.session@1` "with no migration story
yet", while the same page had carried one since `uibcdf/ackredit#33`: Ackredit reads every
session format it has ever written. The document contradicted itself.

## How

The writers and the lock are `_record_item`, `_record_target` and `_lock`. Every caller was
inside the package — `ackredit/core/collector.py` and `_merge` — and the class says what it
promises.

## Why

A public name on a public class is a promise whether or not anyone meant it. Promising
`_record_item` would promise the rule it carries, that a caller holds the lock first, which
is the kind of contract a library should not make by leaving a method unprefixed.

## What was refuted

- **Documenting the surface and leaving the names alone.** It puts the promise and the code
  in two places and lets them drift, which is what the stale half of the reason already
  demonstrated.
- **Making `clear()` private with the writers.** It forgets what was tracked, which is a
  reasonable thing for a caller to want and has a meaning that does not depend on holding
  anything.
- **Making `journal_path` private.** Asking where the journal is being written is
  reasonable; only opening one is `enable_persistence`'s to do, and that is said rather
  than enforced.

## Acceptance criteria

- a session instance exposes those six names and no others — met, asserted against an
  instance, since the mappings are set in `__init__` and are not on the class;
- the writers and the lock exist with an underscore — met;
- each promised name behaves — met;
- the page no longer contradicts itself — met, asserted.
