---
summary: Validate detached bibliography with BibTeX/plain and Pandoc/citeproc.
issue: uibcdf/ackredit#120
status: resolved
opened: 2026-10-06
closed: 2026-10-06
severity: medium
verification: reproduced
area: [formats, attribution]
guard: tests/test_publication_tools.py
normative:
blocked_by: []
supersedes: []
---

# Bibliography in real publication tools

## What

Implement the first bounded checkpoint of roadmap theme M: actual BibTeX and
Pandoc/citeproc receiving evidence for detached BibTeX and CSL-JSON exports.

## How

Retain synthetic software releases, dataset/article records and a typed CFF
preferred work. Save attribution before exporting; read it outside the producing
registry and run the existing external engines with identified styles. Separate
input fidelity, engine import and formatted presentation.

## Why

Internal renderer assertions do not establish real publication interoperability.
Real style engines may omit valid metadata; a successful process alone does not
prove that names and works remain identifiable.

## What was refuted

Process success alone does not establish fidelity: the baseline BibTeX run
returns zero while issuing two sorting warnings and losing both editor lists.
Pandoc's BibTeX reader independently loses them, while the CSL-JSON export and
citeproc keep them. The normalized CFF reader is not responsible for that loss;
BibTeX field/name rendering and work-kind mapping own the repair.

## Scope and exclusions

BibTeX/plain and Pandoc's identified default CSL style, with synthetic fixtures
and retained exact versions/inputs. No new release, required runtime dependency,
reference-manager GUI import, BibLaTeX/Biber qualification, journal-wide style
promise or duplicate-identity merge policy. Keep all broader theme M items open.

## Acceptance criteria

- Detached exports keep original records, software versions and distinct IDs;
  offline reading neither imports a producer nor creates execution credit.
- Actual engines read the exports and identify the retained works/names.
- Fix Ackredit-owned defects found by this probe with mechanism-specific guards.
- Retain receipt, tool/style identities and reproducible fixtures/commands.
- Maintain user guidance distinguishing format fidelity from style presentation.

## Executed correction and receiving evidence (2026-10-06)

The baseline is normally installed wheel `0.11.0+20.g9a27f1b`, from clean source
`9a27f1b4f46c9392f911670f90ad7e8b12ff56c8`. The corrected wheel is
`0.11.0+22.g9efa863`, from clean source
`9efa863914b69f7fc35442f1baab4c25fd08c881`, SHA-256
`294abc93d7f4015f3428c7ec86e8de7f3737b6504c1c3a2d3fbf4d6f29497e4a`.
Both use public SMonitor 0.19.0 and ArgDigest 0.15.0. A separate native Conda clone
preserves the prior environment; the corrected wheel is installed with `--no-deps`
and verified against every original shipped package file before and after tests.
The public Ackredit 0.11.0 archive is unchanged and lacks this repair.

Exactly the same saved attribution bytes feed both receiving probes. Six synthetic
records include two software releases, dataset/article metadata, explicit editors
and a CFF preferred edited collection with corporate names, particles, suffixes
and non-ASCII text. Before/after exports, engine-read data, bibliography output,
engine/style identities and wheel verification are retained in
[`publication_tools_120_2026-10-06.json`](../../devtools/receipts/publication_tools_120_2026-10-06.json).

The owning BibTeX renderer now maps plural editors to `editor`, renders explicit
editor objects as names, reuses the shared private CFF name-declaration reader
and recognizes declared CFF book/edited-work types as `@book`. Stale hints never
override explicit name-list replacement. Generated untyped misc entries retain
editor metadata and get a sorting key when the style cannot use the editor.
Imported BibTeX types and LaTeX names remain original.

The candidate passes **255 selected normally installed Python 3.14.8 tests**
outside the checkout, including all 12 original checkpoint cases with
`--require-publication-tools --receptor=llm`. Actual BibTeX 0.99d / `plain.bst`
has zero warnings, pdfTeX 1.40.25 compiles the PDF, and Pandoc 3.11's two readers
retain all six IDs, software versions and DOI forms. Its bundled Chicago 18
author-date style renders all references, editors, versions and DOI links.
`pip check` and before/after installed file identities pass. Later receipt and
guidance guards are separate from this original installed selection.

The final local reporting/documentation/API selection passes 275 cases, including
the two new receipt/guidance guards and repeated designated engine cases. These
overlap the installed selection and are not an additional disjoint scientific
matrix. Ruff check/format, generated indexes, pinned dependency-route preflight,
local suite conformance and strict Sphinx build pass. Exact-head hosted CI is
inspected separately before issue closure.

The guard asserts singular editor syntax and actual name identity in both
engine-read records and the rendered collection, so it protects the reproduced
loss rather than relying on process status. Portable assertions execute without
external tools; ordinary missing-tool environments explicitly skip the engine
cases, and the designated local command fails instead. The independently useful
repository tool consumes any saved attribution, identifies engines/styles,
preserves original inputs and execution credits, refuses an existing destination
and propagates process failures while retaining local output.

## Retained limitations and follow-up

`plain.bst` does not print version/DOI fields and ignores editors on `@misc`.
Imported `@software` is preserved and emits the expected undefined-type warning.
Pandoc's BibTeX reader changes capitalization and does not reconstruct software
type from `@misc`; these converted records never replace saved attribution.
A full-URL DOI is retained but receives a duplicated prefix in the tested CSL
presentation. DOI normalization, duplicate identity and reference-manager imports
remain explicit theme M work. No merge, scientific equivalence, arbitrary Unicode,
other-style coverage or public release qualification is inferred.

The [publication guide](../../docs/content/user_guide/publication_tools.md) and
roadmap record this bounded checkpoint; all broader M checkboxes remain open.

## Hosted isolation correction (2026-10-06)

Initial head `19e12975dd3dc0a45a4c97914b625ca80d5f606b` passes lint/docs and
both policies but fails one assertion in each full test cell in
[run 37534019846](https://github.com/uibcdf/ackredit/actions/runs/37534019846):
`test_suite_isolation` rejects the new fixture's direct `Registry.items.clear()`.
The fixture already requests `clean_registry`, but the repository additionally
requires fixture-owned temporary replacement for the detached reader probe.
It now uses `monkeypatch.setattr`, restoring the prior registry automatically.
The isolation guard is retained unchanged. The corrected publication module and
complete isolation guard pass **114 normally installed cases** with the required
external engines. Ruff check/format pass. Runtime files, original candidate wheel
and receiving receipt remain unchanged; a new exact-head full CI run is required
before closing #120. This correction does not rewrite the original local evidence.

## Process-owner evolution under #122 (2026-10-06)

The separate BibLaTeX receiving route exposes mixed-encoding pdfTeX diagnostics
that the original UTF-8-only process capturer cannot retain. The shared devtool
owner now captures exact stdout/stderr bytes before text rendering, preserving
their hashes and real process status. #120's installed wheel, input, output and
receipt remain historical and unchanged. The
[#122 receipt](../../devtools/receipts/biblatex_receiving_122_2026-10-06.json)
retains the original process-owner source bytes and hash; this report's guard
verifies that snapshot instead of requiring future tools to remain frozen.
The current classic publication route is rechecked alongside the new Biber route.
