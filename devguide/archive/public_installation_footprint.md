---
summary: Measure the public Conda installation footprint against a fresh Python control.
issue: uibcdf/ackredit#118
status: resolved
opened: 2026-10-06
closed: 2026-10-06
severity: medium
verification: measured
area: [packaging, performance]
guard: tests/test_public_installation_footprint.py
normative:
blocked_by: []
supersedes: []
---

# Public installation footprint

## What

Roadmap L lacks external-user dependency-cost evidence. Developer wheels and
installed plugin fixtures do not establish the public Conda closure.

## How

Use native Conda JSON and separate fresh package caches to create Python-only
and Ackredit 0.11.0 environments on Linux x86-64/Python 3.14. Verify the original
public artifact, exercise installed smoke behavior, and reuse the lifecycle
worker for independent import timings and Python-allocation samples.

## Why

Retain package identities, archive sizes and actual linked-file sizes separately
from the small Ackredit archive and Python allocations. Distinguish current
public providers from completed but unpublished provider source improvements.

## What was refuted

A small noarch archive or a source import does not establish the receiving
installation's size. A single installation duration cannot establish a general
network/solver performance claim.

## Scope and exclusions

One clean Linux/Python 3.14 public route, a contemporaneous Python control and
bounded process samples. No publication, dependency-contract change, cache
implementation, third-party plugin workload or new platform qualification.

## Acceptance criteria

Retain native installed identities and measured facts, original public artifact
identity, behavioral smoke evidence, reproducible commands, documentation guards,
applicable local validation and inspected exact-head CI. Keep roadmap L open.

## Measured outcome (2026-10-06)

The documented strict public solve installs Python 3.14.8 and Ackredit 0.11.0.
All 24 Python-control packages keep their versions, builds and SHA-256 identities;
the receiving environment has 30 packages. The six additions are Ackredit,
ArgDigest 0.14.0, DepDigest 0.13.0, SMonitor 0.18.0, PyYAML 6.0.3 and libyaml 0.2.5.
They add 531,471 compressed bytes and 2,640,785 native-recorded regular-file bytes.
Shared control file-length differences are zero in this observation.

The installation/vision pages' claim that ArgDigest necessarily brings NumPy is
refuted for this published core route. Its actual Python metadata makes NumPy an
extra; its Conda dependencies omit it. Native installed records and all cold
sample module inventories have no NumPy. Compiled PyYAML/libyaml remain required.
Older/lower-bound provider closures and scientific extras are not inferred from
this result. Historical adoption reports retain their original observations.

The original public archive is still `ackredit-0.11.0-py_0.tar.bz2`, SHA-256
`df8963ca2d286f50b19eb778e95c54c5ebb79c12fb55a6504e7c23daf5717d4f`, producer
`85deae594e65b2fd443d6ca9a7347eb2bda537e1`. The installed smoke passes with
all provider origins inside this new environment, canonical self-citation,
independent reused captures, exact portable saved-reader equality and BibTeX
rendering. Public runtime code is distinct from the startup-optimized development
wheel under #116. No dependency requirement, publisher or runtime code changes.

`devtools/receipts/public_installation_118_2026-10-06.json` retains both native
package inventories, original archive hashes and file-length totals, native
create observations, public-registry verification and 20 raw process samples.
Two cases each have seven timing and three independent allocation samples.
Current bounded timing/allocation numbers live in the performance page; their
variation does not establish a developer-wheel optimization effect.

## Reusable operations and guards

Native Conda owns solving/installing and native installed-file records. The
existing shared `verify_public_conda` owns current registry/main-label/index
verification (MolSysSuite source `25363f2a2c902c04b2cdc8b301a3e1c1ff0c0918`).
`devtools/benchmark_public_installation.py` owns the Ackredit-specific comparison
and calls existing `installed_smoke.verify` and `benchmark_lifecycle.study`.
It exposes a bounded Linux x86-64/Python 3.14 measurement, requiring an independent
control, retained original archives and matching public/delivery identities.
Its regular-file metric excludes symlink targets, directories, Conda metadata and
unrecorded imports. It is logical length, not disk allocation or RSS. It does not
implement another installer or replace the original public qualification gates.

The selected pytest module protects the actual failure mechanisms: substituted
same-length archives, staging/foreign channels, missing linked files, escaping
paths, symlink double counting, contradictory public identity/control versions,
source-loaded worker providers and unsupported platform reporting. Receipt guards
bind the documented NumPy correction, byte totals, unchanged control and raw
sample separation to the measured public evidence. These administrative/provenance
guards do not establish scientific equivalence.

## Validation and remaining scope

All 54 selected provenance, installation, conceptual-doc, lifecycle, reporting
and integration-guide cases pass with pytest-receptor, including 16 new study
guards. Ruff, format, regenerated indexes, pinned dependency preflight, suite
conformance and strict Sphinx pass. The initial reporting check correctly detected indexes not yet
regenerated; generation resolves it. Exact-head unskipped CI and policy run IDs
are recorded in the owning issue before closure.

Separate caches start empty, but the two create commands overlap and have only
one wall-time observation each. No installer latency comparison is supported.
After smoke verification the fresh lifecycle processes use warm OS/filesystem
caches. The current solver closure and Python patch version are observational;
future builds can differ. Wider platforms, lower-bound providers, third-party
plugin workloads, independent graph shapes, scientific pairing and the complete
roadmap-L target remain open. No new release is authorized or produced.
