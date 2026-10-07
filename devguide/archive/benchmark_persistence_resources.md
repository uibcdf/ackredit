---
summary: Close persistence writers and remove disposable benchmark and test fixtures on both outcomes.
issue: uibcdf/ackredit#130
status: resolved
opened: 2026-10-07
closed: 2026-10-07
severity: medium
verification: reproduced
area: [development, testing]
guard: tests/test_benchmark_resources.py
normative:
blocked_by: []
supersedes: []
---

# Benchmark persistence resource ownership

## What

At b9a4e45f8997b53e6207fae0a63f739841017be6, each persistence benchmark
sample retained its mkdtemp directory/session.json. A failed callback also bypassed
writer closure. The adjacent session-file stability test unlinked its fixture
only after reading and asserting successfully. These disposable paths have no
caller output contract. Shared coordination is uibcdf/molsyssuite#104.

## How

The actual WORKFLOW string now owns an ExitStack. Persistence enters a managed
TemporaryDirectory and registers writer closure before enabling persistence,
covering partial setup failures. LIFO teardown closes the writer before removing
its files, even when opening, a callback or closure fails. Removal exceptions
propagate with any earlier exception context. Setup and teardown remain outside
the perf_counter pair; bare/tracked modes acquire no persistence resources.

The stability test uses its own managed directory, writes the same legacy
whole-document payload and keeps the existing read/assertion inside the context.
The performance page explains fixture ownership without changing historical
measurements. No runtime API or dependency changes are required.

## Why and reproduced evidence

In molsyssuite@uibcdf_3.14 (Python 3.14.7), ten regression cases execute the actual
benchmark string in cold child interpreters with synthetic Ackredit/MolSysMT
callbacks, or call the actual stability test with a controlled failing read or
assertion. Against the original source, eight fail and the two non-persistence
controls pass. After repair, all ten pass. They check writer closure while the
session still exists, both operation outcomes, partial setup/close errors,
observable removal errors, preserved earlier exceptions, unchanged timing and
caller-owned evidence, and cleanup after both stability-test failures.

The original positive legacy-format test and local reporting guard also pass:
12 selected tests total. Ruff check/format pass across the repository; generated
report indexes are checked after archival. The shared environment and editable
primary receptor origins are unchanged, including the seven existing dependency
conflicts tracked in uibcdf/molsyssuite#82. Hosted exact-head evidence is recorded
in the closing owner issue and the central rollout receipt after execution.

## What was refuted

Closing the writer alone does not remove its files. Unlinking only on success
cannot protect assertion/read failures. Silent removal or an age/prefix cleaner
would hide errors or risk caller resources. Standard managed contexts suffice;
there is no need for a new shared cleanup framework or runtime persistence API.

## Scope and exclusions

Only developer benchmark ownership and the adjacent test fixture are repaired.
Synthetic callbacks verify lifecycle rather than MolSysMT science or performance.
No MolSysMT scientific benchmark/suite, package upload/promotion, release choice,
primary-clone mutation, caller-environment deletion or whole-component resource
compliance claim. All full tool/retrospective reviews remain with their owners.
Registered ACKREDIT_GUIDE.md consumers need no API, guide or caller-pin adoption.

## Acceptance criteria

The module guard is addressable and collectively protects the failing mechanisms:
eight cases fail before the fix and pass afterward, with two unchanged controls.
Writer closure precedes removal; both exits clean; removal failures are visible;
setup/teardown remain outside timing; caller output survives. Preserve exact-head
native CI evidence and remove this task's fixtures/isolated clone after closeout.
