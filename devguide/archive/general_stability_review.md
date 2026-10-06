---
summary: Accept the bounded general 1.x source commitment and promote standalone provider validation.
issue: uibcdf/ackredit#125
status: resolved
opened: 2026-10-06
closed: 2026-10-06
severity: medium
verification: reproduced
area: [api, compatibility, integration]
guard: tests/test_provider_validation.py::test_empty_role_list_keeps_unspecified_use_through_validation_and_saved_report
normative: docs/content/about/stability.md
blocked_by: []
supersedes: []
---

# General 1.0 stability contract review

## What

Theme F requires a final review against actual adoption before the general 1.0
commitment. This review maps the implemented contracts to receiving evidence and
prepared two explicit decisions: accept the general stable surface's bounded
1.x commitment, and promote or retain the remaining provisional validator.
The maintainer explicitly accepted both proposed contracts on 2026-10-06,
as recorded below. No release/version/tag or publication is authorized by these
source decisions.

## How

Use `docs/content/about/stability.md` as the authoritative Python classification
inventory, with `ackredit.__all__` and its addressable guards. Review documented
members of exported classes, saved representations, CLI/report semantics and
extension contracts separately from private implementation. Reuse original
receiving records for their exact historical files and execute current scoped
guards for this source; do not convert either into new public qualification.

## Why

Actual PyUnitWizard and Sabueso workflows exercise session ownership, independent
result capture, original metadata, failure/absence and later offline reading.
Saved-result composition, recorder evidence and real publication receiving add
boundaries that a list of tested names alone cannot explain. The current roadmap
also refuses provisional exports at 1.0: `validate_provider` needs its own explicit
decision rather than being swept into the general promise.

## General decision accepted on 2026-10-06

Accept the currently documented stable Python signatures and meanings for future
1.x. Include documented operations of exported classes and keep saved-schema,
report/CLI and extension meanings at their explicitly reviewed boundaries below.
Apply the existing major-release removal rule and at least two minor releases of
catalog-driven deprecation before incompatible removal or behavior changes.
Compatible additive options and internal optimizations remain possible.

The general public promise begins with a separately authorized, qualified public
1.0.0 delivery. Before then general stable classifications remain source intent,
except existing bounded portable/provider promises and separately accepted
evidence/validator promises from their own delivering releases. A source decision
does not retroactively rewrite public 0.11.0, authorize a release or establish
consumer adoption. Do not tag 1.0 while any export remains provisional.

### Adoption-informed contract map

