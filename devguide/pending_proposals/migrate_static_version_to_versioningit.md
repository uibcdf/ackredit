---
summary: Migrate Ackredit from a static package version to canonical Versioningit tags.
issue: uibcdf/ackredit#20
status: open
opened: 2026-09-21
closed:
severity: medium
verification: inspected
area: [packaging, release, governance]
guard:
normative: uibcdf/molsyssuite@policy-v1.4.1:devguide/release_version_policy.md
blocked_by: []
supersedes: []
---

# Migrate the static package version to Versioningit

## What

Ackredit declares `project.version = "0.5.0"` statically. Migrate the package to
Versioningit so release tags, built package metadata and the public package version derive
from one source of truth.

## How

Replace the static project version with dynamic Versioningit configuration. Use the
effective `[tool.versioningit.tag2version]` parser required by MolSysSuite
`policy-v1.4.1`, including `require-match = true`, and expose the installed version through
package metadata.

Add tests for canonical and rejected tags, built-wheel metadata and the public
`ackredit.__version__`. Repair the import/version workflow assertion tracked by #11 so a
later shell command cannot conceal its failure.

## Why

A static literal requires maintainers to coordinate package metadata and Git tags by hand.
It also permits a superficial fix for #11 that copies the literal into source code and
creates a third version location. The other dynamic-version MolSysSuite components now use
the canonical parser, so adopting the same mechanism removes that divergence.

## What was refuted

Adding `[tool.versioningit.tag2version]` while retaining a static `project.version` was
rejected. Versioningit would not own the version, making the parser inert configuration and
providing no release protection.

Copying `0.5.0` into `ackredit.__version__` was also rejected because it would address the
missing attribute without establishing one authoritative version source.

## Scope and exclusions

This proposal covers repository-local version derivation, package metadata, the public
version and their tests. It does not authorize a release, change Ackredit's incubating
status or authorize Python 3.14 support.

## Acceptance criteria

- `project.version` is dynamic and supplied by Versioningit.
- The effective parser accepts only canonical `X.Y.Z` release tags and rejects prefixes,
  suffixes and leading zeros.
- Built metadata and `ackredit.__version__` agree with the canonical tag-derived version.
- The CI version assertion fails reliably when import or version lookup fails.
- Tests guard parser behavior and installed-package version identity.
