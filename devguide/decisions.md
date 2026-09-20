# Technical Decision Log

## Decisions Made
1.  **Singleton/Class-based Registry and Collector:** It was decided to use class methods to ensure there is only one global state per process, facilitating use from anywhere within a host library.
2.  **Python 3.11–3.13:** FlowCite declares `requires-python = ">=3.11,<3.14"` and is tested
    on 3.11, 3.12 and 3.13, following the MolSysSuite Python policy. This supersedes the
    earlier "Python 3.10+" decision, which predates suite membership.
3.  **MolSysSuite membership:** FlowCite adopts the suite common baseline — Ruff, pytest,
    the supported Python range, the synchronized `MOLSYSSUITE_GUIDE.md` and the issue-backed
    reporting lifecycle. Admission and registration in the central `suite.toml` are tracked
    in `uibcdf/molsyssuite#28`.

## Pending Decisions
1.  **External Dependencies:** Should we use an external library for BibTeX (more robust but adds a dependency) or write our own parser (lightweight but limited)?
2.  **Import Hooks:** How aggressive should we be in intercepting third-party imports?
3.  **Nested Scope:** How should the Collector behave if a tracked function calls another tracked function? Should citations be duplicated or hierarchized?
4.  **Suite infrastructure adoption:** FlowCite is to adopt SMonitor for structured
    diagnostics, replacing the current silent `except Exception: pass` paths, and DepDigest
    for its optional dependencies. This changes the historical "zero core dependencies"
    pillar and is a design change, not part of the governance retrofit; it needs its own
    issue cross-linking `uibcdf/molsyssuite#28`.