| Contract family and public surface | Proposed retained meaning | Evidence and durable guards | Explicit limits |
| --- | --- | --- | --- |
| Declarations: `register_item`, `bind`, `bound_items`, `add_injection`, `load_bibtex` | Declare potential bibliographic work and associations; declaration alone is not observed execution. Preserve original versions and source-field handling. | Real provider declarations and optional clients; `tests/test_function_providers.py`, `tests/test_integration_guide.py`, `tests/test_bibtex_load.py`. | Producer metadata is a claim; no citation/scientific correctness certification. Registry replacement is not a portable-result identity policy. |
| Session and scope: `Session`, `session`, `current_session`, `scope`, `scoped_usage`, `track_target` | Application owns the session; explicit isolated sessions and context-local scopes remain independent. `Session` keeps its documented read fields and `clear()` operation. | PyUnitWizard/Sabueso integration; `tests/test_session_contract.py`, `tests/test_session_isolation.py`, `tests/test_session_sharing.py`. | No inferred scientific completion, chronology or shared multi-process scientific state. Private writers/locks are not public APIs. |
| Observed credit: `track_item`, `credit_bound`, `get_used_items`, `prepare_credit`, `observe_calls` | Explicit reached branches and bounded observer entry; prepared callable credits only when invoked at the host-owned completion boundary. Current session and each active capture receive reused references. | #84/#87/#99 real prepared/observer receiving; `tests/test_prepared_credit.py`, `tests/test_function_providers.py`, `tests/test_provider_lifecycle.py`. | Observer aliases/generators/native internals and automatic thread inheritance remain excluded. Entry is not completion; warning-as-error policy belongs to the application. |
| Saved attribution: `Attribution`, `capture`, `get_attribution` | Complete detached originals, roles/context and graph; independent captures retain reused references without replacing the enclosing session. Validated from/to dict/JSON and reporting are inert. | #75 two-client review and #107 public installed/receiving; `tests/test_attribution_capture.py`, `tests/test_attribution_contract.py`, `tests/test_integration_guide.py`. | No invocation counters, universal instrumentation, producer reimport, automatic enrichment or new credit from reading. |
| Composition/explanation: `AttributionBundle`, `compose_attributions`, `explain_attribution` | Preserve independent original occurrences/graphs, share only equal same-ID bibliography, refuse conflicts; explanations describe recorded and unknown information. | #102 eight installed cells and original receipt; #103 saved-reader evidence; `tests/test_attribution_bundle.py`, `tests/test_attribution_explanation.py`. | Repeated names are not identity. Do not merge graphs, equate different software releases or turn unknown scope into completeness. |
| Evidence: `AttributionEvidence`, opt-in capture `.evidence` and explicit workflow/CLI presentation | Retain #114's accepted positional original-occurrence association, closed schema/enumerations, unknown/empty distinction, bounded positive provider facts and inert/default readers. | Original #104–#106 representation/real receiving; accepted #114 saved #106 fixture and lifecycle guards; `tests/test_attribution_evidence.py`, `tests/test_provider_evidence.py`, `tests/test_workflow_evidence.py`. | Other recorder origins remain unknown. Source/diagnostic identities are declarations, not authentication; existing public 0.11.0 retains its original provisional evidence classification. |
| Output/extension: `report`, `dump`, `available_formats`, `register_format`, `summary`, `compile_pdf` | Preserve documented selected formats, content association, escaped data, detached plugin inputs and refusal of unknown/taken names. PDF runs only when requested with selected available tooling; notebook/string views retain their meanings. | #120–#123 actual style/manager routes; `tests/test_report_formats.py`, `tests/test_format_plugins.py`, `tests/test_optional_surface.py`, `tests/test_workflow_report.py`. | Cosmetic whitespace/style output is not frozen universally. Other managers/journal styles/versions/platforms remain unqualified; a bibliography export is distinct from the complete saved result. |
| Persistence/discovery: `enable_persistence`, `close_persistence`, `aggregate`, `load_plugins`, `enable_import_hooks`, `disable_import_hooks`, `auto_track_calls` | Keep documented journal lifecycle/read compatibility and optional discovery behavior. Imports/static inspection stay coarse opt-in observations; broken plugins retain diagnostics and other usable formats. | Earlier lifecycle/extension repairs and installed plugin checkpoint #117; `tests/test_persistence_cost.py`, `tests/test_citation_plugins.py`, `tests/test_installed_plugins.py`, `tests/test_format_plugins.py`. | No automatic precise branch profiling, remote shared session, completeness or plugin cost guarantee. DepDigest #31 owns reusable discovery/freshness proposals. |
| Optional utilities: `enable_auto_reminder`, `disable_auto_reminder`, `enrich_all`, `export_to_duecredit`, `dependency_info`, `__version__` | Keep explicit opt-in reminder/enrichment, adapter-owned DueCredit translation, versioned dependency information and matching runtime/distribution identity. | Original optional-surface/API/packaging review and #107 clean public installation; `tests/test_optional_surface.py`, `tests/test_api_stability.py`, `tests/test_packaging.py`. | Optional engines and network failures retain their own ownership; table rendering and remote metadata availability are not a universal frozen-byte/service guarantee. |

The stability table remains the single source for classifications and counts.
This grouped map does not promote an unlisted export or private module. Documented
class members and versioned file/plugin/CLI contracts are separate from top-level
exports; private helper names and internals remain changeable.

### Saved and provider protocol boundaries

- `ackredit.session@1`: later Ackredit readers retain supported historic session
  forms, including the older whole-document representation. An older journal
  reader may skip unknown events/torn final lines; forward semantic compatibility
  with unknown future formats is not promised.
- `ackredit.attribution@1`: retain the released closed fields and interpretation;
  unknown schemas are refused. Its reviewed portable operations have their
  bounded public promise from 0.9.0. JSON whitespace/key order is not a guarantee.
- `ackredit.provider@1`: retain the bounded declaration interpretation delivered
  in 0.11.0, original software/version, local references and module/function
  agreement. Roles may be unspecified (`[]`); supplied names are non-empty.
- `ackredit.attribution_bundle@1` and saved explanation/evidence identifiers:
  retain their documented complete-original and descriptive meanings. Closed
  fields/enumerations cannot acquire incompatible interpretations under the same
  identifier. Availability and any pre-1.0 forward promise follow their own
  published/classification records, not the existence of this review.
- Report/CLI operations retain explicit input selection and default behavior;
  complete portable envelopes remain distinct from bibliography-only exports.
  #114's evidence input/inclusion combinations preserve their accepted limits.

For incompatible structure or meaning use a new schema identifier and keep
released readers supported. Source classification cannot substitute for the
installed-file and receiving qualification of a future delivering candidate.

## Validator decision accepted on 2026-10-06

Accept promotion of the existing `validate_provider(module: ModuleType) -> dict`
with the following exact boundary. Its shape was introduced in #111 and exercised
through the independently installed dependency-free author example in #113;
neither source integration nor example success made it stable automatically.

