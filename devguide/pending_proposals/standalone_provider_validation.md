---
summary: Expose inert public provider validation through the existing declaration parser.
issue: uibcdf/ackredit#111
status: partial
opened: 2026-10-06
closed:
verification: measured
area: [core, integration, documentation]
guard: tests/test_provider_validation.py
normative:
blocked_by: []
supersedes: []
---

# Standalone provider declaration validation

## What

Add provisional `ackredit.validate_provider(module) -> dict` for one already
imported ordinary module. Return a detached `ackredit.provider@1` declaration
with original producer identity, all bibliography and merged module/function
uses. The result preserves role order/duplicates so it can be reapplied without
breaking the observer's existing exact module/function agreement. Observation
retains its own sorted/deduplicated role interpretation.

## How

Reuse `_read` in the owning `ackredit/core/providers.py`; retain declaration
refusals and return its detached merged declaration with the existing plans and
records. The standalone function exposes that detached result and has no
registry, session, capture, observer or network mutation path. Existing
catalog E012 describes invalid declarations for both entry points.

## Why

Roadmap G requires independently reusable validation before author tooling.
Activation-only validation makes authors install wrappers/register bibliography
to check metadata or reproduce the parser downstream. Public 0.11.0 already
delivers the accepted provider protocol; this additive development API does not
extend that release's exported surface or promote its own signature by inference.

## What was refuted

Copying the parser into a CLI or client would create two interpretations.
Successful validation does not prove current-registry compatibility or actual
scientific calls. Rejecting lazy exports here would disagree with the accepted
observer. Their loader side effects belong to the selected trusted producer and
cannot be promised inert; Ackredit itself does not activate observation.

## Scope and exclusions

One module's declaration, direct exports and function metadata. No import-name
discovery, new schema interpretation, observer expansion, scientific execution,
DOI enrichment, global conflict checks, stable API promotion or package release.
The producer author guide/example remains the subsequent roadmap task.
Distribution #108/#110 and provider-owner acceptance of MolSysSuite #105 remain
separate; this operation does not depend on the proposed distribution tool.

## Acceptance criteria

- Public export, documented signature/result, errors and provisional boundary.
- Validator and observer share acceptance/refusal for declaration inputs.
- Success/failure preserve registry, session/capture, observer leases and exports.
- Returned nested records are detached; fresh calls reflect current metadata.
- Function-only/empty declarations, explicit lazy exports and supported kinds
  retain the accepted parser's behavior.
- Applicable tests, lint, format, indexes, strict docs and exact-head CI pass,
  using Pytest Receptor locally and GH Run Receptor remotely.

## Source implementation and local evidence

The provisional export and documentation are implemented in development after
0.11.0. `_read` returns its detached merged declaration alongside the existing
activation plans/records; both public entry points use this same parser. Return
role order/duplicates are retained deliberately: normalizing them would make
the returned module declaration disagree with unchanged function metadata.

Local Python 3.14.7 validation of the complete `tests/` selection passes **2,122
tests without skips or warnings** using `pytest --receptor=llm`. This includes
24 new standalone guards and the existing normally installed producer/reader
contract. Ruff 0.16.5 lint/format, index checks and strict Sphinx pass. Ackredit
is installed editable into an isolated temporary environment from this worktree;
these results are development source evidence, not public artifact qualification.

The initial lazy-failure experiment also exposed a SMonitor argument-repr
failure that prevents exception-event emission while retaining the original
exception. Its independent reproduction and source/metadata limits are reported
in [SMonitor #36](https://github.com/uibcdf/smonitor/issues/36). No provider source
is changed or warning suppressed here. Supported ordinary lazy-export tests pass
without warning; arbitrary producer loader side effects remain explicit limits.

Remaining: exact-head hosted gates and integration/acceptance in the default
branch. The result/signature remains provisional after source adoption; a future
promotion requires its own explicit decision. External-author tooling and a new
public release remain separate tasks.
