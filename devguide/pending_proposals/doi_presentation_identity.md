---
summary: Project supported DOI wrappers for display while preserving original ID identity.
issue: uibcdf/ackredit#121
status: active
opened: 2026-10-06
closed:
severity: medium
verification: reproduced
area: [formats, attribution]
guard:
normative:
blocked_by: []
supersedes: []
---

# DOI presentation and original bibliography identity

## What

#120 retains a reproduced duplicate-resolver prefix for a full-URL DOI in CSL
presentation. Ackredit's Markdown, workflow and notebook links use the same
unconditional prefix and have the same problem.

## How

Extend the existing format/link owner with a reusable bounded DOI presentation
projection. Strip supported resolver/label wrappers from the presented name;
never mutate saved records or use that projected name as a composition key.
Exercise the previously retained input with the same real publication engines.

## Why

A style engine needs a DOI name, while a human-facing link needs one resolver
URL. Original field text and caller identity serve a different purpose and must
remain intact, especially for distinct software releases or conflicting claims.

## What was refuted

Shared DOI display does not prove equal original records or interchangeable
software releases. Automatic merging would discard preserved result references
and contradict composition's same-ID conflict refusal.

## Scope and exclusions

Bare DOI names, `doi:` labels and unambiguous exact HTTP(S) doi.org/dx.doi.org
wrappers. Preserve case/punctuation; do not decode resolver URLs with escapes,
queries or fragments, guess identifiers in other URLs, resolve shortDOIs or
validate registration. JSON/saved attribution and BibTeX originals remain intact.
No new API, schema, runtime dependency, automatic alias/merge operation or release.

## Acceptance criteria

- Supported forms reach CSL as a DOI name and human reports as one resolver URL.
- Actual citeproc output has no duplicate prefix, keeping distinct IDs/releases.
- Original inputs and execution credits remain unchanged in a fresh reader.
- Same-ID equal originals share; conflicts refuse; distinct IDs remain distinct
  even when their projected DOI names match.
- Retain paired installed evidence and explicit unsupported boundaries.
