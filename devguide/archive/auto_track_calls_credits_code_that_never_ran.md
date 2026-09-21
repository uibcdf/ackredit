---
summary: auto_track_calls credited citations at import time, and could not read a class method at all.
issue: uibcdf/ackredit#13
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: high
verification: reproduced
area: [core, discovery]
guard: tests/test_inspection.py
normative:
blocked_by: []
supersedes: []
---

# auto_track_calls credits citations for code that never runs

## What

`auto_track_calls` read a function's AST when the module was imported and recorded the
credit there and then. Whether the function was ever called made no difference, which is
the behaviour Ackredit exists to replace.

A second defect made the feature largely inoperative anyway: `inspect.getsource` returns a
method's source carrying its class's indentation, `ast.parse` rejects that, and detection
found nothing. Every method was invisible, which is most of what a scientific library has
to cite.

## How

```python
def never_called():
    mdtraj_load()

auto_track_calls(never_called, {"mdtraj_load": "external:mdtraj"})
```
```python
{'external:mdtraj': ['never_called']}      # nothing has been executed
```

An unreachable branch was credited the same way, and calling the function afterwards
changed nothing, because the credit had already been recorded.

```
class method       -> detected nothing, ACKREDIT-W010
module function    -> detected {'mdtraj_load'}
```

## Why

The README's premise is that Ackredit "records which algorithms, datasets and dependencies
a run actually reached", against the status quo of citing a library because it was
installed. This function reproduced the status quo while appearing to be the automatic
version of the real thing. It was exported in `__all__`, with no documentation and no
tests, so nothing stated the limitation and nothing would have caught it.

## What was refuted

Removing the feature was considered. It is not necessary: the static analysis is sound for
deciding *what* a function would cite, and only the timing was wrong. Gating it on
execution keeps the convenience and restores the guarantee.

Tracing execution to decide which branch ran was also rejected. It would make attribution
exact, at the cost of an interpreter-level hook on every call in a library that must be
cheap enough to leave enabled. The residual coarseness is documented instead, in the same
terms as `credit_bound=True`.

## Scope and exclusions

Covers when the credit is recorded and which functions can be analysed. Excludes
per-branch precision, which is pinned by a test as a known limitation rather than fixed.

## Acceptance criteria

Met by the commit closing this record:

- nothing is credited until the function runs, and the credit happens inside a scope, so
  the provenance tree records the caller, which it did not before;
- attribution is by qualified name, so two methods called `run` stay apart;
- a method is analysed like any other function;
- a function that matches nothing is returned untouched, and an unreadable source reports
  `ACKREDIT-W010` and costs the caller nothing;
- the feature is documented in the user guide for the first time;
- `tests/test_inspection.py` covers all of it, verified by reverting each fix separately:
  removing the dedent fails three tests, restoring import-time crediting fails six.
