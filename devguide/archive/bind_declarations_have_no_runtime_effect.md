---
summary: bind() stored declarations that nothing ever read, leaving half the model inert.
issue: uibcdf/ackredit#1
status: resolved
opened: 2026-09-20
closed: 2026-09-20
severity: medium
verification: reproduced
area: [core, registry]
guard: tests/test_bindings.py
normative:
blocked_by: []
supersedes: []
---

# bind() declarations have no runtime effect

## What

`Registry.bindings` was write-only state. `bind()` appended target-to-item
declarations and nothing read them back: no public accessor existed, and neither
`Collector` nor any renderer in `flowcite/formats/` consumed them.

FlowCite documents a two-half model — static registration of what *could* be cited,
dynamic tracking of what *was* cited. The second half worked. The first half stored
data that never left the dictionary.

## How

Reproduced by running the declaration path without an explicit `track_item`:

```python
register_item(id="p:1", type="article", title="Bound paper")
bind("mylib.run", ["p:1"])


@scoped_usage("mylib.run")
def run():
    pass


run()
get_used_items()  # -> {}
```

A repository-wide search for readers confirmed the diagnosis: `bindings` appeared
only in its own definition, in `bind()` itself, and in one assertion in
`tests/test_registry.py`. No product code path referenced it.

## Why

`bind()` appears in `README`, `SPEC.md`, `ROADMAP.md` and `DEVELOPER_GUIDE.md` as one
of the two halves of the model. A host library could declare bindings across its
entire API and receive nothing, with no error and no warning.

Severity is medium rather than high because the documented flows also call
`track_item`, and those worked. The failure was silent inertness, not broken
behaviour.

## What was refuted

The first diagnosis, that the flow taught by `DEVELOPER_GUIDE.md` and `ROADMAP.md`
produced no citations at all, was wrong. Those documents do call `track_item` inside
the function body, and that flow was verified to work. The defect is narrower: the
declarations themselves had no consumer.

Making `scoped_usage` credit bound items unconditionally was also rejected. `SPEC.md`
section 5 names per-branch decisions as the difference from a plain
"function used, therefore cite everything" mapping. Automatic crediting would report
items a run never needed and erase that distinction.

## Scope and exclusions

Covers the runtime meaning of `bind()` and the API needed to use it. Excludes
reporting of declared-but-unused items, which would be a separate coverage feature,
and excludes the thread-safety of the surrounding scope state.

## Acceptance criteria

Met by commit `cb24ed2`:

- `Registry.bound_items(target)` and `flowcite.bound_items(target)` read declarations
  back, returning a copy so callers cannot mutate the registry;
- `Collector.credit_bound(target)` and `flowcite.credit_bound(target)` credit every
  bound item and return the ids credited;
- `scoped_usage(target, credit_bound=False)` and `scope(name, credit_bound=False)`
  make crediting opt-in;
- the default still credits nothing, held by
  `tests/test_bindings.py::test_scoped_usage_does_not_credit_bindings_by_default`;
- `tests/test_bindings.py` covers introspection, the copy guarantee, coexistence with
  conditional `track_item`, the no-op and idempotent cases, the context manager, and
  that credited bindings reach the provenance tree.

## Correction (2026-09-20)

The repository was renamed from `flowcite` to `ackredit` after this record was
archived. The owning issue keeps its number and is now `uibcdf/ackredit#1`; the
front matter was updated to follow that identity. The analysis above is left as
written, because the defect it describes occurred under the former name and
rewriting it would misstate the history.
