# FlowCite contributor instructions

Read [`MOLSYSSUITE_GUIDE.md`](MOLSYSSUITE_GUIDE.md) before making changes. It routes
suite-wide policy, compatibility, tooling and cross-component proposals to
`uibcdf/molsyssuite` while this repository remains authoritative for its implementation
and product behavior. That file is a synchronized, read-only copy: propose changes at its
canonical source, never in this repository.

## MolSysSuite membership

FlowCite is a UIBCDF development intended as a MolSysSuite component. Its admission and
registration in `suite.toml` are tracked centrally in `uibcdf/molsyssuite#28`; until that
theme is accepted, this repository adopts the common policies without yet appearing in the
central registry, and `check_repository.py` reports it as `UNREGISTERED`.

Keep FlowCite-specific implementation, tests, releases and product issues here. Report
suite-wide rules, shared tooling problems and cross-repository proposals in
`uibcdf/molsyssuite`. When work here exposes a limitation in a sibling component, file the
evidence in that component and cross-link it, as
[`cross_component_feedback.md`](https://github.com/uibcdf/molsyssuite/blob/main/devguide/cross_component_feedback.md)
requires.

`standards/FLOWCITE_GUIDE.md` is the canonical integration guide FlowCite owns and
distributes to its host libraries. Edit it here; consumer copies are synchronized from the
central registry and are never repaired locally.

## Language and scope

Use English in code, documentation, issues and commits. Keep changes focused, test
user-visible behavior, preserve human work and never commit secrets.

FlowCite is an optional dependency of its host libraries: a host must keep working when
FlowCite is absent. Any change that breaks that pattern needs an explicit decision, not a
silent regression.

## Local gates

Run these before committing:

```bash
ruff check .
ruff format --check .
pytest
python devtools/devguide_index.py --check
```

Routine development uses Python 3.13; the supported user range is Python 3.11 to 3.13.

## Reporting

Follow [`devguide/reporting_protocol.md`](devguide/reporting_protocol.md) for every durable
bug or proposal record. Open the owning GitHub issue first, create the record from
`devguide/templates/report.md`, regenerate the indexes after lifecycle changes, and archive
resolved records instead of deleting them.
