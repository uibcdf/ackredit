# Development checkpoint — 2026-10-22

Start here when resuming. The [roadmap](roadmap.md), [status](status.md),
[decisions](decisions.md) and issue-backed queues retain their own scope.

## Verified public maintenance delivery

**0.12.1 is public and complete under
[Ackredit #134](https://github.com/uibcdf/ackredit/issues/134).** The canonical tag
and [GitHub release](https://github.com/uibcdf/ackredit/releases/tag/0.12.1) retain
original producer `28d3643e324da4c714a5c238701baba5ec64d306`; the annotated tag
object is `239ca77e32efa8cba8b1dd0d1b02b86b8e2a44ee`. Later documentation commits
never replace that source or rebuild the coordinate.

Original file: `ackredit-0.12.1-py_0.tar.bz2`. SHA-256:
`46d505016f6d05d7000adfaedde5f1ce596e32eb70d5302fc7f112c1042a73cb`.

All 17 required source jobs and named steps pass, including eight full source
Linux/macOS arm64 × Python 3.11–3.14 cells. Original staging
[39886772212](https://github.com/uibcdf/ackredit/actions/runs/39886772212),
eight-cell installed matrix
[39887248843](https://github.com/uibcdf/ackredit/actions/runs/39887248843),
72 real PyUnitWizard tests without skips
[39887250554](https://github.com/uibcdf/ackredit/actions/runs/39887250554) and
same-file promotion
[39888619992](https://github.com/uibcdf/ackredit/actions/runs/39888619992) pass.
Ten receiving ZIP digests/source bindings and the independently reconstructed
aggregate verify. The shared operator verifies the full native installed matrix;
public label/index verification is independent and read-only.

A fresh ordinary public-channel Linux/Python 3.14.9 prefix, with cache separate
from staging, passes all 70 original package files, runtime/distribution/CFF,
portable/provider/evidence/CLI/fresh-reader contracts, actual optional absence
and `pip check`. Candidate-installed checks pass 43 selected contracts and all
three 5,000-use payloads match the corresponding source originals. Compared
with public 0.12.0, 67 package files are identical; only the reviewed snapshot
implementation, packaged citation and generated version differ.

[Installation](../docs/content/about/installation.md),
[the archived release record](https://github.com/uibcdf/ackredit/blob/main/devguide/archive/release_0121.md)
and [the public receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/conda-build/receipts/ackredit_0.12.1_public_2026-10-22.json)
retain original identities, native effects, proofs, cleanup and limits. Earlier
0.12.0/0.11.0 and older tags, archives and receipts remain unchanged. Public
Conda, GitHub release and tag do not establish Zenodo archival or a DOI.

## Completed source and maintenance work

- **#132:** remaining development-resource owners/lifetimes reviewed;
  [maintained operation review](https://github.com/uibcdf/ackredit/blob/main/devguide/temporary_resources.md),
  twelve new exceptional-cleanup cases and 214 selected passing tests without
  skips. Fifty-four historical paths are absent; shared `/tmp/pytest-of-diego`
  is preserved. Twelve absent worktree registrations were pruned after individual
  path/commit checks. Prior removal attribution remains unknown. Disposition
  delivered to [MolSysSuite #104](https://github.com/uibcdf/molsyssuite/issues/104#issuecomment-6355547940).
- **#133:** `get_attribution()` replaces repeated full-use scans with one
  snapshot-local pair index. Context variants, observed records, ordered legacy
  fallback, unknown references and graph remain intact. Six deterministic
  scaling guards fail before repair; the fidelity control passes on both sides.
  Nine paired source cases retain 126 matching results for corresponding inputs.
  At 5,000 uses source medians improve by 3.87–4.94 times, with 0.79–0.81 MiB
  extra peak traced allocation. Small cases show no consistent speedup. This is
  not RSS or a full scientific-pipeline/universal speed claim; see
  [performance](../docs/content/about/performance.md).
- **Old CI follow-up:** release-closeout 37600532162 and developer-guide
  37602750475 now pass all seven jobs. Their terminal outcomes are recorded in
  #127/#129; the original queued observations remain historical.
- **Resource retirement:** both task-owned Conda prefixes, both temporary Git
  worktrees, the release SDK/cache/evidence root and 18 task files are retired
  after normalized proof was saved. Git/Conda handled their registrations;
  shared environments, caches and pytest root were preserved. Necessary evidence
  may remain in `/tmp` in future tasks; remove it when no longer useful.

Final documentation-head CI is distinct from the original producer's completed
release qualification. The owning #134 retains the final published head and its
inspected applicable checks; do not rebuild/promote/tag again for prose changes.

## Compatibility and consumer ownership

Portable-only clients retain `>=0.9.0`; stable provider/prepared contracts retain
`>=0.11.0`; bounded recorder evidence, opt-in collection/explicit reporting and
standalone validation retain `>=0.12.0`. General 1.x needs a separate explicit,
qualified decision. Maintenance 0.12.1 changes none of these floors or schemas.

The canonical `standards/ACKREDIT_GUIDE.md` is unchanged, SHA-256
`6353892d552eab79973cecec5f8e3c8c31e146416e1cb481786e21cd3fcbf99d`.
No new synchronization or client dependency upgrade is required. If it changes
in later work, publish the canonical bytes here and open an owning MolSysSuite
issue for registered-client synchronization; never repair consumer copies locally.

MolSysSuite #97 and MOLI #46 completed their bounded central reviews. The
2026-10-08 six-consumer guide delivery is recorded in PyUnitWizard #94; MOLI's
2026-10-21 direct-consumer review preserves Sabueso's required portable profile.
Those notices and this pinned PyUnitWizard qualification do not certify every
current consumer source or habitual adoption. MolSysMT owns its adapter work
in #292. For siblings use owning issues; only PyUnitWizard has the separately
authorized source-change route with its own required records.

## Next work

1. Triage [#135](https://github.com/uibcdf/ackredit/issues/135): Setuptools warns
   about the existing license table and requests migration before 2027-02-18.
   Current builds pass. Review backend-floor, recipe and shared template/checker
   implications before a scoped metadata repair; do not silently raise floors.
2. Review actual consumer feedback and select a bounded next product scope.
   Wider roadmap L costs, J recorder coverage and K platform/result boundaries
   retain their own owners/evidence. Do not implement them just to produce a tag.
3. General 1.0 stays explicit and informed by real use. Optional dashboard #58
   is not a priority; acknowledgement work remains deferred under #124 until an
   owned real result/wording/reporting case exists.

## Local resumption

Use Python 3.14 in `molsyssuite@uibcdf_3.14`; install the primary checkout with
`python -m pip install --no-deps --editable .`. Verify origin and matching
runtime/distribution identity at or above 0.12.1 after tag/history changes.
Development suffixes are separate from the exact published Conda installation.
The shared development environment still has seven unrelated dependency
conflicts tracked in MolSysSuite #82; clean release prefixes pass `pip check`.
Do not downgrade shared dependencies or remove another task's resources.

Inspect actual state first:

```bash
git status --short
git log -1 --format='%H %s'
gh run list --repo uibcdf/ackredit --limit 10
gh run-receptor inspect RUN_ID --repo uibcdf/ackredit --receptor=llm
```

Root contributor/suite instructions govern scoped gates and authorized direct
pushes. Empty local queues are not a claim that all GitHub ideas/adoption work
are complete; incoming triage and deliberately deferred issues stay visible.
