---
summary: Join bounded recorder declarations with original workflow bibliography and uses on explicit request.
issue: uibcdf/ackredit#106
status: active
opened: 2026-10-05
closed:
severity: medium
verification: asserted
area: [portability, reporting]
guard: tests/test_workflow_evidence.py
normative:
blocked_by: []
supersedes: []
---

# Workflow recorder evidence

## What

Roadmap J has an actual provider collector under #105, but the workflow narrative
still delegates to the original attribution and omits companion declarations.
Users need an explicitly requested report joining those bounded facts with the
original bibliography, contextual uses and independent result graphs.

## How

Extend the owning workflow renderer and provisional evidence reader with
`report("workflow", include_evidence=True)`. Add the equivalent saved-evidence
CLI flag. Number shared references once and keep each original occurrence's
declarations separate, including reused names, repeated inputs and empty members.
Render field-source declarations beside their reference numbers, observation
boundaries with their declared statuses, and owning recording diagnostic identities.

## Why

The user should be able to inspect the calculation and its attribution limits
without reconciling two separate reports or confusing selected functions with
observed calls. Source locators and recorder identities must remain inert and
retain the producer's original versions.

## What was refuted

Changing report defaults, merging declarations across result occurrences,
inferring missing citations from unknown origins, checking source locators or
replaying stored diagnostics would break the existing bounded interpretation.
A separate rendering stack would duplicate the owning workflow operation.

## Scope and exclusions

Only explicitly requested workflow rendering and its inert reader/CLI are added.
Default workflow and all portable schemas remain unchanged. Other recorders,
stable promotion and public delivery retain their own review/qualification.
No sibling source changes; MolSysSuite #97 and MOLI #46 own shared review.

## Acceptance criteria

- Defaults stay byte-identical; single/bundle/reused/empty inputs retain original
  bibliography, versions, use roles and independent graphs.
- Unknown planes, empty declarations and positive facts remain distinct; selected
  or unsupported/unobserved boundaries do not imply execution or science status.
- Multiple partial field sources and per-result diagnostic identities survive
  safely escaped Markdown without chronology, call counts or coverage scores.
- Invalid option/input combinations fail through existing catalog diagnostics
  before reading/aggregating a live journal or overwriting an input.
- Fresh library/CLI readers add no credits, import no producer/engine, access no
  network and emit no prior diagnostics; real installed receiving checks qualify
  the actual candidate and applicable exact-head controls.

## Source checkpoint — 2026-10-06

Python 3.14.7 passes all 2,073 source tests without skips. Focused reporting,
companion, CLI and qualification-contract checks pass 127 tests. Ruff check/format,
generated indexes, whitespace and strict nitpicky Sphinx pass. The option rejects
invalid input/output combinations through `ACKREDIT-E016` before journal reading;
fresh readers retain input bytes and original reports, escape external declarations,
add no credits and replay no stored diagnostics. Initial test-only parametrization
and table-column assertions were corrected before the complete gate.

The ninth real receiving case now compares the integrated library report with a
fresh offline CLI export, while retaining the original default report identically.
The aggregate requires both new integrated report files. Old #105 files remain
qualification of their original scope. Normal-installed exact-candidate receiving
and hosted controls remain pending; this source checkpoint cannot qualify them.
