---
summary: Review Ackredit Python ecosystem policy adoption.
issue: uibcdf/ackredit#72
status: resolved
opened: 2026-09-27
closed: 2026-10-03
verification: measured
area: [governance, tooling]
guard: tests/test_developer_tool_pins.py
normative:
blocked_by: []
supersedes: []
---

# Review Python ecosystem policy adoption

**Reported:** 2026-09-27 under `uibcdf/molsyssuite#56`; inspected
`88779435bd730d186b6d2f67fbb7b7d517bae2a2` on `origin/main`.

## What

Support-library adoption is **adopted** for Ackredit's applicable surface;
developer-tool adoption is **partial** because maintained Conda environments
do not pin the Pytest Receptor version.

## How

Ackredit declares and uses SMonitor, DepDigest, and ArgDigest. Its citation
and provenance API has no physical-quantity boundary, so PyUnitWizard is
inapplicable. `tests/test_smonitor_integration.py`,
`tests/test_argument_contract.py`, and `tests/test_optional_surface.py`
exercise the relevant diagnostics, argument, and optional-dependency paths.
Previous member issues `uibcdf/ackredit#6` and `uibcdf/ackredit#62` record
the underlying library integrations.

CI run `36310576715` passed seven of seven jobs at the inspected source;
suite-policy run `36310577022` also passed. The workflow selects
`--receptor=ci`, and published GH Run Receptor `1.0.0` inspected both runs.
The test, experimental, and development Conda environments name
`pytest-receptor` without an exact version. Pin a reviewed published version
in maintained environments and verify the installed version in hosted CI.

## Why

The support-library boundaries have tests and prior integration records.
Unpinned test environments can silently change the CI tool while preserving
the same command line.

## What was refuted

PyUnitWizard is not applicable to the citation/provenance API inspected here.
The successful CI matrix does not establish which receptor version will be
installed on future runs.

## Scope and exclusions

This record owns Ackredit's developer-tool pin and adoption evidence. The
support-library implementation history remains in the earlier member issues.

## Acceptance criteria

Pin and verify a published exact receptor version across maintained Conda
environments, retain `--receptor=ci` with equivalent test selection, and keep
support-library boundary tests passing. Reassess if new public quantity
boundaries are introduced.

## Exact published test-tool adoption — 2026-10-03

Pytest Receptor **1.2.1** is independently visible in its stable GitHub Release,
PyPI version index and ordinary public `uibcdf/noarch` solver index. The Conda
file is `pytest-receptor-1.2.1-py_0.tar.bz2`, SHA-256
`77bf3694bc903f606d4323b88e3bb3aea9628618036b53073f5a5dbd5dbc73cb`,
with Python `>=3.11,<3.15` and pytest `>=8.0.0`. Provider release #32 is closed.
The maintained development, ordinary-test and dedicated 3.14 environments now
all declare `pytest-receptor ==1.2.1`.

Routine CI, the required full matrix and the dedicated installed-validation
workflow compare the actual installed distribution version with that pin before
their unchanged `pytest --receptor=ci` test commands. A mismatched version raises
an assertion and fails the native step; the check prints the observed version
for targeted evidence acquisition. No runtime dependency or test selection is
changed, and build/documentation environments that do not run pytest gain no
unused dependency.

`tests/test_developer_tool_pins.py` reproduces the original unpinned environment
failure, checks every maintained environment and hosted compact-test job, and
executes the actual version-check command under matching/mismatched reported
metadata to verify its exit behavior. Its four cases fail before the correction
and pass afterwards. Local qualification uses the public release in an isolated
Python 3.14 environment; the shared workspace's separate editable Pytest Receptor
checkout is preserved, as are Ackredit's nine pre-existing human files.

Support-library evidence remains adopted: SMonitor catalog diagnostics,
DepDigest optional loading and ArgDigest public argument contracts retain their
existing guards. PyUnitWizard remains inapplicable to Ackredit's own runtime
quantity boundaries; its receiving scientific attribution tests are a distinct
consumer relationship. Exact-source hosted tool evidence is recorded below
before closure. Central inventory adoption remains with MolSysSuite #56.

Local implementation qualification passes all **1,548 tests**, no skips, on
Python 3.14.7 with public Pytest Receptor 1.2.1. Ruff lint/format, current report
indexes and Sphinx `-W` pass. Hosted exact-source verification remains pending
for this partial record; no central adopted state is inferred from local gates.

## Exact-source hosted resolution — 2026-10-03

Implementation source `3c6e77c5d69809da0333786572f1edd4689c611b` passes:

- [Routine CI 37158926157](https://github.com/uibcdf/ackredit/actions/runs/37158926157): seven jobs, including five actual installed test cells.
- [Full matrix 37159097254](https://github.com/uibcdf/ackredit/actions/runs/37159097254): all eight Linux/macOS arm64 × Python 3.11–3.14 test cells. The dispatch-only recovery decision job is intentionally skipped and is not a scientific cell.
- [Dedicated installed 3.14 37159098842](https://github.com/uibcdf/ackredit/actions/runs/37159098842): both Linux/macOS arm64 cells.
- [Suite policy 37158926538](https://github.com/uibcdf/ackredit/actions/runs/37158926538) and [publication policy 37158926601](https://github.com/uibcdf/ackredit/actions/runs/37158926601).

All five reports were acquired with published GH Run Receptor **1.1.1**.
Bounded native API evidence independently confirms the exact source and actual
successful `Verify installed Pytest Receptor version` and `Run tests` steps in
all fifteen test cells. The [committed adoption receipt](../../devtools/receipts/python_ecosystem_72_2026-10-03.json)
retains these observations without raw logs or credentials.

Ackredit's applicable support-library and developer-tool adoption is complete.
`tests/test_developer_tool_pins.py` guards maintained pins and the hosted check's
actual matching/mismatched exit behavior. MolSysSuite #56 owns the central
inventory update; this resolution does not write the central registry.
