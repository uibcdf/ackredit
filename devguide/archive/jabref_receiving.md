---
summary: Qualify detached BibTeX import and fresh-process resave in JabRef's real CLI.
issue: uibcdf/ackredit#123
status: resolved
opened: 2026-10-06
closed: 2026-10-06
severity: medium
verification: reproduced
area: [formats, publication]
guard: tests/test_jabref_receiving.py
normative:
blocked_by: []
supersedes: []
---

# JabRef import and resave receiving

## What

Theme M has actual style-engine receiving evidence under #120–#122. The separate
reference-manager boundary needs a real importer and persisted library before
manager compatibility can be claimed.

## How

Use official stable JabRef 5.15's documented no-GUI CLI, isolated portable runtime
and preferences. Receive the original six-record attribution through unchanged
BibTeX export, import/save a separate manager library, then reopen/resave it in a
fresh process. Identify originals and converted output separately; use the
existing publication-process owner to retain byte streams and process failures.

## Why

Pandoc and Biber reading is not manager import. Manager formatting, field
cleanup, citation-key handling or duplicate detection can lose distinct releases
or original name/DOI declarations despite a successful command.

## What was refuted

A headless CLI checkpoint is not GUI interaction, synchronization or another
manager's importer. Successful processing alone does not prove field fidelity;
the manager's converted library cannot replace the saved scientific attribution.

## Scope and exclusions

One official JabRef portable Linux version, real no-GUI import/resave, normally
installed Ackredit on Python 3.14 and the existing six-record synthetic input.
No original user library or preferences, network enrichment, new dependency,
public API, duplicate merging or release. Other managers/platforms, GUI controls
and journal presentation remain outside this independently closable checkpoint.

## Acceptance criteria

- Real manager import and fresh-process reopen/resave retain distinct six-record
  citation keys, releases/versions, names and preferred work metadata.
- Original attribution, exported BibTeX and execution credits remain unchanged.
- Documented reusable tooling selects the exact launcher, isolates preferences,
  rejects absent engines/prior output and preserves actual process failures.
- Retain distribution/runtime/input/output identities, conversions and limits;
  guard the observed mechanism and update guidance, indexes and owning issue.

## Executed receiving checkpoint (2026-10-06)

`devtools/check_jabref.py` is the reusable local route in the publication-probe
owner. The caller supplies the official portable Linux distribution; the tool
selects and executes its exact `lib/runtime/bin/JabRef` script and identifies all
shipped runtime/application files before and after. It exports detached BibTeX,
runs explicit no-GUI import/save, then native reopen/resave in a separate process
with new preferences. Pandoc independently reads each file after actual manager
persistence; it is not used as a substitute importer.

Each manager process uses Java user.home, Java user/system preference roots,
temporary storage and XDG config/cache/data roots under the new destination.
JVM environment options are selected only for those children, without changing
the parent or system Java. The existing `_run` process owner accepts explicit
child-only environment overrides and retains them with exact stream hashes and
native status. Missing requested tools, broken launchers, prior destinations
and output inside the manager distribution fail without alternate routes.

Official `JabRef-5.15-portable_linux.tar.gz` from tag `v5.15` has SHA-256
`ae2a365bcac73f73e8fbffc0363e125c5ff6453ad89b90ac5891445ceb37e9bb`.
Its actual launcher reports `JabRef 5.15--2024-07-10--1eb3493`. The portable tree
is isolated under `/tmp`, using its bundled runtime; no system package is changed.
Version-specific `-n`, `-i ...,...` and `-o` options select the actual tested path.

The original #120 six-record attribution feeds the unchanged normally installed
#121 runtime wheel, `ackredit-0.11.0+25.gc39b1fc-py3-none-any.whl`, SHA-256
`ece4aa401f60b15725c135431f7510a04c8f0b6bbad25d64a500da27928499be`, from clean
source `c39b1fc492a469dd136d1840d942fe870ca612f0`. Python 3.14.8 and public
SMonitor 0.19.0 / ArgDigest 0.15.0 remain unchanged. Original wheel-file identities
verify after probes and tests, separately from all manager distribution files.
No Ackredit runtime source, dependency, schema, public API or release is changed.

Actual import preserves all exported fields and citation keys; its only byte
change is one final newline. Fresh-process reopen/resave is byte-identical to
that imported library. Distinct software IDs/releases and both DOI spellings,
dataset/article metadata, non-ASCII titles/names, institutional authors and
preferred CFF editors/prefix/suffix parts remain intact. The preferred book keeps
its own metadata, not the root software's version or DOI. Original attribution
and exported BibTeX bytes remain unchanged and no execution credit is created.

Pandoc 3.11 reads original/imported/reopened files identically. Its title case,
page and entry-kind conversion remains a separate observation rather than a
replacement original record. The manager preserves the synthetic ISBN; no ISBN
or registered-DOI validation is requested or inferred. The explicit importer
emits `WARN: JabRef could not open the key store`; warning and process status are
retained without treating the warning as a failed metadata import.

The [receipt](../../devtools/receipts/jabref_receiving_123_2026-10-06.json) retains
the official archive digest, full manager/runtime inventory, verified installed
wheel identities, original input, raw saved files, independent reader output,
commands/preferences and versioned source tools. Historical #120–#122 receipts
remain unchanged. **225 selected normally installed tests** pass outside the
checkout with `--receptor=llm --require-jabref-tools --require-publication-tools`
and the explicitly selected distribution, without skips. They include ordinary
and space-containing destinations, fresh preference profiles, requested-engine
absence, actual selected-launcher failure, parent-environment isolation, prior
evidence protection, source/BibTeX contracts, startup and suite isolation.

The guard checks complete raw manager files and equivalent reader observations,
distinct versions/names, distribution/original preservation, actual commands,
independent preferences and retained failure evidence. Ordinary CI may skip the
two live manager cases; the explicit installed local gate supplies those results.
Source/documentation checks overlap this installed selection; their totals are
separate evidence, not disjoint counts. Final-head hosted gates are recorded in
the owning issue before closure.

The source/documentation selection passes **366 tests**, including both real
manager paths, both BibLaTeX styles, classic publication engines, reporting/API
contracts and LaTeX escaping. It overlaps the 225 installed tests. Ruff
lint/format, generated indexes, pinned dependency-route preflight, local suite
conformance, strict Sphinx and whitespace checks pass. The failure guard compares
the selected launcher's resolved path so platform path aliases retain the same
execution contract; its final targeted recheck passes.

## Bounded theme M completion

Together #120–#123 satisfy theme M's representative receiving, metadata/name
coverage, conservative duplicate identity, selected presentation boundaries and
retained fixture/round-trip guards. This closes those bounded exit criteria,
with the publication guide naming exactly the accepted routes. Other managers,
GUI controls, enrichment/synchronization, duplicate detection/merge, journals,
beta/other versions, arbitrary Unicode and other platforms remain unqualified.
Future routes need separate receiving evidence; immutable public 0.11.0 and
future release qualification remain independent.
