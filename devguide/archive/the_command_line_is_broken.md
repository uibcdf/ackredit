---
summary: Every subcommand was wrong in some way, and nothing in the test suite ran the program.
issue: uibcdf/ackredit#40
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: high
verification: measured
area: [cli, documentation]
guard: tests/test_cli.py
normative:
blocked_by: []
supersedes: []
---

# The command line is broken

## What

`ackredit` is a console script in `[project.scripts]`, and the conda recipe tests it — with
`ackredit --help`, the only check that existed anywhere. It passed while the program did
not work.

**`ackredit aggregate` raised.** It called `Collector._save_state()`, removed by the
persistence rewrite in `uibcdf/ackredit#17`:

```
AttributeError: type object 'Collector' has no attribute '_save_state'
exit code: 1
```

Dead since that change, and nothing noticed.

**`ackredit report` on a missing file created it and reported emptiness**, with exit code
0, because it opened its input with `enable_persistence`, which exists to append and
therefore creates. A mistyped name produced a new empty journal and the conclusion that
the session held nothing.

**`--format` listed six of seven formats**, hardcoded: `json` was refused although
`available_formats()` returns it, and after `uibcdf/ackredit#36` no plugin format could be
reached at all.

**"Successfully merged N sessions" counted the arguments.** A missing file is skipped by
design and an unreadable one raises `ACKREDIT-W003`; the message claimed success either
way.

## How

Reading no longer writes: a session file is validated with `session.read`, and a missing or
unreadable one is an error with a non-zero status. The format options come from
`available_formats()`, so the `csl` alias and any plugin format work, and an unknown name
raises `ACKREDIT-E004`, which already names what exists.

`aggregate` opens its output journal before merging rather than after, so the merge is
recorded in it — which `uibcdf/ackredit#39` made possible. It names every skipped file on
stderr, reports how many of the given files were merged, writes nothing when it can read
nothing, and exits non-zero when something the user asked for did not happen.

## Why

This class survived because nothing ran the program. Reading the file would not have found
`_save_state`, because the name looks right; only calling it does.

The command is also the part of Ackredit a user meets without writing Python, and the one
the conda package advertises. A tool that creates a file when asked to read one, and
reports success for work it did not do, is worse than no tool.

## What was refuted

- **Keeping `enable_persistence` for reading and simply checking existence first.** It
  would still open the input for appending and leave a journal open on a file the user
  asked to read.
- **`choices=available_formats()` in argparse.** It gives a tidy error and refuses the
  documented `csl` alias, and it would freeze the list at parser construction in a way that
  reads as complete while a plugin format is missing from it.
- **Printing the unknown-format message from the command.** The catalog already reports it,
  with the code and what to use instead; a second message is the hardcoded prose the
  diagnostics policy exists to prevent. Measured — it appeared twice before this was
  removed.
- **Exiting 0 after a partial merge.** It is the "Successfully merged" defect with better
  wording: something the user asked for did not happen.

## Also fixed

The message said "1 citations". That is the defect closed in `uibcdf/ackredit#35` for the
exit reminder, written again three commits later in a different file, which is worth
recording as the reason the reminder's guard did not help: it holds one call site, not the
class.

## Documented rather than fixed

`ackredit report session.json` prints an item's id and not its title, authors or DOI. A
journal records events — which id was credited and by what — while the metadata lives in
the registry of the process that declared it. Inside a workflow that costs nothing, because
the host library registers its items at import; a command line opening a file on its own
has nothing to import. Stated in `docs/content/user_guide/reporting.md`, which also
documents the command for the first time, and in `devguide/status.md`.

## Scope and exclusions

Covers the three subcommands and their failure paths. Making a session file carry item
metadata is a design change to the journal format and not this report.

## Acceptance criteria

- reading never creates or modifies the input — met;
- a missing or unreadable session is an error with a non-zero status — met;
- every format `available_formats()` offers is reachable, including the `csl` alias — met;
- `aggregate` writes a session holding what it merged, reports what it skipped, and writes
  nothing when it can read nothing — met;
- `tests/test_cli.py` runs the real program in a real process: 16 tests, 3 of which fail
  when the input is opened for writing again.
