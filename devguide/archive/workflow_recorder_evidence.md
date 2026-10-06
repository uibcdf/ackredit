---
summary: Join bounded recorder declarations with original workflow bibliography and uses on explicit request.
issue: uibcdf/ackredit#106
status: resolved
opened: 2026-10-05
closed: 2026-10-06
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

## Normal installed checkpoint — 2026-10-06

Clean producer `9ca7157323d816925da99560dc4ef68b604396ed` builds once in
normal isolation: `ackredit-0.10.1+20.g9ca7157-py3-none-any.whl`, SHA-256
`52db9e95e85d5ae5344201c86833853f0a5faa566787a295fdaf4a03cbec08c7`.
Ackredit and pinned PyUnitWizard `0e422d0` are normally installed outside every
checkout. The owning archive/installed verifier checks all 70 candidate files,
runtime/distribution identity and origins; `pip check` passes. The temporary
Linux/Python 3.14.7 environment reuses the shared dependency foundation and real
Pint/unyt, not a fresh Conda solve.

All nine designated receiving cases execute and pass without skips, including
original defaults, actual opt-in recorder origins, intentionally injected gap,
empty/reused captures, released fallback and optional absence. The fresh offline
reader exports the integrated workflow byte-identically through library and CLI,
with zero producer/engine imports, network attempts, new credits or diagnostic
replay. The original report and saved companion remain unchanged. The
[local receipt](../../devtools/receipts/workflow_recorder_evidence_106_2026-10-06.json)
retains exact sources/packages, complete receptor streams and every proof hash.
The installed eight-cell hosted matrix and final-head source/policy controls
remain separate pending checks. Prior files and receipts retain their identity.

## Hosted qualification and closure — 2026-10-06

Unskipped qualification head `30c622b321250b269530eff67758adafb481d66f`
passes all seven ordinary CI jobs in 37421917342, suite policy 37421917506 and
publication policy 37421917442. GH Run Receptor verifies their executed success.
Receiving run [37421954520](https://github.com/uibcdf/ackredit/actions/runs/37421954520)
passes all ten jobs: eight Linux/macOS arm64 × Python 3.11–3.14 installed cells,
nine designated tests per cell, 72 passed and no skips/deselections. Every cell
retains both integrated report files and confirms fresh CLI/library equality
with the original workflow default unchanged and no new credits/diagnostics.

The original hosted wheel is `ackredit-0.10.1+20.g9ca7157-py3-none-any.whl`,
SHA-256 `95aefd46963917f1fcbd026a355bb42df2f63431a756732c0b43ae03ed5699da`,
from the original clean `9ca7157` producer. It is built once and the same archive
goes to all hosted cells. The separate local build keeps its different digest
above; their complete 70-file package maps match, without relabelling archives.
All ten original GitHub ZIP digests and extracted bytes verify independently;
the owning aggregate reproduces the hosted result exactly. The
[hosted receipt](../../devtools/receipts/workflow_recorder_evidence_hosted_106_2026-10-06.json)
retains the original source/file, eight cells, every reader proof and artifact/file
hashes. The earlier local receipt remains historical.

This resolves only the explicitly requested integrated workflow presentation.
Other recorder origins, non-bibliographic acknowledgement decisions, platform
object boundaries, public delivery and final stability review retain their own
scope. Existing provisional contracts remain provisional; shared review stays
in MolSysSuite #97 and MOLI #46.
