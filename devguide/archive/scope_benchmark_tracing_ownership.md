---
summary: Scope developer benchmark tracing and preserve caller sessions.
issue: uibcdf/ackredit#131
status: resolved
opened: 2026-10-08
closed: 2026-10-08
severity: low
verification: reproduced
area: [development, testing]
guard: tests/test_lifecycle_tracing_resources.py
normative:
blocked_by: []
supersedes: []
---

# Scope benchmark tracing ownership

## What

At `7cc12ee39e0505dffc44ebdbd294ae11d7c949ff`, lifecycle `Stages` always
starts/stops global tracing; failed operations bypass finish. Successful workers
stop a caller's existing session, and failed workers/plugin operations leave a
session they started active. Repeated finish can also stop a newly started caller
session after the owned session has already ended.

## How

Stages records whether it starts tracing, exposes a standard context manager and
finishes only its owned session, once. All maintained users in activation,
result/reference/journal, scientific wrapper and plugin operations use that scope.
Successful operation order, measurement fields and calculations remain unchanged.
The existing explicit finish continues to return the same values and is harmless
when called again. Exit errors propagate; no cleanup failure is suppressed.

## Why

Resource scope covers operation and assertion failures before scratch or surrounding
contexts unwind. This is developer tooling under uibcdf/molsyssuite#104, separate
from uibcdf/ackredit#130's persistence repair. No runtime attribution or scientific
algorithm fix is proposed.

## What is measured

Linux Python 3.14.7 stdlib-only children execute actual worker activation, plugin
callback failure and repeated finish with inert Ackredit callbacks. No molecular,
numerical or backend modules are imported. Nine permanent regression cases cover
owned/caller tracing on success/failure, timing controls and a new caller session
after finish. Four fail before repair; five are controls. All nine pass after
repair. The ten earlier persistence resource guards and reporting guard also pass:
20 selected local tests, plus affected Ruff and current indexes.

AST comparison of `worker`, `scientific` and plugin `operations` against the
original source confirms their operations are identical after unwrapping the new
Stages scope into its original assignment. This is source structure evidence,
not scientific execution or an actual performance/result comparison.

## What was refuted

Successful finish alone cannot protect exceptional exits. Unconditionally stopping
tracing in finally would still terminate a caller session. Standard scoped Stages
ownership handles both, without a shared cleanup framework or dependency change.

## Scope and limits

Memory sampling still intentionally calls `reset_peak`; preserving a caller's entire
profiling history is not claimed. The documented fresh-process benchmark route
remains the route for isolated allocation measurements. The cold-import child owns
its own process lifetime and is unchanged. Scientific operations were not executed;
no numerical stability or benchmark timing threshold is qualified.

No plugin/runtime API, public serialized contract, dependency, retry/deadline,
provider guide, policy/SDK pin, package build/upload/promotion or release change.
The internal push conditionally skips CI to avoid broad scientific/benchmark/build
work in this resource-only tranche; exact-head policy, publication controls and
backlog probe are dispatched manually. Those administrative gates do not execute
the new local regression guard. dprada/LMMV retain full-suite debt and the existing
nightly/weekly/manual recovery route; administrative checks do not clear it.

## Acceptance criteria

The guard fails for the four observed ownership failures and passes after repair;
controls retain caller sessions, values and field names. All Stages users have
exceptional scope, repeated finish is harmless, and caller/shared environments
remain untouched. Record exact native gate evidence separately from local tests
and retire task-owned resources after durable receiving and delivery.
