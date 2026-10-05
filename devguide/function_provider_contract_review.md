# Function-provider contract and release handoff

This is a concrete **proposal for maintainer review**, owned by Ackredit
#84/#87, coordinated through MolSysSuite #97 and MOLI #46. It does not promote
an API or authorize a release. The receiving pilot belongs to PyUnitWizard #94.

## Current decision and delivery (2026-10-05)

The [principal-maintainer decision](https://github.com/uibcdf/ackredit/issues/87#issuecomment-5984968710),
retained centrally in immutable MolSysSuite
`05f866ab7f17af6b046e89befa014460d5d13160`, is to **keep `observe_calls`,
`prepare_credit` and `ackredit.provider@1` provisional**. PyUnitWizard's bounded
experimental receiving pilot is accepted. Stable compatibility, required
observation, a new consumer minimum and shared adoption remain undecided.
Later successful tests or releases do not automatically change that decision.

Corrected public Ackredit **0.10.1** ships all three capabilities. Original
producer/tag `dd500842b6085111e01e62cfc243f68406eb8cc7` and archive SHA-256
`26e75a0780ad4e6abc2de55df90b29b4a2aa4e510d6b50fa54a5812ad929228e`
identify the qualified runtime. [Delivery evidence](https://github.com/uibcdf/ackredit/blob/f71d242705b4b65302fb3eecb0659207d56c47dd/devtools/conda-build/receipts/ackredit_0.10.1_public_2026-10-05.json)
retains eight installed cells, 48 real PyUnitWizard tests, exact-file public
promotion and a clean public Python 3.14 installation, including 56 public
Sabueso receiving tests. The release repairs self-citation under #94 and leaves
original 0.10.0 bytes/tag unchanged. The older source-wheel checkpoints below
remain evidence for their own inputs.

## Recommended product boundary

Retain `observe_calls(*modules)`, the offline `ackredit.provider@1` declaration
and `prepare_credit(item_id, used_by, *, roles=(), context=None)` as bounded
provisional public capabilities while resolving the decisions below.
Their combination supplies function-level
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
| Bibliography integrity | Accept equivalent portable representations at activation while preserving existing registration; freeze detached declarations and original versions | Real conflicts are refused; registered bibliography mutation/replacement is diagnosed; edits to the producer declaration during activation are not adopted |
| Portable result | Reused references enter independent captures; saved original records, roles/context and graph render offline without producer imports or new credit | The released `ackredit.attribution@1` does not encode invocation counts, chronology, scientific success or a complete execution trace |
| Failure boundary | E012 rejects invalid declarations before activation; W019 identifies recording/restoration gaps; prepared replacement/deletion raises E010 | Attribution can be partial after a recording gap; explicitly configured warning-as-error behavior remains the application's choice |

Normalize/detach declarations and fixed-use keys once. Invocation still compares
registered contents and uses the shared session/capture/journal writers. No
mutable-identity cache, broad import scan, background service or network lookup
belongs in these contracts. Applications should instrument coarse operations,
not millions of scalar iterations.

## Exit criteria for provisionality

Evaluate the declaration protocol, observer and prepared callable separately.
A stable prepared callable does not require a stable observer. The existing
portable attribution contract remains stable throughout this review.

| Surface | Decision to record before promotion | Evidence already available |
| --- | --- | --- |
| `ackredit.provider@1` | Accept the exact required fields, local reference resolution, original software/version and per-export use rules. Decide that an incompatible interpretation uses a new schema identifier; unknown identifiers remain refused. | Offline declarations, function/module agreement, atomic preflight, lazy exports and equivalent tuple/list registration; real PyUnitWizard software/article selections and original 0.9.0 fallback. |
| `observe_calls` | Accept entry semantics, awaited execution, selected direct exports, context-local ownership and restoration. Retain documented exclusions and define W019 partial-attribution behavior, including application warning filters. | Existing installed producer/reader gate, eight-cell real receiving matrix and cancellation/failure/strict-warning lifecycle guards below. |
| `prepare_credit` | Accept inert preparation, the zero-argument call into the current session/captures, host-owned completion, detached inputs and E010 replacement/deletion refusal. No prepared callable owns a scientific outcome or creates a scope. | Reused/nested captures, journal writer, real completed-backend pilot, concurrent prepared-callable and expired-capture lifecycle guards below. |

Completion requires the following **recorded decisions**, rather than another
identical scientific run against unchanged runtime bytes:

- Ackredit's principal maintainer explicitly accepts, amends or defers each
  surface and its compatibility promise in #84/#87. Tests cannot make that
  product decision.
- Record the accepted receiving scope and any unresolved concrete objections.
  PyUnitWizard #94's experimental review is settled; MolSysSuite #97 and direct
  MOLI #46 retain their separate shared/platform ownership. A stable provider
  decision does not require every host to adopt it.
- For a promoted surface, update its stability classification, release notes
  and canonical integration guide to the accepted boundary, preserving the
  portable minimum and optional producer contract. Track guide synchronization
  and actual client adoption separately through the central registry.
- Select and qualify the release delivering that stable promise. Reuse existing
  evidence only for unchanged tested inputs and scope; revised runtime or
  candidate bytes require their own applicable gates. Original published files
  and tags remain immutable.

Keep an amended or deferred surface provisional with the specific unresolved
guarantee visible here and in its owning issue. Provisional names must be
promoted or removed before the general 1.0 stability commitment. No automatic
expiry date or additional-engine/platform requirement is imposed by this
checklist. Tell the maintainer when each promotion and its delivering release
are complete; source acceptance and public delivery remain separate states.

## Supplementary lifecycle evidence (2026-10-05)

`tests/test_provider_lifecycle.py` exercises cancellation alongside surviving
observers, scientific failure versus explicit completed credit, one prepared
callable shared by four isolated thread sessions, warning-as-error cleanup,
unawaited coroutines and delayed credits after a result capture expires.
Assertions check original outcomes/exceptions, reference roles, graph parentage,
export/scope restoration, independent reused captures and detached saved readers.
The tests use events/barriers rather than timing assumptions.

All five guards pass against the normally installed **public 0.10.1** archive
on Linux/Python 3.14.7, outside source, with shared same-interpreter provenance
checks before and after tests. [The supplementary receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/provider_lifecycle_2026-10-05.json)
binds the test-module/runtime hashes, exact public Conda identity and complete
Pytest Receptor outcome. This extends guard coverage without changing runtime;
it is not a new real-producer matrix, performance measurement or stable decision.

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
4. **Later maintainer decision.** The accepted current decision is to remain
   provisional. A later explicit decision may accept or amend the bounded
   guarantees above and choose provider-schema compatibility and stability
   classification. Recommendation: preserve accepted
   `ackredit.provider@1` interpretation, use a new identifier for incompatible
   schema/meaning changes, and diagnose unknown identifiers. This forward
   guarantee is proposed here, not already granted to provisional releases.
5. **Receiving adoption.** PyUnitWizard owns its final citation selection,
   optional boundary, entry/completion meanings and released fallback. MOLI
   owns the direct-component contract; MolSysSuite owns a shared adoption
   requirement. A review decision does not automatically establish either.

## Release sequence after acceptance

### 2026-10-04 provisional delivery decision

Diego authorized a release checkpoint and tag; [Ackredit #93](https://github.com/uibcdf/ackredit/issues/93)
prepared **0.10.0 with the current provisional classification retained**.
That delivery does not accept the proposed stable guarantees, close #84/#87 or
establish a shared adoption requirement. It requires the exact Conda archive's
full installed and real-producer gates, promotion and public verification, which
completed for original 0.10.0 and additive corrected 0.10.1 under #93/#94.
The canonical integration guide retains the existing released portable contract;
stable provider-guide distribution waits for its separate review decision.

### Stable promotion remains a separate decision

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
