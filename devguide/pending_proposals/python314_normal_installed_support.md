---
summary: Align the Python 3.14 adoption candidate and verify normal installed-package use.
issue: uibcdf/ackredit#80
status: partial
opened: 2026-10-02
closed:
verification: reproduced
area: [compatibility, packaging, ci]
guard: tests/test_workflow_hygiene.py
normative:
blocked_by: [uibcdf/ackredit#22, uibcdf/ackredit#75]
supersedes: []
---

# Normal Python 3.14 installation

## What

Sabueso requires Ackredit while retaining Python 3.11–3.14
(uibcdf/sabueso#108, uibcdf/moli#36). Ackredit's source works on 3.14, but
its `>=3.11,<3.14` metadata prevents normal installation. The maintainer
authorized preparation of target metadata, environments, recipe and CI with
installed-package verification and central issue coordination.

## How

At published main `6420407`, the clean source passes 1,526 tests locally on
Python 3.14.7. Hosted feasibility run `37070993747` passes on Linux and macOS.
Those are source probes using a metadata override; a normal pip dry run with
build tools instead rejects Python 3.14.7 against the declared range.

The candidate targets `>=3.11,<3.15`, retaining routine development on 3.13.
ArgDigest's public 3.14 support begins at 0.13.0, so the package, recipe and
environments require that floor. Supported CI installs without an override
and tests from outside the source checkout. The historical manual 3.14 route
becomes a normal installed-package gate with visible failures. A shared local
installed smoke checks real provider paths, self-citation, reused portable
result references, enclosing workflow credit and a fresh reader without credit.

## Why

Runtime feasibility is insufficient when consumers cannot install the package.
The installed gate refuses source-shadowed or editable provider paths, and
qualification uses published dependency builds from public Conda channels.

## What was refuted

Changing only the upper bound, retaining `--ignore-requires-python`, or using
editable sibling providers does not prove normal dependency closure. A successful
source probe or local wheel does not establish an immutable public release.

## Scope and exclusions

Component-owned interpreter adoption and installed qualification. No portable API
promotion, package-channel release, MOLI architecture change or central policy
edit. Central `authorized` registration and a compatible policy caller are
requested in uibcdf/molsyssuite#29; public `admitted` status remains independent.
The maintainer's nine uncommitted primary-checkout files are preserved.

## Acceptance criteria

- Metadata, maintained environments, Conda recipe and required CI target 3.11–3.14.
- Clean normal installation executes the built package on 3.14 without overrides.
- Core provider imports resolve to installed public packages, not sibling sources.
- Portable result/workflow and saved-reader behavior works in the installed package.
- Local gates and hosted required cells pass; exact source/evidence are recorded.
- Central transition authorization and public delivery are recorded independently.

## Qualification (2026-10-02)

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
