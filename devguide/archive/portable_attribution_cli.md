---
summary: Read and export original saved attribution through the existing CLI report command.
issue: uibcdf/ackredit#101
status: resolved
opened: 2026-10-05
closed: 2026-10-05
severity: medium
verification: reproduced
area: [cli, portability]
guard: tests/test_cli_attribution.py
normative:
blocked_by: []
supersedes: []
---

# Portable attribution CLI

## What

Roadmap theme I starts by completing the saved-result reporting lifecycle.
The existing CLI reports identifier journals without original bibliography.
Complete portable records already have a validated Python reader and renderer.

## How

Extend `report` with explicit `--input-format attribution`; the default remains
`session`. Reuse `Attribution.from_json` and `Attribution.report`. Add `--output`
for a single requested export instead of stdout. Validate and render before
opening output and refuse output aliases of the input. Catalog failures return
nonzero without repeating the catalog message.

## Why

An external user must obtain faithful original bibliography, roles, context
and graph in a fresh reader without keeping the producer or live registry.
The existing format registry is the authoritative reusable rendering tool.

## What was refuted

Do not guess a contract from a filename, reconstruct bibliography from today's
installed producer, treat bibliography JSON as a complete portable record,
or turn saved uses into new execution credit. No separate renderer is needed.

## Scope and exclusions

CLI, diagnostics, user guidance and contract tests only. No new schema,
composition operation, dependency, public Python API, provisional promotion,
canonical client guide or release/tag. Source qualification and public delivery
remain separate.

## Acceptance criteria

- Fresh CLI reports and exports the real schema-1 PyUnitWizard record through
  all built-in formats, retaining its original metadata and contextual workflow.
- The original producer, unit engines, network and live tracking are unnecessary.
- Invalid/unknown records, formats, UTF-8 and filesystem failures return nonzero;
  rendering failures leave output unchanged and input aliases are refused.
- Empty records and existing session report/aggregate/dump remain usable.
- Applicable quality, documentation/reporting and normally installed candidate
  tests pass; inspect exact-head CI and archive this record on completion.

## Resolved outcome — 2026-10-05

`ackredit report FILE --input-format attribution` reads the released schema-1
contract through the existing portable reader and renders original metadata
through the format registry. `--output/-o` writes the selected UTF-8 report.
Default session reporting, journal aggregation and dump retain their contracts;
`json` remains bibliographic output, separately from the full saved payload.

The frozen real PyUnitWizard record passes fresh CLI reporting through all
built-in formats and the `csl` alias. Exports retain original metadata, versions,
roles and graph where the selected format supports them. A blocked producer,
Pint/unyt imports, socket connections, registration and session operations do
not prevent the offline workflow report; its original session/registry remain
unchanged. Invalid records and formats leave output untouched. Missing files,
directories, invalid UTF-8, missing output parents and same/symlink/hardlink
input aliases return nonzero with catalog diagnostics. Empty records remain valid.

Python 3.14.7 source checks pass 1,865 tests without skips; the focused CLI,
portable-reader and diagnostics selection passes 154. Ruff check/format,
devguide indexes and strict nitpicky Sphinx pass. A normally installed temporary
environment also runs the console script outside the checkout, exports the
original DOI and passes `pip check`; its three changed runtime modules match
the tested source byte-for-byte. This development environment shares the
existing scientific dependency foundation, so it is not a new clean public
channel installation or release qualification.

Source qualification does not publish a new artifact, promote provisional APIs
or change portable schema/client guides. Roadmap theme I marks its CLI milestones
complete while composition remains a separate next implementation. Future public
delivery retains the exact-candidate gates and independent artifact verification.
