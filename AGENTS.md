# Ackredit contributor instructions

Read [`MOLSYSSUITE_GUIDE.md`](MOLSYSSUITE_GUIDE.md) before making changes. It routes
suite-wide policy, compatibility, tooling and cross-component proposals to
`uibcdf/molsyssuite` while this repository remains authoritative for its implementation
and product behavior. That file is a synchronized, read-only copy: propose changes at its
canonical source, never in this repository.

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

Use English in code, documentation, issues and commits. Keep changes focused, test
user-visible behavior, preserve human work and never commit secrets.

Ackredit is an optional dependency of its host libraries: a host must keep working when
Ackredit is absent. Any change that breaks that pattern needs an explicit decision, not a
silent regression.

## Local gates

Choose local gates before committing by the changed code, inputs and scope:

- Documentation, instructions and evidence require applicable reporting/index,
  link and synchronized-guide checks; prose changes alone do not require the
  scientific suite.
- Executable behavior, dependency, metadata, packaging and integration changes
  require relevant code/contract tests and applicable lint, format and local
  type checks. Broaden validation when the affected boundary requires it.
- Scientific exploration requires informative hypothesis cases and explicit
  limits; an administrative check does not establish scientific equivalence.

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

## Direct pushes and scoped local validation

Follow [the common checkpoint policy](MOLSYSSUITE_GUIDE.md#direct-pushes-and-validation-checkpoints)
for authorized internal direct pushes by `dprada` and `LMMV`. Batch focused local
commits when remote visibility is unnecessary; a permitted interim CI skip is
conditional, never the default after every locally checked change. Retain local
results while tested code, inputs, environment and scope remain applicable.
Normally finish with an unskipped head and inspect its applicable CI, or explicitly
execute and verify those exact-head gates manually. Record missing evidence,
untested scope, owning issue and recovery route; administrative checks do not
clear full-suite backlog. External PRs, admission and publication require all
mandatory executed gates for the exact candidate and required installed file.
An authorized manual qualification retains the original producer and artifact
bytes/digest; a marker alone neither waives a gate nor disqualifies that evidence.

## Modular reusable tools

Before adding a feature, inspect existing tools and identify the owning module or
component. Implement or extend independently useful operations as documented reusable
tools in that owner, with their own contracts and tests; have consumers call them.
Keep task-specific decisions local and report missing sibling capabilities to the
provider with linked consumer evidence. Follow
[MOLSYSSUITE_GUIDE.md#modular-reusable-tools](MOLSYSSUITE_GUIDE.md#modular-reusable-tools)
for applicability, compatibility, performance and tracked exceptions.

## Durable working instructions

Keep technical findings in owning issues, fixes, tests and maintained guidance.
Place only accepted lasting contributor actions in root or appropriately scoped
instructions, following
[the common policy](MOLSYSSUITE_GUIDE.md#durable-working-instructions).
For work under `devguide/`, also read [devguide/AGENTS.md](devguide/AGENTS.md)
and its local reporting protocol. Shared instruction proposals belong in
`uibcdf/molsyssuite`; cross-MOLI contracts belong in `uibcdf/moli`.

## Human-facing issue feedback

Surface actionable suspected defects, inconsistencies, missing analyses and
improvements, including uncertain or nonblocking findings. When working with a
human, offer an owning issue at a natural pause; retain existing reporting
authorization and respect declined/deferred disclosure. Follow
[the accepted feedback route](MOLSYSSUITE_GUIDE.md#human-facing-issue-feedback)
for ownership, uncertainty, privacy and exceptions.
