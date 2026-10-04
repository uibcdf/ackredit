---
summary: Import-hook guards depended on optional transitive import side effects.
issue: uibcdf/ackredit#86
status: resolved
opened: 2026-10-04
closed: 2026-10-04
severity: medium
verification: reproduced
area: [tests, integration]
guard: tests/test_hooks_already_loaded.py::test_an_injection_on_a_module_ackredit_already_loaded_is_credited
normative:
blocked_by: []
supersedes: []
---

# Import-hook tests and transitive dependency imports

## What

Three tests assume importing Ackredit loads NumPy through ArgDigest, or that
the import footprint includes NumPy or PyYAML. The current shared editable
ArgDigest 0.13.0+16.g68a506e legitimately loads neither.

## How

The full Python 3.14 suite fails the precondition assertions on both unchanged
Ackredit 148ffb4 and the #84/#85 implementation. Explicit injections themselves
continue working. Use SMonitor, a guaranteed imported core dependency, for
the Ackredit-preloaded injection; explicitly preload NumPy for discovery; hold
the footprint probe to Ackredit and its imported core dependencies.

## Why

Transitive optional imports are not a contract. Reintroducing them would make
Ackredit heavier to satisfy assertions that do not test an import-hook failure.

## What was refuted

The new function provider implementation does not cause the changed footprint;
the untouched baseline has the same footprint. Do not change ArgDigest or add
scientific imports to Ackredit's startup.

## Scope and exclusions

Test preconditions only. Injection behavior, discovery exclusions and public
metadata remain unchanged. Historical NumPy footprint evidence stays archived.

## Acceptance criteria

Preloaded explicit injection earns credit; unswept discovery earns nothing;
the measured footprint probe remains meaningful with lighter dependencies.

## Resolution

The three preconditions are corrected without adding runtime imports. All nine
fresh-process hook tests pass. The selected guard still exercises a dependency
loaded by Ackredit before hook activation and proves its explicit injection is
credited, while the separate discovery guard explicitly preloads NumPy and
proves no sweep credit occurs. This does not promise a transitive import graph.
