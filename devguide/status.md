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
- **Concurrency:** scopes are isolated per thread and per asyncio task, the collector
  serializes its compound updates, and the session file is written atomically. Guarded by
  `tests/test_thread_safety.py`.

## Known defects

None currently recorded. Open reports live in `devguide/pending_bugs/`.

## Work in progress towards 1.0.0

- **API hardening:** finalizing stable interfaces for long-term support.
- **MolSysSuite membership:** the repository follows the common baseline; central
  registration is tracked in `uibcdf/molsyssuite#28`.
- **Suite infrastructure adoption:** SMonitor for structured diagnostics in place of the
  current silent `except Exception: pass` paths, and DepDigest for optional dependencies.

## Future strategic concepts

- **Cloud aggregator:** web-based citation gathering.
- **IDE extensions:** real-time citation hints.
