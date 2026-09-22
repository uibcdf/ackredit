---
summary: The citation plugin loader carried a branch for a Python the package cannot run on, and nothing exercised the promise it makes.
issue: uibcdf/ackredit#54
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: low
verification: measured
area: [core, api]
guard: tests/test_citation_plugins.py
normative: docs/content/about/stability.md
blocked_by: []
supersedes: []
---

# load_plugins asks twice, and is asked nothing

## What

```python
eps = metadata.entry_points()
if hasattr(eps, "select"):
    plugins = eps.select(group="ackredit.citations")
else:
    # Fallback for older versions if necessary
    plugins = eps.get("ackredit.citations", [])
```

`entry_points()` returned a dict before Python 3.10 and an `EntryPoints` object since.
`requires-python` is `>=3.11,<3.14`, so the second branch cannot run, and if it ever were
reached it would raise `AttributeError` rather than fall back — nothing that reaches it has
`.get`. Dead code that fails.

The package also had two entry-point loaders written differently: `ackredit/core/report.py`
asks `metadata.entry_points(group=...)` directly, which is what the supported Pythons
answer.

Nothing exercised the group at all, which was the whole of why the name was classified
provisional.

## How

One way of asking, the modern one, and the promise written on the function: the group name,
that the loaded object is a callable taking nothing, that it is expected to register, bind
or inject, that a failure raises `ACKREDIT-W008` and never propagates, and that loading
twice is safe.

## Why

The rest of the function was sound and that had to be established rather than assumed. It
was, with a stand-in: a pack that registers is loaded, a broken one is reported while the
packs beside it still load, and loading twice has no second effect because `register_item`
overwrites and `add_injection` deduplicates. That last is now stated on the function rather
than left to be discovered.

## What was refuted

- **Loading the citation group lazily and once, as the format group is loaded.** They are
  different promises: a format is needed when a report is asked for, and a citation pack is
  a host's decision about what its run may cite. `load_plugins` is public and explicit for
  that reason.
- **Making the second call a no-op.** It would hide a pack that had been installed since
  the first, for a repetition that costs nothing.

## Acceptance criteria

- a pack that registers is loaded, and several are all loaded — met;
- a pack that fails, and one that cannot even be imported, are reported while the packs
  beside them load — met;
- loading twice has no second effect — met;
- only the citation group is read — met;
- `tests/test_citation_plugins.py` guards it: 7 of its 8 tests fail when the wrong group is
  read, and 2 when a broken pack is swallowed.
