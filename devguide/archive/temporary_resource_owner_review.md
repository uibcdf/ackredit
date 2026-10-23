---
summary: Review remaining development-resource ownership and exceptional cleanup.
issue: uibcdf/ackredit#132
status: resolved
opened: 2026-10-22
closed: 2026-10-22
severity: medium
verification: reproduced
area: [development, testing, documentation]
guard: tests/test_tool_resource_lifecycle.py
normative:
blocked_by: []
supersedes: []
---

# Remaining temporary-resource owner review

## What

Complete Ackredit's incoming owner review under MolSysSuite #104. Previously
resolved persistence and tracing repairs (#130/#131) remain resolved. This
follow-up was received as missing review evidence, not a reproduced leak.
The reviewed operation/lifetime table is maintained in
[temporary_resources.md](../temporary_resources.md).

## How

Review maintained developer tools, tests, documentation, build and qualification
routes. Distinguish managed scratch, explicitly requested evidence, caller-owned
inputs/environments, hosted runner resources and historical resources of unknown
ownership. Reuse standard context managers and existing tests rather than add a
generic cleanup framework. Exercise remaining scratch scopes on success/failure,
retained evidence on process failure and visible cleanup errors.

## Why

Guide delivery and selected successful tests do not establish every tool's
lifecycle. Record the actual operation, owner, useful lifetime, evidence and
limitations in a maintained review; report the disposition to MolSysSuite #104.

## What was refuted

An explicit evidence/output directory is not automatically a leak. Outputs can
remain in `/tmp` while useful, and are removed when their task owner no longer
needs them. Do not impose relocation or blanket age/prefix deletion.

## Scope and exclusions

Ackredit-owned tools and current retained resources; no sibling source edits,
shared-environment cleanup, global `/tmp` cleanup or universal platform/scientific
matrix. Source inspection, executed cleanup and historical attribution are
separate evidence. New product functions and a new release are separate work.

## Reviewed outcome and evidence

No additional Ackredit-owned scratch defect was reproduced. Twelve new cases
exercise the actual lifecycle/provenance/plugin scratch owners with inert
scientific/build/environment callbacks: success, callback failure, cleanup
failure and simultaneous operation/cleanup failure. Scratch is removed on both
normal exits, removal failures remain visible with the original exception,
and caller inputs/requested outputs survive. This verifies lifecycle, not
performance, actual plugin installation or scientific results.

The selected local gate passes 214 tests without skips or warnings on Python
3.14.7: new cases, #130/#131 guards, reporting/documented-API/docs checks,
qualification-bundle contracts and selected receiving failure/refusal guards.
Its managed pytest base directory is removed after extracting the complete
event result. Ruff lint/format and indexes pass; final documentation and hosted
head evidence are retained separately in the validation receipt/owning issue.

All 55 historical central paths were rechecked: 54 absent; the shared
`/tmp/pytest-of-diego` remains untouched. Twelve absent worktree registrations
were pruned only after individual path/commit checks and a dry run. Each commit
is reachable from `origin/main`; no files, branches or environments were deleted.
Earlier removal attribution remains unknown. Task-owned test/build scratch is
retired after its last use; evidence does not need relocation outside `/tmp`.

No implementation exception is required for the reviewed component-owned
scope. Explicit output/environment retention belongs to the invoking task;
shared provider/cache/Jupyter internals and hosted runner retirement retain
their own owners and are not universally certified by this review. No client
API/guide, dependency or published 0.12.0 identity changes. Shared environment
`pip check` still reports the seven unrelated conflicts owned by MolSysSuite #82.

## Acceptance criteria

- Maintained operations have an explicit owner/lifetime and reviewed disposition.
- Applicable scratch scopes clean both exits, preserve caller resources and
  expose cleanup errors; tests exercise the actual owners.
- Retained output/failed-process evidence and input protections remain intact.
- Historical resources have explicit observations without invented deletion
  attribution; any unresolved implementation exception remains owned and bounded.
- Checkpoint and indexes are current; local gates and exact-head CI are recorded,
  and the central owner receives the component disposition.
