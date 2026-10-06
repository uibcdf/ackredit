---
summary: Project supported DOI wrappers for display while preserving original ID identity.
issue: uibcdf/ackredit#121
status: resolved
opened: 2026-10-06
closed: 2026-10-06
severity: medium
verification: reproduced
area: [formats, attribution]
guard: tests/test_doi_presentation.py
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

## Executed correction (2026-10-06)

The existing `ackredit.formats._links` owner now provides private reusable
`doi_name` and `doi_link` operations. CSL export, Markdown, workflow DOI labels
and notebook links consume them. Only a supported wrapper and outer whitespace
are projected away; case and identifier punctuation are retained. Unknown and
ambiguous values keep the prior fallback, rather than being silently repaired.
BibTeX rendering and composition implementation are unchanged.

The baseline is the original normally installed #120 candidate
`0.11.0+22.g9efa863`. The corrected clean source is
`c39b1fc492a469dd136d1840d942fe870ca612f0`, normally installed as
`ackredit-0.11.0+25.gc39b1fc-py3-none-any.whl`, SHA-256
`ece4aa401f60b15725c135431f7510a04c8f0b6bbad25d64a500da27928499be`.
Its separate native clone keeps public SMonitor 0.19.0 / ArgDigest 0.15.0 and
Python 3.14.8; every original shipped package file is verified before/after tests.

The same six-record attribution bytes and identical engines/styles/probe tool
feed the paired before/after study. The CSL record for `software:2.0` changes
only its presented DOI from a resolver URL to the original name. Citeproc now
prints one prefix. All IDs and versions survive, and the exported BibTeX and
BibTeX bibliography output are byte-identical. Actual bundle composition keeps
two original members and six distinct references, including both software
releases. A same-ID original with a different DOI spelling refuses with existing
catalog code `ACKREDIT-E011`. Source, original input, exported records, style and
engine identities, reader/composition output and receiving proof are retained in
[`doi_presentation_121_2026-10-06.json`](../../devtools/receipts/doi_presentation_121_2026-10-06.json).

**278 selected normally installed tests** pass with
`--receptor=llm --require-publication-tools` outside the checkout. They cover
supported/unsupported DOI forms, saved/JSON/BibTeX fidelity, human report escaping,
composition identity, actual publication engines, startup boundaries and suite
isolation. `pip check` and unchanged installed file identities pass. The later
receipt guard and final documentation gates are separate from that selection.

The final source/documentation selection passes **307 tests**, including the
receipt guard, reporting contracts and real publication tools. It overlaps the
installed selection and is not an additional disjoint test count. Ruff lint and
format, generated indexes, pinned dependency-route preflight, local suite
conformance, strict Sphinx and whitespace checks pass. Hosted gates for the final
head are recorded in the owning issue before closure.

The guard protects the actual mechanism: CSL has a name, human links have one
resolver, and original records still conflict or remain distinct by their IDs.
Neither numerical scientific equivalence nor reference-manager import follows
from this bibliography checkpoint. Public 0.11.0 bytes remain unchanged and lack
both #120 and #121 repairs; future delivery needs its own qualification.

## Explicit identity decision

Retain the existing conservative policy rather than introducing automatic DOI
aliases. Caller IDs remain authoritative; exact equal originals under one ID
share, conflicting originals under one ID refuse, and different IDs remain
distinct even if the presented DOI matches. This closes theme M's identity-policy
decision within those limits, not its remaining engine/manager coverage.
Additional alias/merge tooling needs a concrete user story and separate contract.
