---
summary: Complete dependency-constraint and runtime-route review for member distribution adoption.
issue: uibcdf/ackredit#108
status: open
opened: 2026-10-06
closed:
verification: upstream
area: [packaging, integration, governance]
guard:
normative:
blocked_by: []
supersedes: []
---

# Distribution adoption and runtime-route review

## What

Complete Ackredit's formal member-owned distribution review under MolSysSuite #45.
Public deliveries #22/#93/#94/#107 are complete and remain separate evidence.
The remaining review concerns protecting dependency constraints and actual
source/runtime routes when future environment or metadata inputs change.

## How

Inspect existing maintained shared preflights before proposing implementation.
Inventory runtime metadata, recipe, every development/test/docs/next environment
and actual CI/source install route. Compare dependency names, floors/ceilings
and Python bounds; classify build-only and inapplicable source routes explicitly.
Identify an equivalent existing operation or report missing reusable capability
in MolSysSuite #45 before duplicating it locally. Add meaningful negative guards
for missing recipe requirements, weakened runtime constraints and below-floor
source candidates where applicable in the owning module/component.

## Why

Central inspection recorded in #108 verifies original public 0.10.1 source,
producer, eight installed cells, source gates, metadata/resources and public
file/access, while finding no maintained guard for all environment constraints
and actual source routes. That diagnosis is upstream evidence, not a local
completed tool audit. Current Ackredit 0.11.0 has its own exact-file/source/
installed/receiving/public receipt and does not automatically finish this review.

## What was refuted

An artifact receipt alone cannot guard a later weakened environment constraint.
Another build, upload, promotion or release is not requested. A global scientific
suite on every internal push is not the acceptance criterion. Current shared
environment conflicts belong to MolSysSuite #82 and do not invalidate the
separate clean public Ackredit installation.

## Scope and exclusions

Member distribution-policy adoption and maintained dependency/source inputs.
No PyPI or Windows claim, stable API adoption, secret-access guarantee, sibling
source edit, public archive replacement or reopening of completed deliveries.
Source, recipe/CI readiness, public access and formal adoption retain distinct states.

## Acceptance criteria

- Identify/reuse a maintained check or obtain the missing provider-owned capability.
- Cover metadata/recipe/runtime environments and applicable source routes with
  reviewed constraint comparisons and meaningful negative guards.
- Retain exact producer/archive/installed/public evidence separately from current
  source-input checks; qualify a changed boundary with its applicable gates.
- Record the completed whole-policy review with its durable guard/normative
  references and hand adoption/readiness/access results to MolSysSuite #45.

This incoming proposal is recorded for resumption. No implementation or formal
adoption completion is claimed by preparing the checkpoint.
