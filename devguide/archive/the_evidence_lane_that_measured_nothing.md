---
summary: The non-blocking Python 3.14 lane died in the solver, so a green run carried a lane that had measured nothing.
issue: uibcdf/ackredit#64
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: medium
verification: reproduced
area: [tooling, packaging]
guard: tests/test_workflow_hygiene.py
normative:
blocked_by: []
supersedes: []
---

# The evidence lane measured nothing, and the run was green

## What

The Python 3.14 lane added in `uibcdf/ackredit#63` failed in `Setup conda env`:

```
error libmamba Could not solve for environment specs
    ├─ python =3.14 * is requested and can be installed;
    └─ python >=3.11,<3.14 * is not installable because there are no viable options
```

The lane passed `create-args: python=3.14` while handing micromamba
`devtools/conda-envs/test_env.yaml`, which pins `python >=3.11,<3.14`. Because
the lane is `continue-on-error`, the run's own conclusion was `success`, and
`gh run-receptor inspect` reported the run, not the tolerated job: `PASS
conclusion=success | jobs=5/6`. The lane existed to produce evidence and
produced none, while looking like it had.

That second part is a limitation of the sibling tool, not of this repository,
and is filed there as `uibcdf/gh-run-receptor#51`: the JSON report carries
`job_counts.failure` and the job's failed steps, and the human report lists
every job, but the LLM report returns a single header line for a `PASS` and
never reaches the section that would name a failed job.

A second cause sat behind the first: `requires-python` is `>=3.11,<3.14` and
`pip install . --no-deps` honours it, so the install step would have failed too.

## How

`devtools/conda-envs/test_env_next.yaml` holds the evidence lane's environment,
identical to the contract environment but for the interpreter, and the workflow
chooses between the two on `matrix.experimental`. The install step passes
`--ignore-requires-python` in that lane alone — the same bypass the local
3.14.7 run reported in `uibcdf/molsyssuite#29` used, now stated in the workflow
instead of in a person's shell history.

The contract did not move. `requires-python` stays `<3.14` until `suite.toml`
names Ackredit.

## Why

The class is wider than this lane: a matrix cell may request an interpreter its
own environment file forbids. On a gating lane that is a loud failure; on a
non-blocking one it is silence that reads as evidence. Nothing checked the two
against each other.

## What was refuted

The first hypothesis was that the uibcdf channel has no 3.14 builds of the
siblings, which would have made the upstream evidence comment wrong. Channel
metadata refutes it: `smonitor 0.16.0`, `depdigest 0.11.0` and `argdigest
0.13.0` each declare `python >=3.11,<3.15`. The solver never reached them; it
failed on the interpreter alone. The local 1366-test 3.14.7 result stands, and
missed this because it named its packages on the command line rather than using
this file.

## Scope and exclusions

Only the lane's ability to run. Whether Ackredit may claim `>=3.11,<3.15`
remains with `uibcdf/molsyssuite#29`, and no metadata here changed.

## Acceptance criteria

`tests/test_workflow_hygiene.py` holds that every matrix cell's interpreter is
admitted by the environment file that cell uses — which reproduces this failure
locally — that the evidence environment differs from the contract environment
only in the interpreter, and that `--ignore-requires-python` appears in the
experimental lane and nowhere else.
