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
11. **Tags now, channel later (2026-09-21):** releases are cut as Git tags and no conda
    package is published until the release before 1.0.0. The machinery exists and is
    verified, so publishing is a decision rather than a task.

    Why defer: a published package is a commitment to what it contains, and the API is
    still moving — themes C and F may both change it. Publishing early would mean
    superseding artifacts on the channel to correct decisions that were always going to
    be revised, and the release policy is deliberately unforgiving about republished
    identity.

    What it costs: a host library can integrate from a tag and produce the evidence theme
    C exists for, but cannot ship an integration depending on an unresolvable package. The
    tag route is documented and verified, so nothing is blocked that matters yet.

12. **Ackredit reads BibTeX itself, and does not read YAML itself
    (`uibcdf/ackredit#31`):** recorded as pending since the beginning and settled by the
    implementation long ago. `load_bibtex` is Ackredit's own parser; `CITATION.cff` is
    read with PyYAML.

    The two went opposite ways for the same reason. The `.bib` subset Ackredit reads is
    entries, fields and braces, produced by reference managers, and a construct the parser
    does not handle fails where you can see it. YAML is not like that: the specification
    has constructs that a partial reader accepts and resolves to something else, so a
    hand-rolled reader returns a confident wrong answer. A citation library can afford to
    fail; it cannot afford to be quietly wrong.

13. **Import hooks observe and never act (`uibcdf/ackredit#28`, `#31`):** also recorded as
    pending since the beginning. The hook is opt-in — nothing happens until
    `enable_import_hooks()` is called — it only watches `find_spec` and never imports
    anything itself, it credits a top-level distribution once per process, and a failure
    inside it never propagates to the import that triggered it.

    Which source wins was the open part and is decided in `uibcdf/ackredit#28`: what the
    host explicitly asked for, then the package's own `CITATION.cff`, then Ackredit's
    shipped table, then package metadata.

14. **Nested scopes are hierarchized, not duplicated (`uibcdf/ackredit#31`):** the third
    entry recorded as pending and settled by the implementation. An item credited inside a
    nested scope is attributed to the innermost target, and the provenance tree shows the
    path that reached it:

    ```
    └── outer
        ├── (Cite: A)
        └── inner
            └── (Cite: A)
    ```

    A caller is recorded once however many times it credits the same item, so entering a
    scope in a loop does not inflate anything. Duplication was the alternative and it
    loses the tree, which is what distinguishes this library's report from a list.

15. **Stable and provisional, with a deprecation policy (`uibcdf/ackredit#31`):** every
    name in `__all__` is classified in `docs/content/about/stability.md`, and
    `tests/test_api_stability.py` holds the page to `__all__`, so a name cannot join the
    public surface without a decision about what it promises.

    A provisional name reaches 1.0.0 either promoted or removed: shipping one inside a
    stability commitment would make the commitment meaningless. The page carries the
    counts, and is the only place they are written.

    The policy adds a rule worth stating here, because it constrains future work: a
    deprecation adds its SMonitor code with the path that emits it, not in advance. That
    is the same reasoning that refused a truncation marker in
    `devguide/archive/shipped_citation_data_is_not_true.md` — schema added for a case
    nobody has is how it drifts from the code that was supposed to use it.

16. **Output formats are extensible (`uibcdf/ackredit#36`):** the one entry that stood
    under "Pending Decisions" after theme F, and the one theme F could not close over,
    because it decided whether `_RENDERERS` is implementation or surface.

    It is implementation, and `register_format` is the surface in front of it, with an
    `ackredit.formats` entry-point group mirroring `ackredit.citations`. Plugins load
    lazily, the first time the format table is consulted, because requiring a call before
    `report(format="mine")` works would make an unknown-format refusal the normal first
    experience of the feature.

    The rule that carries the decision: **a registered name is never replaced**, built-in
    or from another plugin. Letting a third party take over `bibtex` would make a request
    succeed and return a report that is not the one asked for, which is the defect
    `uibcdf/ackredit#15` closed. For the same reason names are held to one lower-case
    style at registration: lookups match exactly, so `BibTeX` would become a second,
    silently different format rather than an alias.

    Why build it rather than drop the claim: a citation tracker whose report is the
    product should let a group render that report the way its journal, its institution or
    its pipeline needs, without forking. The cost is one public name and three catalog
    codes.

## Pending Decisions

None. `devguide/roadmap.md` carries what is left before 1.0.0, and the open questions
there are measurements and adoption rather than decisions.
