---
summary: Sixteen failure paths lost their reason; SMonitor and DepDigest replace the hand-rolled equivalents.
issue: uibcdf/ackredit#6
status: resolved
opened: 2026-09-20
closed: 2026-09-20
verification: reproduced
area: [diagnostics, dependencies, governance]
guard: tests/test_smonitor_integration.py
normative: devguide/decisions.md
blocked_by: []
supersedes: []
---

# Adopt SMonitor for diagnostics and DepDigest for optional dependencies

## What

Sixteen places discarded the reason a thing failed: eleven `except Exception: pass`
blocks, two `print()` calls, and three logger lines nothing ever configured. A user
whose DOI enrichment failed received a citation report with a bare id and no indication
anything had gone wrong.

Optional dependencies were handled by hand: `flask` and `duecredit` imported inside
functions behind bare `try`/`except ImportError`, with no declared inventory, no install
hint and no way for a user to ask what their environment supported.

## How

Each path was read and classified before being replaced. The result is sixteen catalog
codes, thirteen warning classes and three exceptions, with prose in the catalog and typed
facts at the call site.

## Why

Ackredit is a support library in a suite whose premise is that infrastructure is shared.
Reimplementing diagnostics badly, inside a component that sits in every host library, is
the duplication the suite exists to prevent.

## What was refuted

Three assumptions failed against the real API and were corrected:

- catalog exception entries resolve from the `"exceptions"` group, not `"errors"`;
- `bundle.warn()` takes a message or a `Warning` instance, not a catalog key. Passing the
  key as a string emitted the key itself as the message and dropped `extra` entirely;
- the base classes must not inject the catalog unconditionally. Doing so defeats
  SMonitor's args-only rebuild path, and the hint was appended twice on every rebuild —
  which is how `warnings.warn(text, category)` and pytest-xdist reconstruct an instance.
  Check 4 of the guide's section 7 caught this.

A fourth was caught by a check of our own: `ACKREDIT-E003` named `{pypi}`, a field
DepDigest does not pass, so a literal brace reached the user.

## Scope and exclusions

Covers the mandatory and recommended layers of `SMONITOR_GUIDE.md` and the required
configuration of `DEPDIGEST_GUIDE.md`. Excludes `LazyRegistry`: Ackredit has no lazily
discovered plugin directories, since external citation packs arrive through an entry-point
group. Excludes `pdflatex` and `bibtex`, which are system binaries rather than Python
distributions and stay as `shutil.which` probes.

## Acceptance criteria

Met by commit `b1e1547`:

- `ackredit/_smonitor.py` inside the package, with `_private/smonitor/` holding the
  catalog, metadata, emitter, exceptions and warnings;
- `ensure_configured(PACKAGE_ROOT)` before the package's own imports;
- all sixteen paths emit catalog codes carrying typed facts;
- `@signal` on `report()` and `dump()`;
- optional dependencies declared in `ackredit/_depdigest.py`, guarded with `@dep_digest`,
  and reported by `dependency_info()`;
- `tests/test_smonitor_integration.py` implements the five checks of section 7 plus a
  check that no rendered message contains an unresolved placeholder;
- the "Zero Core Dependencies" pillar is superseded in `devguide/vision.md` and recorded
  in the decision log.
