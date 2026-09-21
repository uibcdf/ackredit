---
summary: Ackredit could only be installed from a clone; it now builds, tests and installs as a conda package.
issue: uibcdf/ackredit#22
status: partial
opened: 2026-09-21
closed:
verification: reproduced
area: [packaging, release]
guard: devtools/conda-build/meta.yaml
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
