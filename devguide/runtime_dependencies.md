# Runtime dependency review

Owner review: [Ackredit #138](https://github.com/uibcdf/ackredit/issues/138),
receiving [MolSysSuite #137](https://github.com/uibcdf/molsyssuite/issues/137).
The 2026-11-11 review starts from `4beb850c8ba814e6103b4d303128a1a36eb57610`.

## Consumed contracts and supported floors

| Dependency | Runtime floor | Consumed boundary and evidence |
| --- | --- | --- |
| SMonitor | `>=0.16.0` | `signal`, `integrations.DiagnosticBundle`, catalog exceptions/warnings and host bootstrap; existing diagnostic/provider tests and the independent minimum-prefix run exercise these operations. |
| DepDigest | `>=0.11.0` | `dep_digest` optional guards and `get_info` dependency-report contract; dependency-report, absence and bridge tests exercise the boundary. |
| ArgDigest | `>=0.15.0` | `arg_digest`, `FunctionContract`, `Domain` and source-configured argument validation; 0.13.0 imports NumPy eagerly and fails the existing import-hook guard; provider fix `bc14d57` is published in 0.15.0. Public argument and fresh-process no-NumPy tests exercise this boundary. |
| PyYAML | `>=6` | `safe_load` of CFF and maintained administrative YAML parsing; preserve the established 6-series floor. The Python 3.14 minimum-prefix solver actually selects 6.0.3, not exact 6.0.0. |
| DueCredit (optional) | `>=0.10.2` | `due.cite`, `entries.Doi` and `entries.BibTeX`; real offline collectors at exact 0.10.2 and public 0.11.2 receive the observed DOI/BibTeX and omit unobserved work. 0.10.2 is the deliberately qualified supported floor, not a claim that these APIs first appeared there. |

No runtime ceiling or exclusion is required by this review. Unknown future
provider versions are not certified. Keep the separately governed Python
`>=3.11,<3.15` range. Optional DueCredit remains absent from required metadata,
Conda run requirements and ordinary test/docs environments; its named extra,
`full` union and optional development selection agree. Absence continues to
raise the owning catalog-backed dependency diagnostic only when requested.

## Routes and classification

`pyproject.toml` owns required/optional runtime declarations. The Conda recipe's
run list and development/test/3.14/docs environments retain all four required
floors. `build_env.yaml` bootstraps packaging only, not Ackredit's runtime.
`devtools/dependency_routes.toml` classifies every maintained workflow and the
pinned shared preflight rejects unreviewed workflow drift. No required sibling
is installed from source in CI. Public Conda supplies required dependencies;
the separately pinned PyUnitWizard source is a receiving fixture.

Build requirements (`setuptools>=77.0.3`, `versioningit>=3.0`) and the packaging
guard's `build>=1.2` are tools, not runtime edges. They are explicit in the test
extra and development/test environments for nonisolated distribution checks.
The installed resource descriptor independently supplies bounded test-tool
ranges required by the shared qualification operation. These test-only ranges,
the exact Ruff/Receptor pins, CI action SHAs and original release coordinates
are reproducibility controls; the runtime `>=X` policy does not remove them.

## Qualification limits and handoff

The independent Linux/Python 3.14 minimum prefix installs exact SMonitor 0.16.0,
DepDigest 0.11.0 and ArgDigest 0.15.0 with PyYAML 6.0.3 and no editable source.
Its commands/results and real optional receiving are retained in the owner
receipt. A separate source-contract probe loads the official 6.0 wheel's pure-Python
loader and passes 92 CFF cases; it is not a cp314 native wheel installation.
Neither probe certifies universal future-version compatibility or a public release. The exact release source, complete
installed matrix and public receiving retain their separate gates under #140.

Central dependency-graph refresh for the optional floor and packaging/test-tool
edges is requested with immutable provider source in
[MolSysSuite #192](https://github.com/uibcdf/molsyssuite/issues/192).
