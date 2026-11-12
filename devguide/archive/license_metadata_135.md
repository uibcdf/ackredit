---
summary: Migrate license metadata with real distribution and minimum-backend evidence.
issue: uibcdf/ackredit#135
status: resolved
opened: 2026-11-11
closed: 2026-11-11
severity: medium
verification: measured
area: [packaging]
guard: tests/test_license_distribution.py::test_wheel_sdist_and_rebuilt_wheel_preserve_license
normative:
blocked_by: []
supersedes: []
---

# Migrate license metadata with real distribution and minimum-backend evidence

## What

Owner receiving for Ackredit #135, reviewed from source
`4beb850c8ba814e6103b4d303128a1a36eb57610`.

## How

Review the actual consumed contracts and immutable provider handoff before edits;
retain executed checks and exact source/tool/artifact identities.

## Why

The maintainer authorized attending the open issues and then qualifying a new
maintenance release. Existing public 0.12.1 bytes and receipts stay immutable.

## What was refuted

A delivered shared guide or permissive declaration alone does not establish
owner adoption, actual minimum compatibility or installed/public qualification.

## Scope and exclusions

This owner review does not change scientific algorithms, schemas or accepted
API stability. No sibling checkout is edited; central feedback uses owning issues.
Dashboard #58 remains a deliberately deferred separate-distribution proposal.

## Acceptance criteria

Record the reviewed/adopted source, tested contracts, original notices and limits;
post an explicit Review completed disposition and link the central owner issue.
Qualify any later public package independently with exact-source and installed gates.

## Owner findings

Preserve the existing MIT expression and original 2025 author/lab notice.
The real distribution guard fails before repair because wheel metadata lacks
`License-Expression: MIT`; the old license file's absence was not alleged.
Migrate the expression and explicit `LICENSE` field, align Setuptools >=77.0.3
in metadata, Conda host, build bootstrap and nonisolated development/test routes.
Preserve versioningit >=3.0. Packaging guard/tool dependencies are test/build,
not core runtime requirements.

The wheel, sdist and wheel rebuilt from that sdist retain exact LICENSE bytes
and SPDX/license-file fields. The guard passes with current Setuptools 84.0.0 /
versioningit 3.3.0, and deliberately installed Setuptools 77.0.3 / versioningit
3.0.0 on Python 3.14.7. The fixture uses Ackredit's actual source/metadata in
managed scratch; it is not a public release or another platform qualification.
Central reference is immutable MolSysSuite
`41698b982ff56983a49c0089b135ed769a38b9da`; return disposition to #162.

## Executed disposition — 2026-11-11

Owner review is complete in source; the retained
[receipt](../../devtools/receipts/packaging_owner_reviews_2026-11-11.json) binds
actual failures, repairs, tools, versions and limits. The clean installed
minimum-prefix repetition has 16,534 passing cases, zero failures and fourteen
explicit skips. Its repository-wide example guards include ignored generated
files, inflating administrative case counts; hosted clean-source qualification
retains its own counts. There are 260 selected primary-provider passes, 28 shared
publication-contract passes, 92 exact PyYAML 6.0 pure-Python CFF passes, two real
DueCredit passes at each tested version and a real distribution pass at the
minimum backend. No package release is inferred; #140 owns that delivery.

The original minimum failure and old generated build contamination are not
rewritten into success. Primary Ruff checks pass, optional tools retain their
own limits, and central owner receiving is linked after this source is published.
