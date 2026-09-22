---
summary: With import hooks on, every standard-library module imported warned that no citation was found and advised registering it by hand.
issue: uibcdf/ackredit#70
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: low
verification: reproduced
area: [hooks]
guard: tests/test_hooks_already_loaded.py
normative:
blocked_by: []
supersedes: []
---

# The import hooks warn about the standard library

## What

With `enable_import_hooks()` on, `import sqlite3` warned for `sqlite3` and `_sqlite3`,
`import decimal` for `decimal` and `_decimal`, and the user guide's discovery example
warned about the generated `_sysconfigdata__linux_x86_64-linux-gnu`. Each warning advised
registering the module with `register_item()`.

## How

Discovery skips `sys.stdlib_module_names` and the `_sysconfigdata*` modules. An explicit
injection on a standard-library module is still credited.

## Why

The standard library is cited as Python, not module by module, and a warning that fires on
`import json` teaches people to ignore the one that matters.

## What was refuted

Skipping by file location, under the interpreter's standard-library directory. That
directory contains `site-packages`, so a prefix test would have silenced discovery for
every installed package.

## Scope and exclusions

Only discovery. Injections are a person deciding, and are honoured.

## Acceptance criteria

`tests/test_hooks_already_loaded.py` imports standard-library modules that were not yet
loaded, with the hooks on, and requires no warning and no citation; it fails against the
previous finder. An injection on `sqlite3` is still credited.
