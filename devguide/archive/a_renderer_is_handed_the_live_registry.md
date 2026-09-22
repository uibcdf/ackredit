---
summary: report passed the registry itself to a renderer, and options reached the latex format by name and were dropped for every other.
issue: uibcdf/ackredit#53
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: high
verification: measured
area: [api, formats]
guard: tests/test_format_plugins.py
normative: docs/content/about/stability.md
blocked_by: []
supersedes: []
---

# A renderer is handed the live registry

## What

**A renderer could empty the registry.**

```python
def vandal(used, items):
    items.clear()
    return "gone"

ackredit.register_format("vandal", vandal, "txt")
ackredit.report(format="vandal")
# items in the registry afterwards: 0
```

`used` was a copy, built fresh by `get_used_items`. `items` was `Registry.items` itself, so
since `uibcdf/ackredit#36` made formats extensible, a third party was handed a mutable
reference to the declarations every later report depends on.

**An option meant for one format was dropped by another.** The dispatcher read
`if canonical == "latex": return render(used, items, **kwargs)`, so
`report(format="bibtex", style="unsrt")` succeeded and discarded the option — a request
returning a report that is not the one asked for, which is `uibcdf/ackredit#15`.

**A mistyped option was a traceback from inside the renderer**, naming `render()` rather
than the format, and not a catalog diagnostic.

## How

The registry is wrapped read-only at both levels, because a proxy over the mapping alone
still lets an item be written through it. The format name is gone from the dispatcher: any
renderer may take options, which is what a plugin needs, and the options are bound against
the renderer's signature before it is called, so one that does not take them refuses with
`ACKREDIT-E007` and says what it does accept.

What a renderer is handed is now written on `register_format`: a copy of the used map, a
read-only registry, and the fact that an id in `used` need not be in `items` — a host may
credit an id it never declared, and every built-in reports it with the id as its own title.

## Why

This was the whole of why `register_format` was provisional: "what a renderer is handed is
the shape the built-in renderers take, and that shape is what would change". It was not a
shape anyone had chosen; it was what the dispatcher happened to pass, including a special
case for one format by name.

## What was refuted

- **Copying the registry for each report.** It freezes the values as well and costs a copy
  per item per report, to prevent something a proxy prevents for the price of one object.
- **Leaving `items` mutable and documenting that renderers must not write.** A document is
  not a boundary, and the renderer may come from a package we have never seen.
- **Catching the `TypeError` from calling the renderer.** A `TypeError` raised inside the
  renderer for an unrelated reason would be reported as a bad option. Binding the
  signature first asks exactly the question.
- **Passing `**options` to every renderer unconditionally.** It would break a plugin
  written as `render(used, items)` the moment any option is passed, rather than telling
  its user that the format takes none.

## Acceptance criteria

- a renderer can neither empty the registry nor rewrite an item through it — met;
- writing to the used map changes nothing — met;
- an id credited but never declared still reaches a renderer — met;
- a plugin may take options, an option a format does not take is refused by name, and the
  option that already worked still does — met;
- `tests/test_format_plugins.py` guards it: 2 of its 37 tests fail when the live registry
  is passed again, and 3 when options go by format name.
