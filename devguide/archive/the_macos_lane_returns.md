---
summary: CI ran on Linux only after the dependencies stopped forcing it; macOS is back, gating on 3.13 and weekly on 3.11 to 3.14.
issue: uibcdf/ackredit#71
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: medium
verification: reproduced
area: [ci]
guard: tests/test_workflow_hygiene.py
normative:
blocked_by: []
supersedes: []
---

# The macOS lane returns

## What

CI ran on Linux only. The macOS lane had been removed because `smonitor` and `depdigest`
were published as `linux-64` builds with per-interpreter ABI pins, which no macOS
environment could solve. By 0.8.0 the floors Ackredit requires — `smonitor 0.16.0`,
`depdigest 0.11.0`, `argdigest 0.13.0` — were `noarch` in the channel, verified against
its repodata, and the lane had not come back.

The weekly `CI_full_matrix.yaml` had lost its purpose too: since `uibcdf/ackredit#63`,
`CI.yaml` runs 3.11 to 3.13 on every push, and the weekly run repeated it exactly.

## How

The weekly workflow is now the operating-system matrix: Linux and macOS on 3.11 to 3.13,
and 3.14 on both as the non-blocking evidence lane `CI.yaml` already had. `CI.yaml` gains
a gating macOS lane on 3.13, so a platform regression shows on the push that causes it.

The workflow guards read only `CI.yaml`, so the defect of `uibcdf/ackredit#64` — a lane
asking for an interpreter its environment forbids — could have returned in the weekly
file unseen. They now find every workflow with a Python matrix and check each. A lane is
experimental exactly when its version is outside the contract, which allows an extra
operating system for a promised version and refuses a gating lane on an unpromised one.

## Why

Ackredit's risks on macOS are specific: the session journal relies on `O_APPEND`
atomicity with tests that write from several processes, `multiprocessing` starts with
`spawn` there rather than `fork`, and temporary paths pass through `/var` →
`/private/var`.

## What was refuted

That the lane would need work to pass. The first run, dispatched before anything gated on
it (run 35783947461), passed all eight cells with 1437 tests and the same six skips on
both systems. `tests/test_session_sharing.py`, the multi-process journal tests, has no
skip path, so it ran there. The expected platform problems did not appear.

## Scope and exclusions

Windows has never been run and is not claimed. Adding it is a separate decision.

## Acceptance criteria

The weekly matrix passed on macOS for every version before the gating lane landed, each
job inspected rather than the run's conclusion alone. Against a weekly file that gave 3.14
the contract environment, `tests/test_workflow_hygiene.py` fails naming that file, as it
does for `CI.yaml`.
