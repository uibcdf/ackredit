---
summary: A recursive function made the provenance report come out empty, and a cycle below a root raised RecursionError.
issue: uibcdf/ackredit#46
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: high
verification: measured
area: [formats]
guard: tests/test_provenance_cycles.py
normative:
blocked_by: []
supersedes: []
---

# A cycle empties the provenance report

## What

`devguide/vision.md` calls this "Hierarchical Provenance: see exactly *why* a citation was
triggered". A recursive function made it show nothing:

```python
@scoped_usage(target="lib.fib")
def fib(n):
    track_item("a:1")
    return n if n < 2 else fib(n - 1) + fib(n - 2)
```

```
tree:       {'lib.fib': {'items': ['a:1'], 'children': ['lib.fib']}}
provenance: # Citation Provenance Graph        <- and nothing else
```

Entering `scope("lib.fib")` inside itself records the target as its own child, so no target
was left that nobody calls, `roots` was empty and nothing was walked. Two mutually
recursive functions did the same.

With the cycle below a root that does exist, `walk` followed it forever:

```
tree: {'top': ['b'], 'b': ['c'], 'c': ['b']}
provenance: RecursionError: maximum recursion depth exceeded
```

## How

The renderer carries the path walked so far, and a target already on it is drawn as
`target (above)` rather than followed — the recursion stays in the report, which is part of
why the citation happened, without being unrolled.

`_entry_points` returns the targets nobody calls, and then anything those cannot reach. A
graph that is all cycle has no uncalled target at all, and is drawn from its smallest
member instead of vanishing.

## Why

The graph is not a tree and never was; the renderer assumed one twice. Recursion is
ordinary in scientific code, and this is the format that carries the library's own claim
against a plain citation list. One failure mode was silent and the other ended the report.

## What was refuted

- **Refusing to record a target as its own child.** It would fix the recursive function at
  the source and not two functions that call each other, which is the same cycle one step
  longer. The renderer has to be total for any graph, so that is where it is made total.
- **Dropping a repeated target silently.** The repetition is information: a report that
  shows `lib.fib` reaching itself says something true about the run.
- **A global visited set instead of the walked path.** It prevents the recursion and also
  stops a target appearing under two different callers, which is the ordinary case and
  exactly what the provenance is for.

## Scope and exclusions

Covers the renderer. What the collector records is unchanged.

## Acceptance criteria

- a recursive function, two mutually recursive ones and a cycle below a real root are all
  drawn, and the report is finite — met;
- every target appears somewhere, including one no root can reach — met;
- an ordinary tree renders exactly as before, asserted against the whole string — met;
- `tests/test_provenance_cycles.py` guards it: 5 of its 8 tests fail when the path is not
  carried, and 3 when the unreachable targets are not entered.
