(About_Stability)=
# API stability

## What this page is

Ackredit is pre-1.0. **1.0.0 means the public API is stable and we commit to not breaking
it**, and this page says in advance which names that covers.

Until 1.0.0 is tagged the table is a statement of intent, not the commitment itself. It
exists so the commitment, when it is made, is made on purpose: a name reaches 1.0.0 as
`stable` because someone decided it should, not because it happened to be exported.

`__all__` is the boundary. Anything not listed there is private whatever it is called, and
may be renamed or removed without notice — including the modules under `ackredit.core`,
`ackredit.formats` and `ackredit.contrib`, which are implementation.

## What the two levels mean

**Stable.** We intend to keep the name, its meaning and its call signature across 1.x. It
is exercised by the test suite, documented, and its shape was decided deliberately — most
of them appear in `devguide/decisions.md` or in an archived report explaining why they are
the way they are.

**Provisional.** We expect this to change. It may be renamed, reshaped or removed in any
minor release before 1.0.0, and it reaches 1.0.0 either promoted to stable or removed —
shipping a provisional name inside a stability commitment would make the commitment
meaningless. Every provisional name below says why it is one.

## The surface

| name | status | why |
| --- | --- | --- |
| `register_item` | stable | The declaration primitive. Its fields are the citation record every renderer reads. |
| `bind` | stable | Declares what a target may require. Decision 4: a declaration with an opt-in runtime effect, never automatic. |
| `bound_items` | stable | The reader `bind` lacked when it was write-only dead state. Decision 4. |
| `credit_bound` | stable | The opt-in that makes a binding credit. Decision 4. |
| `track_item` | stable | What a run actually reached. The central claim of the library. |
| `track_target` | stable | Decision 10 examined renaming it and refused: `target` already means "a named unit of code" in seven public functions. |
| `scope` | stable | Context-local, decision 5. Used in every worked example and in both example libraries. |
| `scoped_usage` | stable | Delegates to `scope`, so the isolation has one implementation. Decision 5. |
| `add_injection` | stable | How a host credits a third-party package it calls. Exercised by both example libraries. |
| `report` | stable | The output. Decisions 8 and 9 settled `format` as a string and what `dump` does beside it. |
| `dump` | stable | Decision 8: it renders files and optionally compiles the PDF, and the two failures are explained separately. |
| `available_formats` | stable | Added with the refusal in `uibcdf/ackredit#15`, so an unknown format is answerable rather than silent. |
| `get_used_items` | stable | The supported reader of what a run credited. |
| `load_bibtex` | stable | Its provenance behaviour is decided and guarded: fields from a `.bib` file are LaTeX already and are never re-escaped. |
| `session` | stable | Decision 7. The context manager is how a session is entered. |
| `current_session` | stable | Decision 7. The session the module functions are recording into. |
| `__version__` | stable | Derived from the tag by Versioningit and guarded against the packaging metadata. |
| `Session` | provisional | Exported so a session can be named in a type hint. Which of its attributes are part of the promise is not settled, and the journal it writes is `ackredit.session@1` with no migration story yet. |
| `Registry` | provisional | Direct access to shared declaration state. `register_item` and `bound_items` are the supported surface; this is the class behind them. |
| `Collector` | provisional | Its state is a read-only view onto the current session now. `get_used_items` is the supported reader; the class remains exported for the code that predates the session. |
| `enable_persistence` | provisional | Exported as a bound method of `Collector` rather than a function, and the journal schema has no migration story. Both want settling before they are frozen. |
| `close_persistence` | provisional | The counterpart of `enable_persistence` and provisional with it. |
| `aggregate` | provisional | Merging several runs is the least exercised part of the design, and how it should behave across machines is open. |
| `auto_track_calls` | provisional | Detection is per function, not per branch, so a run that takes a path never reaching the detected call is credited anyway. That coarseness is documented, not resolved. |
| `enable_import_hooks` | provisional | It installs a process-wide finder and has no counterpart that removes it. The order in which sources of citation metadata win also changed in `uibcdf/ackredit#28`. |
| `summary` | provisional | Returns an object whose only contract is `_repr_html_`. What else that object should offer is unexplored. |
| `dependency_info` | provisional | Returns the shape `depdigest.get_info@1.0` defines, so its stability is DepDigest's to promise, not ours. |
| `compile_pdf` | provisional | `@software` and `@dataset` are undefined in common `.bst` styles, so what a compiled report contains is not settled. |
| `enrich_all` | provisional | Reaches the network. There is no policy yet on rate limits, offline behaviour or how long a cached answer is good for. |
| `export_to_duecredit` | provisional | A bridge to another project's API, which we do not control. |
| `load_plugins` | provisional | The promise is the entry-point group name, `ackredit.citations`, and no real plugin has used it yet. |
| `enable_auto_reminder` | provisional | Registers a process-exit side effect with no way to unregister it. |
| `serve_ui` | provisional | Its own docstring calls it a conceptual stub. |

`tests/test_api_stability.py` holds this table to `__all__`, so a name cannot join the
public surface without a decision about what it promises.

## Deprecation policy

This is what we commit to from 1.0.0 onward.

1. **A stable name is removed only in a major release.** Not in a patch, not in a minor.
2. **A removal is announced first.** The name keeps working and emits an SMonitor
   deprecation code for **at least two minor releases** before the major release that
   removes it. Two, not one, so a user who skips a release still meets the warning.
3. **The warning says what to use instead.** A deprecation with no replacement named is a
   removal with extra steps; if there is no replacement, the release notes say why the
   capability is going away.
4. **The message lives in the catalog.** Ackredit's diagnostics are catalog-driven and
   nothing is hardcoded, so a deprecation adds its code the way every other code was
   added: with the path that emits it, not in advance.
5. **A change in behaviour is a removal.** Keeping a name while changing what it does is
   the harder failure to debug, so it follows the same route.
6. **A provisional name may change in any minor release**, and the change is recorded in
   the release notes. That is what provisional buys, and it is why the list above is short
   and reasoned rather than a catch-all.
