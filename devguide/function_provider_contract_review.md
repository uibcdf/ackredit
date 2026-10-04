# Function-provider contract and release handoff

This is a concrete **proposal for maintainer review**, owned by Ackredit
#84/#87, coordinated through MolSysSuite #97 and MOLI #46. It does not promote
an API or authorize a release. The receiving pilot belongs to PyUnitWizard #94.

## Recommended product boundary

Retain `observe_calls(*modules)`, the offline `ackredit.provider@1` declaration
and `prepare_credit(item_id, used_by, *, roles=(), context=None)` as bounded
public capabilities in the next planned minor release, after the decisions
and exact candidate gates below. Their combination supplies function-level
and completed-backend attribution without a profiler or producer dependency.
Do not require scientific hosts to adopt either capability.

| Capability | Proposed guarantee | Explicit limit |
| --- | --- | --- |
| Declaration | Offline JSON-compatible bibliography, original producer name/version and per-export uses; no import of Ackredit or credit on declaration | Metadata is the producer's claim; Ackredit does not verify the underlying scientific citation |
| Function metadata | `function.__ackredit__ = {"uses": [...]}` resolves against the module bibliography without wrapping the producer's function | If both forms declare an export, their declared lists must agree; an unmaterialized metadata-only lazy export is undiscoverable |
| Entry observer | Explicit selected ordinary modules; sync entries and awaited coroutine execution preserve arguments, results and scientific exceptions | No pre-existing aliases, generators, descriptors, custom module subclasses, native internal calls or subprocess observation |
| Lazy exports | Resolve only declared missing PEP 562 names during activation; refuse invalid exports before installing observation or references | The producer's loader can have ordinary caching/import side effects; Ackredit cannot roll them back |
| Context ownership | Nested/concurrent activations share wrappers with context-local leases; expired owners stop recording; last exit restores original exports | Threads do not automatically inherit context; external export replacements are preserved and diagnosed |
| Prepared credit | Inert fixed-use preparation; zero-argument call writes to the current session and each active capture after the host's chosen completion boundary | Creates no scientific scope, success interpretation or backend call; the host decides when to invoke it |
| Bibliography integrity | Accept equivalent portable representations at activation while preserving existing registration; freeze detached records and original versions | Real conflicts are refused; metadata mutation/replacement during active use is diagnosed, never silently adopted |
| Portable result | Reused references enter independent captures; saved original records, roles/context and graph render offline without producer imports or new credit | The released `ackredit.attribution@1` does not encode invocation counts, chronology, scientific success or a complete execution trace |
| Failure boundary | E012 rejects invalid declarations before activation; W019 identifies recording/restoration gaps; prepared replacement/deletion raises E010 | Attribution can be partial after a recording gap; explicitly configured warning-as-error behavior remains the application's choice |

Normalize/detach declarations and fixed-use keys once. Invocation still compares
registered contents and uses the shared session/capture/journal writers. No
mutable-identity cache, broad import scan, background service or network lookup
belongs in these contracts. Applications should instrument coarse operations,
not millions of scalar iterations.

## Evidence and remaining decisions

1. **Executed provider/receiver behavior.** Synthetic installed producer and
   producer-blocked reader guards are mandatory ordinary CI. The real
   PyUnitWizard pin is `33fec8a627505a4f5426babe87e8e85438105041`.
   Existing [receiving documentation](receiving_validation.md) and immutable
   receipts distinguish each exact installed candidate from its documentation
   head and from the public 0.9.0 Conda archive.
2. **Independent review.** MolSysSuite reviewed original receiving source
   `fc00a6c`, its eight cells/40 tests, all ten artifact ZIP identities and the
   provider-owned aggregate. Central record/receipt commit is
   `b23c774958d1fcf9bf1360a671e822ee283be80e`; [the review comment](https://github.com/uibcdf/molsyssuite/issues/97#issuecomment-5983604647)
   explicitly retains the maintainer decision and later-candidate review.
   Ackredit's later reporting source `cb3e58d` independently passes eight
   cells/48 tests, documented with its own receipt. Neither result can be
   transferred to revised runtime bytes without a new exact-bundle gate.
3. **Representation defect before stabilization.** Ackredit #92 reproduces
   refusal of valid pre-existing tuple authors against equivalent provider JSON
   lists. The repair preserves raw registrations and detached invocation
   comparisons while keeping portable output normalized. Its changed runtime
   is now qualified at source `1a5dd4566737f6195571b4cb421af6f01647c5f6`:
   [CI 37230213187](https://github.com/uibcdf/ackredit/actions/runs/37230213187)
   passes seven jobs, and
   [matrix 37230225286](https://github.com/uibcdf/ackredit/actions/runs/37230225286)
   passes eight cells/48 tests without skips. The real report test pre-registers
   tuple authors through the public API. Downloaded identities and the aggregate
   independently verify. Its [reviewed receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/provider_registered_representation_matrix_2026-10-04.json)
   retains the exact candidate identity; earlier gates remain dated evidence.
4. **Maintainer decision.** Accept or amend the bounded guarantees above and
   decide provider-schema compatibility, API stability classification and
   the first release containing them. Recommendation: preserve released
   `ackredit.provider@1` interpretation, use a new identifier for incompatible
   schema/meaning changes, and diagnose unknown identifiers. This forward
   guarantee is proposed here, not already granted to development snapshots.
5. **Receiving adoption.** PyUnitWizard owns its final citation selection,
   optional boundary, entry/completion meanings and released fallback. MOLI
   owns the direct-component contract; MolSysSuite owns a shared adoption
   requirement. A review decision does not automatically establish either.

## Release sequence after acceptance

Record the accepted decision and receiving owners first. Update Ackredit's API
stability page, release notes and canonical integration guide around the
accepted boundary; propose consumer delivery through the central registry.
Do not edit synchronized consumer copies locally. Select the next tag only
when the maintainer chooses a release checkpoint.

Build one exact candidate, retain its source/version/file SHA-256, complete
staging and qualify that same file on Linux/macOS arm64 × Python 3.11–3.14,
with the real producer and independent reader. Retain the genuine released
0.9.0 optional-provider fallback and client-owned qualification separately.
Promotion must preserve candidate bytes; verify a clean installation from the
public channel and deliver its identity and evidence to receiving owners.

Public Ackredit 0.9.0 remains the portable minimum until an actual new release
provides a reviewed capability requiring another minimum. No package rebuild,
withdrawal or new tag follows from this proposal.
