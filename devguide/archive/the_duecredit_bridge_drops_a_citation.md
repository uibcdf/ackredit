---
summary: A tracked item that was never registered was skipped on export, the one path in the library that dropped a citation silently.
issue: uibcdf/ackredit#47
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: medium
verification: measured
area: [contrib]
guard: tests/test_duecredit_bridge.py
normative:
blocked_by: []
supersedes: []
---

# The DueCredit bridge drops a citation

## What

```python
item = items.get(item_id)
if not item:
    continue
```

Every other renderer reports a tracked item that is not in the registry: `bibtex` emits a
minimal `@misc`, and `markdown`, `json` and `csl-json` use the id as the title. This was the
one path in the library that dropped a tracked citation and said nothing, which the
diagnostics policy does not allow.

A host reaches that state by calling `track_item` for an id it has not declared — a typo,
or a declaration that moved.

## How

The item is handed over with what is known, as the other formats do.

## Why

The bridge exists so the two systems agree about what a run used. Disagreeing quietly is
worse than not bridging at all.

## What was refuted

- **Reporting the unregistered item as a diagnostic instead.** The other renderers do not,
  and a citation that is merely undeclared is not a failure; handing it over with its id is
  what the rest of the library already does.

## Stated, not changed

`path` is built as `"ackredit." + item_id`, so a citation arrives at DueCredit under
`ackredit.numpy:paper:2020`. In DueCredit a `path` is the module or object a citation is
attributed to, which would mean its summary shows everything as belonging to Ackredit
rather than to the packages being cited — the provenance this bridge exists to carry — and
a colon is not valid in a module path. It is recorded rather than changed, because it
depends on DueCredit's behaviour and that has not been verified against it.

## Also found

Faking an optional dependency leaks. DepDigest memoises `is_installed` with an `lru_cache`,
which is right for a library — a package does not appear mid-run — and wrong for a test
that makes one appear: the first version of these tests left every later test believing
duecredit was installed, so `tests/test_optional_surface.py` met a real `ImportError`
instead of the diagnostic. The fixture clears that cache on the way in and on the way out,
and the suite passes with its files in reverse order.

## Scope and exclusions

Covers which citations are handed over. The stand-in in the guard records what it is given;
what DueCredit does with it is DueCredit's.

## Acceptance criteria

- every tracked item is handed over, registered or not — met;
- an item with a DOI arrives as a `Doi` and one without as `BibTeX` — met;
- one item failing does not cost the others, which `ACKREDIT-W013` promises — met;
- `tests/test_duecredit_bridge.py` guards it, 6 tests, 2 of which fail when the item is
  skipped again.
