---
summary: Render original bibliography, contextual uses and pipeline graph together.
issue: uibcdf/ackredit#89
status: active
opened: 2026-10-04
closed:
verification: reproduced
area: [reporting, integration]
guard: tests/test_workflow_report.py::test_saved_workflow_report_preserves_reference_roles_and_original_versions
normative:
blocked_by: []
supersedes: []
---

# Readable contextual workflow reports

## What

The existing portable payload records bibliography, roles, original versions,
context and graph separately. The explicitly selected `workflow` format puts
them together in a readable Markdown report without changing the payload.

## How

Saved `Attribution.report(format="workflow")` reads only its detached payload;
the live report obtains the existing current-workflow snapshot. Bibliography
presentation shares the Markdown renderer; reference numbers join contextual
use rows to exact records. The graph reuses the provenance renderer. Original
capture/use contexts and additional bibliography fields remain explicit.

## Why

A software description article and two software versions can share one
bibliographic identity while describing different uses. Bibliography alone
cannot show that relationship. Counting distinct recorded uses is useful but
does not prove invocation counts, scientific success or complete instrumentation.

## What was refuted

Readers must not rediscover citations from the current environment, infer roles
from bibliographic type or overwrite an article with its describing software's
version. A new schema, renderer-plugin signature or tracking-path dependency is
unnecessary. Existing formats keep their behavior and selection.

## Scope and exclusions

One built-in development format, reserved name `workflow`, with `.md` output.
Plugins previously using this name must choose another. No public 0.9.0 claim,
API promotion, tag or canonical-guide rollout. Provisional function-provider
decisions remain in #84/#87 and MolSysSuite #97/MOLI #46.

## Acceptance criteria

Original versions, software/article roles, context and graph survive a saved
producer-free reader; references connect to contextual uses without invented
counts/success. Legacy, unscoped, empty, missing-bibliography and cyclic/shared
graphs remain readable. External metadata cannot break tables or code fences.
Existing plugins and Markdown bibliography remain compatible; local full
gates and the designated installed real-producer matrix pass.

## Local development evidence

The first test-first run refuses `workflow` as an unknown format. Implemented
guards now pass original-version/shared-article, frozen live bibliography,
legacy/unscoped, empty scope, recursive graph, safe markup/fences, fresh offline
reader and dump collisions. Nested-plugin isolation is separately tracked in
#90; shared/deep graph rendering in #91.

External duplicate uses are counted distinctly without modifying the original
payload. Same-title software versions retain separate reference numbers in the
graph. Newlines/control characters are visible escapes in graph labels, so
external metadata cannot invent hierarchy. Full local Python 3.14.7 gates pass
1,694 tests, Ruff, indexes and strict Sphinx. The designated installed gate now
requires six passed tests per cell, including a separate real report reader.
