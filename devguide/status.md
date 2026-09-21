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
- **Diagnostics:** every failure path emits an SMonitor catalog code with typed facts
  instead of being swallowed; optional dependencies are declared to DepDigest and
  reported by `dependency_info()`. Guarded by `tests/test_smonitor_integration.py`.
- **Concurrency:** scopes are isolated per thread and per asyncio task, the collector
  serializes its compound updates, and the session file is written atomically. Guarded by
  `tests/test_thread_safety.py`.

## Known defects

None currently recorded. Open reports live in `devguide/pending_bugs/`.

## Known limitations, deliberately out of scope

- **Two processes cannot share one session file.** Each save replaces the whole document,
  so a shared path means the last writer wins. This is reported as `ACKREDIT-W014` rather
  than absorbed (`uibcdf/ackredit#8`), and the supported pattern is one file per process
  merged with `aggregate`, which is verified by `tests/test_session_sharing.py`. No file
  locking is attempted, and none is planned.
- **`@software` and `@dataset` are not defined by `plainnat.bst`.** BibTeX warns and
  degrades those entries rather than failing. Choosing a style or mapping the types is a
  separate question, noted in `devguide/archive/bibtex_does_not_escape_latex.md`.

## Work in progress towards 1.0.0

- **API hardening:** finalizing stable interfaces for long-term support.
- **MolSysSuite membership:** the repository follows the common baseline and its CI uses
  the suite's conda environments. Central registration is tracked in
  `uibcdf/molsyssuite#28`, and until it is granted two things stay blocked: the README
  badges, which the central generator produces only for a registered member and whose
  role badge would otherwise assert a membership that has not been granted; and
  `molsyssuite-policy.yml`, which reports `UNREGISTERED` by design.

## Future strategic concepts

- **Cloud aggregator:** web-based citation gathering.
- **IDE extensions:** real-time citation hints.
