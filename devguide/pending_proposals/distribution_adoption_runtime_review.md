---
summary: Complete dependency-constraint and runtime-route review for member distribution adoption.
issue: uibcdf/ackredit#108
status: partial
opened: 2026-10-06
closed:
verification: measured
area: [packaging, integration, governance]
guard: tests/test_dependency_routes.py
normative:
blocked_by: [uibcdf/molsyssuite#105]
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

## Member-owned review, 2026-10-06

The review now covers every maintained input at source baseline `71f7f19` plus
this proposal's inventory, consumer invocation and CI quality steps. The root
metadata remains authoritative: Python `>=3.11,<3.15`, `smonitor>=0.16.0`,
`depdigest>=0.11.0`, `argdigest>=0.13.0` and `pyyaml>=6`. There is no required
Python/Conda name translation. DueCredit remains optional; build, test and docs
tools do not become runtime requirements.

| Route | Classification and reviewed behavior |
| --- | --- |
| `devtools/conda-build/meta.yaml` | One noarch artifact; run requirements retain all metadata names/floors/Python bounds. Existing shared recipe/resource/launcher checks are reused. |
| `development_env.yaml` | Complete runtime plus development/test/docs tools; routine Python 3.14 selection is a reviewed narrowing. Create with strict channel priority. |
| `test_env.yaml` | Complete runtime for ordinary/full/coverage/receiving gates; supported Python range is retained and the workflow narrows each installed cell. |
| `test_env_next.yaml` | Complete runtime for normal Python 3.14 installed validation; its historical filename does not represent an unsupported interpreter probe. |
| `docs_env.yaml` | Complete runtime because Sphinx imports installed Ackredit; CI uses Python 3.14 and strict channels. |
| `build_env.yaml` | Build/upload bootstrap only; it does not install Ackredit. The Conda recipe creates the separate build environment. |
| `CI.yaml`, `CI_full_matrix.yaml`, `coverage.yaml`, `python314_feasibility.yaml` | Conda-supplied runtime, source installation with `pip --no-deps`, outside-source installed checks and `pip check`. `CI.yaml` also runs the pinned standalone preflight after Ruff. |
| `function_provider_receiving.yaml` | Candidate/released Ackredit artifacts and exact PyUnitWizard producer `0e422d06b0af56e4dd2b43cafd00f059221eb405` are receiving fixtures. Core required Ackredit siblings remain Conda-supplied; no required sibling-source replacement is claimed. Existing artifact/receiving provenance checks retain ownership. |
| Staging, installed and promotion wrappers | Pinned shared one-file/exact-file publication operations; recipe/runtime identity and installed/public qualification retain their existing independent gates. |
| Suite/publication policy workflows | Administrative audits; no Ackredit runtime is installed by these jobs. |

All five environment files, the recipe and all ten workflows are classified in
[`devtools/dependency_routes.toml`](../../devtools/dependency_routes.toml).
Complete reviewed workflow hashes conservatively detect both new routes and
edits inside existing jobs. Updating a hash requires a renewed route review;
the checker does not interpret arbitrary shell or prove a workflow executed.
Unsupported recipe/constraint/source layouts fail for a provider-owned profile.

## Reuse, provider ownership and consumer integration

The existing shared `noarch_conda.inspect_recipe` and `required_constraints`
cover recipe/resources and exact requirements, but not the complete environment
inventory. `check_repository.py` checks acquisition names; the distribution
status tool reports adoption states. MolSysMT's auditors include local form,
controlled-source and workflow rules and are not a documented general client tool.

The missing operation was reported in
[MolSysSuite #45](https://github.com/uibcdf/molsyssuite/issues/45#issuecomment-6012850550)
before implementation. [Provider PR #105](https://github.com/uibcdf/molsyssuite/pull/105)
owns the additive `dependency_routes.audit` operation and its negative guards;
the primary MolSysSuite checkout is preserved. The proposed tool commit is
`43b9f94bf5ab0ec3f54a4b2ca5b23b791d6af0bc`. It has no automatic publisher
rollout and does not change a policy release or any member adoption state.

Ackredit's [thin consumer command](../../devtools/check_dependency_routes.py)
checks the exact provider commit and refuses modified/untracked provider tool
inputs before delegating. The CI quality job checks out that same full commit
and invokes the supported operation. Local use is:

```bash
python devtools/check_dependency_routes.py --suite-root /path/to/pinned/molsyssuite
```

The provider owns omitted-recipe, weakened-floor/ceiling, invalid-Python and
below-floor-source guards in
[its tests](https://github.com/uibcdf/molsyssuite/blob/43b9f94bf5ab0ec3f54a4b2ca5b23b791d6af0bc/tests/test_dependency_routes.py).
The local `guard` protects exact-provider selection, tamper refusal and preserved
failure exit/root forwarding. A required sibling-source route is currently
inapplicable here; its generic installed-version/provenance guards remain
provider-owned rather than fabricated as an Ackredit route.

Local Python 3.14 validation passes all 16 inventoried routes, 229 selected
consumer/packaging/workflow/reporting/documentation tests with
`pytest --receptor=llm`, Ruff 0.16.5 lint/format, generated indexes and strict
Sphinx. The provider passes 355 top-level tests and 21 focused route/recipe
tests; its final test-only lint correction reruns the focused tests under the
same pinned Ruff. These source checks do not qualify a new installed artifact.
The shared developer environment's Ruff 0.16.10 differs from the required pin;
validation used a temporary Python 3.14 environment with Ruff 0.16.5 rather than
modifying the shared environment.

## Retained delivery evidence and review limits

The intended public package route is the verified `uibcdf` Conda channel.
PyPI and Windows qualification remain unclaimed. Public 0.11.0 is the original
producer `85deae594e65b2fd443d6ca9a7347eb2bda537e1` and original noarch file,
SHA-256 `df8963ca2d286f50b19eb778e95c54c5ebb79c12fb55a6504e7c23daf5717d4f`.
Its [delivery receipt](https://github.com/uibcdf/ackredit/blob/aae9ad98c89d162b946a65fa01603707db02359a/devtools/conda-build/receipts/ackredit_0.11.0_public_2026-10-06.json)
retains exact source gates, eight installed cells, real receiving, promotion,
independent public file/index and clean installation evidence. Earlier receipts
retain their own identities. This review neither repeats nor transfers those
gates to revised package bytes.

Resource inventory, generated version, packaged CFF and console-command checks
already belong to the shared noarch route and existing packaging/release tests.
Publication access is confirmed only for the observed authorized deliveries;
future credential availability is unknown. Existing shared-environment conflicts
remain MolSysSuite #82's scope and do not become an Ackredit dependency repair.

## Remaining acceptance

- Provider-owner review and acceptance of MolSysSuite #105 are pending.
- The consumer proposal needs exact-head applicable CI and acceptance before
  its tool invocation becomes the maintained default-branch guard.
- After those steps, hand the source/input checks and retained delivery evidence
  to MolSysSuite #45 for its distinct adopted/readiness/access decisions; then
  archive this report and synchronize #108. No adopted state or closure is claimed.
