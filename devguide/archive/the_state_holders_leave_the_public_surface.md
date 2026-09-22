---
summary: Registry and Collector were exported at the top level and nothing Ackredit teaches used either.
issue: uibcdf/ackredit#55
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: low
verification: measured
area: [api]
guard: tests/test_public_surface.py
normative: docs/content/about/stability.md
blocked_by: []
supersedes: []
---

# The state holders leave the public surface

## What

`Registry` and `Collector` hold the two halves of Ackredit's process-wide state and were
exported at the top level, both classified provisional for the same reason: the supported
surface is the functions in front of them.

Counted before deciding:

- `standards/ACKREDIT_GUIDE.md`, the document every host library copies: no mentions;
- `examples/`, the two libraries that integrate Ackredit as the guide describes: no
  mentions;
- `docs/content/`, only under `developer_guide/` and the API reference's "Core Components",
  which document the modules for contributors.

No user-facing page used either.

## How

Both leave `ackredit.__all__` *and* the namespace. Leaving them out of the list while still
reachable would contradict the rule beside it — `tests/test_public_surface.py` says an
accidental export is still an export, and either declare it or bind it privately. They
remain exactly where they always were, at `ackredit.core.registry.Registry` and
`ackredit.core.collector.Collector`.

Nothing inside the package depended on the top-level export: every internal caller already
imported from the module. Nine places in the test suite reached for `ackredit.Registry` and
now import it, one of them through a multi-line `from ackredit import (...)` that a
line-oriented search had missed.

Thirty-six public names became thirty-four: thirty-one stable and three provisional.

## Why

A provisional name reaches 1.0.0 either promoted or removed, and promoting these would
promise a class whose whole surface is state. The alternative was to decide what of
`Registry.items` and `Collector.used_items` is contractual, for a use nothing we teach has.

## What was refuted

- **Taking them out of `__all__` and leaving them reachable.** It is the gentler step and
  it contradicts the boundary the page defines. A name on the package is a promise whether
  or not it is listed, which is why the guard exists.
- **Removing the classes.** They are the implementation, and the functions are in front of
  them; this is about what is promised, not about what exists.
- **Keeping `Collector` for the code that predates the session.** That code is inside the
  package and imports from the module.

## Acceptance criteria

- neither name is in `__all__` nor reachable on the package — met;
- both are where they always were — met;
- the supported readers still answer what the classes would have — met, asserted rather
  than assumed;
- the API reference says its "Core Components" are internals — met;
- `tests/test_public_surface.py` guards it, and fails when either is exported again.
