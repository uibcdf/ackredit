# Release notes

## 0.10.0 — candidate preparation

Delivery is tracked in [Ackredit #93](https://github.com/uibcdf/ackredit/issues/93).
The current public portable-attribution minimum remains 0.9.0 until the exact
0.10.0 Conda archive completes staging, installed qualification and publication.

- Explicit `observe_calls` records entered declared exports, including awaited
  coroutine execution, with original software and article references. Libraries
  declare an offline `__ackredit__` dictionary without depending on Ackredit.
- `prepare_credit` prepares a fixed contextual credit for repeated operations;
  the host invokes it at its chosen completion boundary. PyUnitWizard provides
  the real optional producer and released-provider fallback pilot.
- The `workflow` report combines numbered references, original roles and software
  versions with the saved graph. A fresh reader renders it without importing the
  producer, contacting a service or crediting execution.
- Shared graph targets expand once; deep provenance graphs avoid recursive
  traversal. Report plugins receive detached nested bibliography. Equivalent
  registered tuple/list metadata is accepted without replacing the registration.

`observe_calls`, `prepare_credit` and provider declaration interpretation remain
**provisional**. Observation covers selected direct module exports, not existing
aliases, generators, native internal calls or subprocesses. Credits do not claim
invocation counts, scientific success or a complete execution trace. See
[function providers](../user_guide/function_providers.md) and
[API stability](stability.md).

The released portable `ackredit.attribution@1` contract remains unchanged. No new
core dependency, automatic observation or consumer minimum follows from these
additions. Installed candidate and public delivery evidence will be linked here
once those operations complete.
