---
summary: Import hooks never credited a module loaded before them, and since ArgDigest arrived numpy always is, so the documented numpy example and the guide's injection recipe credited nothing.
issue: uibcdf/ackredit#69
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: high
verification: reproduced
area: [hooks, docs]
guard: tests/test_hooks_already_loaded.py
normative:
blocked_by: []
supersedes: []
---

# The import hooks are blind to what came first

## What

The finder credits a module when it is imported, and an import of a module already in
`sys.modules` never reaches a finder. Since `uibcdf/ackredit#62`, `import ackredit` loads
numpy itself: ArgDigest's package `__init__` imports `pipelines.data`, which imports numpy
at module level. So in every process:

- the user guide's discovery example, `enable_import_hooks()` then `import numpy`,
  credited scipy and not numpy;
- the integration guide's recipe, `add_injection("numpy", ...)` then the hooks, credited
  nothing.

The class is older than #62: a host whose submodules import mdtraj before its `__init__`
enables the hooks never credited mdtraj either.

Found while reviewing the superseded root demo before deleting it. Its numpy injection had
credited nothing since #62, and it exited 0.

## How

`ackredit/core/injections.py` becomes the one place that credits an injection.
`enable_import_hooks()` credits every declared injection whose module is already loaded,
and `add_injection()` does the same for its own module when the hooks are on. The finder
calls the same function for imports it sees.

Discovery is unchanged, and its boundary is now documented in `tracking.md`,
`injections.md` and the integration guide: it sees imports after it is enabled. Declaring
an injection is how to credit a package that may already be loaded.

## Why

numpy is the package most of the suite's work rests on, and the documentation showed it
being credited.

## What was refuted

Sweeping `sys.modules` for discovery as well. It would credit Ackredit's own dependencies
in every report, and in a notebook the 32 third-party packages an empty kernel had already
loaded — IPython, debugpy, psutil, pygments, measured. A declared injection is a person
saying the module matters; a loaded module is not.

Making Ackredit import ArgDigest lazily. ArgDigest's decorators run when Ackredit's
modules are imported, and importing any ArgDigest submodule runs its package `__init__`.
The root cause is ArgDigest's eager numpy import, filed as `uibcdf/argdigest#15`; until it
is resolved, discovery cannot credit numpy in a process that imports Ackredit, and the
pages say so.

## Scope and exclusions

Discovery of numpy waits on `uibcdf/argdigest#15`. Injections do not.

## Acceptance criteria

`tests/test_hooks_already_loaded.py`, each case in a fresh interpreter: an injection on a
module loaded before the hooks is credited, whether declared before or after enabling
them, and so is one on a module a host imported first. Against the previous code these
fail. So does a scan of every page for a discovery example that imports a package
Ackredit loads itself, computed rather than listed. Guards that pass on both sides stop
an overcorrection: an injection on a module not yet imported waits for the import,
nothing is credited without the hooks, and discovery credits nothing already loaded.
