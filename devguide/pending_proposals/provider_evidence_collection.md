---
summary: Collect bounded provider-recorder facts only in opted-in overlapping captures.
issue: uibcdf/ackredit#105
status: active
opened: 2026-10-05
closed:
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
