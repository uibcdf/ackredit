---
summary: Prepare and qualify exact noarch Conda delivery; the current hosted build remains incomplete.
issue: uibcdf/ackredit#22
status: partial
opened: 2026-09-21
closed:
verification: reproduced
area: [packaging, release]
guard: tests/test_conda_release_route.py
normative: devguide/roadmap.md
blocked_by: [uibcdf/action-build-and-upload-conda-packages#46]
supersedes: []
---

# Ackredit is published to no channel and can only be installed from a clone

## What

No conda recipe, no build environment, no publishing workflow, while every sibling had all
three. Roadmap theme A, and the one that blocks the rest: a host library cannot adopt what
it cannot depend on, and measuring a checkout is not measuring a release.

## How

```
                                          ackredit   smonitor
devtools/conda-build/meta.yaml            NO         yes
devtools/conda-envs/build_env.yaml        NO         yes
build_and_upload_conda_packages.yaml      NO         yes
```

## Why

This is the theme where a mistake is least recoverable. A published package cannot be
withdrawn the way a commit can be amended, and `devguide/release_version_policy.md`
forbids moving or deleting a published tag.

## What was refuted

**The simplest shape, publishing straight to the public label**, as `argdigest` does in 63
lines. It was refused because it verifies after publishing, which for a registry is the
wrong order. The workflow stages a candidate, installs it *from the staging label* into a
fresh environment, checks it, and promotes only on an explicit input.

**Treating this as coupled publication.** `uibcdf/molsyssuite#27` standardises staging for
components whose publication order is circular. Ackredit depends on SMonitor and DepDigest
and nothing depends on Ackredit, so there is no cycle; staging is adopted here for
verification, not coordination, and that distinction is recorded so the heavier protocol
is not assumed to apply.

## Scope and exclusions

Delivers and verifies the machinery. Excludes publishing, which needs the channel token
and is a release decision. The record stays `partial` until a package is on the channel
and the installation documentation is rewritten around it.

## What is done

Verified locally rather than asserted:

- `conda build` produces `noarch/ackredit-0.6.0-py_0.conda` and its own `test:` block
  passes — the version it reports equals the version it was built as, it discovers its own
  `CITATION.cff`, it renders a report, and `ackredit --help` runs;
- installing that artifact into a clean conda environment resolves the whole chain from
  the channel — `depdigest 0.10.1`, `smonitor 0.16.0`, `pyyaml 6.0.3` — and the installed
  package reports `0.6.0`, discovers itself with both authors, and renders BibTeX;
- the recipe's tests run against the built package rather than the source tree, which is
  where `uibcdf/ackredit#2` and `#21` both hid.

## What remains

- publishing a candidate to `uibcdf/label/staging` and promoting it;
- rewriting `docs/content/about/installation.md` around the published package, which must
      not be done before it exists.

## Candidate route repair (2026-10-03)

The combined workflow's `promote: true` step rebuilt and uploaded the version
again instead of promoting the tested bytes. The maintainer authorized candidate
preparation; the route now uses the reviewed shared noarch workflows at full
MolSysSuite commit `4010595a2ed756b20114730c6a91561a16d7be2f`.

Separate wrappers stage once, qualify the exact archive across Linux x86-64 and
macOS arm64 on Python 3.11–3.14, and promote only with an existing successful
installed run and SHA-256. The provider acquires exact-source executed native
gates, checks resources before upload, uses public dependency channels, retains
receipts and verifies public registry/index state independently. The source
publication guard and recipe/resource inspection pass; they do not certify an
upload or runtime artifact. `tests/test_conda_release_route.py` guards the former
rebuild/promotion defect and the exact installed-file/no-secret interface.

The committed staged plan prepares 0.9.0 build 0, the first reviewed portable
contract. CFF metadata and installation guidance identify the prepared candidate
without advertising an unverified public route. This release replaces the former
indefinite deferral with an exact candidate and qualification gates; it is not
permission to skip those gates. The repository has access to the organization
secret named `ANACONDA_UIBCDF_TOKEN`; availability is not proof of upload success.
No remote release tag or public promotion is performed by source preparation.


## Hosted candidate execution and provider handoff (2026-10-03)

Candidate `840aab3d415312144e4f5754d5def11b3068832f` passes normal CI
`37108539116`, full matrix `37108712359`, suite policy `37108539501` and
publication policy `37108539376`. Final local qualification passes 1,544 tests, Ruff,
devguide indexes and Sphinx `-W`. The full matrix executes all eight Linux and
macOS-arm64 Python 3.11–3.14 test cells; its conditional decision job is skipped
by design and is not a scientific test cell.

Staging run `37109889925` independently acquires the passing native source
gates and passes recipe/resource inspection and ephemeral version freeze.
The environment setup succeeds, including conda-build 26.9.0 in the named
`noarch-publisher` environment, but the selected action's compilation step
fails because `conda build` is not recognized. Recipe execution, archive
inspection and upload do not complete; there is no 0.9.0 artifact or digest.
GH Run Receptor locates the failed step; a targeted native step excerpt supplies
the missing exact error. Login shells are already selected by both the provider
and action, so adding that default is not a demonstrated correction.

The executable/plugin environment boundary is reported for provider reproduction
in uibcdf/action-build-and-upload-conda-packages#46, with shared-consumer
evidence in uibcdf/molsyssuite#27. No sibling implementation was modified and
no recipe test was suppressed. Historical 0.6.0 local evidence above remains
historical; it cannot qualify 0.9.0. The current candidate has no successful
production/installed/publication receipt. Resume from a reviewed immutable
provider correction and rerun the exact candidate's required source gates if
its committed inputs change, then stage and qualify the newly produced file.
