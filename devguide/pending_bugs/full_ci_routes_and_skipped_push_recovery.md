---
summary: Protect full CI routes and recover skipped direct pushes.
issue: uibcdf/ackredit#74
status: partial
opened: 2026-09-30
closed:
severity: medium
verification: inspected
area: [ci, governance]
guard: tests/test_ci_backlog.py
normative:
blocked_by: []
supersedes: []
---

# Full CI routes and skipped-push recovery

## What

**Current range correction (2026-10-02):** uibcdf/ackredit#80 and the
maintainer's suite-wide requirement supersede the earlier instruction to
leave 3.14 outside the supported source contract. Source `e4a006a` now has
required four-minor CI and ordinary 3.14 installation; routine run
`37073478950`, policy `37073479396`, full eight-cell matrix `37074118479`,
and zero-debt recovery probe `37075039313` pass. The recovery watermark
requires actual successful 3.14 execution. Main has seven strict checks,
including Linux 3.14, with the internal administrator route preserved.
The original evidence below remains the history of the narrower rollout;
public artifact qualification still belongs to #80, not this CI-route issue.

At `7233f67`, full push/PR CI covers Linux Python 3.11–3.13 and macOS 3.13;
the weekly matrix covers Linux/macOS 3.11–3.13. Unsupported 3.14 cells
are tolerated inside those workflows. `main` has no branch protection and
skipped direct pushes have no daily recovery route.

The [push CI](https://github.com/uibcdf/ackredit/actions/runs/36349576188)
passed. The later [weekly matrix](https://github.com/uibcdf/ackredit/actions/runs/36415326167)
failed macOS 3.13 in
`tests/test_persistence_cost.py::test_crediting_one_more_caller_costs_the_same_at_ten_thousand`:
0.7 microseconds per call against no callers became 2.4 against 5,000.
This existing component performance result remains visible and is not
repaired by a CI-routing change.

## How

Preserve required supported-minor coverage and the Conda dependency route.
Move 3.14 to `python314_feasibility.yaml`, dispatch-only with two platform
cells and no tolerated failures. Keep `requires-python >=3.11,<3.14`.
Required workflows contain only supported, gating cells; environment and
installation guards retain the original interpreter-admission protection.

Use explicit `macos-15` arm64 runners and assert their architecture in the
full and feasibility workflows. Stagger weekly coverage at Monday 05:23
UTC. Add daily conditional recovery at 01:31 `America/Mexico_City`, plus a
manual detector probe. Recognize successful full Linux coverage from
supported push/manual CI or the periodic matrix, requiring every supported
minor's actual test step. Probes, failures, other branches, PRs and the
feasibility workflow cannot clear debt. Uncertain history runs the full
matrix; a later successful full push can clear existing skip debt.

Require existing Ruff, documentation and supported Linux/macOS routine
checks, plus explicit PR integration for external changes. Administrators
`dprada` and `LMMV`, the only current collaborators, retain direct pushes.

## Why

Implements `uibcdf/molsyssuite#39` with visible outcomes and preserves the
component's support promise. An unsupported minor must not make an otherwise
green required workflow hide its own failure or silently expand the support
claim under `uibcdf/molsyssuite#29`.

## What was refuted

A configured daily cron is not recovery evidence. A probe with omitted
tests is not a full watermark. Branch-filtered API run listings returned
old evidence in other members, so filtering is local. Packaging metadata
and a single representative macOS lane cannot certify published artifacts.

## Scope and exclusions

Owns CI routing, required checks and skipped-push recovery. Runtime behavior,
performance assertions, citation semantics, platform publication claims and
Python 3.14 admission remain separate component or suite decisions.

## Acceptance criteria

- Full supported suites gate external PRs and administrators retain direct pushes.
- Supported workflows have no unsupported or tolerated test cells.
- Manual 3.14 feasibility preserves its actual success or failure.
- Hosted probes demonstrate zero debt, skipped debt and recovery after a green matrix.
- All six required Linux/macOS full cells execute, with architecture checks.
- Actual daily execution, hosted PR enforcement and publication claims are reviewed.

## Resolution

The initial local suite passed 1,381 tests with one wheel-build skip because
isolated build dependencies were unavailable in the restricted environment.
The updated suite reran with build-dependency access and passed all 1,390
tests, including the wheel check, with no skips. Ruff, generated report
indexes and central repository conformance also passed.

At `2bb6967`, [CI](https://github.com/uibcdf/ackredit/actions/runs/36692957081)
passed all six mandatory Ruff/documentation/supported-test jobs, and the
[suite policy](https://github.com/uibcdf/ackredit/actions/runs/36692957976)
passed. The [initial probe](https://github.com/uibcdf/ackredit/actions/runs/36693051220)
recognized executed full push CI at `2bb6967`, found zero skipped commits
and omitted heavy jobs. `main` now explicitly requires PRs with zero
mandatory approvals and the six strict checks, while administrators retain
direct pushes. The [manual 3.14 feasibility run](https://github.com/uibcdf/ackredit/actions/runs/36693052801)
passed both Linux and macOS arm64 cells at `2bb6967`; this is exploratory
evidence and does not admit 3.14 or change the package support range.
Documentation push `abce1b0` deliberately used `[skip ci]`; GitHub accepted
it with explicit PR and six-check bypass notices. The
[debt probe](https://github.com/uibcdf/ackredit/actions/runs/36694080410)
found exactly one skipped commit since executed full CI at `2bb6967` and
omitted heavy jobs. The [required manual full matrix](https://github.com/uibcdf/ackredit/actions/runs/36694709030)
passed all six Linux/macOS cells at `abce1b0`, including the actual
interpreter/architecture assertions and full pytest steps. The decision job
was intentionally skipped for this unconditional manual matrix. GH Run
Receptor preserved GitHub success; native job/step evidence separately
verified execution of all six cells.
The [recovery probe](https://github.com/uibcdf/ackredit/actions/runs/36695131397)
recognized `abce1b0` as the new full watermark, found zero skipped commits
and omitted heavy jobs. Final local validation passed all 1,453 collected
tests with no skips. Keep this issue open until actual daily execution,
hosted PR enforcement and publication reviews complete.
