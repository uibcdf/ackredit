---
summary: The examples showed Ackredit inside a host library and never from the user's side; a script and a notebook now run a workflow and collect its references.
issue: uibcdf/ackredit#68
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: low
verification: asserted
area: [docs, examples]
guard: tests/test_example_workflow.py
normative:
blocked_by: []
supersedes: []
---

# A workflow from the user's side

## What

`examples/dummy_solver` and `examples/dummy_pipeline` show Ackredit from inside a host,
held by the test suite to the integration guide. Nothing showed it from the other side —
someone who runs an analysis and asks for the references at the end — and the
documentation's "Running them yourself" was a `python -c` one-liner.

## How

`examples/workflow.py` analyses two samples through the example libraries, prints the
report and the provenance, and writes the citation files to `citations/` or a directory
it is given. `examples/workflow.ipynb` is the same analysis in a notebook, with
`summary()` as a table, stored with its outputs. The documentation includes the script
from the file and links the notebook. `devtools/refresh_example_notebook.py`
re-executes the notebook with a real kernel when its outputs need to change.

## Why

Running this workflow is how `uibcdf/ackredit#65` and `#67` were found: both were
invisible from inside a host and obvious from the user's side. Keeping it keeps that view
in the suite.

## What was refuted

A third example library. The two existing ones already cover integration, and a workflow
over them is what was missing. Executing the notebook in the documentation build was also
set aside: `nb_execution_mode` is off, and turning it on would make the build need a
kernel for one page when the test suite can hold the stored output instead.

## Scope and exclusions

The examples remain outside the packaged distribution. They are not a real adoption;
that stays with the roadmap's Theme C.

## Acceptance criteria

`tests/test_example_workflow.py` runs the script as a user would and checks the report
and the files it writes, and executes every notebook cell without a kernel, failing when
a stored output differs from what the cell produces now and naming the refresh command.
It also checks the notebook's claim that rerunning a cell cites nothing twice.
