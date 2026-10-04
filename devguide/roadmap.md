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

### 0.9.0 — Portable attribution and public Conda delivery

The public `uibcdf` channel carries the first stable `Attribution`, `capture`
and `get_attribution` contract with the portable `ackredit.attribution@1` schema.
One noarch archive was staged, qualified on Linux/macOS arm64 × Python 3.11–3.14
and promoted without rebuilding. Clean public Linux/Python 3.14 installation
and receiving Sabueso compatibility are recorded in
[the delivery record](https://github.com/uibcdf/ackredit/blob/main/devguide/archive/ackredit_cannot_be_installed.md). Conda delivery
does not itself create a GitHub tag or release. The matching `0.9.0` Git tag
now identifies the original producer under #82; GitHub Release/DOI publication
remains a separate outcome.

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

### Theme A — Ackredit can be installed — **done**

Ackredit 0.9.0 is published and independently verified on the public `uibcdf`
Conda channel. Publication is complete under `uibcdf/ackredit#22`; the earlier
deferral ended with the reviewed exact-artifact release decision.

The recipe lives in `docs/content/about/installation.md` and only there, held by
`tests/test_installation_page.py` to `CITATION.cff` and to the declared dependencies. A
copy here pinned `0.6.0` and missed ArgDigest long after the page was corrected
(`uibcdf/ackredit#66`), which is why this is a pointer and not a copy.

The exact 0.9.0 archive installs normally from the public channel with its runtime
dependencies, packaged `CITATION.cff` and portable contract. Theme C's receiving
components still own their integration and release decisions.

- [x] a conda recipe under `devtools/conda-build/`, `noarch: python`, and a build
      environment;
- [x] `build_and_upload_conda_packages.yaml`, staging first and promoting only what was
      verified;
- [x] a build verified locally: the `noarch` package passes the recipe's own tests and
      installs into a clean conda environment where it reports its version, discovers
      itself and renders a report;
- [x] **published to the channel**, retaining exact-file promotion and public receipts;
- [x] the installation documentation rewritten around the verified public package.

Coordination: `uibcdf/molsyssuite#27` standardises staging for components whose
publication order is coupled. Ackredit's dependencies are already public, so
there is no cycle here. Sabueso now requires Ackredit; its owner receives the
published version/file/hash evidence under `uibcdf/sabueso#108`.

### Theme B — Ackredit can be cited — **done**

Before #21, Ackredit shipped no discoverable `CITATION.cff` and its package
metadata named only the team. The installed package now includes the citation
file and discovers itself, with authorship held to package metadata by
`tests/test_self_citation.py`. That historical gap is closed.

- a `CITATION.cff` with real authors, and package metadata that agrees with it;
- a test asserting Ackredit discovers itself, which is the smallest honest end-to-end
  check this library can have;
- a decision on Zenodo archival, currently `optional` in `suite.toml`.

### Theme C — A host library has actually adopted it

Real receiving integration is now demonstrated. PyUnitWizard #92 exercises
Pint/unyt backend attribution through an opt-in context. Sabueso #108 requires
Ackredit for automatic knowledge-packet attribution. Its receiving tests pass
against the exact Ackredit 0.9.0 archive on all four Linux Python minors in
staging, and against a clean public installation on Python 3.14. The canonical
guide is guarded by executed examples in `tests/test_integration_guide.py`.

- [x] real provider/consumer operations, reused bibliography, enclosing credit,
      absence/failure and detached fresh-reader behavior;
- [x] the portable capture and guide corrected from those observations under #75;
- [ ] receiving scientific releases qualified against the public provider;
      Sabueso #108/#110 owns its candidate, and MolSysMT #292 owns its adoption.

Tested integration, synchronized guides and released consumer adoption remain
separate evidence. MolSysMT and other clients own their scientific schemas and
release decisions; their runtime work is requested through their issues.

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

### Theme E — Python 3.14 — component delivery complete

The suite-wide requirement authorizes Python 3.11–3.14 adoption and routine
development on 3.14. Ackredit #80 is resolved with the actual public 0.9.0
artifact, its eight-cell installed matrix and clean public Linux/Python 3.14
receiving evidence. Metadata is `>=3.11,<3.15`; ordinary installed tests do
not bypass Requires-Python or tolerate failures.

- [x] source compatibility, locally and in hosted CI;
- [x] required range, maintained environments, recipe and full CI aligned;
- [x] same-file Linux/macOS-arm64 × Python 3.11–3.14 installed qualification;
- [x] public artifact and normal public Python 3.14 dependency closure;
- [x] central admission recorded as `admitted` in immutable `policy-v1.5.6`;
      Ackredit adopted that caller and its verified four-minor badge in
      `8c743b3`. MolSysSuite #51 remains open for other members. Component
      delivery and central admission retain separate evidence.

### Theme F — The stability commitment itself

The last theme, and the one that earns the number.

- [x] **every public name marked stable or provisional**, with a reason for each
      provisional one, in `docs/content/about/stability.md`, which also carries the
      counts. `tests/test_api_stability.py` holds the page to `__all__`, so a name
      cannot join the public surface without a decision about what it promises, and a
      name cannot be called stable while no test exercises it;
- [x] **the previously untested public operations** — `compile_pdf`, `dependency_info`,
      `enable_auto_reminder`, `enrich_all`, `export_to_duecredit` and `load_plugins` —
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
stability commitment would make the commitment meaningless. The new `observe_calls`
surface, and `prepare_credit` under #87, remain provisional pending provider and receiving review under #84 and
MolSysSuite #97; it must be promoted or removed before 1.0. Existing names have
been decided once, on the evidence available now. Names were removed rather than promised:
`Registry` and `Collector` in `uibcdf/ackredit#55`, `serve_ui` in `#57`.

What remains is the unchecked review above, which waits on theme C by definition:
adoption is what can reopen a decision taken without it. Review session ownership,
capture/reused-reference semantics, software/article versions, failure boundaries,
saved-reader compatibility and extension contracts against actual receiving
workflows. Existing tests and a stable-intent classification do not substitute
for that final general 1.0 decision. The released portable promise remains
bounded as [API stability](../docs/content/about/stability.md) specifies.

### Theme G — Accurate, lightweight function providers

Ackredit #84 proposes offline, dependency-free third-party declarations and an
explicit observer of actually entered function exports. This differs from AST
inspection: untaken calls earn no references, while executed functions can earn
both software and description articles with original producer versions. #85
measures portable capture separately from the historical plain tracking path.

- [x] normally installed test provider works without Ackredit and produces faithful
      portable attribution when observation is explicitly enabled;
- [x] nested captures, failed calls, asynchronous contexts and export restoration
      are exercised, with unsupported aliases/generators documented;
- [x] before/after capture and observation timings are reproducible without
      mutable-identity caches, missing reused credit or hidden validation failures;
- [x] the real PyUnitWizard producer pilots declared lazy exports, original
      software/article roles and explicit prepared completed-dispatch credits
      (#87), with a released-provider fallback;
- [x] the same installed candidate/real-producer bundle passes all eight
      Linux/macOS arm64 × Python 3.11–3.14 receiving cells without skips;
      first qualified source `357083e`, run
      [37216812721](https://github.com/uibcdf/ackredit/actions/runs/37216812721);
      corrected source `fc00a6c` also passes ordinary CI and receiving run
      [37217520167](https://github.com/uibcdf/ackredit/actions/runs/37217520167);
      the manual gate and evidence requirements are documented in
      [`receiving_validation.md`](receiving_validation.md);
- [ ] real provider and receiving review resolves the provisional API, coordinated
      through MolSysSuite #97 before any shared adoption requirement.

This development does not rebuild public 0.9.0 or certify a consumer release.

---

## Not on this roadmap

Recorded so nobody re-proposes them as blockers:

- **Multi-process session sharing beyond a local filesystem.** Appends are atomic on a
  local filesystem and one journal per process merges everywhere; NFS locking is not
  something Ackredit will attempt.
- **SQLite as the session store.** Measured and refused in
  `devguide/archive/persistence_rewrites_everything_on_every_item.md`, with the conditions
  under which it would win.
- **Universal interpreter profiling.** `auto_track_calls` and `credit_bound` retain
  their coarse contracts. Theme G can observe selected declared exports without
  claiming every branch, alias or native internal call is visible.
