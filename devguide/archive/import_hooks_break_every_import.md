---
summary: enable_import_hooks raised ImportError on the first import in any fresh process, because a lazy import inside discovery re-entered the finder.
issue: uibcdf/ackredit#60
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: high
verification: measured
area: [core, discovery]
guard: tests/test_import_hooks_fresh.py
normative:
blocked_by: []
supersedes: []
---

# Import hooks break every import

## What

```python
import ackredit
ackredit.enable_import_hooks()
import csv
```
```
ImportError: cannot import name 'find_and_parse_cff' from partially initialized module
'ackredit.core.cff' (most likely due to a circular import)
```

Reproduced with `csv`, `sqlite3` and `molsysmt`. The auto-discovery that
`standards/ACKREDIT_GUIDE.md` tells a host library to enable did not work at all in a
process that had not already loaded `ackredit.core.cff`.

The cycle: the finder calls `_record`, which calls `_read_citation_file`, which does
`from .cff import find_and_parse_cff`; `cff` imports yaml at module level; the finder sees
`yaml` and calls `_record` again, which asks `cff` for a name while `cff` is still
executing its own import line. `_triggered` does not help — it guards one name, and these
are two.

## Why nothing caught it

Every test that enables the hooks runs in a process where `ackredit.core.cff` is already
imported, by an earlier test or by the test module itself. The cycle needs `cff` unloaded at
the moment of the first hooked import, which only a fresh interpreter gives. The guard is
therefore a subprocess, and for no other reason.

Found by roadmap theme D, instrumenting a real workflow — `import molsysmt` with hooks on —
which is what that theme exists for. No synthetic benchmark could have found it.

## How

`enable_import_hooks` loads what discovery needs — `ackredit.core.cff` and
`importlib.metadata` — before installing the finder. A lazy import inside the discovery
path is the whole cause, and loading them first is the whole fix. The cost is paid only by
a process that asked for discovery.

## What was refuted

- **A re-entrancy guard on the finder**, which is what I wrote first. It passed the
  original reproduction and then a test I wrote for the fix found a second entrance it did
  not cover: a caller importing `ackredit.core.cff` itself, from outside the finder.
  Loading eagerly closes both.
- **Keeping the guard as well.** With the imports loaded, no test could exercise it — its
  removal broke nothing — and machinery no case needs is what was refused in
  `uibcdf/ackredit#26`, `#31` and `#50`. What replaced it is a test of the invariant the
  fix rests on: the discovery machinery is in `sys.modules` before the finder is in
  `sys.meta_path`.
- **Importing `cff` at the top of `hooks.py`.** It would put yaml in every `import
  ackredit`, for a path most processes never take.

## Acceptance criteria

- a fresh interpreter with hooks on can import a package that is not loaded — met, for
  `csv`, `sqlite3` and `xml`;
- discovery still credits what it finds — met;
- a package Ackredit pulled in for itself is not marked as handled, so a caller importing
  it later is still discovered — met;
- the discovery machinery is loaded before the finder is installed — met, the invariant
  asserted directly;
- `tests/test_import_hooks_fresh.py` guards it: the eager load removed, one of its eight
  tests fails.
