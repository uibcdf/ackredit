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

Thirty names are stable and six provisional. This is the only place those counts
are written; everything else links here, so they cannot drift apart.

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
| `enable_auto_reminder` | stable | Says once, at exit, that the run used work worth citing. `uibcdf/ackredit#34` gave it the counterpart that was its only recorded reason to be provisional. |
| `disable_auto_reminder` | stable | The counterpart. Idempotent, and calling it without having enabled anything does nothing. |
| `disable_import_hooks` | stable | Removes every Ackredit finder from `sys.meta_path`. What it undoes is the watching, not the crediting that already happened, and that is the whole of its contract. |
| `__version__` | stable | Derived from the tag by Versioningit and guarded against the packaging metadata. |
| `enable_persistence` | stable | Was exported as a bound method of `Collector`, which bound a public name to a provisional class; `uibcdf/ackredit#33` gave it a function like its siblings. |
| `close_persistence` | stable | The counterpart of `enable_persistence`, and stable with it. Closing is where the single `fsync` is paid. |
| `aggregate` | stable | Merging saved runs into this one. `uibcdf/ackredit#39` settled what it does to the journal and exercised it; what it does across machines is decided rather than open — one journal per process, merged here. |
| `auto_track_calls` | stable | Detection is per function, not per branch, and that is the promise rather than a gap in it: `devguide/roadmap.md` refuses per-branch precision, which would need an interpreter hook on every call. |
| `enable_import_hooks` | stable | Decision 13 settles what the hook does — it observes and never acts — and `uibcdf/ackredit#28` settles which source of metadata wins. `uibcdf/ackredit#34` gave it a counterpart. |
| `compile_pdf` | stable | That `@software` is undefined in common `.bst` styles is a known limitation of those styles, recorded in `devguide/status.md`. It bears on what the PDF contains, not on this call. |
| `enrich_all` | stable | Fills in what a DOI can supply. How it asks was settled in `uibcdf/ackredit#48` and how long a cached answer keeps in `#50`; both are what it does, not what it promises. |

| `Session` | stable | What it promises is written on the class: `used_items`, `used_targets`, `usage_tree`, `journal_path`, `name` and `clear()`. `uibcdf/ackredit#52` made the machinery private, so the surface and the promise are the same thing. |
| `summary` | stable | Its contract is three renderings of the same run: `_repr_html_` for a notebook, `str()` and `repr()` everywhere else. `uibcdf/ackredit#51` added the last two, which is what it was missing. |
| `register_format` | stable | What a renderer is handed is written on it and guarded: a copy of the used map, a read-only registry, and options a format may take. `uibcdf/ackredit#53` settled all three. |
| `Registry` | provisional | Direct access to shared declaration state. `register_item` and `bound_items` are the supported surface; this is the class behind them. |
| `Collector` | provisional | Its state is a read-only view onto the current session now. `get_used_items` is the supported reader; the class remains exported for the code that predates the session. |
| `dependency_info` | provisional | Returns the shape `depdigest.get_info@1.0` defines, so its stability is DepDigest's to promise, not ours. |
| `export_to_duecredit` | provisional | A bridge to another project's API, which we do not control. |
| `load_plugins` | provisional | The promise is the entry-point group name, `ackredit.citations`, and no real plugin has used it yet. |
| `serve_ui` | provisional | Its own docstring calls it a conceptual stub. |

`tests/test_api_stability.py` holds this table to `__all__`, so a name cannot join the
public surface without a decision about what it promises.

## The session file is a separate contract

`enable_persistence` writes a journal, and that file outlives the process that wrote it. Its
format is promised apart from the names above, because a user can hold a file written by a
version of Ackredit they no longer have installed.

**Ackredit reads every session format it has ever written.** The journal carries a schema
line, `ackredit.session@1` today, and a format change raises that number rather than
reusing it. The reader already honours this: it loads the whole-document format Ackredit
used before the journal existed, and `tests/test_persistence_cost.py` holds it to that.

Nothing is promised in the other direction. An older Ackredit meeting a newer journal reads
the events it understands and skips the rest, the same way it skips the torn last line an
interrupted run leaves.

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

   What counts as one is the *promise*, not the mechanism. `enrich_all` fills in metadata a
   DOI can supply; giving its cache a freshness changes when a request is made and not what
   the call is for, so it is an ordinary change. `track_item` records what a run reached;
   making it credit at import instead would change exactly that, and is a removal however
   the name stays. Adding an optional argument is neither — it is an addition, and nothing
   that worked stops working.

   This line is here because leaving it out is what misfiled four names in
   `uibcdf/ackredit#49`: an open question about behaviour was read as an expected change of
   shape.
6. **A provisional name may change in any minor release**, and the change is recorded in
   the release notes. That is what provisional buys, and it is why the list above is short
   and reasoned rather than a catch-all.
