---
summary: Preserve explicit recorder declarations separately from original portable attribution.
issue: uibcdf/ackredit#104
status: active
opened: 2026-10-05
closed:
severity: medium
verification: asserted
area: [portability, reporting]
guard: tests/test_attribution_evidence.py
normative:
blocked_by: []
supersedes: []
---

# Explicit attribution evidence

## What

Roadmap J needs explicit metadata origins, selected observation boundaries and
diagnosed recording gaps. Existing single/bundle portable schemas define none
of these. The #103 descriptive view correctly keeps them unknown.

## How

The provisional `AttributionEvidence` tool validates and detaches a separate
`ackredit.attribution_evidence@1` envelope around a complete original single
attribution or bundle. Positional entries retain independent original boundaries,
even for repeated names and empty captures. Each evidence plane is null
(unrecorded) or a list of explicit recorder declarations. Empty lists do not
establish completeness or absence of failures.

Origins identify retained item fields, method, source locator and recorder.
Multiple origins can describe the same field; the reader does not infer history,
select a winner or verify bibliographic truth. Observation boundaries identify
mechanism, recorder and selected/unsupported/unobserved status. Gaps retain
boundary, recorder and owning diagnostic code. A gap can be known even when
observation scope is unrecorded; boundary names are recorder identities, not
inferred graph targets or missing calls.

JSON and explanations remain inert. CLI selects `--input-format evidence`
explicitly. The companion's explanation reports declarations separately from
the original descriptive view; bibliography/workflow/provenance formats delegate
to the unchanged original. Saving both planes requires `to_json`, never a
bibliography-only JSON report.

## Why

Accurate coverage reports need positive, bounded evidence. This representation
lets a host retain what its recorder actually knows without inventing reserved
meaning inside arbitrary caller-owned context or changing the released schema-1
promise. Saved readers require no scientific producer, network or new credits.

## What was refuted

Do not infer origin from DOI/URL, selected scope from graph membership, execution
from selected instrumentation, or scientific failure from recording diagnostics.
Do not merge repeated original names, union independent graphs, infer ordering
as time, accept unknown structural fields, or silently auto-detect the envelope.
Accepting a recorder's source declaration cannot verify its truth.

## Scope and exclusions

This independently closable representation milestone is provisional pending
recorder and receiving review. Existing `prepare_credit` and `observe_calls`
remain provisional. No automatic collection, observer/capture/registry hot-path
change, sibling source edit, canonical-guide rollout, dependency change or public
release. Recorder integration remains a separate J milestone. Shared-provider
and platform review are linked in MolSysSuite #97 and MOLI #46.

## Acceptance criteria

- Complete detached originals remain separately readable and existing reports
  byte-identical; original versions, empty/reused members and planes survive.
- Refuse unknown contracts, absent referenced items/fields, unsupported statuses
  and invalid diagnostic/recorder identities through the diagnostics catalog.
- Explanations retain explicit partial failures and unsupported/unobserved scope,
  without citation truth, completeness, call counts or scientific success claims.
- Fresh CLI and a normal installed reader block producer/network/new recording.
- Applicable local and exact-head gates retain their executed/missing scopes;
  queued hosted jobs never count as passed evidence.

## Implementation checkpoint — 2026-10-05

Implementation and focused qualification are underway. Codecov has been reported
fixed by the maintainer; pending runner acquisition remains separately tracked
in #102/#103. No earlier cancelled job or historical receipt is relabelled green.

Focused Python 3.14.7 qualification passes 198 tests covering the companion,
existing explanation/CLI and public stability classification. Ruff check and
format, current indexes and strict nitpicky Sphinx pass. Full source and normal
installed saved-reader qualification remain separate and underway. The sandbox
cannot resolve isolated build requirements or the official Python documentation
inventory; unrestricted gates execute those boundaries without weakening them.

Full Python 3.14.7 source qualification passes 2,018 tests without skips. Complete
Pytest Receptor events are retained at the local checkpoint. Explicit source
`PYTHONPATH` selects this owned worktree for spawned CLI tests; the forthcoming
normal installed reader will use neither source insertion nor an editable import.
The initial sandbox run passed 2,016 tests, but isolated-build DNS caused one
failed and one skipped build test. The unrestricted final gate executes and
passes both. No behavior or dependency requirement was weakened.

## Normal installed saved-reader checkpoint — 2026-10-05

Clean source `cddf48fe1cc30da5d4c3ff933793fc600e7f0ae5` builds once in
normal isolation. Candidate `ackredit-0.10.1+15.gcddf48f-py3-none-any.whl`,
SHA-256 `f6c7b157488d5b012aad06c91290dd1748b286e99f52a419c824f7b7afb32f98`,
is normally installed outside every checkout. The owning `wheel_record` and
`verify_installed` tools verify archive identity, version/origin and all 70
package files. `pip check` passes. Its separate environment reuses the shared
Python 3.14.7 dependency foundation; the shared editable install is not evidence
for this normal-installed gate.

Eight retained actual #102 receiving inputs exercise original single/bundle
readers, unknown planes and explicitly controlled companion declarations. Fresh
CLI reads match library reports while producer/engine imports, network and new
recording are blocked. Original versions/results stay exact and sixteen prior
workflow reports reconstruct byte-identically. The companion declarations are
contract-test fixtures: they do not establish original producer origins, observed
scope or actual recording failures. This is a local Linux/Python 3.14 saved-reader
gate, not a newly executed scientific/platform matrix or recorder integration.

The [reviewed receipt](../../devtools/receipts/explicit_attribution_evidence_104_2026-10-05.json)
retains exact source/wheel, complete source events, installed identity and input/
output hashes. Qualification of the final hosted head remains pending; #104 stays
active until applicable controls execute. Recorder integration and provisional
promotion are separate follow-ups even after this representation milestone closes.

## Final hosted head observation — 2026-10-05

Head `d7120eb270d016b8b01360b7c5a8512141baf775` suite policy
37374182562 and publication policy 37374182641 pass. CI 37374181512
passes six jobs but cancels Linux/Python 3.11 job 111978448341 before any
steps. Its native annotation identifies hosted runner acquisition failure.
The missing executed CI cell keeps #104 open. Provider-recorder collection is
independently owned in #105; no cancelled attempt is relabelled successful.
