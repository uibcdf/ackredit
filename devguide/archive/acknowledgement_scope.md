---
summary: Defer non-bibliographic acknowledgements until an owned real use case justifies their contract.
issue: uibcdf/ackredit#124
status: resolved
opened: 2026-10-06
closed: 2026-10-06
severity: medium
verification: asserted
area: [product, formats, portability]
guard:
normative: devguide/roadmap.md
blocked_by: []
supersedes: []
---

# Non-bibliographic acknowledgement scope review

## What

Theme N requires an explicit maintainer decision to accept, defer or exclude
acknowledgements of people, institutions and funders. This review prepared that
decision. On 2026-10-06 the maintainer chose deferral until a real use case exists;
the outcome below records that decision without accepting the proposed contract.

## How

Inspect the implemented declaration, saved-reader, composition and presentation
owners. Compare three branches and a bounded first implementation. Keep existing
bibliographic data and compatibility promises separate from any new statements.

## Why

The original vision and public descriptions say "citation and acknowledgement
tracking". Markdown, LaTeX and notebook headings also mention acknowledgements.
Their actual content is bibliographic references and callers; those headings do
not establish a separate gratitude or funding contract. A user needs to know
whether Ackredit stores independently authored statements or only citations.

### Observed implementation boundary

| Owner | Current behavior | Consequence for this proposal |
| --- | --- | --- |
| `ackredit/core/registry.py` | Registers bibliographic records, including optional notes and arbitrary metadata. | A note on a work does not create a separate acknowledgement recipient or statement. |
| `ackredit/core/attribution.py` | Saves complete `ackredit.attribution@1` bibliography, contextual uses and graph; validates an exact envelope. | Adding a new top-level field in place would be rejected by existing readers. |
| `ackredit/core/composition.py` | Preserves original result occurrences and shares only equal same-ID bibliographic records. | Repeated result names are not identities; gratitude must not enter bibliography deduplication. |
| `ackredit/core/evidence.py` | A separate companion contains original attribution and recorder declarations per result occurrence. | Reuse this architectural pattern; its recorder-evidence planes do not mean gratitude or funding. |
| `ackredit/formats/workflow.py` | Renders detached references, original use context, graph and explicit evidence. | A distinct opted-in statement section can reuse its presentation, with existing escaping tools. |
| Markdown, LaTeX and notebook renderers | Acknowledgement-labelled headings contain only bibliographic records. | Names alone do not qualify the proposed feature; existing report behavior needs a separate wording decision. |
| CLI and canonical host guide | Portable citation/evidence readers and optional host boundaries already exist. | New input routes and host collection would need independently scoped compatibility and receiving work. |

This is source inspection, not executed acknowledgement receiving. No such
public tool or accepted acknowledgement schema currently exists.

## Options requiring a decision

| Branch | Product outcome | First delivery work |
| --- | --- | --- |
| Accept bounded explicit statements (recommended) | Callers retain and present authored gratitude or funding text alongside saved result attribution. | Specify and implement a separate portable companion and explicit Markdown workflow report; qualify a fresh-process example. |
| Defer | Ackredit continues delivering bibliography and contextual credit; acknowledgement capability stays an explicit future decision. | State the limitation in maintained guidance and record an owned user-story condition for reconsideration. |
| Exclude | Independent gratitude/funding statements belong to applications or manuscripts, outside Ackredit's product scope. | Record that boundary and review descriptive wording; preserve historical citation metadata and public compatibility. |

The recommendation follows the original vision while starting with an explicit,
offline operation. A human or application decides whether a statement applies;
Ackredit retains that declaration without interpreting it as verified funding,
authorship, contribution, observed execution or scientific success.

## Proposed accepted branch (not yet accepted)

### Concrete user stories

1. A workflow owner writes a statement thanking a facility for access and keeps
   it with the saved result. A later reader can display exactly that text without
   importing the original scientific library or adding a citation.
2. An application retains caller-supplied funding wording and a grant identifier
   in statement context. Ackredit does not consult a funder registry or certify
   the wording, award or obligation.
