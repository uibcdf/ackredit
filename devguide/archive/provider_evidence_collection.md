---
summary: Collect bounded provider-recorder facts only in opted-in overlapping captures.
issue: uibcdf/ackredit#105
status: resolved
opened: 2026-10-05
closed: 2026-10-05
severity: medium
verification: asserted
area: [portability, providers, performance]
guard: tests/test_provider_evidence.py
normative:
blocked_by: []
supersedes: []
---

# Provider evidence collection

## What

The provisional #104 companion retains explicit declarations, but its original
reader qualification used controlled declaration fixtures. Roadmap J also needs
facts supplied by the real runtime recorder, with bounded costs and ownership.

## How

The provisional `capture(..., record_evidence=True)` extension allocates a private
bounded collector and exposes a detached `.evidence` companion. Existing capture
and attribution defaults remain unchanged. Observer activation and capture entry
retain selected direct exports only when their context/session overlaps. Actual
successful reference writes retain the original provider-declaration field source;
a partial writer failure retains the origins already successfully credited.
Provider warning identities enter the gap plane without replaying diagnostics.

Use the existing validated `AttributionEvidence` representation. Metadata sources
name the frozen `module.__ackredit__.items` activation declaration. Recorder
identity includes the original Ackredit runtime version. Deduplicate bounded
facts by selected boundary, item/source and boundary/diagnostic code, not by call
count. Reused/nested captures each retain their own facts. Other sessions,
unselected task contexts and closed captures do not receive them.

## Why

Users need useful positive evidence without guessing completeness. Selecting an
export does not imply a call. Recording its metadata origin does not verify
bibliographic truth or successful science. An observer's diagnosed gap should
survive with its result while the scientific callable remains available.

## What was refuted

Do not infer import/discovery/DOI origins or missing references from this observer.
Do not assign origins to plain explicit credits or aliases obtained before
activation. Generator refusal remains the existing activation error, not an
invented selected/unsupported capture event. Scientific exceptions are outside
recording diagnostics and must not become recording gaps. Empty planes remain
unknown rather than being stamped complete.

## Scope and exclusions

Only opted-in provider-observer collection is implemented. Existing original
portable schemas, report defaults, client optionality and legacy journals retain
their contracts. This extension and observer/prepared/evidence APIs remain
provisional. No sibling source edit, dependency, canonical-guide rollout, tag or
public artifact. Shared review is linked in MolSysSuite #97 and MOLI #46.
Discovery, enrichment, explicit-credit origins and broader workflow presentation
remain subsequent roadmap J work.

## Acceptance criteria

- Selected-but-unused boundaries and actual successfully credited field sources
  stay separate; partial writer failures and scientific failures remain distinct.
- Origins, recorder version and diagnostic identities survive saved explanation
  without new warnings, producer imports, engine access or credits.
- Reused/nested captures, context-local tasks/sessions, aliases and closed scopes
  retain bounded evidence; default captures allocate no evidence builder.
- Use the owning benchmark to record local costs and limits, without timing tests
  or a claim of global performance/coverage certification.
- Source and real normal-installed receiving gates validate the actual candidate,
  resources and dependency closure; pending exact-head controls remain visible.

## Implementation checkpoint — 2026-10-05

The provider boundary and opt-in collector are implemented. Source, benchmark,
real receiving and hosted gates are being completed. #104's exact-head suite
policy 37374182562 passes and publication policy 37374182641 passes. CI
37374181512 passes six jobs but cancels Linux/Python 3.11 job 111978448341
before any steps; the native annotation identifies hosted runner acquisition
failure. This is separate from the maintainer-reported Codecov correction.
#104 remains open pending its missing executed control, without blind retries.

Focused qualification passes 107 source tests without skips. Python 3.14.7 full
runtime source qualification passes 2,043 tests, followed by 26 passing aggregate
contract tests after adding the ninth designated receiving case. The updated
aggregate refuses old eight-test or missing provider-evidence proof records;
historical source/artifact identities remain unchanged. Final expanded source
qualification and actual normal-installed receiving still need completion.
Ruff and strict nitpicky Sphinx pass; sandbox DNS failures in isolated-build and
inventory access are rerun with network permitted, without weaker requirements.

