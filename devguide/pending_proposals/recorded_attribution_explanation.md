---
summary: Explain recorded evidence while preserving unknown instrumentation, metadata origins and diagnosed gaps.
issue: uibcdf/ackredit#103
status: active
opened: 2026-10-05
closed:
severity: medium
verification: reproduced
area: [portability, reporting]
guard: tests/test_attribution_explanation.py
normative:
blocked_by: []
supersedes: []
---

# Recorded attribution explanation

## What

Roadmap J requires accurate explanations of coverage, reference origins and
recording gaps. Existing portable schemas define bibliography, contextual uses
and graphs, but no negotiated observation-scope/origin/diagnosed-gap evidence.
An empty capture or full bibliography cannot justify a completeness claim.

## How

The reusable offline `explain_attribution` tool accepts validated `Attribution`
or `AttributionBundle` and returns a detached `ackredit.attribution_explanation@1`
descriptive view. Count distinct contextual evidence within each original, retain
its roles/targets, describe explicitly absent fields and preserve reused/empty
bundle members. Do not aggregate independent graphs or treat input order as time.
The new `explanation` format delegates to this tool for saved/live/CLI reports.

## Why

Users need to distinguish recorded citations from actual instrumentation scope,
metadata sources, diagnosed recording failures and scientific completion. The
first milestone makes those distinctions useful without pretending a stronger
collection contract already exists or adding hot-path work.

## What was refuted

Do not derive origin from DOI/URL or arbitrary caller-owned context/extra fields.
Do not call a graph node without direct citations a recording failure; enclosing
workflow nodes legitimately have none. Bibliography without contextual uses is
not proof of unused software. Field absence is not a compulsory citation rule,
quality rating or scientific/bibliographic verification. No coverage percentage,
call count, success or global missing-citation inference is available.

## Scope and exclusions

This independently closable first J milestone changes no portable payload or
existing default format. Instrumentation scope, metadata origin and diagnosed
gaps explicitly remain `not_recorded`. The view is not a new attribution reader
payload. Its tool has deliberate pre-1.0 stable intent; observer/prepared APIs
remain provisional. No dependency, observer/capture change, guide rollout, tag,
public artifact, client source change or shared adoption mandate.

## Subsequent representation and collection decision

Stronger explanations need explicit producer/recorder evidence. Before adding
fields, review a separate typed evidence representation and ownership, preserving
the released schema-1 meaning and arbitrary host context. Retain selected
observation boundaries and actual metadata origins separately from evidence of
use; diagnosed recording gaps retain owning diagnostic identities and bounds.
Saved readers must preserve original information without inspecting their own
registry or services. Partial failure and unsupported/unobserved operations need
positive evidence; absence remains unknown. Shared/platform review remains in
MolSysSuite #97 and MOLI #46. This later collection work remains unchecked in J.

## Acceptance criteria

- Reuse validated readers, independent original boundaries and existing reporting.
- Guard empty/partial/identifier-only metadata, absent software version,
  distinct/repeated use contexts, entry/backend roles, unscoped uses and cyclic
  or structural graph nodes without inventing missing calls or success.
- Views are detached and originals/registry/session unchanged; arbitrary claims
  in caller-owned data cannot become negotiated origin/scope/gap evidence.
- Fresh saved-input readers and CLI exclude producer/engine imports, network
  and new credits; normal installations operate outside source checkouts.
- Applicable code/quality/reporting/docs checks and exact-head evidence pass;
  retain missing hosted scope and recovery instead of claiming queued jobs pass.

## Implementation checkpoint — 2026-10-05

The provider-owned analysis and format are implemented, using catalog-backed
input/option refusal. Existing workflow/bibliographic renderings and portable
schemas retain their defaults. Source, installed-reader and hosted gates remain
to complete before closing this issue.

Python 3.14.7 source qualification now passes 1,956 tests without skips, plus
Ruff check/format, current indexes and strict nitpicky Sphinx. The complete
Pytest Receptor events are retained locally. For this disjoint source worktree,
the source gate explicitly sets `PYTHONPATH` to its root so spawned CLI readers
test the selected code rather than the primary human-edited installation. An
initial mismatch revealed that environment distinction. A sandboxed retry had
one failed and one skipped normal-build test because DNS blocked build
requirements; the unrestricted final run executes and passes both. No test or
dependency requirement was weakened. Clean source installation, saved real
receiving inputs and exact-head hosted checks remain separate gates.

## Normally installed saved-reader checkpoint — 2026-10-05

Clean source `faa330b68013d08afa0421d3055db097dfb355a3` builds in normal
isolation. The candidate `ackredit-0.10.1+13.gfaa330b-py3-none-any.whl`,
SHA-256 `8ff0c78018b749d3d361aca5894c8fde9e63272fa4666a3f488937898bf50623`,
is normally installed outside the source checkouts into a separate Python
3.14.7 environment. The owning `verify_bundle` / `verify_installed` operations
verify its archive, distribution/runtime identity and all 69 package resources;
`pip check` passes. The shared editable installation is not substituted for it.

Offline Python and fresh CLI readers reconstruct single-result and bundle
explanations from retained actual PyUnitWizard inputs in all eight original
#102 scientific cells. Original versions and members remain exact; producer
imports, network access and new credits are blocked. Sixteen earlier workflow
reports reconstruct byte-identically. This tests the new saved-reader boundary
on Linux/Python 3.14, not a newly executed eight-platform scientific matrix.
The temporary normal installation reuses the shared dependency foundation.

The [reviewed receipt](../../devtools/receipts/recorded_attribution_explanation_103_2026-10-05.json)
retains exact source/wheel/resources, complete source events and each original
input/view/report hash. Source CI 37370412974 and both policy lanes remain
pending; this report/issue remains active until applicable gates complete.