| Property | Proposed retained contract | Guard |
| --- | --- | --- |
| Input | One already imported trusted ordinary module object; no import-name discovery or custom module subclass. | `tests/test_provider_validation.py` |
| Output | A fresh detached JSON-compatible `ackredit.provider@1` declaration: original software identity, all local items and merged module/direct-function declarations. Preserve role order/duplicates so returned metadata can still agree with function metadata; JSON-compatible tuples become lists. | `test_return_is_detached_and_validation_reads_changed_metadata`, `test_function_only_declaration_is_merged_and_can_be_reused` |
| Fresh reads | Each call reads current declarations; prior output mutation cannot alter the producer or validation of later edits. | `test_return_is_detached_and_validation_reads_changed_metadata` |
| Refusal | Invalid declarations raise catalog `ACKREDIT-E012` as a `ValueError`, not a partial success return; same parser acceptance/refusal as activation. | `test_validator_and_observer_refuse_the_same_input_without_mutating_state` |
| Ackredit-owned effects | No scientific function execution, reference registration, use credit, capture/evidence collection, export wrapping, observer lease change or DOI query. | `test_validating_does_not_activate_credit_registry_or_wrappers`, `test_active_observer_and_capture_are_unchanged` |
| Lazy exports | Resolve only explicitly declared missing exports; selected producer loaders retain their normal caching/import effects and diagnosed failures. | `test_only_explicit_lazy_exports_are_resolved`, `test_lazy_resolution_failure_is_diagnosed` |
| Unspecified roles | Retain `roles=[]` through validation, actual observed entry and a saved report; do not invent a relationship. | `test_empty_role_list_keeps_unspecified_use_through_validation_and_saved_report` |
| Registry/science boundary | Successful preflight does not promise registry compatibility, actual calls, scientific correctness, valid DOI/metadata truth or rollback of producer-owned side effects. | `test_registry_conflict_is_separate_from_declaration_validation`; installed example guard in `tests/test_function_providers.py` |

All short guard names above belong to `tests/test_provider_validation.py`. Shared
parser reuse remains in `ackredit/core/providers.py`; no downstream parser fork,
new module sweep, provider/schema reinterpretation or engine dependency is needed.

If promoted, the bounded forward promise begins with the first separately
qualified public release delivering the acceptance, including remaining pre-1.0
patch/minor releases and 1.x. Use the existing deprecation/removal policy from that
delivery. Public 0.11.0 lacks this export; do not name it as a validator minimum.
Promotion needs classification, docstring/guidance, development release notes and
canonical host-guide notice, with consumer copies synchronized centrally.

Alternatives are to retain the validator as provisional and postpone 1.0 pending
promotion/removal, or explicitly choose removal with its own scoped implementation.
Do not silently exempt a provisional export from the accepted roadmap rule.

## Evidence identity and limits

- Public 0.11.0's original producer is
  `85deae594e65b2fd443d6ca9a7347eb2bda537e1`; the immutable
  `ackredit-0.11.0-py_0.tar.bz2` has SHA-256
  `df8963ca2d286f50b19eb778e95c54c5ebb79c12fb55a6504e7c23daf5717d4f`.
  #107's receipt retains eight installed Linux/macOS arm64 × Python 3.11–3.14
  cells, 72 real receiving tests and independent public Linux installation.
- Original #102/#104–#106 and #114 receipts retain separate source/artifact and
  saved-reader identities. Their evidence does not qualify a new 1.0 candidate.
- #111 implements the validator and #113 supplies its normal installed author
  example. Those checkpoints establish a bounded author operation, not all
  external libraries or a newly published validator release.
- #120–#123 reuse their original fixture and selected installed development
  candidate for actual BibTeX/Pandoc, BibLaTeX/Biber and JabRef routes. Their
  metadata preservation and selected presentation limits do not cover arbitrary
  managers, GUI workflows or journal styles.
- SMonitor #36 retains the provider-owned argument-repr emission limitation.
  Selected lazy-loader failures preserve E012 in the validator guards; no
  universal emission/rollback guarantee under arbitrary producer behavior is
  inferred. Optional-host applications own diagnosed attribution-failure handling.

Historical receipts remain unchanged. Current test results support this source
review; they do not replace full candidate release gates, add Windows support,
certify scientific equivalence or force every client to adopt a provider feature.

## Review correction

The concise author guide incorrectly required a non-empty role list. The existing
shared parser allows `[]`, meaning an unspecified role, while requiring every
supplied role name to be non-empty. Guidance is corrected to match that existing
contract. The new guard checks inert validation, detached return mutation,
actual entry credit, original empty roles and saved-report unknown presentation
without changing the session on read. No executable parser change is needed.

## What was refuted

- Test-name references alone are not complete contract or scientific coverage.
  The current API inventory check is administrative; the receiving map and actual
  lifecycle/content assertions supply the relevant evidence and limits.
