---
summary: Protect full CI routes and recover skipped direct pushes.
issue: uibcdf/ackredit#74
status: resolved
opened: 2026-09-30
closed: 2026-10-04
severity: medium
verification: measured
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

## Python 3.14 adoption update (2026-10-02)

The candidate under uibcdf/ackredit#80 expands the required Linux matrix to
3.11–3.14 and the periodic Linux/macOS arm64 matrix to eight cells. The
historical manual filename remains available, but its candidate implementation
now verifies normal installed-package use without a metadata override. It still
cannot clear full-matrix debt. The recovery detector now requires an executed
3.14 test cell too; the regression
`tests/test_ci_backlog.py::test_a_previous_three_minor_matrix_cannot_clear_314_debt`
rejects a green historical three-minor matrix as a complete recovery watermark.
Central authorization and public admission remain tracked in MolSysSuite #29
and Ackredit #80. Earlier evidence above retains its original support boundary.

## Routine policy 1.5.4 adoption — 2026-10-03

The maintainer authorized publication and adoption of policy-v1.5.4 under
uibcdf/molsyssuite#39. The immutable tag points to central e459ea0; the
component now calls that published gate and receives the byte-identical
canonical guide through the suite synchronizer. Routine development uses
Python 3.14. The existing full Python 3.11–3.14 matrices and skipped-commit
recovery semantics are preserved; no public package is published here.
Local conformance and changed-workflow Actionlint checks pass. Hosted
policy and applicable routine checks are dispatched separately from skipped
direct pushes; their exact commits and outcomes remain to be measured.

The additional routine macOS arm64 lane, quality job and documentation
build use 3.14. Linux still tests every supported minor on PRs, and the
weekly matrix retains every supported minor on Linux and macOS.


## Current scope and closure review — 2026-10-04

The original three-minor feasibility and six-cell criteria above are retained
history. Ackredit #80 delivered the required Python **3.11–3.14** range, ordinary
3.14 installed validation and an **eight-cell** Linux/macOS arm64 full matrix.
All supported test cells are gating; no metadata override or tolerated failure
is used. Central admission remains MolSysSuite #51's separate owner decision.

The remaining scheduled and PR-route review now has hosted evidence:

- [Scheduled recovery 37016646381](https://github.com/uibcdf/ackredit/actions/runs/37016646381), source `2e9f5091a449b8c01ffaf11a46d3d51cefd211bb`, actually detects **six skipped commits** since watermark `7277bd5241a18c15c0fa9eb8e7acc98ce1332c90` and executes all six then-supported Linux/macOS cells. Every `Run tests` step succeeds. Its three-minor scope is preserved rather than relabeled as a 3.14 result.
- [Scheduled zero-debt decision 37123561413](https://github.com/uibcdf/ackredit/actions/runs/37123561413), source `1863f33af465b3c3fa66fe6ea4cb466141ffcd8d`, recognizes its successful full watermark and detects zero omitted commits. The detector executes; scientific jobs are intentionally skipped.
- [Fresh detector probe 37182979403](https://github.com/uibcdf/ackredit/actions/runs/37182979403) executes on current `main` source `a8219b86e85f9b9fc29e8bfee7982040ffe27215`. It independently recognizes that source's full Linux push coverage, reports zero skipped commits and omits scientific jobs. A probe is not itself a recovery watermark.
- [Actual PR CI 37066492857](https://github.com/uibcdf/ackredit/actions/runs/37066492857) executes for PR #79 at `561989e5dfa0c48e172440b0f130a1efae961e95`; all six then-required jobs and four scientific test steps pass. This is historical PR execution with its original range, not a new four-minor external merge qualification.

Published GH Run Receptor inspects all four executions. Native identity/step
projections and the detector's bounded decision line establish the facts its
compact verdict omits. The [committed CI receipt](../../devtools/receipts/ci_recovery_74_2026-10-04.json)
retains these observations and the current branch-protection snapshot.

Current `main` requires the seven stable Ruff/documentation/Linux 3.11–3.14/
macOS 3.14 checks with strict status enforcement and an explicit PR requirement;
zero approving reviews are mandated. Force pushes and branch deletion are
disabled. Administrators are exactly `dprada` and `LMMV`; administrator status
enforcement remains disabled, preserving the accepted internal direct-push
route. Earlier authorized pushes retain GitHub's visible bypass notices.
The protected route is reviewed through native configuration and actual hosted
PR execution. No rejected non-administrator merge attempt is claimed.

Current routine [CI 37160043460](https://github.com/uibcdf/ackredit/actions/runs/37160043460)
passes all seven checks at `a8219b8`. The [eight-cell full matrix 37159097254](https://github.com/uibcdf/ackredit/actions/runs/37159097254)
passes at implementation `3c6e77c5d69809da0333786572f1edd4689c611b`, with actual
interpreter/architecture and pytest execution retained separately in #72's
receipt. Its qualification branch does not make it a `main` recovery watermark;
the fresh probe instead uses the executed current push CI. The relevant workflow
and detector content is unchanged between those sources.

Public artifact and installed-platform review is complete under #22/#75/#80:
original producer `598abf993a2409c025de5e912acd7eb45a257ebd`, exact archive
`ackredit-0.9.0-py_0.tar.bz2`, SHA-256
`37661090f6ad19a74b8155d8a4d4b4a068c9099f4ceba0743b3abfe887e97fe1`.
Those separate receipts are not inferred from a cron, PR, policy or probe.

The CI implementation and remaining member-local evidence review are complete.
`tests/test_ci_backlog.py` guards omitted commits remaining due, actual execution
of every supported minor, refusal of historical three-minor watermarks, exclusion
of probe/PR/feature/failure results and conservative recovery on uncertain
history. MolSysSuite #39 owns the central rollout state and future common
pattern enforcement; this closure does not close that suite-wide work.

Closure qualification passes **1,547 Ackredit tests without skips** on Python
3.14.7 with public Pytest Receptor 1.2.1, Ruff lint/format, generated report
indexes and Sphinx `-W`. All nine pre-existing human files remain byte-identical.
No CI/runtime implementation or branch-protection setting changes in this
closure; the existing mechanisms are verified and their remaining evidence is
archived rather than silently inferred.
