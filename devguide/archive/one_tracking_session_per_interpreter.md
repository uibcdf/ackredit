---
summary: Tracking state was class attributes, one set per interpreter; it now belongs to a session.
issue: uibcdf/ackredit#18
status: resolved
opened: 2026-09-21
closed: 2026-09-21
verification: reproduced
area: [api, core]
guard: tests/test_session_isolation.py
normative: devguide/decisions.md
blocked_by: []
supersedes: []
---

# Tracking state is one global per interpreter

## What

`Collector.used_items`, `used_targets` and `usage_tree` were class attributes, so a
notebook could not start a fresh count between cells, a host library could not keep its
tracking apart from its user's, and nothing could produce two reports in one process. The
only available workaround was reaching into internals, which is also what the test suite
did.

## How

Decided in `uibcdf/ackredit#16` after measuring: a `ContextVar` read costs 0.118 µs
against the 1.3 µs a `track_item` already spends, 0.1% of what was already being paid, and
the mechanism is the one already proven for `scope`.

## Why

Ackredit sits inside host libraries, so "one per interpreter" is not one per user's
intention. A single global was right while this was a script-scale tool and becomes the
limit as soon as two things in one process want their own answer.

## What was refuted

**Scoping declarations alongside observations** was rejected. `Registry` holds what
*could* be cited, which a host library registers once at import; scoping it per session
would mean a session entered after import sees no declarations at all. Only tracking and
reporting are session-scoped, so `register_item` and `bind` behave exactly as before.

**A separate object-oriented API** — `s = Session(); s.track_item(...)` — was rejected as
the primary form. It is the "two ways to do everything" that `uibcdf/ackredit#14` closed.
The module functions remain the API; what changes is which session answers them.

**A plain module global holding the current session** was rejected in favour of a
`ContextVar`: a thread entering a session would otherwise change what every other thread
sees, which is the defect fixed in `uibcdf/ackredit#5` reintroduced one level up.

## Scope and exclusions

Covers where tracked state lives and how a caller chooses it. Excludes the rest of the
1.0 shape questions in `uibcdf/ackredit#16`, which remain open.

## Acceptance criteria

Met by the commit closing this record:

- `ackredit.report()` and every other module function work untouched, on a default
  session;
- `with ackredit.session()` isolates, restores on an exception, and copies rather than
  aliases under `inherit=True`;
- sessions are isolated between threads, verified with six;
- `Collector.used_items` keeps reading as before, through the current session;
- a journal opened inside a session closes when the session does;
- `tests/test_session_isolation.py` covers all of it.