3. Two reused calculation results share bibliographic references but retain their
   own statements. An enclosing report does not transfer one result's declared
   support to another, even when names repeat.

### Candidate portable representation

A new companion contains a complete original `Attribution` or
`AttributionBundle`, plus declarations aligned with every original occurrence.
The following identifier and keys are review candidates, not a shipped schema:

```json
{
  "schema": "ackredit.acknowledgements@1",
  "attribution": {"schema": "ackredit.attribution@1", "...": "complete original payload"},
  "results": [
    {
      "acknowledgements": [
        {
          "id": "facility-access",
          "text": "We thank the Example Facility for access to its instruments.",
          "declared_by": "workflow-owner",
          "source": null,
          "context": {"facility": "Example Facility"}
        }
      ]
    }
  ]
}
```

The abbreviated `attribution` above illustrates placement only; an actual reader
would require the complete original validated payload. Candidate rules:

- `id`, `text` and `declared_by` are non-empty strings. Preserve original text,
  case, punctuation, Unicode and context; validation must not rewrite wording.
- `source` is a non-empty source locator string or `null` when not supplied. It
  is declaration provenance, never opened, enriched or evidence of verification.
- `context` is a JSON object for original caller claims, such as a grant ID or
  explicit target. It does not create an observed runtime use or graph edge.
- `results` has exactly one entry per original single result or bundle member,
  associated by position. Reused inputs and repeated names remain independent.
- Each saved result's declaration list has unique IDs. A construction operation
  may share equal same-ID statements but must refuse differing same-ID statements
  within that result. Different results keep their own declarations, including
  different wording under the same local ID. Do not merge by text or recipient.
- `null` means no acknowledgement declarations were supplied; `[]` means an
  explicit empty declaration list. Neither means no acknowledgement is owed.
- Acknowledgement-only results are allowed: an original attribution can have no
  bibliography or recorded uses while its companion has explicit statements.
- Reading/writing/rendering does not register works, credit a session, consult
  the current registry, emit stored diagnostics again or open scientific tools.

This avoids changing either original portable envelope, the released provider
protocol or the recorder-evidence planes. It adds no funder/person/institution
identity registry: the caller's statement ID identifies a declaration, and the
caller owns the recipient wording and metadata.

### First independently closable implementation

If the maintainer accepts this branch, specify the final public names and schema
before implementation. Implement one reusable detached companion tool in
`ackredit/core/` with construction, validated JSON read/write and explicit
workflow rendering. Reuse the portable attribution readers and JSON validation,
and render through the workflow owner and existing escaping helpers. Factor a
shared internal operation only where both actual consumers need it; do not
duplicate a portable parser or turn acknowledgement selection into a provider
feature.

The initial report presents an explicit **Acknowledgements** section per result,
separate from references, uses, graph and recorder evidence. Plain text is escaped
as data, never interpreted as Markdown/HTML/TeX instructions. Original text stays
in JSON. Unknown and explicitly empty declarations have different descriptions;
they do not infer completeness. Existing citation-only reports stay applicable.
BibTeX and CSL-JSON continue representing bibliographic works; they do not receive
fabricated acknowledgement entries. Unsupported requested exports must be
explicitly refused rather than silently dropping statements.

Choose source classification under the existing API policy; accepting this scope
does not automatically grant a stable API or public compatibility promise. A new
diagnostic must belong to Ackredit's SMonitor catalog. No new runtime dependency
or optional external engine is needed for the proposed offline route.

Meaningful gates include malformed/unknown schema refusal, exact text/context
round trips, declaration conflicts, acknowledgement-only results, per-occurrence
association and repeated inputs, escaping, inert reading, original bibliography
preservation and a normally installed fresh-process receiving example. The
application must continue to compute when optional Ackredit is absent. Local
pytest uses `--receptor=llm`; required hosted and installed gates retain their
ordinary scopes and inspect remote runs with GH Run Receptor.

### Later work requiring its own scope

