---
summary: Release qualification misses stale packaged self-citation versions.
issue: uibcdf/ackredit#94
status: active
opened: 2026-10-04
closed:
severity: medium
verification: reproduced
area: [packaging, discovery]
guard: tests/test_release_citation.py::test_self_citation_matches_committed_release_candidate
normative:
blocked_by: []
supersedes: []
---

# Release qualification misses stale self-citation versions

## What

Published 0.10.0 reports runtime/distribution 0.10.0 but its packaged CFF
discovers version 0.9.0. Both CFF copies were overlooked during preparation.
The same staged file passed source, installed and real-producer gates because
none compared the citation version with the committed candidate/runtime.

## How

The public archive is `ackredit-0.10.0-py_0.tar.bz2`, SHA-256
`2ed4841af32eaee603574b185a644fc16c9473497ad15a732788d6630b9cedc3`,
original source `16c356d54f245db8dd7fd6aaab72200df9a96e7d`.
A clean public Python 3.14.7 installation reproduced discovered self-citation
version 0.9.0 while runtime/metadata equal 0.10.0. Optional-provider/prepared
credit and detached reporting pass there; self-citation is still inaccurate.

Two new guards first fail: candidate-plan/CFF identity and the missing installed
citation-version verifier. The source guard compares both copies to the plan
before a tag exists. The recipe/source installed smoke now rejects canonical
release versions whose discovered CFF disagrees. Development versions may name
a planned next release in CFF; they do not certify an exact release identity.

## Why

Discovery prefers the project's CFF version. A tool preserving original
bibliography must ship accurate bibliography of itself. The prior source guard
only compared with the preceding tag; packaged-resource presence, correct
authors and correct runtime metadata were insufficient.

## What was refuted

This is Ackredit's preparation and gate omission, not a shared publisher defect.
The byte-preserving build/promotion did what its inputs requested. No provider
cache, public environment corruption or consumer source change caused the gap.

## Scope and exclusions

Prepare additive 0.10.1 with updated root/packaged version and release date,
then repeat its own exact-file gates and public verification under #93. Preserve
0.10.0 bytes, source/tag and receipts; no overwrite, withdrawal or retargeting.
No API, payload-schema, core dependency or stable-classification change.

## Acceptance criteria

Both source and installed guards pass; the exact corrected published archive's
discovered self-citation equals runtime/distribution 0.10.1. Retain the original
defect and corrected delivery evidence, then archive this record and close #94.
