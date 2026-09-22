---
summary: An unfinished HTTP server was removed rather than promised, and what a dashboard would need is recorded instead.
issue: uibcdf/ackredit#57
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: low
verification: measured
area: [api, contrib]
guard: tests/test_public_surface.py
normative: docs/content/about/stability.md
blocked_by: []
supersedes: []
---

# serve_ui removed

## What

`serve_ui` started a local Flask server showing what a run had collected. Its own docstring
called it "a conceptual stub for the 0.4.0 release", which was the whole reason it was
classified provisional.

A provisional name reaches 1.0.0 either promoted or removed, so what finishing it would
cost had to be counted rather than guessed:

- it started a daemon thread and **nothing stopped it** — the missing-counterpart shape
  closed in `uibcdf/ackredit#34` for `enable_import_hooks` and `enable_auto_reminder`, and
  a server is where it matters most;
- it printed a URL and returned, so a caller could not tell a bound port from a failed one;
- the path that serves was **exercised by nothing**. Its only test was that it names Flask
  when Flask is absent.

## How

The name, `ackredit/contrib/web_ui.py`, the `flask` declaration in `ackredit/_depdigest.py`
and the `web` extra are gone, with the rows in `docs/content/about/installation.md`,
`docs/content/developer_guide/contributing.md` and `devguide/workflow.md`. `jinja2` left
the test environment with the dashboard escaping guard it had been added for.

The escaping itself stays: `ackredit/formats/_html.py` and `_links.py`, from
`uibcdf/ackredit#25`, are what the notebook renderer uses, with their own guards.

`uibcdf/ackredit#58` records what a dashboard would need, so the decision is not re-made
from nothing.

## Why

Not the work of finishing it. 1.0.0 means keeping what we promise, and an HTTP server
inside a citation library is surface with an indefinite cost for something `summary()`
already answers in a notebook and `report()` answers anywhere. If a dashboard is ever
wanted, `uibcdf/ackredit#36` built the `ackredit.formats` entry-point group, so a separate
distribution can serve one without this package depending on a web framework.

## What was refuted

- **Finishing it.** The path is clear — a counterpart that stops it, a signal that it came
  up, tests that ask it for a page — and each is a promise kept for as long as 1.x lasts.
- **Keeping the name and deprecating it after 1.0.0.** The policy would then require two
  minor releases carrying the deprecation, for a name nothing has ever served from.
- **Removing the name and keeping the module.** It would leave a Flask dependency declared,
  reported by `dependency_info()` as a feature the environment could support, for code
  nothing reaches.

## Acceptance criteria

- the name is gone from `__all__` and from the package — met;
- no module in `ackredit/` mentions Flask, and `flask` is no longer a declared optional
  library — met, so `dependency_info()` no longer offers a feature that does not exist;
- `full` still installs every optional library declared — met,
  `tests/test_packaging.py`;
- thirty-three public names: thirty-two stable and one provisional.
