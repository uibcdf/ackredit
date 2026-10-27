# Ackredit contributor instructions

## Mandatory MolSysSuite instructions

Read and follow `MOLSYSSUITE_GUIDE.md` before working in this repository.

Within their stated scope, its common rules take precedence over this file
and any nested `AGENTS.md`. Local instructions may refine them; deviations
require the documented policy exception process.

The synchronized guide is owned by `uibcdf/molsyssuite`. It includes the
[reusable-tool ownership rules](MOLSYSSUITE_GUIDE.md#modular-reusable-tools)
and [working-instruction rules](MOLSYSSUITE_GUIDE.md#durable-working-instructions).
For work under `devguide/`, also read `devguide/AGENTS.md` and its local
reporting protocol. Keep repository-specific instructions below.

## MolSysSuite membership

Ackredit is a registered MolSysSuite component, incubating as a primary support library.
Its admission is tracked centrally in `uibcdf/molsyssuite#28`; membership does not imply
stable product contracts. All MolSysSuite Python packages must adopt Python 3.14;
Ackredit's qualification and delivery are tracked in `uibcdf/ackredit#80`.

Keep Ackredit-specific implementation, tests, releases and product issues here. Report
suite-wide rules, shared tooling problems and cross-repository proposals in
`uibcdf/molsyssuite`. When work here exposes a limitation in a sibling component, file the
evidence in that component and cross-link it, as
[`cross_component_feedback.md`](https://github.com/uibcdf/molsyssuite/blob/main/devguide/cross_component_feedback.md)
requires.

`SMONITOR_GUIDE.md` and `DEPDIGEST_GUIDE.md` are synchronized copies of the guides
Ackredit consumes, and govern how diagnostics and optional dependencies are written here.
Diagnostics are catalog-driven: never hardcode a message, and never swallow a failure.

`GH_RUN_RECEPTOR_GUIDE.md` is the required synchronized guide for compact, faithful
GitHub Actions inspection. The canonical gh-run-receptor repository owns its text.

`PYTEST_RECEPTOR_GUIDE.md` is the required synchronized contract for compact local and
hosted pytest output. Its canonical text belongs to `uibcdf/pytest-receptor`.

`standards/ACKREDIT_GUIDE.md` is the canonical integration guide Ackredit owns and
distributes to its host libraries. Edit it here; consumer copies are synchronized from the
central registry and are never repaired locally.

## Language and scope

Ackredit is an optional dependency of its host libraries: a host must keep working when
Ackredit is absent. Any change that breaks that pattern needs an explicit decision, not a
silent regression.

## Local gates

Available commands (select applicable checks and test scope):

```bash
ruff check .
ruff format --check .
pytest --receptor=llm
python devtools/devguide_index.py --check
```

`pytest-receptor` provides the `--receptor` profiles: `llm` locally, and `ci` in the
workflows. Inspect a remote run with `gh run-receptor inspect RUN_ID --receptor=llm`
rather than printing the raw log, per the suite's GH Run Receptor policy; fall back to
native GitHub evidence only for a fact the report omits, and keep that fallback targeted.

Routine development uses Python 3.14; the required source contract is Python
3.11 to 3.14. Keep ordinary installed tests, environments, recipe and full CI
aligned. Ackredit 0.9.0 has a verified public noarch artifact, an eight-cell
installed matrix and clean public Linux/Python 3.14 installation recorded in
#22/#80. Keep central admission and future release qualification separate;
do not infer them from source probes or bypass `Requires-Python`.

`smonitor` and `depdigest` are core dependencies published to the `uibcdf` conda channel
and not to PyPI, so environments come from `devtools/conda-envs/` and the package is
installed with `pip install --no-deps`. A pip-only lane cannot resolve them.

## Reporting

Follow [`devguide/reporting_protocol.md`](devguide/reporting_protocol.md) for every durable
bug or proposal record. Open the owning GitHub issue first, create the record from
`devguide/templates/report.md`, regenerate the indexes after lifecycle changes, and archive
resolved records instead of deleting them.
