---
summary: enable_import_hooks and enable_auto_reminder changed the process permanently, with no counterpart to undo either.
issue: uibcdf/ackredit#34
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: medium
verification: measured
area: [api, core]
guard: tests/test_lifecycle.py
normative: docs/content/about/stability.md
blocked_by: []
supersedes: []
---

# What is switched on cannot be switched off

## What

`enable_import_hooks()` inserts a finder into `sys.meta_path`. `enable_auto_reminder()`
registers a function with `atexit`. Neither could be undone: there was no
`disable_import_hooks`, no `disable_auto_reminder`, and the module flags that stop a second
call from doubling the effect were private.

Both are process-wide. A notebook user who called one to try it had changed the interpreter
for as long as it lived.

## How

A counterpart each, idempotent, restoring what the enable did and nothing more.

`disable_import_hooks` removes *every* Ackredit finder rather than the first, so the
process is left clean however many were inserted, and clears the flag — without that, a
second `enable` would silently do nothing. It stops the watching; it does not undo
crediting that already happened, which the docstring says and a test fixes.

## Why

The cost was measured before it was fixed, in `uibcdf/ackredit#31`: `tests/test_hooks.py`
had to reach into `sys.meta_path` and put it back by hand, because a finder left installed
made every later `find_spec` in the suite run discovery and emit diagnostics for modules no
test chose — six warnings on a green suite. A test suite undoing a public call through a
private mechanism is the defect stated plainly.

It also settled a classification. `enable_auto_reminder` was provisional and this was the
only reason recorded against it, so it is stable now, with its counterpart.

## What was refuted

- **A context manager instead of a pair.** It reads well and does not fit: both are enabled
  at import by a host library and must stay on for the life of the process, which is the
  opposite of a block.
- **Removing only the first finder.** Cheaper and leaves the process dirty in exactly the
  case worth handling, which is more than one having been inserted.
- **Leaving the flags private and documenting the `sys.meta_path` dance.** That is what the
  test suite was already doing, and documenting a workaround is not a counterpart.

## Scope and exclusions

Covers the two `enable_*` functions. `enable_persistence` already had `close_persistence`.

## Acceptance criteria

- after enable and disable the process is as it was, including `sys.meta_path` compared
  element by element — met;
- every finder is removed, not just the first — met;
- disabling without enabling, and twice, does nothing — met;
- enabling again after disabling works, which the flag would otherwise prevent — met;
- the reminder is verified by running a real interpreter to exit, which is when it happens.
