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
  and LaTeX, plus `dump()` to a directory and PDF compilation when `pdflatex` is present.
- **Automated discovery:** import hooks, `CITATION.cff` parsing and PEP 621 metadata.
- **Metadata enrichment:** DOI lookup against Crossref and DataCite, with a local cache.
- **Ecosystem integration:** entry-point plugin loading, a DueCredit bridge, session
  persistence and a multi-session aggregator.
- **Developer tools:** command-line interface and a Jupyter HTML summary.
- **Distribution:** an installed wheel imports and works outside the source tree, guarded
  by `tests/test_packaging.py`.
- **Documentation:** the Sphinx site builds with no warnings, and every documented Python
  snippet is checked against the real API by `tests/test_documented_api.py`.
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
  serializes its compound updates, and the session file is written atomically. Guarded by
  `tests/test_thread_safety.py`.

## Known defects

None currently recorded. Open reports live in `devguide/pending_bugs/`.

## Known limitations, deliberately out of scope

- **CI runs on Linux only.** `smonitor` and `depdigest` are published to the `uibcdf`
  channel as `linux-64` builds with per-interpreter ABI pins, so a macOS environment
  cannot be solved. Both recipes already declare `noarch: python` at HEAD, so their next
  release restores the lane; noted upstream in `uibcdf/molsyssuite#29`. The macOS lane
  is removed rather than left failing, so the CI keeps meaning something.
- **Python is 3.11 to 3.13.** Adopting 3.14 is governed by the transition in
  `uibcdf/molsyssuite#29` and waits on the same two dependencies, which are capped at
  `<3.14`. Ackredit is registered behind DepDigest in that dependency order.
- **Sharing one session across processes needs a local filesystem.** The session is an
  append-only journal, and POSIX makes an `O_APPEND` write below `PIPE_BUF` atomic, so
  several processes may write one journal without losing events — verified with four and
  with eight. NFS does not provide that guarantee, so a network filesystem wants one
  journal per process, merged with `aggregate`.
- **`@software` and `@dataset` are not defined by `plainnat.bst`.** BibTeX warns and
  degrades those entries rather than failing. Choosing a style or mapping the types is a
  separate question, noted in `devguide/archive/bibtex_does_not_escape_latex.md`.

## Work in progress towards 1.0.0

Organised as themes with exit criteria in [`roadmap.md`](roadmap.md), rather than as a
fixed number of releases. The minor rises when behaviour a caller can see changes, so how
many land before 1.0.0 is an outcome rather than a plan.

- **Distribution:** Ackredit is published to no channel, so it can only be installed
  from source. This blocks every other theme (roadmap A).
- **Self-citation:** Ackredit ships no `CITATION.cff`, so its own auto-discovery cannot
  find it, and its package metadata declares no author beyond the team name (roadmap B).
- **Adoption:** no host library has integrated the guide yet. Every defect found in it so
  far was found by reading it rather than using it (roadmap C).
- **API hardening:** the shape questions are decided (`uibcdf/ackredit#16`); what remains
  is marking each public name stable or provisional, and a deprecation policy
  (roadmap F).
- **MolSysSuite membership:** the repository follows the common baseline and its CI uses
  the suite's conda environments. Central registration is tracked in
  `uibcdf/molsyssuite#28`, and until it is granted two things stay blocked: the README
  badges, which the central generator produces only for a registered member and whose
  role badge would otherwise assert a membership that has not been granted; and
  `molsyssuite-policy.yml`, which reports `UNREGISTERED` by design.

## Future strategic concepts

- **Cloud aggregator:** web-based citation gathering.
- **IDE extensions:** real-time citation hints.
