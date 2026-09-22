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

### 0.7.0 — What the reports say, and what the API promises
Every module in the package was probed, and thirty-four reports were opened, fixed, guarded
and archived.

**The reports were wrong in ways that reach a manuscript.** Markdown, the default format,
escaped nothing, so a `[` in a title broke the link and a `<script>` reached a renderer that
passes HTML through. The BibTeX parser cut every field at its first inner brace, so a `.bib`
file loaded from a reference manager was written back with braces that do not balance and a
document that will not compile — and what did compile had lost the publisher of a book and
the editor of a conference paper. CSL-JSON marked every author as indecomposable, so no
reference manager could sort or abbreviate them, and raised on a year Ackredit itself
produces. The notebook summary showed an object address anywhere but a notebook.

**The data was wrong too.** Half the shipped citations named `"et al."` as a person, and one
named a paper that does not exist; the guide every host library copies taught the same.
Enrichment stored Crossref's HTML entities as characters, invented an author called "None",
and could end a run on a metadata quirk.

**The command line did not work.** `ackredit aggregate` had raised `AttributeError` since
the persistence rewrite, and `ackredit report` on a missing file created it and reported
emptiness. Nothing in the suite had ever run the program.

**Theme F.** Every public name is classified, the deprecation policy is written, and the
list of provisional names is empty: thirty-three names, all stable, four decided by removal
rather than promotion — `Registry`, `Collector` and `serve_ui`. Output formats became
extensible, which the vision had promised and nothing implemented.

**Behaviour a caller can see changed**, which is what the minor is for, and three public
names were removed, which is why it is not a patch.

### 0.8.0 — What a host library needs before it adopts
Driven by running Ackredit the way a host and its users would, which found what reading
it had not.

**Auto-discovery broke the program.** In 0.7.0, `enable_import_hooks()` made the next
import of anything in a fresh process raise `ImportError` (`#60`), found by instrumenting a
real MolSysMT workflow for theme D. The hooks were also blind to anything imported before
them, and ArgDigest loads numpy with Ackredit, so the documented numpy examples credited
nothing (`#69`); a declared injection is now credited whatever the import order, and the
pages say what discovery can see. The standard library stopped warning module by module
(`#70`).

**The report could go missing on its way to disk** (`#65`), and **authors ran together**
in the lists a person reads (`#67`), both found by an example workflow run as a user runs
it, which now stays as a script, a notebook and a test (`#68`).

**Arguments are checked at the public boundary** through ArgDigest (`#61`, `#62`), CI
runs every Python version promised (`#63`), and the installation page is held to the
release and the dependencies (`#66`).

The minor rises because a caller can see it: a new runtime dependency that brings numpy,
higher floors, arguments refused that were accepted, and `dump("refs.bib")` writing
BibTeX where it wrote Markdown.

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

Those were released as 0.6.0.

---

## Towards 1.0.0

1.0.0 means one thing: **the public API is stable and we commit to not breaking it**.
Everything below exists to make that commitment honest rather than optimistic.

### Theme A — Ackredit can be installed

**Publication is deliberately deferred to the release before 1.0.0.** Until then the tag
is the release artifact: an exact version installs from it, into an environment that has
the dependencies.

The recipe lives in `docs/content/about/installation.md` and only there, held by
`tests/test_installation_page.py` to `CITATION.cff` and to the declared dependencies. A
copy here pinned `0.6.0` and missed ArgDigest long after the page was corrected
(`uibcdf/ackredit#66`), which is why this is a pointer and not a copy.

Verified for `0.6.0`: the recipe yields the tagged version in `site-packages`, discovering
its own `CITATION.cff`.

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

### Theme D — Performance under a real workload — **done**

Every performance claim before this came from a synthetic benchmark. They were enough to
find two O(n²) defects, and not enough to say the library is light in a real run.

- [x] **a scientific workflow instrumented end to end**: MolSysMT reading a protein from
      the PDB, converting, querying, selecting and converting again, measured with and
      without Ackredit in `devtools/benchmark.py`;
- [x] **the overhead published as a number**, in `docs/content/about/performance.md`,
      which is where the numbers live: microseconds for `track_item` and for a `scope`
      around one, and tens of milliseconds once for auto-discovery at import. On the
      workflow itself there is no number to give, and that is the finding — the
      run-to-run spread is 259 ms and every difference Ackredit makes is smaller, coming
      out negative as often as positive;
- [x] **what it surfaced, fixed**: `enable_import_hooks` raised `ImportError` on the first
      import in any fresh process (`uibcdf/ackredit#60`). Auto-discovery, the feature the
      guide tells a host to enable, did not work at all. No synthetic benchmark could have
      found it, which is the argument for this theme in one line.

Two measurements were wrong before they were right, and the method that fixed them is in
the script: the minimum of several runs, each in its own interpreter, both sides importing
Ackredit, and a baseline that reports its own spread so a difference beneath it is labelled
rather than published.

### Theme E — Python 3.14

Governed centrally by `uibcdf/molsyssuite#29`, where the decision now rests. The
dependencies are ready: SMonitor, DepDigest and ArgDigest all declare `<3.15` and are
admitted there. CI runs a non-blocking 3.14 lane from the public channel builds and it
passes with the same results as 3.11 to 3.13 (`uibcdf/ackredit#63`, `#64`); the evidence
is posted on that issue.

- [x] source compatibility, locally and in hosted CI;
- [ ] authorization in `suite.toml`, which is not Ackredit's to give;
- [ ] then `requires-python`, the promised matrix and the environment files, which the
      workflow tests move together.

### Theme F — The stability commitment itself

The last theme, and the one that earns the number.

- [x] **every public name marked stable or provisional**, with a reason for each
      provisional one, in `docs/content/about/stability.md`, which also carries the
      counts. `tests/test_api_stability.py` holds the page to `__all__`, so a name
      cannot join the public surface without a decision about what it promises, and a
      name cannot be called stable while no test exercises it;
- [x] **the seven public names nothing tested** — `compile_pdf`, `dependency_info`,
      `enable_auto_reminder`, `enrich_all`, `export_to_duecredit`, `load_plugins` and
      exercised in `tests/test_optional_surface.py`, so "provisional" is a judgement
      rather than a gap. `serve_ui` was among them and was removed instead
      (`uibcdf/ackredit#57`);
- [x] **a deprecation policy**: a stable name is removed only in a major release, after
      at least two minor releases carrying a deprecation code that names the replacement;
      changing what a name does follows the same route as removing it;
- [x] **the three entries standing under "Pending Decisions"** since the beginning, which
      the implementation had settled long ago, recorded as decisions 12 to 14;
- [x] **the extension point for output formats**, the one decision theme F opened rather
      than closed, built in `uibcdf/ackredit#36`: `register_format` and an
      `ackredit.formats` entry-point group, with a registered name never replaced. That
      settles `_RENDERERS` as implementation;
- [ ] **the decisions reviewed once more against what adoption taught**, which waits on
      theme C by definition.

A provisional name reaches 1.0.0 either promoted or removed. Shipping one inside a
stability commitment would make the commitment meaningless, so that list was the real
measure of how far this theme had to go — and it is empty. Every public name has been
decided once, on the evidence available now, and four were removed rather than promised:
`Registry` and `Collector` in `uibcdf/ackredit#55`, `serve_ui` in `#57`.

What remains is the item below, which waits on theme C by definition: adoption is what can
reopen a decision taken without it.

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