Automatic or explicit runtime collection, provider declarations, session journals,
combined evidence-plus-acknowledgement input, CLI input routing, notebook display,
LaTeX/PDF and publication-tool receiving are separate operations. Do not advertise
them as implied by the first detached tool. A public release and host-guide
adoption also retain their own qualification and owners.

## What was refuted

- A role called `acknowledgement` still refers to a bibliographic item. It does
  not establish a separate statement, recipient or funding relationship.
- An item's `note`, arbitrary capture context or an existing heading is not a
  validated portable acknowledgement contract. Existing opaque context remains
  allowed, without claiming the proposed feature.
- Automatic contributor/funder inference would create claims that an observed
  library call cannot support. This proposal retains authored declarations.
- Adding fields under existing schema identifiers breaks the closed saved-reader
  contracts. A companion keeps the original payload and compatibility separate.
- Preparing or approving a review does not demonstrate executed receiving,
  stability promotion, synchronized-guide rollout or a public release.

## Scope and exclusions

This checkpoint is documentation and product review only. No implementation,
dependency, API promotion, schema adoption, existing renderer changes, public
artifact, release/tag or canonical-guide rollout. No sibling limitation or shared
suite rule has been identified; Ackredit owns the product decision. The proposal
does not block completed theme M, public 0.11.0 or the separate general 1.0 review.

## Acceptance criteria

- The maintainer explicitly accepts, defers or excludes the scope and its limits.
- The issue, review, roadmap, status and resumption checkpoint record that decision
  faithfully; only the chosen scope-decision criterion is completed under deferral.
- If accepted, finalize and implement the bounded tool and demonstrate actual
  receiving before claiming support or resolving its delivery work. Scope
  acceptance alone does not complete the implementation criteria of theme N.
- If deferred/excluded, record the rationale and revisit condition, align maintained
  guidance, then archive the decision record with its normative boundary.
- Applicable reporting/index, link, unchanged-guide and strict documentation gates
  pass. No scientific suite is required for this review-only checkpoint.

## Maintainer decision — 2026-10-06

The maintainer selected: **"Posponer los agradecimientos hasta tener un caso de
uso real."** Non-bibliographic acknowledgement support is deferred. The synthetic
stories and candidate companion above are design alternatives, not sufficient
demand to adopt a schema or build the feature. This is a deferral, not permanent
exclusion from the original vision.

Reopen scope review when an identified application/workflow owner brings an
actual result needing independent acknowledgement statements, authored example
wording and its source, intended saved/reporting route and an observable receiving
criterion. That case must establish why bibliography, existing opaque context
and application/manuscript text are insufficient. Revisit the proposed design
against that evidence rather than treating these draft names/keys as accepted.

Until then Ackredit delivers bibliographic attribution and contextual use;
acknowledgement-labelled headings do not store separate gratitude/funding records.
Applications and manuscript authors retain their own authored statements. No new
API, schema, collection, renderer, dependency or compatibility promise follows.
Existing bibliography metadata, optional host behavior, public 0.11.0 and its
historical citation text remain unchanged. No release is authorized by this scope
decision. Theme N's implementation and receiving criteria remain conditional on
a future accepted use case, not required work for the current product or 1.0.

The normative boundary is maintained in theme N of `devguide/roadmap.md` and
decision 19 of `devguide/decisions.md`; user-facing reporting and product guidance
state the current limitation. Archive this review and close #124 as the completed
scope decision, rather than claiming feature delivery.

## Documentation checkpoint validation

Python 3.14.7 local validation passes 261 selected reporting, documented API,
stability, integration-guide, devguide-claim and documentation tests with
`--receptor=llm`. Ruff lint/format, generated indexes, whitespace and local
MolSysSuite conformance pass. A fresh strict Sphinx HTML build passes with
warnings treated as errors; the first restricted-network attempt could not
fetch Python's intersphinx inventory, and the permitted networked build supplies
that external inventory successfully. Consumed synchronized guides are unchanged.
No executable/scientific input changed, so this documentation gate does not
repeat a scientific suite or establish acknowledgement receiving. The owning
issue retains exact final-commit hosted results before closure.
