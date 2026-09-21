---
summary: The public namespace exported names nobody chose, including one that answered the version question wrongly.
issue: uibcdf/ackredit#14
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: medium
verification: reproduced
area: [api]
guard: tests/test_public_surface.py
normative:
blocked_by: []
supersedes: []
---

# The public namespace publishes names nobody chose

## What

Four names reached `ackredit`'s public namespace because `__init__.py` imported them for
its own setup: `version`, `PackageNotFoundError`, `ensure_configured` and `PACKAGE_ROOT`.
`Collector` was public but undeclared while `Registry` was both, and the documentation
had split on the consequence, teaching two spellings of the same call.

## How

```python
>>> ackredit.__version__
'0.5.0'
>>> ackredit.version("pytest")
'9.1.1'
```

`ackredit.version` is `importlib.metadata.version`, one tab-completion from
`__version__`, answering plausibly and wrongly what a citation tool's own version is.

```
standards/ACKREDIT_GUIDE.md      ackredit.enable_persistence(...)
docs/user_guide/tracking.md      ackredit.Collector.enable_persistence(...)
docs/user_guide/reporting.md     ackredit.aggregate(...)
```

## Why

`__all__` is the statement of what the library promises to keep. Everything beside it is
something a user can come to depend on and a maintainer can remove without knowing they
broke it. Ackredit is heading for 1.0 and was registered as a suite component the same
day, so the surface should be the one that was chosen rather than the one that
accumulated.

## What was refuted

Reviewing the surface was rejected as the remedy, because that is what had been happening:
each leak arrived with a change that was itself correct. A namespace that must be
remembered will drift again, so the check is a test rather than a habit.

Removing `Registry` from `__all__` to match `Collector` was also considered. Adding
`Collector` was preferred: `Registry` was already published, and withdrawing a name costs
users more than declaring one.

## Scope and exclusions

Covers what `ackredit` exports and which spelling the documentation teaches. Excludes the
shape of the functions themselves, which is API hardening proper and is not attempted
here.

## Acceptance criteria

Met by the commit closing this record:

- every import made for the module's own setup is bound to a private name;
- `Collector` and `Registry` are exported alike;
- the documentation teaches the flat form everywhere;
- `tests/test_public_surface.py` fails on any public name that is neither declared nor a
  submodule, on any declared name that is missing, and on any exported name belonging to
  another project. Verified by reintroducing the `version` leak, which fails two of them.
