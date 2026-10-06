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

The product/architecture review accepted on 2026-10-05 is recorded under
[Ackredit #100](https://github.com/uibcdf/ackredit/issues/100). It extends this
roadmap rather than replacing completed work. Checked items retain their dated
source/public evidence; unchecked items distinguish implementation from a
decision. Recording this plan does not implement a capability or promote an API.

Ackredit owns bibliographic attribution and its tools. Scientific clients own
their methods and result schemas; MolSysSuite owns shared member contracts,
and MOLI owns platform boundaries. Open a focused owning issue before starting
each new implementation or decision, reusing existing issues where the scope
already fits. #100 owns this planning update, not every future implementation.

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
Theme F defines that exit. The completed foundation and remaining contract
review make that commitment honest rather than optimistic. The product
continuation in themes I–N can span multiple releases, including work after
1.0; it does not make every proposed feature, client adoption or optional
integration a prerequisite for 1.0. Resolve the scope of public promises before
making the stability commitment, and keep deliberately deferred work visible.

### Theme A — Ackredit can be installed — **done**

Ackredit 0.9.0 is published and independently verified on the public `uibcdf`
Conda channel. Publication is complete under `uibcdf/ackredit#22`; the earlier
deferral ended with the reviewed exact-artifact release decision.

The recipe lives in `docs/content/about/installation.md` and only there, held by
`tests/test_installation_page.py` to verified public delivery receipts and the
declared dependencies. Candidate CFF metadata is not publication evidence. A
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
- [x] a released scientific application uses the public provider: Sabueso
      0.12.0 completed its staged release under #110, and clean public receiving
      evidence with Ackredit 0.10.1 retains 56 tests and its offline example;
      [the provider delivery receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/conda-build/receipts/ackredit_0.10.1_public_2026-10-05.json)
      records that separate receiving checkpoint;
- [x] PyUnitWizard's experimental function-provider pilot #94 is resolved;
      its completed #111 optimization is qualified together with Ackredit in #99;
- [ ] MolSysMT's portable-adapter adoption remains client-owned under
      [#292](https://github.com/uibcdf/molsysmt/issues/292).

Tested integration, synchronized guides and released consumer adoption remain
separate evidence. MolSysMT and other clients own their scientific schemas and
release decisions; their runtime work is requested through their issues.

The original real-adoption milestone is demonstrated. Further host integrations
remain valuable and separately owned; the final stability review learns from
the receiving evidence already available rather than waiting for every host.

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
- [ ] **the decisions reviewed once more against what adoption taught**, using
      theme C's demonstrated receiving workflows and released application.

A provisional name reaches 1.0.0 either promoted or removed. Shipping one inside a
stability commitment would make the commitment meaningless. The principal
maintainer accepted stable source contracts for `observe_calls`,
`prepare_credit` and `ackredit.provider@1` on 2026-10-06 under #84/#87.
Their bounded promise is delivered in public 0.11.0; consumer adoption remains separate.
The newer evidence surfaces received their separate bounded source acceptance
on 2026-10-06 under #114; their future public delivery remains pending. The
[evidence-contract review](recorder_evidence_contract_review.md) under #114
records explicit acceptance of representation, collection and requested
presentation, supported by original receiving data and supplementary lifecycle
guards. General 1.0 remains a separate decision. Names were removed rather than promised:
`Registry` and `Collector` in `uibcdf/ackredit#55`, `serve_ui` in `#57`.

What remains is the unchecked review above: adoption can reopen a decision
taken without it, and the real receiving evidence is now available. Review session ownership,
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
- [x] real provider and receiving evidence informs the explicit principal-maintainer
      decision: accepted stable source contracts on 2026-10-06 under #84/#87;
      coordinated with MolSysSuite #97/MOLI #46, without requiring client adoption;
- [x] qualify and publish 0.11.0 delivering the accepted stable-provider promise,
      retaining the original exact file and separate public verification under #107;
- [x] implement a documented standalone declaration validator in development
      under #111, with a chosen provisional
      public/API stability boundary, that checks offline metadata without
      recording uses, installing wrappers, registering bibliography or querying
      a DOI; callers and tooling must reuse the provider-owned validation;
      source integration and public delivery remain separate from local evidence;
- [x] offer a [concise third-party author guide](../docs/content/user_guide/provider_authors.md)
      and an independently installable dependency-free producer example under
      #113; the existing installed guard now tests the published example;
      a producer's declaration requires no Ackredit import, decorator or runtime
      dependency;
- [x] explicitly retain the reviewed observation exclusions for pre-activation
      aliases, methods/descriptors, generators and native internal calls. Any
      expansion needs a concrete use case, lifecycle contract and bounded cost.

This work first shipped provisionally in corrected public 0.10.1 under #93/#94.
Its exact Conda file passes eight installed cells and eight real PyUnitWizard
cells (48 mandatory tests), followed by verified public promotion and clean
public receiving checks. See the
[delivery receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/conda-build/receipts/ackredit_0.10.1_public_2026-10-05.json).
The 2026-10-06 decision supersedes provisionality within the bounded accepted
contract; public 0.11.0 delivers that promise under #107, with eight installed
cells, 72 real receiving tests and clean public verification. The original release does
not rebuild 0.9.0, require consumer adoption or certify a consumer release.

Later development checkpoint #99 combines Ackredit's writer optimization #97
with resolved PyUnitWizard #111. Source `cf21cc1` and pinned producer `0e422d0`
pass eight installed cells and 56 receiving tests in [run
37309592507](https://github.com/uibcdf/ackredit/actions/runs/37309592507),
with independently verified artifacts and aggregation. Warmed declarations
are reused while version changes and metadata conflicts preserve original
results and diagnostics. This evidence does not change provisionality or
claim a new public artifact or cumulative speedup.

The declaration protocol, observer and prepared callable are decided
independently. Accepting the current bounded scope can be sufficient for a
stable surface; broad observation or another scientific engine is not an added
promotion gate. Standalone `validate_provider` is implemented provisionally in
development under #111; public 0.11.0 exposes activation-time validation only.

### Theme H — Faithful, compact workflow reports

- [x] explicit `workflow` format, shipped since 0.10.0, joins original bibliography,
      numbered references, contextual roles/versions and the saved graph
      without producer imports or invented invocation/success claims (#89);
- [x] detached nested plugin inputs preserve registered bibliography even
      after renderer mutations or failures (#90);
- [x] shared graph targets expand once with all incoming links retained;
      deep graphs avoid recursive traversal, backed by raw report-only
      before/after samples and unchanged ordinary tree output (#91);
- [x] the contextual report passes the same exact installed real-producer
      bundle across all eight supported receiving cells: source `cb3e58d`,
      [run 37228402277](https://github.com/uibcdf/ackredit/actions/runs/37228402277),
      48 passed tests without skips/deselections, independent downloaded
      evidence verification and the reviewed durable reporting receipt.

These changes affect requested reports, not the calculation's tracking path.
Corrected public 0.10.1 retains them and their exact Conda qualification.
They do not promote #84/#87 or change the portable schema or public 0.9.0.

### Theme I — Portable results from execution to later reporting

Python already reconstructs complete saved `Attribution` records offline.
The original CLI reads identifier journals, and `aggregate` merges those
journals. Development under #101 adds an explicit saved-attribution report/export
mode, preserving both existing session contracts while completing the external
user's lifecycle. Source qualification remains separate from public delivery.

- [x] define and implement CLI reporting/export from a saved
      `ackredit.attribution@1` payload, retaining the distinction from a session
      journal and returning failure for malformed/unknown inputs;
- [x] read and export in a fresh process without the original producer, registry,
      scientific engines, network lookup or new execution credit;
- [x] decide the public contract for composing multiple saved attributions:
      result names/context, duplicate uses, software versions, shared graph
      targets, conflicting identities and the relationship to original inputs;
- [x] implement the accepted composition operation as a reusable Ackredit tool,
      preserving detached originals, every retained graph edge and distinct
      software releases, and diagnosing conflicts before returning a result;
- [x] qualify a real multi-result notebook/batch workflow and fresh reader,
      including reordered/reused inputs, an empty result and metadata conflicts:
      source `95ada1a`, all eight installed cells and 64 tests in
      [run 37362423664](https://github.com/uibcdf/ackredit/actions/runs/37362423664).

Development under #102 uses a separate `AttributionBundle` envelope of complete
original schema-1 results. `compose_attributions` shares equal reference records
by ID and rejects metadata conflicts before returning; original graphs remain
independent. Workflow reports number shared bibliography once and retain each
original result's contexts/uses/graph. The explicit CLI `bundle` mode reuses its
reader. The new names have deliberately recorded pre-1.0 stable intent; old
provisional surfaces and the released individual-record promise are unchanged.
The eight-test installed receiving gate separately qualifies this new boundary;
all ten native archives verify and independent aggregation equals the hosted
result. The [archived record](https://github.com/uibcdf/ackredit/blob/main/devguide/archive/saved_attribution_composition.md) and
[receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/saved_attribution_composition_102_2026-10-05.json)
retain the completed development checkpoint separately from public delivery.

CLI/export comes first, then composition. Do not reconstruct absent bibliography
from the reader's current installation or interpret composition as chronology,
call counts, completed science or shared live sessions. A released schema-1
meaning stays readable; changed structural meanings require a new schema.

### Theme J — Explain coverage, reference origin and attribution gaps

Theme H explains recorded references, roles and targets. Its report correctly
does not assert complete instrumentation. Add actionable explanations when the
producer or observation boundary actually supplies evidence for them.

The first independent milestone #103 adds an inert `explain_attribution` tool
and `explanation` format in development. Each saved original retains distinct
evidence counts, roles/targets and explicit field absence; scope, origins and
diagnosed gaps remain `not_recorded`. This descriptive view changes no portable
schema or default workflow report. Source checks pass 1,956 tests without skips;
a normal Linux/Python 3.14 installation explains the eight retained real input
cells offline and reconstructs sixteen prior workflow reports identically.
Later head `6f8f361` passes all seven CI jobs and both policy controls; the
expanded eight-cell receiving gate also retains the saved-reader contract.
The stronger representation/collection milestones below keep their own scope. The
[saved-reader receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/recorded_attribution_explanation_103_2026-10-05.json)
retains actual source, wheel and scope.

- [ ] define which scope information can be recorded: selected observation
      boundaries, explicit credits, declared-provider/discovery metadata origins,
      incomplete bibliography and diagnosed recording gaps;
- [x] decide bounded representation, ownership and compatibility under #114;
      distinguish the origin of bibliographic metadata from evidence of use and
      from any claim about bibliographic or scientific truth; broader recorder
      ownership requires separate concrete use cases;
- [x] preserve recorded gap/scope information in saved results and explain it
      in the requested workflow report, with no producer imports or new credit;
- [ ] guard partial failure, unsupported/unobserved operations, metadata fallback
      and complete absence of scope information. An empty capture means no
      references were recorded, not proof that nothing citable was used.

Coverage is bounded by instrumentation. Never invent an unobserved call, missing
citation, success state or global coverage percentage. The client decides
scientific completion; catalog diagnostics retain their own failure details.

The next independent milestone [#104](https://github.com/uibcdf/ackredit/issues/104)
implements a provisional `AttributionEvidence` companion around complete original
single/bundle results. Explicit recorder declarations are positional per original
and distinguish null/unknown from empty lists. They retain metadata field sources,
selected/unsupported/unobserved boundaries and owning gap diagnostics separately
from recorded use. Existing original readers and default reports stay unchanged.
Local representation qualification passes 2,018 Python 3.14 source tests and a
normal installed offline reader over the eight retained real input cells with
controlled companion declarations; sixteen prior workflow reports stay identical.
The [saved-reader receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/explicit_attribution_evidence_104_2026-10-05.json)
retains exact bytes and limits. Later head `6f8f361` passes all seven CI jobs
and both policies, clearing earlier runner-acquisition cancellations through
new executed controls. The original source/wheel identities remain unchanged;
real collector qualification belongs to the separate milestone below.

The next collector milestone [#105](https://github.com/uibcdf/ackredit/issues/105)
adds provisional `capture(record_evidence=True)` / `.evidence` support. It collects
actual overlapping observer selections, field sources for successfully credited
provider items and owning recording diagnostics. Default captures and original
portable records remain unchanged. Local Python 3.14 qualification passes 2,047
source tests and nine normal-installed real receiving cases with inert saved
readers. The [collector receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/provider_evidence_collection_105_2026-10-05.json)
retains exact local bytes and bounded costs. Expanded hosted receiving run
[37419599184](https://github.com/uibcdf/ackredit/actions/runs/37419599184)
passes all eight Linux/macOS arm64 × Python 3.11–3.14 cells and 72 tests with
no skips. All ten original artifact digests verify and independent aggregation
equals the hosted result. The
[hosted receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/provider_evidence_hosted_105_2026-10-05.json)
retains the original development wheel separately from the local build.
At this historical checkpoint, broader requested presentation was still pending;
#106 subsequently implements it. Other recorder origins and final
provisional-contract review remain pending.

Completed bounded J checkpoints are:

- [x] inert descriptive explanation without inventing unknown scope/origins/gaps (#103);
- [x] explicit, validated companion declarations around complete saved originals (#104);
- [x] opt-in collection of actual provider-observer origins, selected boundaries
      and catalog diagnostic identities, with bounded deduplication (#105);
- [x] real normally installed collector/science and fresh-reader qualification
      across Linux/macOS arm64 × Python 3.11–3.14 (#105).

These do not complete the wider unchecked J criteria above. Explicit-credit,
prepared-backend and discovery/enrichment recorder origins still need ownership
decisions and focused implementation issues. Requested workflow presentation
must combine the evidence with the narrative without changing report defaults.

That requested presentation is qualified below. Broader recorder origin/scope
decisions remain part of the unchecked criteria above.

The focused presentation milestone [#106](https://github.com/uibcdf/ackredit/issues/106)
implements provisional `evidence.report("workflow", include_evidence=True)` and
the explicit saved-evidence CLI option. It extends the owning renderer, keeping
shared reference numbering and attaching recorder declarations to their original
result occurrence. Unknown planes, empty declarations and actual diagnostic
identities retain their bounds. Defaults and schemas stay unchanged. Source
qualification passes 2,073 Python 3.14 tests; all eight normally installed cells
pass 72 tests without skips in
[run 37421954520](https://github.com/uibcdf/ackredit/actions/runs/37421954520).
Original ZIP digests/extracted bytes verify independently and aggregation equals
the hosted result. Head `30c622b` passes all seven CI jobs and both policies;
the [hosted receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/workflow_recorder_evidence_hosted_106_2026-10-06.json)
keeps the original hosted producer/wheel separate from the local build. This
bounded presentation checkpoint is resolved and delivered in public 0.11.0 under
#107; other recorders and final provisional review remain separate.

The separate [J/F contract review](recorder_evidence_contract_review.md) under
#114 maps the existing representation, collection and presentation to concrete
guarantees/exclusions and 149 selected source tests, including original hosted
saved-reader and opted-in lifecycle guards. The maintainer explicitly accepted
the bounded three-surface source promise on 2026-10-06. Forward public delivery
awaits a separately qualified future release; public 0.11.0 retains its original
provisional evidence classification. Wider unchecked J criteria remain visible.

### Theme K — Attribution at MOLI object boundaries

Coordinate platform decisions in [MOLI #46](https://github.com/uibcdf/moli/issues/46)
and suite/member decisions in [MolSysSuite #97](https://github.com/uibcdf/molsyssuite/issues/97),
opening focused owner issues when an additional boundary needs its own review.
Ackredit supplies portable bibliography and recorded uses; the owning components
define Sabueso knowledge, Praxis protocols and Nextia runs/artifacts/results/evidence.

- [ ] agree how owning result schemas attach or reference attribution, keep
      original software/source versions and retain usable saved bibliography
      when the producer or authoritative object is unavailable;
- [ ] agree how attribution is composed across component/result boundaries and
      how its relation to historical source/object references is represented;
- [ ] distinguish a citation, a source observation, execution provenance and
      scientific evidence. Recording a reference alone establishes none of the
      other objects' validity or scientific support;
- [ ] define absent/failing-provider behavior per client profile, keeping
      optional scientific hosts operational and explicit required dependencies
      under the application's ownership;
- [ ] retain actual client-owned round-trip/receiving cases for accepted
      boundaries, alongside decisions, published-provider identity and limits.

This is a contract/adoption discussion, not authorization to edit other
components or a demand for every platform component to adopt Ackredit before
1.0. Share accepted integration guidance through its central registry; guide
delivery, runtime adoption and a client's release remain separate.

### Theme L — Measure the complete cost of being lightweight

Theme D and #85/#97/#99 retain their scoped runtime and receiving evidence.
Repeated-credit timings do not measure cold import, dependency installation,
activation or memory. Extend the measurement contract before optimizing again.

- [ ] measure cold import/first use, inactive operation, provider activation,
      tracking/capture, journal writes, snapshot/export and requested large
      reports separately, with actual source/dependency identities and raw samples;
- [ ] measure memory and scaling with references, graph nodes/edges, independent
      results, active captures and plugin/declaration size;
- [ ] pair real scientific controls and instrumented workloads, retaining
      numerical parity and ordinary variation. Do not add percentages from
      independent historical measurements;
- [ ] review plugin initialization and the external user's dependency closure,
      including NumPy through ArgDigest. Keep the accepted four core dependencies
      unless a separately recorded owner/shared decision changes that boundary;
- [ ] identify measured bottlenecks and improve the owning reusable operations
      while preserving validation, conflict preflight, diagnostics and every
      independent capture's references;
- [ ] record whether the verified Conda route meets the external-user target.
      Any additional distribution route needs its providers' real published
      dependency closure and shared review, not duplicated infrastructure.

Publish bounded numbers and limits, not an unconditional zero-cost claim.
Select performance checks by the changed boundary; this plan does not impose
fresh scientific benchmarks on every documentation or unchanged-code checkpoint.

### Theme M — Bibliography that survives real publication tools

BibTeX, CSL-JSON and the format extension point exist. Development after public
0.10.1 improves typed CFF work selection (#95), publication kinds/dates/pages
(#96) and declared person/entity name identity (#98). Those repairs remain
delivered in public 0.11.0 under #107. Actual publication-tool interoperability
remains the separate work below.

- [ ] exercise exported records with representative real reference-manager
      imports and BibTeX/BibLaTeX or journal-style workflows, recording tested
      versions, selected styles and intentional unsupported cases;
- [ ] cover software, datasets, articles, institutional authors, preferred works,
      structured editors/names, original versions and non-ASCII metadata;
- [ ] decide duplicate bibliographic identity handling across caller-defined
      IDs/DOI forms without silently merging different software releases or
      replacing conflicting original records;
- [ ] define supported presentation expectations and style/plugin boundaries,
      including software/dataset entries that a selected BibTeX style cannot
      render. Reuse a suitable external style engine if one is required;
- [ ] guard accepted interoperability with retained fixtures/round trips and
      separate metadata preservation from a tool's chosen formatted output.

Export fidelity and citation-style rendering are distinct operations. Ackredit
must not guess authorship or rewrite original bibliographic claims to make a
particular style appear correct.

### Theme N — Decide the scope of acknowledgements

The original vision names citations and acknowledgements. Existing bibliographic
records and use roles do not define a distinct product contract for thanking
people, institutions or funders.

- [ ] explicitly accept, defer or exclude non-bibliographic acknowledgements,
      with concrete user stories and maintained guidance matching the decision;
- [ ] if accepted, define their source, wording responsibility, identity,
      contextual use, distinction from bibliographic works and saved representation;
- [ ] specify and implement the accepted acknowledgement section/export through
      the owning data/rendering tools, preserving original claims and context;
- [ ] guard citation/acknowledgement separation, reuse, portability and relevant
      output formats with an actual receiving example.

This theme starts with a product decision. It does not already promise a funder
database, automatic acknowledgements, inferred contributions or a mandatory
feature before 1.0. A deliberate deferral remains visible in the roadmap.

## Execution order and release checkpoints

The [development checkpoint](checkpoint.md) records the current resumption order:
retain #108's completed distribution-input guard and #113's provider author
guide/installable example and #114's accepted bounded evidence contracts, then
continue the wider roadmap and separately authorized release qualification.
The 0.11.0 release is complete;
central handoffs and the
remaining product decisions below retain their own owners.

The accepted continuation order is:

1. Theme I: portable saved-result CLI and exports, then the reviewed composition
   operation. Each independently useful operation gets its own issue, contract
   and meaningful receiving guards before implementation.
2. Theme J: scope/origin/gap explanations, built on those preserved saved results.
3. In parallel, resolve F/G's explicit provider stability decisions and K's
   platform/member boundaries with their existing owners. The 2026-10-06
   decision accepts the three provider surfaces; #114 separately accepts the
   bounded evidence source contracts with future delivery pending. Public 0.11.0
   completes stable-provider delivery and retains provisional evidence contracts.
4. Run L's complete-cost measurements and M's publication-tool interoperability
   against selected actual candidates; optimize or repair measured boundaries.
5. Decide N's acknowledgement scope and implement only its accepted branch.

Prepare the next delivery from completed, reviewed work; it need not wait for
every theme. Post-0.10.1 fidelity/performance and saved-result/evidence work is
delivered in qualified public 0.11.0. Original development receipts remain
distinct from that published artifact's qualification.
Select its version when the release scope is concrete, preserve the original
producer and exact archive digest, and apply the existing source/installed/
receiving/staging/promotion/public-verification gates. Source completion,
API acceptance, canonical-guide synchronization and receiving-client release
are separate outcomes. A stable guide update follows its accepted contract
and central consumer synchronization, not a local repair of copied guides.

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
