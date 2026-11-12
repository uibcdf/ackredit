---
summary: Review required and optional runtime floors and align maintained acquisition routes.
issue: uibcdf/ackredit#138
status: resolved
opened: 2026-11-11
closed: 2026-11-11
severity: medium
verification: measured
area: [dependencies]
guard: tests/test_hooks_already_loaded.py::test_discovery_credits_nothing_that_was_already_loaded
normative: devguide/runtime_dependencies.md
blocked_by: []
supersedes: []
---

# Review required and optional runtime floors and align maintained acquisition routes

## What

Owner receiving for Ackredit #138, reviewed from source
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

The initial independent installed run collects 12,587 cases: 12,571 pass,
14 skip and two fail. Exact ArgDigest 0.13.0 eagerly imports NumPy and violates
`tests/test_hooks_already_loaded.py::test_discovery_credits_nothing_that_was_already_loaded`.
Provider fix `bc14d57` is released at tag 0.15.0, source
`57447cc4ec1f7ce85078f8a939892efd075bc919`. Raise this consumed-contract floor
to >=0.15.0 across metadata, recipe and all runtime environments; no cap.

The second failure is local build contamination: a generated September
`build/lib/ackredit/contrib/web_ui.py` survives source deletion and enters the
wheel. Its file inventory/digests are retained, the exhausted generated tree is
retired and a clean wheel is installed. This is not evidence that immutable
public 0.12.1 contains the obsolete module. Its recorded original files remain
authoritative; qualification of 0.12.2 uses a fresh immutable producer checkout.

The optional DueCredit boundary has real receiving proof at exact 0.10.2 and
public 0.11.2: two cases per version pass without skips, preserving observed
DOI/BibTeX and omitting unused records. This is a qualified supported floor,
not a claim about the API's earliest historical availability. The ordinary
runtime/core requirements still omit DueCredit. PyYAML's 6-series floor remains;
the resolved Python 3.14 prefix selects 6.0.3, while a separate official 6.0
wheel pure-Python source probe passes 92 CFF cases, not native cp314 installation.

The maintained `devguide/runtime_dependencies.md` records consumed APIs,
route classifications and limits. Central graph receiving belongs to
MolSysSuite #192; owner adoption confirmation goes to #137 after source publication.

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
