---
summary: Adopt required Python 3.14 support and qualify ordinary installed delivery
issue: uibcdf/ackredit#80
status: partial
opened: 2026-10-02
closed:
verification: reproduced
area: [compatibility, packaging, ci, governance]
guard: tests/test_workflow_hygiene.py
normative:
blocked_by: [uibcdf/ackredit#22, uibcdf/ackredit#75]
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

## Independent installed-provider qualification — 2026-10-03


The candidate passes 1,534 tests on the routine Python 3.13 environment and
1,534 tests against a normally installed wheel on Python 3.14.7, with no skips.
Ruff check, Ruff format and generated report indexes pass. The 3.14 wheel was
installed with `pip install --no-deps --no-index`, without a metadata override.
The installed smoke and `pip check` pass from `/tmp`; every checked provider
resolves beneath the fresh environment's `site-packages` directory.

The independent 3.14 Conda environment uses public `uibcdf` builds SMonitor
0.16.0 `py_1`, DepDigest 0.11.0 `py_2` and ArgDigest 0.13.0 `py_1`, plus Python
3.14.7 and PyYAML 6.0.3 from `conda-forge`. Build/versioning/Ruff tools were
installed separately for the development-only checks that initially skipped.
A clean public-dependency Python 3.11.16 environment also resolves successfully.
The source candidate retains `noarch: python`: Ackredit has no compiled payload;
its NumPy dependency is installed separately for the selected interpreter.

Clean implementation commit
[`5f7bf49`](https://github.com/uibcdf/ackredit/commit/5f7bf49012920a70d6b5a22c9dad5fe570c8ac4d)
was rebuilt as wheel `ackredit-0.8.0+46.g5f7bf49-py3-none-any.whl`, SHA-256
`55a71e54962bbbc6e8194c276f6034b85dfe06c0cd6838aeafd0daca83dacb71`.
Normal installations of that same file pass the shared smoke and `pip check`
in fresh public-dependency environments on Python 3.11.16 and 3.14.7. The
installed 3.14 suite passes all 1,534 tests again against this clean artifact.

The [hosted periodic matrix](https://github.com/uibcdf/ackredit/actions/runs/37076447854)
passes all eight Linux/macOS arm64 Python 3.11–3.14 cells at that commit. Native
step evidence confirms installed verification, interpreter/architecture checks
and the full suite actually executed in every cell. Only the conditional
backlog detector is skipped on this unconditional manual dispatch.
[CI](https://github.com/uibcdf/ackredit/actions/runs/37076447646) passes all seven
jobs, including quality, documentation and the five normal installed test cells.
Both reports were inspected with GH Run Receptor.

These are development-wheel and source-installation checks. Central
`policy-v1.5.3` registers Ackredit as `authorized` for this issue and requires
3.11–3.14 across all registered Python packages. Ackredit adopts that caller
and synchronizes its read-only suite guide through the registered central tool.
The central badge generator confirms that the README must retain its previous
three-minor delivery claim until public admission. No public package or admission
is claimed; immutable delivery and receiving-consumer closure remain open.

The merged implementation adds ArgDigest 0.13.0 as the public 3.14 floor, the shared installed-provider smoke, off-checkout full suites, and the four-minor future staging qualification. Concurrent work and prior evidence are retained.


## Real noarch local installation (2026-10-03)

The corrected build-action diagnostic under #22 produces
`ackredit-0.9.0-py_0.tar.bz2`, SHA-256
`99e6f9b9f0a3b0a22c66e476230dddabd2ba0017c59beb3253fbadc781d665c6`,
from prepared source `15b1958b9752a89974bb1d0df882a17841ed62b4`.
Recipe tests and shared archive/version/resource inspection pass. A normal
installation of that exact file passes off-checkout installed smoke, portable
saved bibliography/reused capture and `pip check` on Python 3.14.7 with public
SMonitor 0.18.0, DepDigest 0.12.0 and ArgDigest 0.13.0. No metadata override,
editable provider or sibling source path is used.

This local Conda check confirms that Ackredit operates on 3.14 through its
noarch artifact. Public delivery and the full hosted installed matrix remain
pending; neither central admission nor a delivered-support badge is advanced.
The executable correction is owned by action #46, and central publication-pin
adoption is tracked in uibcdf/molsyssuite#78 and uibcdf/moli#38.
