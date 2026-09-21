---
summary: The suite depended on the order its files ran in, so a test could pass for the reason of the test before it.
issue: uibcdf/ackredit#30
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: medium
verification: measured
area: [testing]
guard: tests/test_suite_isolation.py
normative:
blocked_by: []
supersedes: []
---

# Tests share tracking state

## What

`tests/test_csl_json.py` asserted on `report(format="csl-json")[0]` for an item it had
registered itself. The session is process-wide, so that entry is the first item *any* test
tracked. Adding `tests/test_citation_authority.py`, which sorts between `test_cff` and
`test_collector`, changed the order and the assertion read `paper:1`, tracked by
`tests/test_collector.py`.

The opposite problem was live at the same time. Seven files called `Registry.items.clear()`
directly. The registry holds declarations, made once at import, and
`tests/test_example_libraries.py` relies on the ones `examples/dummy_solver` and
`examples/dummy_pipeline` make when imported. Emptying the registry destroys them for
everything that runs afterwards, and they cannot be remade because the import already
happened. It worked only while those files happened to sort last.

## How

`tests/conftest.py` isolates the two halves of the state the way the library separates
them:

- the **session** is per run, so it is cleared around every test, always;
- the **registry** holds declarations, so it is left alone unless a test asks for
  `clean_registry`, which empties it and puts it back.

The seven files were converted to the fixture, including two that cleared the registry
inline inside a test body.

## Why

A suite that shares state reports failures in files that are not at fault — that is the
visible half, and it costs the time spent reading the wrong file. The invisible half is
worse: a test that passes because of what ran before it is not testing anything, and
nothing says so. `test_csl_json` had been in that state for as long as it existed.

Found while adding the guard for #28. The new file changed nothing about the library and
broke a test three files away, which is the signature of this defect.

## What was refuted

- **Clearing the registry around every test too.** It is the obvious symmetry and it is
  wrong: the import-time declarations cannot be remade, so the first test to import an
  example library would be the last one able to see it. Measured — two tests in
  `test_example_libraries.py` failed exactly that way.
- **Snapshotting the registry before each test and restoring after.** Same failure, for a
  subtler reason: a test that triggers the first import of a library registers items the
  snapshot does not contain, so the restore removes them and the next import is a no-op.
- **`pytest-randomly` to shuffle order in CI.** It would find this class continuously,
  and it turns a deterministic suite into one whose failures need a seed to reproduce.
  Worth reconsidering once the suite has no known order dependence; it is not the fix for
  one.

## Scope and exclusions

Covers the tracking state Ackredit holds process-wide. Fixtures owning files, environment
variables or `sys.path` were already scoped by pytest.

## Acceptance criteria

- the suite passes with its files run in reverse order — met, 707 tests;
- no test empties the registry by hand — met, enforced per file by
  `tests/test_suite_isolation.py`.
