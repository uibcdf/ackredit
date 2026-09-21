# Technical Decision Log

## Decisions Made
1.  **Singleton/Class-based Registry and Collector:** It was decided to use class methods to ensure there is only one global state per process, facilitating use from anywhere within a host library.
2.  **Python 3.11–3.13:** Ackredit declares `requires-python = ">=3.11,<3.14"` and is tested
    on 3.11, 3.12 and 3.13, following the MolSysSuite Python policy. This supersedes the
    earlier "Python 3.10+" decision, which predates suite membership.
3.  **MolSysSuite membership:** Ackredit adopts the suite common baseline — Ruff, pytest,
    the supported Python range, the synchronized `MOLSYSSUITE_GUIDE.md` and the issue-backed
    reporting lifecycle. Admission and registration in the central `suite.toml` are tracked
    in `uibcdf/molsyssuite#28`.
4.  **Bindings are declarations, credited only on request:** `bind()` was write-only
    dead state, read by nothing. It now has a reader (`bound_items`) and an opt-in
    runtime effect (`scoped_usage(..., credit_bound=True)`, `scope(..., credit_bound=True)`,
    `credit_bound()`). Crediting is *not* automatic: deciding per code path is the
    differentiator against DueCredit, and silently crediting every bound item would
    report citations a run never needed.
5.  **Context-local scope, not process-global:** the current scope lives in a
    `contextvars.ContextVar` rather than a class attribute, so threads and asyncio tasks
    are isolated without the caller opting in. `scoped_usage` delegates to the `scope`
    context manager instead of duplicating its logic, so the isolation has a single
    implementation. The collector uses a reentrant lock for compound updates and writes
    its session file atomically via a temporary file and `os.replace`.
6.  **Suite infrastructure adopted (`uibcdf/ackredit#6`):** SMonitor provides the
    diagnostics and DepDigest the optional-dependency handling. Sixteen paths that lost
    their reason — eleven `except Exception: pass`, two `print()` calls and three logger
    lines nothing configured — now emit catalog codes carrying typed facts. This
    supersedes the "Zero Core Dependencies" pillar, since `depdigest` requires `smonitor`
    and both arrive together; in suite context they add nothing a host does not already
    have.
7.  **A session holds observations; the registry holds declarations
    (`uibcdf/ackredit#18`):** what was used belongs to a `Session` reached through a
    `ContextVar`, so a notebook, a host library and its user can each have their own
    without threading an object through every call. What *could* be cited stays in the
    shared `Registry`, because a host library registers it once at import. The module
    functions keep working untouched on a default session, which is the ergonomics the
    global existed for; a `ContextVar` read costs 0.118 µs against the 1.3 µs a
    `track_item` already spends.
8.  **`dump` keeps compiling the PDF (`uibcdf/ackredit#16`):** it renders files and
    optionally runs `pdflatex`, which are unrelated failures. Separating them was
    considered and refused: the argument against was that a missing system binary failed
    obscurely, and that stopped being true when `ACKREDIT-W011` and `W012` started
    explaining it. `dump(path, build_pdf=True)` is the one call a user wants at the end of
    a run, and `compile_pdf` is already exported for anyone who wants the two steps apart.

9.  **`format` stays a string (`uibcdf/ackredit#16`):** an enum would be checkable and
    discoverable, at the cost of an import for a value that is a name. Command lines,
    configuration files and JSON all carry strings, and the real defect — an unknown name
    silently producing a different format — was closed in `uibcdf/ackredit#15` with a
    refusal and `available_formats()`.

10. **The `target` vocabulary stays (`uibcdf/ackredit#16`):** `track_target` reads as a
    pair with `track_item` without being one, which suggested renaming it. The evidence
    refused that: `target` already means "a named unit of code" in seven public
    functions, so `track_target` is consistent with all of them and renaming would break
    that coherence. What was actually missing was documentation — `bind` had 13 mentions
    in the user-facing docs, `credit_bound` 11, and `track_target` none — so the
    distinction between an item and a target is now written down instead.

## Pending Decisions
1.  **External Dependencies:** Should we use an external library for BibTeX (more robust but adds a dependency) or write our own parser (lightweight but limited)?
2.  **Import Hooks:** How aggressive should we be in intercepting third-party imports?
3.  **Nested Scope:** How should the Collector behave if a tracked function calls another tracked function? Should citations be duplicated or hierarchized?