The owning `benchmark_portable.py` now includes opted-in observation, nested
capture, snapshot and explanation scenarios. Five local samples of 2,000 warmed
calls retain default provider-capture medians around 9–10 microseconds and an
opted-in median around 12 microseconds for one reference. Snapshot/report cases
are measured separately after execution, outside the scientific loop. This small
workload, single interpreter/machine and sequential sampling do not establish a
global speedup, memory budget, cold-import cost or large/dense workflow guarantee.

Expanded Python 3.14.7 source qualification now passes 2,047 tests without
skips, with complete/integrity-valid receptor events. The mandatory receiving
module adds its ninth real pipeline case and the aggregate requires the new
proof files in all eight platform/minor cells. Local normal-installed execution
and subsequent hosted qualification remain separate checkpoints below.

## Normal installed receiving checkpoint — 2026-10-05

Clean producer `cbaa93727bcf8a64902a76e72d961909c203a6b9` builds one
local candidate `ackredit-0.10.1+17.gcbaa937-py3-none-any.whl`, SHA-256
`bad4e656038cde1ddb6bc8f4f45cb2d97d2aaf4516163a91d9427d97a44d5485`.
The owning qualification bundle verifies its archive and all 70 package files.
Ackredit and pinned PyUnitWizard `0e422d06b0af56e4dd2b43cafd00f059221eb405`
are installed normally into a separate Linux/Python 3.14.7 environment with real
Pint/unyt. `pip check` passes; neither editable/source import substitutes for this
receiving checkpoint. The temporary environment reuses the shared dependency
foundation and its existing installed unit engines, not a fresh Conda solve.

All nine designated cases pass without skips, including the new actual collector
case, preceding pipeline/report/composition checks, optional absence and original
0.9.0 fallback. The new case checks real field-bounded provider declaration origins,
unknown backend-recorder origins, selected-but-unused scope and a controlled writer
fault without changing scientific values/units. A fresh offline reader blocks
producer/engine imports and new credits, retains the original companion/workflow,
and replays no diagnostics. The fault is deliberately injected into the recorder;
it is not a discovered scientific/backend failure.

The first local nine-test pass lacked its receptor stream because its output
folder was created after the receptor opened. After the directory existed, the
entire designated gate reran: all nine pass with complete, integrity-valid events.
Only that latter stream qualifies this receipt. No artifact requirement is waived.
The [reviewed receipt](../../devtools/receipts/provider_evidence_collection_105_2026-10-05.json)
retains exact source/packages, events, proofs and all benchmark samples/limits.

The expanded eight-cell hosted scientific matrix and final-head source/policy
checks still require separate execution. This local case does not qualify another
platform/minor, a public file or stable promotion. #105 remains active until its
applicable hosted gates complete. Follow-up recorder origins and broader workflow
presentation remain pending even after this provider collector qualifies.

## Hosted receiving and closure — 2026-10-05

Unskipped qualification head `6f8f361fc11143d7507ba9ff6c7aee75a7a4ac6e`
passes all seven CI jobs in 37419490119, suite policy 37419490746 and publication
policy 37419490614. GH Run Receptor reports each executed lane successful.
Receiving run [37419599184](https://github.com/uibcdf/ackredit/actions/runs/37419599184)
also passes all ten jobs. Its eight normally installed Linux/macOS arm64 ×
Python 3.11–3.14 cells each execute all nine designated tests: 72 passed, zero
skips/deselections. Actual real-provider origins, selected-but-unused boundaries,
controlled recording faults and producer-free saved readers qualify together
with the preceding scientific, optional-absence and released-fallback contracts.

The original hosted candidate is
`ackredit-0.10.1+17.gcbaa937-py3-none-any.whl`, SHA-256
`b9d5caf7fab45a250b5d20dd1c1b4e63c0cf38bee0cb635a795148a8226662b3`,
from the original clean `cbaa937` producer. It is built once and the same archive
goes to every hosted cell. The separately built local wheel retains its different
digest above; the complete 70-file package maps match, but the archives are not
relabeled as each other. All ten GitHub artifact ZIP digests and extracted files
verify independently; the owning aggregate reproduces the hosted result exactly.
The [hosted receipt](../../devtools/receipts/provider_evidence_hosted_105_2026-10-05.json)
retains source/package identity, each cell's reader proofs, original archive/file
hashes and executed controls. The earlier local receipt remains historical.

The bounded provider collector is qualified and this implementation record is
resolved. All stated provisional contracts remain provisional. Broader recorder
origins, workflow presentation, public delivery and final stability review stay
separate. MolSysSuite #97 and MOLI #46 retain the cross-component review routes.
