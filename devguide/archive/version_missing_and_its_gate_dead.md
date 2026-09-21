---
summary: The package stated no version, and the CI step checking it printed a traceback on a green run.
issue: uibcdf/ackredit#11
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: medium
verification: reproduced
area: [packaging, tooling]
guard: tests/test_workflow_hygiene.py
normative:
blocked_by: []
supersedes: []
---

# The package states no version, and the CI check for it cannot fail

## What

`ackredit.__version__` did not exist. The workflow step that imports the package from
outside the source tree and prints its version raised `AttributeError` and the job
reported success.

## How

A multi-line `run:` is one shell script and GitHub reads its exit status from the last
command. `bash -l {0}` carries no `-e`, so the failure did not stop the script and
`echo "::endgroup::"` returned zero:

```
603  /home/runner
604  Traceback (most recent call last):
606  AttributeError: module 'ackredit' has no attribute '__version__'
```

Reproduced locally:

```
$ bash -l -c 'echo x; echo "import nonexistent_xyz" | python; echo "::endgroup::"'
exit status: 0
```

## Why

Everything the step checked after its first line was unverified: the import itself,
running from outside the source tree, and the version. A gate that cannot fail is worse
than no gate, because it is counted as coverage.

## What was refuted

Repeating the literal from `pyproject.toml` in `__init__.py` was rejected; the sibling
components read it from installed metadata with a `_version.py` fallback, and two copies
of a version drift.

## Scope and exclusions

Covers this repository's workflows. The same step shape makes the same check unable to
fail in four of the six sibling components; that is reported to `uibcdf/molsyssuite`
because it is theirs to decide, not Ackredit's to fix locally.

## Acceptance criteria

Met by the commit closing this record:

- `__version__` is read from installed metadata, with the fallback the siblings use, and
  is exported;
- every multi-line `run:` in the workflows begins with `set -euo pipefail`;
- `tests/test_workflow_hygiene.py` parses the workflows and fails on any multi-line step
  without it. It found a second dead step, `Info conda`, where a failed
  `micromamba activate` would have left the later steps running in the wrong environment;
- `tests/test_packaging.py` asserts the package states a version.
