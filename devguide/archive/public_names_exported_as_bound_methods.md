---
summary: Two public names were attributes of the Collector class rather than functions, binding the API to a class we intend to change.
issue: uibcdf/ackredit#33
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: low
verification: measured
area: [api]
guard: tests/test_public_surface.py
normative: docs/content/about/stability.md
blocked_by: []
supersedes: []
---

# Public names exported as bound methods

## What

`ackredit/core/collector.py` ends with six module-level functions that delegate to
`Collector`. Two public names were missing from that block and were patched into the
namespace differently:

```python
enable_persistence = Collector.enable_persistence
aggregate = Collector.aggregate
```

So `ackredit.enable_persistence` *was* `Collector.enable_persistence`, a bound classmethod,
while its sibling `ackredit.close_persistence` was a function. `help()` described one as a
method of a class and the other as a function, for two calls used together.

## How

Both got a delegating function beside the six others, and the aliases are gone. A bound
classmethod already has `cls` supplied, so the call signature is unchanged: this is the
shape of the export, not its behaviour. 823 tests pass unchanged.

## Why

Tidiness was not the reason. An alias binds a public name to the identity of `Collector`,
a class the stability page calls provisional and whose state is now only a view onto the
current session (`uibcdf/ackredit#18`). Freezing the public API at 1.0.0 while two of its
names are attributes of a class we intend to change is coupling the release should not
inherit.

Removing it settled both names. They were provisional for two reasons, the export shape and
the journal format; with the first gone, the second turned out to be a contract that
already existed and only needed naming, so `enable_persistence` and `close_persistence` are
now stable. `aggregate` stays provisional on its own merits: two tests, and how merging
should behave across machines is open.

## What was refuted

- **Exporting the rest of `Collector` the same way, for consistency.** It would make the
  whole class public by accident, which is the coupling this removes.
- **Promoting `aggregate` with the other two.** Its blocker was never the export shape.
- **Inventing a migration policy for the journal.** The reader already loads the
  whole-document format written before the journal existed, and
  `tests/test_persistence_cost.py` holds it to that. The page states what the code does —
  Ackredit reads every session format it has ever written, and a format change raises the
  schema number rather than reusing it — rather than promising something new.

## Scope and exclusions

Covers how the two names reach the namespace. `Collector` and `Registry` remain exported
and remain provisional.

## Acceptance criteria

- every callable in `__all__` is a function or a class, never a bound method — met, and
  the guard was verified by restoring the alias and watching it fail;
- the counts of stable and provisional names are written in one place and checked against
  the table — met, `tests/test_api_stability.py`;
- the session file contract is stated and exercised — met.
