# Development checkpoint — 2026-10-22

Start here when resuming work. This operational handoff points to the
[roadmap](roadmap.md), [status](status.md), [decisions](decisions.md) and queues.

## Public stabilization release complete

Qualified public **0.12.0** completes [Ackredit #127](https://github.com/uibcdf/ackredit/issues/127).
The immutable `0.12.0` tag identifies original producer
`6f4dbf39996a7185b8aaff7c52b9daeb167a100a`; documentation closeout is separate.
Original file `ackredit-0.12.0-py_0.tar.bz2` has SHA-256
`160b452c2b9de3b44bc6c6e2f4bd8c47e44b1d2779b620f63048231708a1d4aa`.

All required exact-source gates, eight Linux/macOS arm64 × Python 3.11–3.14 full
installed cells, 72 real PyUnitWizard receiving tests without skips and independent
aggregate verification pass. The same installed candidate also passes 158
selected contracts without skips, the dependency-free author/validator example
and real BibTeX/Pandoc, two BibLaTeX/Biber styles and JabRef 5.15 checks.
Synthetic ISBN and manager key-store warnings remain in the receipts.

Same-file public promotion, independent labels/solver index and a fresh ordinary
public Linux/Python 3.14 installation pass. All 70 installed package files match
the original archive; runtime/distribution/CFF identity, detached readers/CLI,
evidence, standalone validation, actual optional absence and dependency closure
pass. [Installation](../docs/content/about/installation.md), the
[archived release record](https://github.com/uibcdf/ackredit/blob/main/devguide/archive/release_0120.md)
and [public receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/conda-build/receipts/ackredit_0.12.0_public_2026-10-07.json) retain original evidence and limits.
Do not rebuild or promote this coordinate again. Original 0.11.0 and earlier
receipts remain unchanged. Closeout-head CI and consumer notices are recorded in
#127 separately from original-producer release qualification.

## Documentation handoff and CI follow-up

The release closeout is `887b81c525ff9b285150b2d801c557321b4d48fa`.
Its [ordinary CI 37600532162](https://github.com/uibcdf/ackredit/actions/runs/37600532162)
now passes all seven jobs. GH Run Receptor rechecked terminal success on
2026-10-22, including the macOS/Python 3.14 job queued at the original review. Both
[suite policy](https://github.com/uibcdf/ackredit/actions/runs/37600532896) and
[publication policy](https://github.com/uibcdf/ackredit/actions/runs/37600532962)
pass. The separate #129 documentation-head
[CI 37602750475](https://github.com/uibcdf/ackredit/actions/runs/37602750475)
also passes all seven jobs on reinspection. These terminal results complete the
previously retained hosted follow-up; original-producer release proofs are unchanged.

This developer-guide review is owned by
[Ackredit #129](https://github.com/uibcdf/ackredit/issues/129); its final commit,
validation and any queued hosted checks are recorded there. Start a new session
by inspecting the working tree and the exact current head, then use the run ID
returned for the applicable workflow:

```bash
git status --short
git log -1 --format='%H %s'
gh run list --repo uibcdf/ackredit --commit "$(git rev-parse HEAD)" --limit 10
gh run-receptor inspect 37600532162 --repo uibcdf/ackredit --receptor=llm
```

Inspect the current head's applicable CI with GH Run Receptor as well; the last
command addresses the separately retained release-closeout run. Diagnose only
an observed failure in its owning issue, preserve
human work, and do not rebuild or promote 0.12.0 to repair documentation CI.

The delivered [canonical integration guide](https://github.com/uibcdf/ackredit/blob/887b81c525ff9b285150b2d801c557321b4d48fa/standards/ACKREDIT_GUIDE.md)
has source `887b81c525ff9b285150b2d801c557321b4d48fa` and SHA-256
`6353892d552eab79973cecec5f8e3c8c31e146416e1cb481786e21cd3fcbf99d`.
Those bytes are unchanged by this review. Guide publication is separate from
the original package producer/tag; consumer copies follow the central registry.

## Current resumption and compatibility

The maintainer resumed work on 2026-10-22, with a possible later tag/release.
The focused owner review is complete under [#132](https://github.com/uibcdf/ackredit/issues/132):
remaining temporary-resource ownership, exceptional scratch cleanup, retained
output and historical-path disposition. See the
[maintained operation review](https://github.com/uibcdf/ackredit/blob/main/devguide/temporary_resources.md).
It adds lifecycle guards and contributor evidence, not a runtime API change.
Source inspection, executed cleanup and historical attribution remain separate.
The selected local gate passes 214 tests without skips; the owning issue records
the final published head and applicable hosted checks. Fifty-four historical
paths are absent, the shared pytest root is preserved, and twelve stale worktree
registrations were pruned after reachability checks. No old files/environments
were deleted. The canonical client guide is unchanged.

After that review, select focused product work from concrete consumer feedback
or an explicitly chosen roadmap boundary. A possible release still needs its
own scope/version decision and exact-source/installed/receiving/public gates;
do not tag or rebuild an existing coordinate merely for maintenance evidence.
If Ackredit changes its canonical client guide, publish it here and open an
owning MolSysSuite issue for registered client synchronization. Do not change
consumer copies from this checkout.

Portable-only clients retain `>=0.9.0`. Stable provider/prepared credit retains
`>=0.11.0`. Recorder evidence, opt-in collection/explicit reporting and standalone
validation have their bounded public promises from `>=0.12.0`. The general 1.x
commitment still awaits an explicitly authorized, qualified 1.0.0. Review
[API stability](../docs/content/about/stability.md) for precise exclusions.

The prior adoption pause was accepted under #126 and delivered through #127.
The explicit resumption does not turn automated receiving into habitual
dogfooding or certify consumer releases. No last-pre-1.0 schedule or arbitrary
stabilization duration is imposed.

The delivered version/file/digest/guide identities have been handed off to:

| Owner | Retained handoff | Next owner action |
| --- | --- | --- |
| MolSysSuite | [#97 notice](https://github.com/uibcdf/molsyssuite/issues/97#issuecomment-6035035826) | Coordinate registered-consumer adoption and canonical-guide synchronization. |
| MOLI | [#46 notice](https://github.com/uibcdf/moli/issues/46#issuecomment-6035036721) | Own platform/result-boundary decisions and direct-component adoption. |
| PyUnitWizard | [#94 notice](https://github.com/uibcdf/pyunitwizard/issues/94#issuecomment-6035037580) | Retain qualified pilot evidence; own actual adoption and released client closure. |
| Sabueso | [#108 notice](https://github.com/uibcdf/sabueso/issues/108#issuecomment-6035038368) | Own its integration, guide adoption and release/actual-use evidence. |

MolSysSuite #97 and MOLI #46 are now closed for their bounded central reviews.
PyUnitWizard #94 records the 2026-10-08 registered six-client guide delivery,
including commit `4e4eefad58f12778f31e9ec3f81f53193750d567` in PyUnitWizard.
MOLI #46's 2026-10-21 review preserves Sabueso's required portable `>=0.9.0`
profile and does not mandate later optional APIs. MolSysMT #292 remains open
for its own portable-adapter implementation. These are owner records, not fresh
execution against every current consumer source or habitual adoption evidence.
The canonical `standards/ACKREDIT_GUIDE.md` publishes verified version boundaries;
consumer copies are synchronized through the central registry, never repaired
locally. Other consumers keep their own adoption issues.

The local bug queue is empty after #128's installed-DueCredit absence-test repair.
Optional dashboard #58 is not a priority. Acknowledgements stay deferred under
#124 until an actual owned result/wording/reporting case exists. Broader recorders,
MOLI object boundaries, additional cost studies and new publication expectations
keep their separate scope and owners; choose concrete work rather than implementing
deferred features just to produce a tag.

For a useful adoption report, retain the consumer/version, real operation and
attribution boundary, provider present/absent/failing behavior, original saved
result and its fresh-reader report, expected/observed outcome, and any measured
friction/cost. File defects or missing capabilities in the owning component and
cross-link this provider when relevant. No arbitrary number of consumers or
elapsed pause duration qualifies 1.0; reconsider it from actual-use evidence and
a separate maintainer release decision.

## Retained limits

Publication tools qualify only the recorded fixtures, versions and two styles;
they do not certify arbitrary managers, journals, Unicode, GUI or platforms.
PyUnitWizard receiving uses its pinned original producer and released 0.9.0
fallback; no consumer scientific release is inferred. Shared scientific
environment conflicts remain MolSysSuite #82; fresh release environments do not
repair or downgrade human environments. Sibling checkouts and synchronized
external guides remain untouched. Zenodo/DOI archival has not been claimed.
