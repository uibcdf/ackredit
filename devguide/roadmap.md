# Roadmap

## How to read this

Each milestone is a **theme with exit criteria**, not a fixed version number. A minor
release happens when a theme's criteria are met, and the next theme takes the next number.

This is deliberate. Planning "0.12.0 is the last before 1.0.0" invites the plan to be wrong
as soon as a theme needs two releases instead of one, and then the plan is either broken or
quietly ignored. Themes can be split, reordered or added; arriving at 1.0.0 from 0.24.0
rather than 0.12.0 costs nothing and means the numbers stayed honest.

What a number does say: **the minor rises when behaviour a caller can see changes**, and a
tag is only cut when the gates are green and the documentation matches what the code does.

## Shipped

### 0.1.0 — Core consolidation
Robust BibTeX generation, the optional-dependency pattern, the `scope` context manager.

### 0.2.0 — Automation and metadata
Jupyter summary, `CITATION.cff` and package-metadata discovery, DOI enrichment, session
persistence, exit reminders.

### 0.3.0 — Ecosystem and connectivity
Entry-point plugins, metadata cache, DueCredit bridge, command-line reporter.

### 0.4.0 / 0.5.0 — Full feature set
LaTeX and PDF output, multi-session aggregation, DataCite support, AST inspection.

### Since 0.5.0 — correctness, and the suite baseline
Not a feature phase, and the largest body of work so far. Twenty reports opened, fixed,
guarded and archived: `bind` had no runtime effect; the wheel shipped two files; the
documentation taught imports that raise; the Sphinx build could not run; scopes were
cross-attributed between threads and the session file was corrupted; BibTeX output was not
escaped and authorship was invented; `auto_track_calls` credited code that never ran;
persistence was O(n²) and so was crediting a caller; an unknown format silently produced a
different one; the public namespace exported names nobody chose.

Also in this period: SMonitor and DepDigest adopted, the MolSysSuite baseline and
registration, conda environments and CI lanes, a session object, and versions derived from
the tag.

These are unreleased. The next tag carries them.

---

## Towards 1.0.0

1.0.0 means one thing: **the public API is stable and we commit to not breaking it**.
Everything below exists to make that commitment honest rather than optimistic.

### Theme A — Ackredit can be installed

**Publication is deliberately deferred to the release before 1.0.0.** Until then the tag
is the release artifact: an exact version installs from it, into an environment that has
the dependencies.

```bash
conda create -n work -c uibcdf -c conda-forge python=3.13 smonitor depdigest pyyaml pip
conda activate work
pip install --no-deps "git+https://github.com/uibcdf/ackredit@0.6.0"
```

Verified: that yields `0.6.0` in `site-packages`, discovering its own `CITATION.cff`.

This revises what this theme claimed. It does not block every other one; what it blocks is
narrower and worth stating exactly. A host library can integrate Ackredit from a tag and
produce the evidence theme C is for — but it cannot *release* an integration that depends
on a package nobody can resolve. So theme C can run to the point of evidence and stops
short of a shipped integration, which is the right trade while the API is still moving.

- [x] a conda recipe under `devtools/conda-build/`, `noarch: python`, and a build
      environment;
- [x] `build_and_upload_conda_packages.yaml`, staging first and promoting only what was
      verified;
- [x] a build verified locally: the `noarch` package passes the recipe's own tests and
      installs into a clean conda environment where it reports its version, discovers
      itself and renders a report;
- [ ] **published to the channel**, deferred by decision to the release before 1.0.0;
- [ ] the installation documentation rewritten around the published package, which must
      not be written before it exists.

Coordination: `uibcdf/molsyssuite#27` standardises staging for components whose
publication order is coupled. Nothing depends on Ackredit, so there is no cycle here; the
staging step is adopted for verification rather than coordination.

### Theme B — Ackredit can be cited — **done**

A citation tracker that ships no `CITATION.cff` cannot be discovered by its own
auto-discovery. Verified: `find_and_parse_cff` finds nothing for Ackredit, and the package
metadata declares no author beyond "UIBCDF Development Team" and no contact.

- a `CITATION.cff` with real authors, and package metadata that agrees with it;
- a test asserting Ackredit discovers itself, which is the smallest honest end-to-end
  check this library can have;
- a decision on Zenodo archival, currently `optional` in `suite.toml`.

### Theme C — A host library has actually adopted it

The integration guide is guarded by tests that execute its template
(`tests/test_integration_guide.py`), but **no host library has adopted it yet**. Every
defect found in the guide so far was found by reading it, not by using it, and the
difference between those two is where the remaining unknowns live.

- `molsysmt` or `topomt` integrating Ackredit for real;
- what that surfaces, fixed here;
- the guide corrected from the experience rather than from inspection.

This is the theme most likely to need more than one minor, and the most valuable.

### Theme D — Performance under a real workload

Every performance claim so far comes from a synthetic benchmark. They were enough to find
two O(n²) defects, and they are not enough to say the library is light in a real run.

- a scientific workflow instrumented end to end, measured with and without Ackredit;
- the overhead published in the documentation as a number, not an adjective;
- whatever that surfaces, fixed.

### Theme E — Python 3.14

Governed centrally by `uibcdf/molsyssuite#29`. Ackredit sits behind DepDigest in the
dependency order and both its dependencies are capped at `<3.14`, so this waits on them.
The local work is small: `pyproject.toml`, two workflows, three environment files.

### Theme F — The stability commitment itself

The last theme, and the one that earns the number.

- every public name marked stable or provisional, and the provisional ones justified;
- a deprecation policy: what a removal requires and how long it is announced;
- the decisions already recorded in `devguide/decisions.md` reviewed once more against
  what adoption taught.

---

## Not on this roadmap

Recorded so nobody re-proposes them as blockers:

- **Multi-process session sharing beyond a local filesystem.** Appends are atomic on a
  local filesystem and one journal per process merges everywhere; NFS locking is not
  something Ackredit will attempt.
- **SQLite as the session store.** Measured and refused in
  `devguide/archive/persistence_rewrites_everything_on_every_item.md`, with the conditions
  under which it would win.
- **Per-branch citation precision.** `auto_track_calls` and `credit_bound` are documented
  as coarse; exact attribution would need an interpreter hook on every call.
