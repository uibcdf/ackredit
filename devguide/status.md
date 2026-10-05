# Current Project Status

Ackredit is pre-1.0. This document records what is verified to work, what is known to be
broken, and what is planned. Claims here must be checkable; if a feature is listed as
working, a test or a reproducible command backs it.

## Verified working

- **Hierarchical core:** Registry, Collector and the `scope` context manager, with nested
  scopes and a provenance tree.
- **Static registration and dynamic tracking:** `register_item`, `bind`, `bound_items`,
  `track_item`, `credit_bound`, and the opt-in `credit_bound=` option on `scoped_usage`
  and `scope`.
- **Scientific formats:** Markdown, plain text, BibTeX, CSL-JSON, JSON, provenance tree
  and LaTeX, plus contextual workflow Markdown, `dump()` to a directory and PDF
  compilation when `pdflatex` is present.
- **Automated discovery:** import hooks, `CITATION.cff` parsing and PEP 621 metadata.
  Development after 0.10.1 preserves typed preferred CFF work identity and
  publication fields, without borrowing root software metadata or crediting
  unrelated listed references (#95). Root dataset types are retained. This repair
  is not present in the public 0.10.1 archive.
  CSL-JSON now also interprets unambiguous original CFF kinds, full calendar
  dates and page counts (#96), preserving unknown kinds and literal/conflicting
  date metadata in the portable records. This is development after 0.10.1.
- **Metadata enrichment:** DOI lookup against Crossref and DataCite, with a local cache.
- **Ecosystem integration:** entry-point plugin loading, a DueCredit bridge, session
  persistence and a multi-session aggregator.
- **Developer tools:** command-line interface and a Jupyter HTML summary.
- **Distribution:** an installed wheel imports and works outside the source tree, guarded
  by `tests/test_packaging.py`. Public Ackredit 0.10.1 is available from the `uibcdf`
  Conda channel as one verified noarch file. The same archive passed Linux/macOS
  arm64 × Python 3.11–3.14 installed qualification and a clean public Linux/Python
  3.14 receiving installation. See [installation](../docs/content/about/installation.md)
  and the [public delivery receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/conda-build/receipts/ackredit_0.10.1_public_2026-10-05.json).
- **Portable attribution:** `capture` observes per-calculation references without
  replacing the application session; `get_attribution` snapshots the workflow.
  `Attribution` preserves detached bibliography, contextual roles, original versions
  and the usage tree through the released `ackredit.attribution@1` schema. Reading
  and rendering saved results add no execution credit. Guarded by
  `tests/test_attribution_capture.py`, `tests/test_attribution_contract.py` and the
  executed examples in `tests/test_integration_guide.py`.
- **Documentation:** the Sphinx site builds with no warnings, twice in a row, and every
  documented Python snippet is checked against the real API by
  `tests/test_documented_api.py`. The documented report formats, the citation page and the
  stability classification are each held to the code they describe.
- **Sessions:** tracking belongs to a session reached through a `ContextVar`, so two
  analyses in one process are separable and threads are isolated. The module functions
  act on a default session, so nothing needs ceremony. Guarded by
  `tests/test_session_isolation.py`.
- **Persistence:** the session is a journal, one appended line per event, so the cost of
  tracking an item does not depend on how many were tracked before: 6.6 µs, flat, where
  the previous design reached 2 958 µs and kept rising. Guarded by
  `tests/test_persistence_cost.py`.
- **Diagnostics:** every failure path emits an SMonitor catalog code with typed facts
  instead of being swallowed; optional dependencies are declared to DepDigest and
  reported by `dependency_info()`. Guarded by `tests/test_smonitor_integration.py`.
- **Concurrency:** scopes are isolated per thread and per asyncio task, the collector
  serializes compound updates, and journal appends retain observations. Explicit
  sessions separate analyses; callers that keep the default session share its
  observations. Guarded by `tests/test_thread_safety.py` and
  `tests/test_session_isolation.py`.
- **Coverage:** a weekly/manual installed Linux/Python 3.14 producer retains
  validated runtime XML and publishes it to Codecov. The README explains the
  last-uploaded report and scope; a percentage is not scientific or full-matrix
  certification. Guarded by `tests/test_coverage_workflow.py`, with evidence in
  [the coverage record](https://github.com/uibcdf/ackredit/blob/main/devguide/archive/scoped_runtime_coverage.md).

## Known defects

Open reports live in [the maintained bug queue](https://github.com/uibcdf/ackredit/blob/main/devguide/pending_bugs/README.md).
Documentation corrections and runtime defects retain separate evidence there.

## Known limitations, deliberately out of scope

- **Platform and interpreter evidence is bounded.** The required source range is
  Python 3.11–3.14, declared as `>=3.11,<3.15`; routine development uses 3.14.
  Ordinary CI gates all four Linux minors and macOS arm64/Python 3.14; the full
  weekly/manual matrix covers both platforms on every minor. Skipped-push
  detection and full recovery are guarded by `tests/test_ci_backlog.py` and
  recorded under #74. Windows has no qualification claim here. Component
  delivery under #80 is separate from central admission: immutable
  `policy-v1.5.6` now records Ackredit as `admitted`; adoption commit `8c743b3`
  updates the caller and verified four-minor README badge. MolSysSuite #51
  remains open for other components.
- **Sharing one session across processes needs a local filesystem.** The session is an
  append-only journal, and POSIX makes an `O_APPEND` write below `PIPE_BUF` atomic, so
  several processes may write one journal without losing events — verified with four and
  with eight. NFS does not provide that guarantee, so a network filesystem wants one
  journal per process, merged with `aggregate`.
- **A session file names items without describing them.** The journal records events —
  which id was credited and by what — while the metadata lives in the registry of the
  process that declared it. So `ackredit report session.json` lists the ids a run
  credited and cannot reconstruct their original titles, authors, DOIs or contextual
  uses. A portable result instead saves the detached `Attribution` payload beside
  its scientific data and can render that bibliography in a fresh reader.
  Development after public 0.10.1 (#101) adds the explicit CLI input mode:
  `ackredit report result.json --input-format attribution --format workflow`;
  `--output` exports a chosen format without modifying the saved input.
  Journal aggregation and portable attribution are separate contracts; see
  [architecture](architecture.md) and the [portable contract](../docs/content/user_guide/portable_attribution.md).
- **`@software` and `@dataset` are not defined by `plainnat.bst`.** BibTeX warns and
  degrades those entries rather than failing. Choosing a style or mapping the types is a
  separate question, noted in `devguide/archive/bibtex_does_not_escape_latex.md`.

## Work in progress towards 1.0.0

Organised as themes with exit criteria in [`roadmap.md`](roadmap.md), rather than as a
fixed number of releases. The minor rises when behaviour a caller can see changes, so how
many land before 1.0.0 is an outcome rather than a plan.

- **Distribution:** complete for public 0.9.0 under #22/#75/#80. The matching
  `0.9.0` Git tag identifies its original producer under #82. Later candidates
  require their own release gates; GitHub Release and DOI publication are
  separate outcomes (roadmap A, done).
  The 0.10.1 checkpoint is delivered under #93, including additive repair #94;
  its exact-file gates, public receipt and original-producer tag are retained.
- **Self-citation:** done. Ackredit ships `CITATION.cff` inside the package, finds
  itself from an installed distribution, and its metadata names the same authors
  (`uibcdf/ackredit#21`). Candidate-plan and installed release-version guards
  under #94 prevent stale packaged self-citation metadata; public 0.10.1 matches.
- **Adoption:** PyUnitWizard #92 exercises real Pint/unyt operations through its
  optional context; Sabueso #108 exercises required knowledge-packet attribution
  and has clean public-provider receiving evidence. Sabueso #110 completed its
  0.12.0 release; PyUnitWizard #94's experimental function-provider pilot is
  resolved, and its #111 optimization is jointly qualified under Ackredit #99.
  Further released integration claims remain client-owned. MolSysMT #292 still
  owns its portable-adapter adoption. The original real-adoption milestone is
  demonstrated; the explicit final stability review remains open (roadmap C/F).
- **Performance:** measured on a real MolSysMT workflow and published in
  `docs/content/about/performance.md`, which is where the numbers live: microseconds per
  instrumented call, tens of milliseconds once for auto-discovery at import, and on the
  workflow itself a difference smaller than the run-to-run spread. `devtools/benchmark.py`
  reproduces it (roadmap D, done).
- **API hardening:** done but for what adoption teaches. Every public name is classified
  in [API stability](../docs/content/about/stability.md), which is the authority
  for classifications and counts. The deprecation policy is written and portable
  schema/operations have a bounded released compatibility promise. The general
  API commitment remains pre-1.0 intent. Output formats are extensible through `register_format` and the
  `ackredit.formats` entry-point group. What remains of roadmap F is the review against
  demonstrated receiving workflows and released adoption; theme C already
  supplies that evidence, while the final stability decision remains explicit.
- **MolSysSuite membership:** granted in `uibcdf/molsyssuite#28`. Ackredit is a
  registered, incubating support library. Common policy and admission records
  remain MolSysSuite-owned; registration, source compatibility, public delivery
  and consumer release are separate states.

## Future strategic concepts

The maintainer-accepted continuation under Ackredit #100 is maintained in
[roadmap themes I–N](roadmap.md): portable saved-result CLI and composition,
scope/reference-origin/gap explanations, MOLI object-boundary decisions,
complete lifecycle cost, real publication-tool interoperability and the scope
of non-bibliographic acknowledgements. Theme G also plans a standalone inert
declaration validator and a concise external-producer guide. These are planned
implementations or decisions, not capabilities already shipped or implicit
conditions for every client or the general 1.0 stability commitment. Portable
CLI report/export is implemented in development under #101; composition and
report explanations are next. Provider/platform review can proceed in parallel.
New implementations need focused owning issues.

Active core improvements are tracked separately: #84 implements provisional
dependency-free function providers and actual-call observation; #85 measures
and reduces portable capture overhead; #87 prepares fixed explicit contextual
credits for completed dispatch. The first real function-provider pilot is
PyUnitWizard #94, with lazy exports and before/after scientific conversion
measurements. MolSysSuite #97 and MOLI #46 own cross-component
review. These capabilities ship provisionally in 0.10.0 and recommended 0.10.1;
they are absent from 0.9.0. Publication does not establish stable promotion or
consumer adoption.

The manually dispatched [coupled installed receiving gate](receiving_validation.md)
builds one wheel bundle and requires eight Linux/macOS arm64 × Python 3.11–3.14
cells. The first hosted qualification passes five tests per cell without skips
for source `357083e`, run
[37216812721](https://github.com/uibcdf/ackredit/actions/runs/37216812721).
Its downloaded archive/resource hashes and complete receptor artifacts verify
locally; #84/#87 retain the evidence. Ordinary CI exposed a separate minimal
discovery-test defect, tracked in #88 and corrected without adding NumPy.
The corrected source `fc00a6c` passes both ordinary CI 37217509058 (seven jobs)
and coupled receiving run 37217520167 (eight cells, 40 passed tests, no skips).
Its validated public receipt is retained in
`devtools/receipts/function_provider_matrix_2026-10-04.json`; #88 is archived.
The gate compares installed resources with the wheels and exercises actual
software/article roles, reused captures, graph parentage, provider absence and
the original 0.9.0 API fallback. It does not publish or promote the APIs.

The later Conda profile qualifies exact release bytes through the pinned shared
installer/verifier before and after science. Corrected source `dd50084` passes
the full source and installed matrices and real receiving run
[37268949118](https://github.com/uibcdf/ackredit/actions/runs/37268949118): eight
cells, 48 tests and no skips/deselections. Promotion
[37269544505](https://github.com/uibcdf/ackredit/actions/runs/37269544505)
verifies public 0.10.1 without rebuilding. Public Linux/Python 3.14.7 passes
portable/provisional smoke checks, accurate self-citation, CLI and `pip check`;
public Sabueso 0.12.0 passes 56 receiving tests and its three-result example.
These proofs remain separate from a client's own release and stable API review.

These are ideas, not missing core functionality or acceptance criteria for 1.0:

- **Cloud aggregator:** web-based citation gathering; no implementation contract.
- **IDE extensions:** real-time citation hints; no implementation contract.
- **Citation dashboard:** #58 records a possible separate distribution using
  the format extension point. Ackredit does not include a web server.
