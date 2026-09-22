---
summary: The installation page pinned a superseded release and its environment omitted a dependency main needs, so the next release would have installed broken.
issue: uibcdf/ackredit#66
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: medium
verification: reproduced
area: [docs, packaging]
guard: tests/test_installation_page.py
normative:
blocked_by: []
supersedes: []
---

# The installation page fell behind the release and the dependencies

## What

`docs/content/about/installation.md` installed `ackredit@0.6.0` and showed
`__version__ == '0.6.0'` after `0.7.0` was tagged and named by `CITATION.cff`.

Its `conda create` line named `smonitor depdigest pyyaml pip`. Since
`uibcdf/ackredit#62`, `main` also requires `argdigest`; with it blocked,
`import ackredit` raises `ModuleNotFoundError: No module named 'argdigest'`. And the
page called the dependencies pure Python after ArgDigest brought `numpy`, a correction
`devguide/vision.md` had received and this page had not.

## How

The pin and both version examples now say `0.7.0`, the environment line names
`argdigest`, and the prose matches `vision.md`: four runtime dependencies, three of them
suite components distributed through `uibcdf`, with `numpy` behind ArgDigest.

## Why

This is the page a user follows literally, and `pip install --no-deps` installs nothing
it does not name. The dependency gap was latent — neither released tag needs ArgDigest,
so the recipe worked for both — and would have become a broken install at the next
release, when raising the pin is the one edit that looks sufficient.

## What was refuted

That the recipe was broken today. It was not: `argdigest` was adopted after `0.7.0`, and
`git show 0.7.0:pyproject.toml` lists only `smonitor`, `depdigest` and `pyyaml`.

## Scope and exclusions

The page is built from `main` and pins the last release, so for a moment between
releases the environment line may name a package the pinned tag does not need. Naming
`argdigest` for `0.7.0` installs one unused package; leaving it out breaks the next
release. The guard therefore holds the line to `main`'s dependencies, which is what the
next release will be cut from.

Publication to a conda channel remains `uibcdf/ackredit#22`.

## Acceptance criteria

`tests/test_installation_page.py` holds every release the page tells a user to install
to `CITATION.cff`, and its `conda create` line to `[project].dependencies`. Against the
previous page both fail, with the stale version and the missing package named.
