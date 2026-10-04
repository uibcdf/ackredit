---
summary: Provenance rendering repeatedly expands shared graph descendants.
issue: uibcdf/ackredit#91
status: resolved
opened: 2026-10-04
closed: 2026-10-04
severity: medium
verification: reproduced
area: [reporting, performance]
guard: tests/test_provenance_scale.py::test_shared_subgraph_expands_once_and_retains_every_target
normative:
blocked_by: []
supersedes: []
---

# Shared and deep provenance graphs

## What

A 20-node/36-edge graph renders 2,048 lines without references. A regression
with two leaf references renders 3,072 lines. A valid flat linked graph longer
than the recursion limit raises `RecursionError`. Both behaviors reproduce
against the unchanged provenance renderer from `136b5d6`.

## How

Reachability and drawing now use explicit stacks. Each target expands once;
all parent/child edges remain, with an already shown shared target marked
`(shared; shown above)` separately from an ancestor cycle `(above)`. Each
target's references render once. Ordinary tree output remains unchanged.

## Why

Attribution is a graph: multiple workflow branches can use the same backend.
Expanding every path makes report time/output grow exponentially although the
stored evidence is small. Portable schema graphs are flat, so valid deep links
should not fail merely because rendering recurses.

## What was refuted

Removing edges, flattening to a bibliography or treating repeated links as
invocation counts would lose or invent evidence. The structural traversal visits
each node/edge once; total output still includes indentation and bibliographic
text, so character cost depends on depth/content.

## Scope and exclusions

Requested provenance/workflow rendering only, no capture/tracking optimization
claim, schema change, dependency or complete scientific execution trace.

## Acceptance criteria

Shared output is bounded by the stored nodes/edges, with every target/reference
and parent link retained. Deep valid graphs render, cycles remain identified,
ordinary trees retain their byte output and reproducible before/after graph-only
measurements retain samples and source hashes.

## Local evidence (2026-10-04)

The graph-only receipt `devtools/receipts/provenance_graph_91_2026-10-04.json`
retains 15 samples of 50 warmed renders and exact baseline/new renderer hashes.
The shared case changes from 2,048 to 40 lines and median 4,670.32 to 52.14 µs;
the ordinary chain keeps 22 lines (55.72 to 40.61 µs). These are synthetic
report timings, not tracking/capture or calculation speedups. Full local
Python 3.14.7 gates pass 1,694 tests, Ruff, report indexes and strict Sphinx.

## Resolution

Implementation `cb3e58df0a82ecc46da50f1969ddc921a097664e` passes ordinary
CI 37224726278 (seven jobs) and both policy lanes. Installed real-producer
matrix 37228402277 passes all eight Linux/macOS arm64 × Python 3.11–3.14
cells and the aggregate, with 48 tests and zero skips/deselections. Shared
parentage, recursion-depth and unchanged ordinary output guards pass in the
ordinary source CI; the receiving graph is also rendered in an independent
reader. The downloaded identities and local aggregate verify, with reviewed
evidence in `devtools/receipts/workflow_reporting_matrix_2026-10-04.json`.
