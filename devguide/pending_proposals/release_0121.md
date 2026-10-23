---
summary: Qualify one exact maintenance artifact for faithful large-workflow snapshots.
issue: uibcdf/ackredit#134
status: active
opened: 2026-10-22
closed:
severity: medium
verification: asserted
area: [distribution, release, performance]
guard:
normative:
blocked_by: []
supersedes: []
---

# 0.12.1 maintenance delivery

## What

Prepare the maintenance candidate following the maintainer's 2026-10-22
resumption toward a possible tag/release. #133 removes quadratic enclosing
snapshot reconciliation, preserving complete output and bounded contracts.
The completed #132 review and #130/#131 tool repairs retain their separate
developer-only scope. No new public API or general 1.x promise is introduced.

## How

The committed staging plan, root/packaged CFF and candidate notes name 0.12.1.
Require exact-source CI, full Linux/macOS arm64 x Python 3.11–3.14 qualification,
both policy gates, one inspected noarch build, full installed same-file matrix
and real pinned PyUnitWizard receiving. Verify the new snapshot guards against
the installed file. Then complete the release decision, exact-file promotion,
independent public labels/solver verification and clean public installation.
Only verified delivery permits a canonical tag at the original producer and
updated recommended installation. GitHub release title, if published, is
exactly `0.12.1`; Zenodo remains a separate unclaimed outcome.

## Why

The editable-source study in #133 finds a real bounded improvement: at 5,000
uses, snapshot medians fall from 1.20–1.28 s to 0.24–0.33 s with all 126 full
payload fingerprints preserved. Peak traced allocation increases by about
0.8 MiB; small cases do not show a consistent speedup. Those measurements
justify a maintenance candidate, not a universal or installed performance claim.

## What was refuted

Source timings, a green development probe or guide delivery do not qualify a
public file. No old coordinate/tag/archive may be overwritten or rebuilt.
The source maintenance review alone is not a new product feature.

## Scope and exclusions

Portable >=0.9.0, providers >=0.11.0 and bounded evidence/standalone validation
>=0.12.0 remain unchanged. Scientific algorithms, client sources, provider
dependency floors, saved schemas and canonical guide contents are unchanged.
Any later guide edit requires a MolSysSuite synchronization issue; clients own
their runtime/release adoption. General 1.0 and acknowledgement work remain deferred.

## Acceptance criteria

- Commit reviewed inputs; execute every mandatory gate for the exact candidate.
- Retain original producer/archive/SHA-256, installed/real receiving proofs,
  independent public verification and clean-channel installation evidence.
- Preserve tags/artifacts, candidate and qualification source identities; report
  any shared-publisher failure with its execution and receipts to its owner.
- Publish release documentation and owning closures only after applicable proof;
  retire task-owned resources when no longer useful and refresh the checkpoint.

## Local candidate gates

The complete local source run collects 6,449 cases: 6,435 pass, five isolated
build cases fail/error because the sandbox cannot resolve PyPI, and nine skip.
Targeted network-enabled retries execute those five build cases plus the wheel
case that skipped for the same reason: all six pass with unchanged source.
Therefore 6,441 distinct cases have passing evidence; eight optional real
publication-tool cases remain skipped for absent Pandoc/Biber/JabRef. This is
not an all-tools execution claim. Strict Sphinx, Ruff and reporting indexes pass.
All test/build scratch is managed and removed after extracting normalized proof.
The current shared environment's seven unrelated dependency conflicts remain
MolSysSuite #82; fresh release dependency closure must be verified separately.
