---
summary: A cached DOI answer had no age, so a record cached while it was in press stayed that way for ever.
issue: uibcdf/ackredit#50
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: medium
verification: measured
area: [core, discovery]
guard: tests/test_cache_freshness.py
normative: docs/content/user_guide/registration.md
blocked_by: []
supersedes: []
---

# A cached answer never goes stale

## What

`enrich_item` read `~/.cache/ackredit` and never looked at the age of what it found, so an
answer was kept for as long as the directory survived. For a published record that is
almost always right. For one that was `"in press"` when it was cached it is wrong
permanently: the year arrives and Ackredit keeps reporting what it saw first. Corrections
to a title or an author list behave the same way.

## How

An answer is used for thirty days and then asked again. The age comes from the file's own
modification time, so the stored format is still exactly what the service replied and an
entry written before this has a freshness rather than being discarded.

**Staleness triggers a refresh and never a discard.** If the second request does not come
back, the answer already held is used. Nothing is reported when that happens, because
nothing was lost: the user asked for metadata and has it.

## Why

A cache exists for two reasons — sparing a shared service, and letting a run without a
network keep its metadata. An expiry that threw the answer away would serve the first and
destroy the second, taking from an offline user a citation they already had.

Thirty days is long enough that the services are spared and short enough that a year
arrives before a manuscript does. Deleting the directory forces everything to be asked
again, which is the escape hatch, and is documented.

## What was refuted

- **An environment variable for the age.** It is a knob nobody has asked for, and the same
  reasoning that refused a truncation marker in
  `devguide/archive/shipped_citation_data_is_not_true.md` applies: configuration added for
  a case nobody has drifts from the code meant to use it. The stale-fallback makes the
  default safe, and deleting the directory covers the rest.
- **Storing a timestamp inside the cache file.** It changes the format, so every entry
  written before this would have to be discarded or migrated, for a fact the filesystem
  already records.
- **Reporting that a stale answer was used.** It would fire on every offline run, and the
  code that means something went wrong — `ACKREDIT-W006` — would be buried under it.
- **Expiring into nothing, as an ordinary cache does.** Measured as a failing case rather
  than argued: with it, a run without a network loses metadata it had a moment before.

## Acceptance criteria

- a fresh answer is used without a request, and a stale one is refreshed — met;
- a stale answer whose refresh fails is still used, and nothing is reported — met;
- a failure with nothing to fall back on is still reported — met;
- an entry written before this is aged rather than discarded, and the stored format is
  still what the service answered — met;
- `tests/test_cache_freshness.py` guards it: 2 of its 12 tests fail when the age is
  ignored, and 2 when staleness discards.
