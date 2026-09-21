---
summary: A shipped injection marked the package as handled, so its own CITATION.cff was never read.
issue: uibcdf/ackredit#28
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: high
verification: measured
area: [core, discovery]
guard: tests/test_citation_authority.py
normative:
blocked_by: []
supersedes: []
---

# An injection shadows the citation file

## What

`InjectionsFinder.find_spec` ran the shipped table first and added the package to
`_triggered`. Auto-discovery was guarded by the same set, so `_discover_and_register` —
which reads the package's `CITATION.cff` — never ran for any package Ackredit ships an
entry for.

The authority was inverted. A `CITATION.cff` is the project's own statement of how it
wants to be cited, versioned and updated by the project. Ackredit's table is a snapshot
that can only go stale, and the snapshot won.

Not hypothetical: before #26 this meant `import molsysmt` credited a 2024 article that
does not exist, while MolSysMT's `CITATION.cff` sat unread in the same directory saying to
cite the software through its Zenodo DOI.

## How

The finder now works in order of authority:

1. a **manual injection**, which is a human integrating the library and saying what to
   credit;
2. the package's **`CITATION.cff`**;
3. Ackredit's **shipped entry**, for a package that has no file or whose file cannot be
   read — which `ACKREDIT-W004` already reports;
4. **package metadata**, as a last resort.

Where both a file and a shipped entry exist, the file supplies every field and the shipped
entry supplies the id, so a host that bound to `molsysmt:software` still matches. The file
describes the software, so it replaces a shipped entry of type `software` and nothing
else: a paper shipped alongside it is a different work and is still credited. That rule is
read from the entry's type rather than its position in the list.

`_triggered` is marked before the work rather than after, because discovery calls
`find_spec`, which reaches this finder again; that marker is what stops it.

## Why

Fixing the data (#26) did not change which source wins, so the next divergence — a new
DOI, a new author, a new version — would have reproduced the defect with a table that had
just been corrected. The correction would have looked like the fix.

## What was refuted

- **Keeping the table first and refreshing it.** It is a cache with no invalidation, of
  data that belongs to someone else and changes without telling us.
- **Dropping the shipped entries for packages that ship a `CITATION.cff`.** The file can
  be unparseable, and Ackredit reports that rather than failing; the entry is what it
  falls back to. It is also the only source for NumPy, SciPy and Matplotlib, which ship no
  file and whose papers package metadata cannot name.
- **Using `discovered:{package}` even where a shipped entry exists.** It is simpler and it
  silently breaks any `bind` that names the shipped id.
- **Taking the first shipped entry as the one the file replaces.** Positional, and wrong
  the first time a package ships a paper before its software entry. The type says which
  one it is.

## Scope and exclusions

Covers the order in which the import hook consults its sources. What each source yields is
unchanged, except that a discovered item now carries the `version` the file states.

## Acceptance criteria

- a package with both a file and a shipped entry is credited from the file, under the
  shipped id — met;
- a shipped paper alongside it still stands — met;
- a package with no file falls back to the entry, and one with neither to its metadata —
  met;
- a manual injection wins over both — met;
- a package is credited once — met;
- `tests/test_citation_authority.py` guards it, failing when the table is put back in
  front.
