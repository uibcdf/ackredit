---
summary: Qualify staged noarch delivery with the centrally accepted build action.
issue: uibcdf/ackredit#22
status: partial
opened: 2026-09-21
closed:
verification: reproduced
area: [packaging, release]
guard: tests/test_conda_release_route.py
normative: devguide/roadmap.md
blocked_by: []
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


## Local real-artifact diagnosis (2026-10-03)

The maintainer subsequently authorized fixing the owning build action and
required coordination in uibcdf/moli#38 and uibcdf/molsyssuite#78. A controlled
Miniforge reproduction confirms that the activated named environment contains
conda-build 26.9.0 but Conda's shell function delegates to the base manager
without that plugin. The action correction selects the activated environment's
executable with `command conda` for compilation and conversion. Failure exit
statuses and recipe tests remain enforced; provider regressions belong to
uibcdf/action-build-and-upload-conda-packages#46. The separate multi-variant
fixture/interpreter qualification repair belongs to provider #47.

The corrected compilation step builds the prepared Ackredit source
`15b1958b9752a89974bb1d0df882a17841ed62b4` after the shared ephemeral version
freeze. This local diagnostic uses action source
`e57130f913f8ffcb37fbdf91db0644b40bd25823`, public dependency channels and no
upload. Real recipe tests and the shared version/resource inspection pass for
`noarch/ackredit-0.9.0-py_0.tar.bz2`, SHA-256
`99e6f9b9f0a3b0a22c66e476230dddabd2ba0017c59beb3253fbadc781d665c6`.

That exact file installs normally in a fresh Python 3.14.7 environment with
public SMonitor 0.18.0, DepDigest 0.12.0 and ArgDigest 0.13.0. Off-checkout
installed smoke, saved original PyUnitWizard/unyt bibliography, capture of
reused references and `pip check` pass. Checked providers resolve under the
fresh environment's site-packages. The diagnostic receipt explicitly records
`uploaded: false` and `promoted: false`.

This demonstrates the failure mechanism and a working local noarch build;
it does not substitute for the shared hosted producer, staged registry file,
eight-cell installed gate or public delivery. Central immutable-pin adoption
remains owned by MolSysSuite #78. After adoption, Ackredit must update its
reviewed caller, qualify that exact candidate's source gates, stage once,
qualify the newly produced file and request the separate public promotion.


## Qualified provider publication and remaining adoption (2026-10-03)

The authorized correction is published on the build action's `main` at
`8da628d9b393e184c3bf3722708b19dcfbf7ef0a`. Hosted run `37115921728`
passes all four base/named-environment build cells, including actual recipe
execution and retained noarch files on Linux, macOS arm64 and Windows. Run
`37115921702` passes the unit job and both Linux/Windows multi-variant jobs:
eight archive payloads are checked per host and fresh Python 3.11/3.12 imports
assert their interpreter, prefix and module origin. GH Run Receptor confirms
both completed successes. All 23 provider unit tests also pass locally on
Python 3.14.7. The provider does not upload a registry package during these
checks. Its durable guards and qualification repair are recorded under #46/#47.

MOLI #38 and MolSysSuite #78 receive the immutable source and executed evidence.
The shared publisher still selects action `8a1f203`; central adoption must
update that pin through its owning repository. Ackredit must then adopt the
reviewed shared workflow source. This handoff changes the remaining blocker
from the provider implementation to central adoption; no central code is
modified here and no Ackredit public artifact is claimed.

At the maintainer's request, remaining local verification uses the Python
3.14.7 interpreter from `molsyssuite@uibcdf_3.14`. The clean candidate's isolated
wheel installation passes all 1,544 tests without skips; Ruff and report indexes
pass. This keeps the maintainer's nine pre-existing files byte-identical and
preserves the requested editable installation of the primary checkout in that
shared environment. The valid pip development flag is `--editable`; pip rejects
`--development`.


## Real installed receiver checkpoint (2026-10-03)

The local exact-file Python 3.14.7 environment now also installs the PyUnitWizard
wheel from source `dbafcc5`. All 17 existing owned attribution tests pass outside
both checkouts with no skips or editable imports; pip check passes. The precise
wheel/digest and runtime public dependencies are recorded under #75. This
supplies local installed-receiver compatibility while the shared hosted
staging/installed/publication gates remain pending. MolSysSuite #78's one-pin
adoption is prepared and passes its 277 central tests; central publication is
not claimed by that isolated preparation.


The maintainer requested central review through a PR rather than direct push.
PR uibcdf/molsyssuite#81 proposes commit
`4c96e794d207c7fe527b1676302f280b2fb31bff`; its full 277 local tests and
offline governance pass. The shared `main` remains unchanged by this proposal.
Ackredit's caller update and hosted staging await acceptance; an open PR is
not an adopted provider or an artifact receipt.

## Accepted central adoption (2026-10-03)

MolSysSuite PR #81 is merged at
`2a2a459cc3795bb92766fffa0fe28f4d80f01ad4`; its hosted governance run
`37125099269` succeeds. The shared publisher now selects the qualified build
action `8da628d9b393e184c3bf3722708b19dcfbf7ef0a`. Relative to Ackredit's
previous shared source, the publication workflows change only that build pin;
the installed gate, promotion route and publication checks retain their logic.

Ackredit pins all four publication callers to the accepted immutable central
commit. Its versioned engineering-policy adoption remains independent. Central
adoption no longer blocks this candidate; exact-source hosted gates, staging,
the exact-file installed matrix and receiving-consumer qualification must still
succeed before the separate public-promotion decision. This source change
does not claim a registry upload or close uibcdf/ackredit#22 or
uibcdf/ackredit#75.

Concurrent accepted commits adopt engineering policy 1.5.4 and the routine
Python 3.14 baseline. The release plan's required normal-CI macOS job is aligned
with that new interpreter; the eight-cell full and installed matrices retain
Python 3.11–3.14 coverage.
