---
summary: Review Ackredit Python ecosystem policy adoption.
issue: uibcdf/ackredit#72
status: active
opened: 2026-09-27
closed:
verification: measured
area: [governance, tooling]
guard:
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
