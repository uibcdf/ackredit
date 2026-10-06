# Recorder evidence contract review

This is the **proposal awaiting principal-maintainer decision** under
[Ackredit #114](https://github.com/uibcdf/ackredit/issues/114), prepared on
2026-10-06 after #113. Coordination belongs to MolSysSuite #97 and MOLI #46.
It covers three separately decidable surfaces. Their public 0.11.0
classification remains provisional; the accepted provider decision excludes them.

## Recommendation and decision choices

Accept the existing bounded representation, provider-observer collector and
explicit integrated presentation together, preserving the guarantees below.
Their receiving evidence and supplementary guards support that scope. Additional
recorder integration need not precede acceptance; it requires a concrete owning
use case. General 1.0 acceptance and platform object boundaries remain separate.

| Surface | Recommended decision | Meaning to preserve |
| --- | --- | --- |
| `AttributionEvidence` | Accept bounded stable source contract | Complete detached originals, positional declarations, closed versioned envelope, unknown/empty distinction and inert readers. |
| `capture(record_evidence=True)` / `.evidence` | Accept bounded provider-observer collection | Active overlapping captures in the same session retain positive selection/origin/diagnostic facts; default captures allocate no collector and other recorder origins remain unknown. |
| Integrated workflow reporting and explicit CLI options | Accept bounded opt-in presentation | Original reference numbering, bibliography, versions, roles and graph retain their meaning; declarations stay beside their own original occurrence; defaults and offline reading remain unchanged. |

The maintainer can accept any subset, amend a specific guarantee, or defer a
surface with its unresolved reason. This recommendation is neither that decision
nor a release authorization. Retain provisional classifications until the
explicit outcome is recorded in #114 and the decision log. Do not infer approval
from green tests or from the earlier provider acceptance.

## Representation and reading

The proposed saved envelope is `ackredit.attribution_evidence@1`, containing
exactly `schema`, `attribution` and `results`. `attribution` is a complete original
`ackredit.attribution@1` or `ackredit.attribution_bundle@1`, separately readable
through its own existing contract. The companion is not a replacement original.
`explain()` uses `ackredit.attribution_evidence_explanation@1` to separate the
existing descriptive attribution view from these recorder declarations.

| Guarantee | Proposed boundary | Durable guard |
| --- | --- | --- |
| Original occurrence association | Exactly one result entry per original, including repeated names/inputs; an empty bundle has zero entries. Position is the association. Reordering originals requires reordering their declarations. | `tests/test_attribution_evidence.py::test_reused_names_empty_members_and_order_keep_separate_declarations` |
| Detached originals and declarations | Construction validates and detaches inputs; returned originals, dictionaries and explanations are fresh detached objects. Reading and rendering create no credit. | `tests/test_attribution_evidence.py::test_payload_properties_and_explanation_are_deeply_detached` |
| Unknown versus empty | Each result has exactly `metadata_origins`, `observation_scope` and `recording_gaps`. `null` means unrecorded; `[]` means no declarations supplied. Neither certifies completeness or absence of failures/citable work. | `tests/test_attribution_evidence.py::test_unknown_empty_and_partial_planes_never_establish_completeness` |
| Local field sources | Origins name an item and unique non-empty retained fields in that original, a declared method/source and recorder. Multiple sources and repeated declarations remain separate without choosing a winner or chronology. | `tests/test_attribution_evidence.py::test_invalid_or_dangling_declarations_are_catalog_refused` and `test_multiple_field_sources_do_not_credit_a_reference_or_invent_chronology` |
| Instrumentation declarations | Scope has boundary, mechanism, status and recorder; `selected`, `unsupported` and `unobserved` are declarations, independent of a graph node. Selection does not assert entry or scientific success. | `tests/test_attribution_evidence.py::test_round_trip_preserves_sources_scope_and_failure_without_new_uses` |
| Diagnosed recording gaps | Retain boundary, diagnostic owner/code and recorder without replaying the diagnostic, inventing lost references or deciding scientific completion. Gaps may be recorded while scope is unknown. | `tests/test_workflow_evidence.py::test_unknown_empty_and_gap_only_planes_remain_distinct` |
| Closed schemas | Unknown identifiers, extra/missing keys, invalid enums, wrong result cardinality and dangling field references are refused with E016; original reader errors keep their original identities. | `tests/test_attribution_evidence.py::test_invalid_or_dangling_declarations_are_catalog_refused` |

Freeze the current field sets and accepted enumerations for schema 1 as specified
in the [user guide](../docs/content/user_guide/attribution_evidence.md). Later
readers retain their interpretation; incompatible structural/meaning changes
require a new identifier. Adding an enum value or envelope field that an existing
closed reader refuses needs explicit versioning review. Compatible additional API
options may remain possible without silently changing saved meanings.

Recorder identities, source locators and diagnostic identities are producer
claims. Readers neither open locators nor authenticate those identities.
Positional validation checks cardinality and local references; it cannot detect
a dishonest swap between originals with compatible bibliography. Producers own
association truth. The declared origin of metadata establishes neither execution
nor bibliographic/scientific correctness.

## Collector ownership and failure boundary

Only the provider observer currently owns automatic recorder collection. Existing
accepted entry semantics, lazy-loader effects, observation exclusions and warning
filters remain those of the [provider contract](function_provider_contract_review.md).

| Guarantee | Proposed boundary | Durable guard |
| --- | --- | --- |
| Opt-in and defaults | Strict boolean opt-in. Default captures allocate no evidence collector; `.evidence` still supplies a detached companion with unknown planes. | `tests/test_provider_evidence.py::test_default_and_unobserved_captures_keep_unknown_planes_and_no_builder` |
| Context overlap | Selection is retained whether observation or capture starts first. Successfully activated selected exports can be unused. No successful overlap leaves planes unknown. | `tests/test_provider_evidence.py::test_selected_boundaries_do_not_imply_calls_or_citations` |
| Ownership | Only active opted-in captures in the current session receive facts; other sessions, unselected tasks and closed captures retain isolation. Threads do not automatically inherit observation contexts. | `tests/test_provider_evidence.py::test_other_sessions_and_closed_captures_do_not_receive_new_evidence` and `test_async_tasks_preserve_awaited_evidence_and_context_local_selection` |
| Original metadata | Successfully credited provider references keep their detached activation-time item fields, source and original producer version, independent of later module edits. Recorder version is the original Ackredit runtime. | `tests/test_provider_evidence.py::test_actual_credits_retain_activation_metadata_sources_and_original_fields` |
| Bounded positive facts | Deduplicate by selected boundary, item/source and boundary/diagnostic identity; repeated calls still credit independent reused captures. No invocation counters, chronological trace or global completeness percentage. | `tests/test_provider_evidence.py::test_reused_calls_and_nested_captures_keep_bounded_origins_without_call_counts` |
| Partial recording | Successfully recorded origins survive a later recording fault; the companion retains W019. Normal observer warning behavior preserves the scientific result or its own exception. | `tests/test_provider_evidence.py::test_partial_tracking_failure_retains_only_successfully_credited_field_origins` |
| Scientific failure/cancellation | Entry references and their origins survive a later scientific failure/cancellation, without inventing a recording gap or completed-backend credit. | `tests/test_provider_lifecycle.py::test_cancelled_and_failed_tasks_retain_entry_without_completed_backend` |
| Warning filters | Application warning-as-error policy can stop the scientific body at a recording fault. The companion retains the diagnosed gap and observer/scope cleanup still happens. Unconditional preservation under every warning filter is excluded. | `tests/test_provider_lifecycle.py::test_warning_as_error_restores_observer_and_parent_scope` |
| Deferred execution | An unawaited coroutine can retain selection but no entry credit/origin. Delayed prepared credit cannot change a closed capture and receives no guessed provider origin. | `tests/test_provider_lifecycle.py::test_unawaited_coroutine_cannot_earn_completed_or_entry_credit` and `test_delayed_prepared_credit_cannot_change_an_expired_result_capture` |
| Restoration | Rebound exports are preserved and diagnosed; restoration gaps enter evidence only while its capture remains active. | `tests/test_provider_evidence.py::test_export_rebinding_gap_is_retained_only_during_capture_overlap` |

Automatic explicit-credit, prepared-backend, import-hook, discovery/enrichment
and other host-integration origins remain outside this collector. The manual
companion accepts supported declarations for those mechanisms without claiming
they were automatically collected. Pre-activation aliases and refused generators
receive no guessed origin or successful selection. General resource-exhaustion
recovery, every internal failure mode and complete performance/memory guarantees
are outside this proposal; roadmap L owns measured complete costs. Application
diagnostic filters and the existing scientific-result boundary are explicit limits.

## Presentation and compatibility

`report("explanation")` describes the companion. Other existing formats delegate
to its complete original by default. `report("workflow", include_evidence=True)`
explicitly attaches declarations to each original occurrence. The CLI requires
evidence input, workflow output and explicit `--include-evidence`, refusing invalid
combinations before session aggregation and refusing input overwrite.

References shared across a bundle retain one reference number; repeated original
occurrences retain separate declarations and graphs. Unknown/empty declarations,
unsupported/unobserved scope, original versions and diagnosed gap identities keep
their meanings. Locators and untrusted strings are escaped as data. Stored gaps
are not emitted again. This proposed promise covers content/association and
default delegation, not a universal freeze of cosmetic whitespace.

`tests/test_workflow_evidence.py` guards per-occurrence rendering, unknown/empty
meaning, hostile strings, invalid combinations, fresh offline CLI/library equality
and input preservation. Original portable readers, default capture/report paths
and producer-absence behavior retain their accepted contracts. Metadata-source
declarations do not fill missing bibliography or infer an unobserved citation.

## Evidence considered and practical limits

Original #104 qualifies controlled explicit declarations and detached reading.
Original #105/#106 qualify real normally installed Pint/unit conversion and
Pint-to-unyt receiving, reused captures, a controlled recording fault and fresh
producer/engine-blocked readers. The
[original #106 hosted receipt](https://github.com/uibcdf/ackredit/blob/42d30e4e081601ec1198331f0fb3e23b6b12f12b/devtools/receipts/workflow_recorder_evidence_hosted_106_2026-10-06.json)
retains eight Linux/macOS arm64 × Python 3.11–3.14 cells, 72 tests without skips,
original wheel/ZIP hashes and independent aggregation. Public 0.11.0 later
qualifies the same bounded capabilities against its exact Conda archive under
#107, with its own
[public receipt](https://github.com/uibcdf/ackredit/blob/aae9ad98c89d162b946a65fa01603707db02359a/devtools/conda-build/receipts/ackredit_0.11.0_public_2026-10-06.json).
Those are separate original producers/artifacts, not a new qualification here.

Under #114 the original #106 Linux/Python 3.13 companion is retained unmodified
as `tests/data/attribution_evidence_v1_pyunitwizard.json`. The native ZIP and
extracted JSON hashes were rechecked against the original receipt. Its four
actual original occurrences retain conversion, reuse, controlled fault and
selected-but-unused scope. Two new guards in `tests/test_attribution_evidence.py`
verify original recorder versions, declarations and default/integrated reports,
plus a fresh offline CLI reader with producer imports, network and recording
blocked. This is cross-revision saved-reader evidence, not fresh receiving science.

Four supplementary opted-in lifecycle variants in `tests/test_provider_lifecycle.py`
exercise cancellation/scientific failure, strict warning filters, unawaited
execution and delayed completed credit. The selected contract qualification
passes **149 Python 3.14.7 tests without skips or warnings**. Representation,
capture, workflow/explanation renderer and CLI implementation files are unchanged
from original public 0.11.0. The later provider parser/validator work #111 retains
its separately qualified scope; this review changes no runtime code.

These cases do not claim other recorder adoption, Windows qualification,
comprehensive instrumentation, scientific equivalence across all engines,
cryptographic authentication of declarations or full cost measurements. Current
source and exact-head controls belong to #114, separately from prior release receipts.

## After the explicit decision

1. Record acceptance/amendment/deferral for each surface in #114, the decision log
   and this review; leave an unresolved surface provisional with a concrete reason.
2. For accepted surfaces, update source classification, API counts, release notes
   and the canonical host guide to the exact accepted promise. Coordinate that
   guide through MolSysSuite #97/MOLI #46 and consumer owners; never repair copies.
3. Select and qualify the future release delivering the promise. Its exact source,
   installed file, real receiving and public delivery require their own applicable
   gates. Public 0.11.0 keeps its original provisional evidence classification.
4. Keep general 1.0, broader recorders, platform object contracts, full cost work
   and publication/acknowledgement decisions independently visible in the roadmap.
