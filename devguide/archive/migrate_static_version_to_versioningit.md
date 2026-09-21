---
summary: Migrate Ackredit from a static package version to canonical Versioningit tags.
issue: uibcdf/ackredit#20
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: medium
verification: reproduced
area: [packaging, release, governance]
guard: tests/test_versioning.py
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

## What was refuted

**Keeping the static literal and only exposing it as `__version__`** was the shape
`uibcdf/ackredit#11` left behind, and this record exists because that is a symptom fix:
the tag and the metadata stay two sources coordinated by hand, and `policy-v1.4.1`'s tag
parser cannot protect a repository that has no Versioningit configuration.

**Reading the version from `importlib.metadata` first** was refused after measuring.
SMonitor's `__init__` records that the metadata machinery pulls in `email.message`,
`zipfile` and `inspect`; measured here it is 55 to 65 ms of a 118 ms import. `_version.py`
is read first, as SMonitor does.

That reordering **saves nothing today**, and saying otherwise would be a claim the
measurement does not support: `depdigest/__init__.py` imports `importlib.metadata` on its
first line, so a consumer pays it regardless. The ordering is still the correct one — it
is what makes the saving available once the provider stops forcing it — and the
observation is reported to DepDigest as consumer evidence.

## Acceptance criteria

Met by the commit closing this record:

- `project.version` is gone and `dynamic = ["version"]` takes its place, with
  `versioningit>=3.0` in the build requirements;
- `tool.versioningit.tag2version.regex` is byte-identical to
  `policies.release-version.versioningit-pattern` in `suite.toml`, asserted by a test
  rather than copied and trusted, with `require-match = true`;
- canonical tags are accepted and `v1.2.3`, `1.2.3rc1`, `1.2.3.dev0`, `1.2.3+local`,
  `01.2.3`, `1.2` and `1.2.3.4` are refused;
- `ackredit.__version__` equals what Versioningit derives from the tag, which is the one
  assertion that catches the two drifting apart;
- the CI import check repaired in `uibcdf/ackredit#11` already cannot be hidden by a
  later shell command, guarded by `tests/test_workflow_hygiene.py`.
