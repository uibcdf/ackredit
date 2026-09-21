---
summary: The exit reminder wrote ANSI colour to stderr unconditionally, so redirected logs received the escapes literally.
issue: uibcdf/ackredit#35
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: low
verification: measured
area: [core, diagnostics]
guard: tests/test_exit_reminder.py
normative:
blocked_by: []
supersedes: []
---

# The exit reminder writes ANSI into logs

## What

`_exit_reminder` wrote colour to `sys.stderr` whatever the stream was. Redirected to a
file, which is what a batch job, a scheduler and a CI log all do:

```
^[[94mℹ️  Ackredit: Your analysis utilized 1 components requiring citation.^[[0m
   Run `ackredit.report()` or `ackredit.summary()` to view the full list.
```

It also said "1 components", and described a citation report in the vocabulary of an
inventory. It was the last ANSI sequence in the package.

## How

Colour only when `sys.stderr` is a terminal, through a helper that treats a stream which
cannot answer as not one — a replaced stderr may have no `isatty`, and a closed one raises
`ValueError`. The sentence is written twice, once for one work and once for several, so
both are grammatical:

```
Ackredit: this run used 1 work that asks to be cited.
   ackredit.report() lists it; ackredit.summary() shows it in a notebook.
```

## Why

A library writes to streams it does not own and cannot see. Deciding that the reader has a
terminal is the same class of assumption as deciding that a citation title contains no
markup: right in the author's environment, wrong in the one that matters.

## What was refuted

- **Routing it through the SMonitor catalog.** The obvious move given
  `uibcdf/ackredit#6`, which converted the other two `print` calls, and wrong here. The
  catalog carries diagnostics — something went wrong, here is what and why — and a host
  filters, escalates and reports them as such. Nothing has gone wrong at the end of a
  successful run, and a host's warning configuration could turn a courtesy into an error.
  The reason is written at the call site so the question is not reopened.
- **Dropping the colour entirely.** It earns its place in the terminal, which is where a
  reminder at the end of an interactive session is read.
- **Checking an environment variable such as `NO_COLOR`.** A reasonable convention and a
  larger commitment than this defect justifies; `isatty` already covers every case
  measured here.

## Scope and exclusions

Covers the reminder. The `print` calls in `ackredit/cli.py` are a command line writing its
output to stdout and are not diagnostics either.

## Acceptance criteria

- a redirected stream receives no escape sequences — met, verified by running a real
  interpreter to exit with its stderr on a pipe;
- one work reads in the singular and several in the plural — met;
- a stream with no `isatty`, and one that raises, are treated as not terminals — met.