- General stable intent does not retroactively extend public pre-1.0 promises.
  Acceptance and exact-file public delivery retain separate identities.
- A provisional validator cannot enter 1.0 through a general approval that never
  decides its input/return/side-effect boundaries.
- Full roadmap completion, every client release, optional managers/journals,
  broad recorder collection or acknowledgements are not blanket prerequisites.
  Theme N's deliberate deferral under #124 remains accepted.
- Metadata/capture observations do not establish scientific truth, complete
  instrumentation or authored gratitude/funding.

## Scope and exclusions

Source review, narrowly related documentation correction and a meaningful existing
provider-contract guard. No new API shape, executable parser behavior, dependency,
engine, public artifact, version/tag, release, sibling source or copied guide
change. The accepted decision changes source classification and docstrings/guidance,
preserving executable behavior and existing public minimums. Ackredit owns this
product review; MolSysSuite #97/MOLI #46 retain shared-guide/platform/client ownership.

## Acceptance criteria

- The maintainer explicitly accepts/amends/defers the general 1.x source decision
  and separately promotes/retains/removes the validator under the stated boundary.
- Maintain the chosen decision consistently in stability/compatibility guidance,
  roadmap, status, decisions, checkpoint and any affected development release notes.
  Scope acceptance is not publication authorization.
- Map owning modules/contracts to original receiving evidence and current scoped
  guards, keeping historic identities and unqualified scope explicit.
- Correct the empty-role guidance and execute its lifecycle/saved-reader guard.
- Applicable local contract/code, lint/format, index/guide and strict docs checks
  pass; record final-head hosted results inspected with GH Run Receptor.
- Before a future release, separately authorize concrete version/scope and execute
  exact-source, installed-file, real receiving and public verification gates.
  Archive this record only once the review's decisions are explicitly resolved.

## Explicit accepted outcome — 2026-10-06

The maintainer separately selected **accept the bounded 1.x commitment** and
**promote the bounded validator contract**. Both exact guarantees and exclusions
above are accepted source contracts. The general public promise begins with a
future separately authorized, qualified public 1.0.0. The validator's bounded
forward promise begins with its first separately qualified delivering release,
including subsequent pre-1.0 and 1.x patch/minor versions. No version is selected
and no tag/publication is authorized. Public 0.11.0 and historical receiving
artifacts retain their original bytes and classifications.

The stability table and validator docstring implement the promotion. General and
validator compatibility guidance, development release notes, decisions, roadmap,
status, checkpoint and Ackredit's owned canonical host guide record the two
boundaries. No provisional export remains in the current source inventory; future
exports still require their own classification. This completes theme F's final
adoption-informed source review, not public 1.0 qualification. Optional-client
absence/failure, private ownership and existing schemas remain unchanged.

Pre-publication impact notices are retained in
[MolSysSuite #97](https://github.com/uibcdf/molsyssuite/issues/97#issuecomment-6027174042)
and [MOLI #46](https://github.com/uibcdf/moli/issues/46#issuecomment-6027182825).
Their owners retain canonical-copy synchronization and client adoption. No
sibling source or synchronized consumer guide is repaired here.

The new empty-role guard protects the review's actual prose defect: inert
preflight and real observer entry keep the declared empty roles, detach returned
metadata, and render the saved unknown role without adding session credit on
read. It does not tighten the shared parser or certify scientific semantics.

## Current decision validation

Final local Python 3.14.7 source/contract/documentation selection passes **862
tests**, without skips or warnings, using `--receptor=llm`. The selection covers
the contract families above, including the current normally installed
dependency-free author example, provider lifecycle, saved evidence, public API,
reporting, guide and package-resource guards. The pre-acceptance review selection
passed 861 cases; promoting the validator adds its stable-name inventory case.
That administrative case is separate from its actual lifecycle/content guards.

The **25 validator tests** separately pass outside the checkout on Python 3.14.8
against the preserved normally installed #121 development wheel
`ackredit-0.11.0+25.gc39b1fc-py3-none-any.whl`, SHA-256
`ece4aa401f60b15725c135431f7510a04c8f0b6bbad25d64a500da27928499be`.
Original installed identities verify after validation. This selection overlaps
the source selection and demonstrates the unchanged operation; it is not a
delivering artifact or additive test total.

All 68 tracked package Python modules have identical executable ASTs, after
removing docstrings, against baseline
`71bed3ef2af409a2d03b2a1098ba0676f941a2e5`. Only the provider validator docstring
changes in package code. Generated local version files are outside this tracked
source comparison. Ruff lint/format, generated indexes, whitespace, local suite
conformance and a fresh strict Sphinx HTML build pass. Consumed synchronized
guides and historical receipts are unchanged; the owned canonical Ackredit guide
has its announced source update. Final exact-head hosted evidence is recorded in
the owning issue before closure. These source checks do not qualify public 1.0.
