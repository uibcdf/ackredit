---
summary: Bind installed release identity to the candidate rather than checkout tags.
issue: uibcdf/ackredit#141
status: resolved
opened: 2026-11-11
closed: 2026-11-11
severity: medium
verification: measured
area: [tests, distribution]
guard: tests/test_versioning.py::test_installed_candidate_identity_does_not_depend_on_checkout_tags
normative:
blocked_by: []
supersedes: []
---

# Installed candidate identity and additive receiving

## What

All eight cells of installed build-0 matrix 43138505283 fail one source-only
version assumption: installed 0.12.2 versus shallow checkout fallback 0.0.0.
The new explicit packaging tools activate a previously skipped versioningit probe.
The shared runner correctly verifies/install bytes and freezes original producer
tests; the failure is in Ackredit's test contract, not the uploader.

## How

GHR identifies the failed step. One native Linux/Python 3.14 job log, acquired
only for the omitted exception, reports 2,252 passes, 17 skips and one failure.
Existing local package smoke and real PyUnitWizard receiving pass but cannot
replace this mandatory failing matrix.

Distinguish exact installed canonical runtime/distribution against the committed
candidate version from development/source Git-derived versions. Keep the source
parser, development suffix and actual installed-file/provenance guards. Reject
stale installed packages and mismatched metadata. Three boundary regression
cases fail before repair, including the valid installed/no-tags case and
wrong-identity diagnosis; corrected tests pass without manufacturing tags,
setting version overrides, skipping or deselecting the failed assertion.

The bundle operation already owns receiving identity. Extend its strict existing
Conda-record check to canonical nonnegative build numbers and bind filename to
actual source plan. Three plan/build cases fail before the repair; negative
build forms are rejected and legacy build-0 manifests remain supported. Schema
fields do not change, and full digest/producer/after-science checks remain.

## Why

A canonical package is qualified before its release tag exists. Its original
source Git baseline cannot establish the separately frozen artifact identity.
The source-only comparison would turn correct metadata/tool provisioning into
an erroneous installed release failure.

## What was refuted

A shallow checkout is not evidence that the installed archive is version 0.0.0.
Fetching old tags alone still cannot make a pre-tag development baseline equal
the future canonical candidate. Forcing tags/version overrides or waiving tests
would mask this scope error. Passing smoke/receiving alone does not qualify the
full installed suite. No failure of immutable public 0.12.1 is inferred.

## Scope and exclusions

Original build 0 at `045b33df72c83ad5663a9a35c6cfdbafd925f6ae`, staging
43137946395, file `ackredit-0.12.2-py_0.tar.bz2`, SHA-256
`bbbb545e24ae3a8871c9431603ee1a4c2e4090ad86ad8f648a3a18f294fed29c` stay immutable
and unqualified. #140 selects additive build 1 with a new original producer and
all new gates. No package is overwritten, rebuilt under the old coordinate,
promoted from failed evidence or withdrawn. No runtime/API/schema change.

## Acceptance criteria

Reproduce the old boundary failure and retain rejecting cases after correction.
Exercise actual exact installed package identity locally. Preserve strict legacy
and additive receiving, then commit the new build plan and repeat all release
gates. Retain original producer/archive and failed-run evidence separately.

## Executed correction

[The receipt](../../devtools/receipts/installed_candidate_identity_141_2026-11-11.json)
retains all eight native failure summaries/log digests and the unchanged archive
proof. Six added regression cases fail before repair; 60 selected cases pass after
repair. With the original exact build-0 archive still installed outside the
checkout, the corrected version/bundle module selection also passes without skips.
This is evidence for the test correction, not a waived release qualification.
#140 remains active for the new additive producer and all mandatory gates.
