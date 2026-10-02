---
summary: Adopt required Python 3.14 support and qualify ordinary installed delivery
issue: uibcdf/ackredit#80
status: active
opened: 2026-10-02
closed:
verification: inspected
area: [compatibility, packaging, ci, governance]
guard:
normative:
blocked_by: []
supersedes: []
---

# Required Python 3.14 support

## What

All MolSysSuite Python packages must adopt Python 3.11–3.14 under the
maintainer's 2026-10-02 decision, coordinated by uibcdf/molsyssuite#29 and
uibcdf/molsyssuite#51. Ackredit also blocks Sabueso's required dependency
closure under uibcdf/sabueso#108. Source `6420407` still excludes 3.14 and root
instructions deny authorization, despite earlier source feasibility.

## How

The source contract now declares `>=3.11,<3.15`. The noarch recipe, ordinary
development/test/documentation environments, full Linux routine/PR matrix,
weekly/recovery Linux/macOS arm64 matrix and root instructions agree. Python
3.13 remains the routine development interpreter. The existing explicit 3.14
workflow becomes ordinary installed validation without
`--ignore-requires-python`; its filename retains historical run identity.

The recovery detector requires an executed successful 3.14 test job before
advancing its watermark. Historical three-minor matrices no longer clear debt.
Existing direct maintainer pushes, PR routes, schedules and scientific/runtime
assertions are preserved. The shared policy caller adopts the new immutable
`policy-v1.5.3`; synchronized guides are distributed by the central tool.

## Why

The narrower provider metadata prevents normal installation in a consumer
environment on Python 3.14. An instruction that treats 3.14 as unauthorized
would perpetuate that incompatibility. Cohort membership cannot waive the
common requirement; qualification and public delivery still need evidence.

## What is measured and what is assumed

Prior run `36693052801` passed both Linux/macOS feasibility cells at `2bb6967`,
but bypassed Requires-Python. It authorizes migration, not ordinary public
delivery. New hosted and local results are recorded below as obtained. No
artifact publication or installed public 3.14 closure is inferred from a
source metadata edit.

## What was refuted

Keeping 3.14 only in a non-claiming experimental lane contradicts the new
common requirement. Using `--ignore-requires-python` conceals an incompatible
provider declaration and is not an installed-support gate.

## Scope and exclusions

Interpreter contract, packaging/CI alignment and qualification only. Runtime
or performance defects remain visible and are owned separately; tests are not
weakened to make this migration green. Public distribution remains coordinated
with uibcdf/ackredit#22 and the portable API work in uibcdf/ackredit#75.

## Acceptance criteria

- Full relevant tests and normal installed-package smoke pass on Python 3.14
  against the candidate, without metadata overrides.
- Metadata, recipe, environments, required CI, recovery watermark and
  contributor instructions agree on the four-minor source contract.
- A released build with the portable API is normally installable in the
  consumer's required closure; record channel/artifact and fresh clean-install
  evidence before central admission or a delivered-support badge.
- Preserve full-suite failure visibility and the internal direct-push route.

Potential durable guards are the workflow/environment contract checks and
`tests/test_ci_backlog.py::test_a_previous_three_minor_matrix_cannot_clear_314_debt`.
The issue remains open until its public-delivery acceptance is met.

## Local implementation checkpoint — 2026-10-02

The isolated ordinary wheel installation on Linux/Python 3.13.15 passes all
1,530 tests (`python -m pytest --receptor=llm`, 32.08 seconds), with no skips.
The clone's complete version history and an isolated installation were needed
to avoid comparing a pre-existing system package with a shallow checkout.
Ruff lint/format (197 files), report indexes and the current suite conformance
check pass. Central governance passes 272 tests and five focused admission/
ecosystem tests. This is local regression evidence on 3.13, not new 3.14
execution or public artifact verification.

## Hosted source qualification — 2026-10-02

Exact source `e4a006a6931f3fb5f97be5b09767c144dfb35662` passes routine CI
`37073478950`, shared policy `37073479396` at immutable `policy-v1.5.3`,
and full matrix `37074118479`. All eight Linux/macOS arm64 Python 3.11–3.14
jobs actually execute normal installation, the off-checkout import,
interpreter/architecture assertions and the full test step successfully.
GH Run Receptor reports eight successful test jobs; native job/step evidence
confirms those executions. The decision job is intentionally skipped during
unconditional full dispatch and is not counted as test evidence.

The existing six strict branch checks remain app-bound; the successful Linux
3.14 test is added as the seventh required check. Administrator bypass is
preserved. Recovery probe `37075039313` executes the decision and reports zero
pending skipped commits since the new four-minor source watermark `e4a006a`;
the matrix is omitted intentionally. Historical three-minor evidence is no
longer accepted by the detector.

Source/installed qualification is now demonstrated on both tested platforms.
Public delivery of the portable API and independent consumer closure remain
pending under this issue and #22/#75. No public artifact or admission claim is
added. Platform coordination is communicated through uibcdf/moli#37.
