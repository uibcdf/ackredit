---
summary: Qualify unchanged detached BibTeX exports in a real BibLaTeX/Biber reader and style.
issue: uibcdf/ackredit#122
status: resolved
opened: 2026-10-06
closed: 2026-10-06
severity: medium
verification: reproduced
area: [formats, publication]
guard: tests/test_biblatex_receiving.py
normative:
blocked_by: []
supersedes: []
---

# BibLaTeX and Biber receiving

## What

Theme M has real BibTeX/plain and Pandoc/citeproc evidence under #120/#121.
An unchanged exported bibliography still needs an independently observed
BibLaTeX/Biber receiving boundary before that compatibility can be claimed.

## How

Extend the existing publication-probe owner with a reusable offline devtool.
Use the original detached six-record synthetic attribution, unchanged exporter,
normally installed Ackredit and explicitly identified tools/style. Read actual
backend output separately from compiled style output; retain original bytes.

## Why

A successful classic BibTeX style does not establish Biber data-model handling,
version retention or BibLaTeX presentation. Distinct releases and declared names
must survive the receiving route even where a selected style omits fields.

## What was refuted

Pandoc's BibTeX reader is not Biber. Compilation alone is not evidence that all
original metadata survives, and a style's choice is not authority to rewrite
original bibliographic claims. This checkpoint cannot qualify a manager GUI.

## Scope and exclusions

One real BibLaTeX/Biber pair and named standard style on local Linux/Python 3.14.
Optional engines remain development tools. No dependency floors, public API,
saved schema, original claims, automatic merging or release are changed.
Journal styles, other engines/platforms and reference-manager imports stay open.

## Acceptance criteria

- Preserve detached input, exported fields and existing execution credits.
- Observe distinct six-record IDs and versions, institutional names and editors
  in actual backend output; compile with explicitly identified tools/style.
- Retain warnings/omissions and distinguish reader metadata from display.
- Reusable tooling rejects missing engines, process failure and prior outputs.
- Guard the observed mechanism, retain a sanitized installed receipt and update
  publication guidance, indexes and the owning issue with bounded evidence.

## Executed receiving checkpoint (2026-10-06)

`devtools/check_biblatex.py` is the reusable offline route in the existing
publication-probe owner. It exports detached attribution through the unchanged
BibTeX renderer, identifies resolved executables and actual loaded TeX resources,
runs Biber tool-mode XML and manuscript BBL separately, then compiles and extracts
presentation for standard `authoryear` or `numeric`. Existing destinations and
missing requested tools fail; process errors propagate with retained streams.
No engine is installed by the probe or selected as a fallback.

The original six-record #120 input is received by the same normally installed
#121 wheel, `ackredit-0.11.0+25.gc39b1fc-py3-none-any.whl`, SHA-256
`ece4aa401f60b15725c135431f7510a04c8f0b6bbad25d64a500da27928499be`, from clean
runtime `c39b1fc492a469dd136d1840d942fe870ca612f0`. Its Python 3.14.8 prefix
retains public SMonitor 0.19.0 / ArgDigest 0.15.0; all original shipped-file
identities verify unchanged after probes and tests. No runtime source, API,
dependency, saved schema or immutable public release is changed here.

Official historical BibLaTeX 3.19 / Biber 2.19 archives and Logreq 1.0 are isolated
under `/tmp`, with the existing pdfTeX 1.40.25 / TeX Live 2023 Debian engine.
Downloaded BibLaTeX 3.22a fails its initial TeX pass on the host kernel's missing
`IfDocumentMetadataT`; downloaded Biber 2.22 is not exercised in that pass.
This refutes a latest-pair claim, not Ackredit interoperability with every pair.

Both selected styles compile and display software versions 1.0/2.0 and dataset
version 2024.1. Actual Biber XML/BBL preserve six distinct IDs, both original DOI
spellings, institutional names as indivisible names and declared editor
prefix/suffix parts. The CFF preferred work keeps its own book metadata without
the root version or DOI. Original input and exported BibTeX bytes are identical
across styles; no execution credit is created. Name order and extracted
discretionary line-break hyphens are presentation, never replacement records.

Biber warns about the original synthetic ISBN `978-0-00-000000-0` in both routes;
it is retained, not silently repaired. Standard styles omit the generic record's
publisher even though the XML and BBL retain it. Compilation does not establish
valid registration, lossless formatted output or metadata-validation success.

The real installed tests expose the shared process capturer's UTF-8-only
assumption: pdfTeX produces a non-UTF-8 diagnostic byte and raises decoding failure
before the streams/status are saved. `check_publication_tools._run` now captures
exact bytes first, hashes both streams, and renders undecodable bytes as explicit
backslash escapes. A regression emits non-UTF-8 stdout/stderr with exit 9 and
checks their original bytes, hashes and retained failure. The classic publication
route is rechecked. The original #120/#121 receipts remain unchanged; their
process-owner source is retained separately rather than freezing future tooling.

The [receiving receipt](../../devtools/receipts/biblatex_receiving_122_2026-10-06.json)
retains official archive hashes, installed identity, original input, actual reader
and presentation exports, loaded fonts/format/style identities and source tools.
**221 selected normally installed tests** pass outside the checkout with
`--receptor=llm --require-publication-tools --require-biblatex-tools`, without
skips. They exercise both actual styles, classic engines, DOI/original fidelity,
BibTeX contracts, process failures, startup and suite isolation. The later
guidance-only guard and source/documentation gates are separate, overlapping work.

The final source/documentation selection passes **356 tests**, including that
guidance guard, both real styles, classic publication engines, reporting/API
contracts and LaTeX escaping. It overlaps the installed selection; the counts
are not disjoint. Ruff lint/format, generated indexes, pinned dependency-route
preflight, local suite conformance, strict Sphinx and whitespace checks pass.

The guard protects backend records and distinct versions, original bytes,
selected presentation, mixed-encoding failure preservation and the retained
receipt. Ordinary CI may skip the two external Biber cases; this executed local
installed gate supplies that evidence. Latest tools, manager imports, journal
styles, arbitrary Unicode and other platforms remain open. Hosted final-head
gates are recorded in the owning issue before closure.
