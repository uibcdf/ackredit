---
summary: Keep the optional DueCredit absence guard independent of installed packages.
issue: uibcdf/ackredit#128
status: resolved
opened: 2026-10-07
closed: 2026-10-07
severity: medium
verification: reproduced
area: [tests, dependencies]
guard: tests/test_duecredit_bridge.py::test_the_only_error_it_raises_is_ours
normative:
blocked_by: []
supersedes: []
---

# DueCredit absence guard in an installed development environment

## What

During #127 qualification the full source suite failed because the public bridge
absence test did not raise `AckreditError` with the optional DueCredit installed.
The clean maintained Conda development recipe includes that package. The failure
also reproduced in the single existing guard, with no preceding tests.

## How

The test inserted `sys.modules["duecredit"] = None` and then deleted that sentinel
before the public call. DepDigest correctly rediscovered the installed package.
Keep the sentinel through the call, assert the owning exception names DueCredit,
and clear discovery cache in `finally` so later present-package tests can resolve
normally. The bridge and dependency implementations remain unchanged.

## Why

The failed full run returned exit 1 with 1 failed, 2277 passed and 1 skipped.
The repaired bridge/optional-surface selection returns exit 0 with 17 passed and
1 skipped. The skip is the independent test conditional on actual optional
absence; the repaired guard always executes. Original failed events are retained
at `/tmp/ackredit012-local/source-events.jsonl`; the release's durable local
receipt retains their identity/outcome and the subsequent complete source gate.

## What was refuted

No production missing-dependency diagnostic defect was found. Removing DueCredit
from the development environment would hide an environment-dependent test setup
and would not repair this guard. A stand-in bridge tests handoff behavior, not
DueCredit's scientific or reference-management implementation.

## Scope and exclusions

Only the existing absence-test setup and its module description change. No
runtime behavior, dependency floors, host optionality or public API changes.

## Acceptance criteria

The public absence diagnostic executes regardless of installation, retains the
DueCredit name, and restores the discovery cache for subsequent present-package
fixtures. The focused selection passes; #127 separately owns complete source,
installed and public release qualification.
