---
summary: Register the published 0.9.0 Git identity and restore compatible editable metadata.
issue: uibcdf/ackredit#82
status: resolved
opened: 2026-10-03
closed: 2026-10-03
severity: medium
verification: measured
area: [packaging, development]
guard: tests/test_versioning.py::test_installed_version_is_not_older_than_verified_public_delivery
normative:
blocked_by: []
supersedes: []
---

# Register the published release identity

## What

Sabueso requires `ackredit>=0.9.0`. The Python 3.14 shared development workspace
reported editable Ackredit `0.8.0+69.g3c6e77c.dirty`, which failed that minimum
although the portable API was present and Conda 0.9.0 was already public.

## How

Both local and remote tags lacked `0.9.0`. Versioningit correctly derived the
version from the last available tag, `0.8.0`. Register the immutable annotated
`0.9.0` tag at original public producer source
`598abf993a2409c025de5e912acd7eb45a257ebd`; its remote tag object is
`b73944e9a930938ba3528f7aa52df9693c13eb91`.

The previously committed [public delivery receipt](../../devtools/conda-build/receipts/ackredit_0.9.0_public_2026-10-03.json)
records exact-source gates, eight installed matrix cells, promotion and public
installation. The original `ackredit-0.9.0-py_0.tar.bz2` archive retains SHA-256
`37661090f6ad19a74b8155d8a4d4b4a068c9099f4ceba0743b3abfe887e97fe1`.
The producer's build and promotion wrappers are manual-dispatch only. Registering
this tag does not rebuild, replace or upload that package.

Reinstall the current descendant checkout in `molsyssuite@uibcdf_3.14` with
`python -m pip install --no-deps --editable .`. Observed metadata and runtime
both report `0.9.0+7.g3c6e77c.dirty`; the actual import and editable direct URL
point to `/home/diego/repos@uibcdf/ackredit`. Sabueso's own declared requirement
accepts that version and `python -m pip check` reports no broken requirements.
All nine pre-existing human files remain byte-identical.

## Why

Public package identity and Git-derived development metadata must agree on the
release baseline. Consumer dependency checks consult distribution metadata,
even when the runtime API is already compatible.

## What was refuted

No static version override, lowered consumer requirement or replacement of the
required editable installation is needed. The tag belongs on the producer,
not on the later reporting commit or the dirty working tree. Conda promotion
alone does not create the matching Git tag or a GitHub Release.

## Scope and exclusions

This correction repairs Git and editable identity for the already qualified
public release. It does not create a GitHub Release/DOI, change runtime behavior,
qualify current human edits as a public candidate, or certify Sabueso's release.
The receiving coordination remains Sabueso #108; #22/#75 retain public delivery.

## Acceptance criteria and guard

Local and remote `0.9.0` resolve to the original producer. Editable metadata,
runtime origin, consumer minimum and dependency closure all pass.
`tests/test_versioning.py::test_installed_version_is_not_older_than_verified_public_delivery`
compares installed metadata and runtime identity with the verified public
release receipt. It fails against the original stale 0.8.0 installation and
passes after reinstalling from the corrected tag history. Existing versioning
guards continue to require dynamic derivation and truthful development suffixes.

## Closure qualification — 2026-10-03

The unchanged public-minimum guard first fails against the stale 0.8.0 wheel
and then passes after rebuilding from the corrected tag history. All **1,548
Ackredit tests pass without skips** on Python 3.14.7, including wheel packaging,
with published Pytest Receptor 1.2.1. Ruff lint/format, report indexes and Sphinx
`-W` pass. The initial sandbox-only attempt could not fetch isolated build
dependencies and omitted that wheel test; the subsequent complete run supersedes
that incomplete result.

An additional current receiving probe in the shared editable Python 3.14
workspace passes **44 unchanged Sabueso attribution/acquisition tests**, no
skips. It runs outside both repositories with a read-only fixture link. This
confirms the development environment after the identity repair; the prior
normal public-channel installation and receiving receipts remain separate.
