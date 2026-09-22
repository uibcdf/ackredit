---
summary: CI ran Python 3.13 alone while the contract promised 3.11 to 3.13, so two of the three had never been executed.
issue: uibcdf/ackredit#63
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: medium
verification: measured
area: [tooling, testing]
guard: tests/test_workflow_hygiene.py
normative:
blocked_by: []
supersedes: []
---

# CI runs one of three versions

## What

`pyproject.toml` declares `requires-python = ">=3.11,<3.14"` and `MOLSYSSUITE_GUIDE.md`
says CI covers 3.11, 3.12 and 3.13. `.github/workflows/CI.yaml` pinned
`python-version: "3.13"` in every job and declared no matrix.

Two of the three versions Ackredit promises had never been run by anything. A syntax or a
behaviour that needs 3.13 would have shipped to a 3.11 user and been found by them.

Measured by hand, in an environment built the way `devtools/conda-envs/test_env.yaml`
describes:

```
Python 3.11.16     1366 passed
Python 3.14.7      1366 passed
Python 3.13.14     1366 passed
```

The library was fine. What was missing was anything that kept it so.

## How

A matrix over the versions the contract names, derived by passing the version to the conda
solver rather than repeating the range in a second place.

3.14 is in the matrix as a **non-blocking** lane, marked evidence for
`uibcdf/molsyssuite#29`, which asks for component-specific evidence before a component may
claim `>=3.11,<3.15`. It makes that evidence continuous instead of a snapshot from one
machine, and catches a regression on the day it appears rather than on the day
authorization arrives.

**It claims nothing.** `requires-python` stays at the default contract until `suite.toml`
names Ackredit, which is not this repository's to decide. The guard holds that apart: the
promised list must equal the contract, and an experimental entry must be outside it and
must not gate a merge. Moving 3.14 into the promised list without moving the contract fails
a test.

## Why

Asking for a wider range while not covering the current one is weak ground, and that is the
smaller reason. The larger one is that a promise nothing exercises is not a promise; it is
a sentence in a file.

Found while answering whether Ackredit could adopt 3.14, which is the kind of question that
makes you read what you already claim.

## What was refuted

- **Adding 3.14 to the promised list now.** The evidence is posted and the authorization is
  not ours: only components `suite.toml` names may claim the wider support. Claiming it
  because the tests pass would be deciding a suite rule in a component.
- **A separate workflow for the experimental lane.** It would drift from the one that runs
  the supported versions, which is how the single pinned version survived in the first
  place.
- **Leaving 3.14 out until authorization.** Then the evidence stays a snapshot from one
  machine on one day, and the first thing anyone asks of evidence is whether it still
  holds.

## Acceptance criteria

- the matrix equals the versions `requires-python` promises, derived from it rather than
  written twice — met;
- an experimental version is outside the contract and does not gate a merge — met;
- both guards fail when the matrix shrinks back to one version and when an experimental
  lane moves into the contract.
