---
summary: Sphinx scanned its own output directory, so a clean documentation build passed and the next one failed.
issue: uibcdf/ackredit#29
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: low
verification: measured
area: [documentation, tooling]
guard: tests/test_docs_build.py
normative:
blocked_by: []
supersedes: []
---

# The documentation build is not repeatable

## What

`docs/conf.py` set `exclude_patterns = []`. MyST-NB writes its executed notebooks into
`docs/_build/jupyter_execute/`, and Sphinx collected them as source on the next run.

```
rm -rf docs/_build && (cd docs && python -m sphinx -b html -W . _build/html)   # succeeds
                      (cd docs && python -m sphinx -b html -W . _build/html)   # fails
```

The second build reported duplicate labels for every showcase notebook and
`toc.not_included` for the copies under `_build`; `-W` made those errors.

## How

`exclude_patterns = ["_build", "**.ipynb_checkpoints"]`.

## Why

The first build passes because `_build/jupyter_execute/` does not exist when sources are
collected, and CI builds from a clean checkout, so this was invisible to every automated
check. A contributor building twice met a failure naming their own notebooks and their own
labels, which reads as something they broke. The cost is the time spent looking for a
defect that is not there.

Found while verifying a documentation change in #27: the first build was clean, the
re-run was not, and the difference was not the change.

## What was refuted

- **A test that builds twice.** It is the honest check and it costs more than the entire
  test suite, for a defect whose cause is one configuration line. The configuration is
  asserted instead, at the line that caused it.
- **Deleting `_build` before each build.** It hides the cause, throws away the incremental
  cache that makes the build usable locally, and leaves the next output directory to
  reintroduce it.

## Scope and exclusions

Covers the source-collection configuration. The notebooks themselves are unchanged.

## Acceptance criteria

- two consecutive builds with `-W` both succeed — met, measured;
- `tests/test_docs_build.py` holds `conf.py` to excluding its own output.
