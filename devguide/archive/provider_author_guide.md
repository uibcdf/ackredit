---
summary: A concise author guide backed by an independently installed dependency-free provider.
issue: uibcdf/ackredit#113
status: resolved
opened: 2026-10-06
closed: 2026-10-06
verification: measured
area: [documentation, integration]
guard: tests/test_function_providers.py::test_normally_installed_provider_and_reader_outside_checkout
normative:
blocked_by: []
supersedes: []
---

# Provider author guide and installable example

## What

Complete roadmap G's author-facing documentation and reusable producer example.
The existing installed-provider fixture proves the boundary but is hidden under
tests; the full protocol guide is useful reference rather than a concise start.

## How

Promote that single producer to `examples/citation_provider`, route its existing
observer/evidence guards to the same source, and extend the installed guard for
dependency metadata and public development validation. Publish a short author
guide linked from the user guide and full protocol.

## Why

Authors can install, inspect and adapt one tested example with no Ackredit
runtime dependency. The guide distinguishes stable observation in public
>=0.11.0 from provisional development-only standalone validation, retaining
original versions, real-call semantics and selected lazy-loader side effects.

## What was refuted

A second declaration parser or a duplicate example would drift from the public
validator or installed guard. A new workflow is unnecessary: the existing source
matrix already executes the installed example test. The fictional bibliography
is demonstration data, not evidence of scientific citation correctness.

## Scope and exclusions

Documentation, example discoverability and installed producer/reader behavior.
No new Ackredit API, observation boundary, public release, API promotion or
acceptance of the separate evidence contracts.

## Acceptance criteria

- The ordinary installed example computes with Ackredit imports blocked and has
  no runtime requirements.
- Standalone validation preserves exports, credit and bibliography; observed
  actual calls save software/article references, exclude untaken references and
  retain original versions for a reader that cannot import the producer.
- The concise guide and linked example preserve contract and release limits.
- Applicable reporting/index, Ruff, documented API, strict docs, dependency-route
  and exact-head CI checks pass.

## Verification and delivery

Local Python 3.14.7 gates pass 389 selected tests: function providers, recorder
evidence, standalone validation, documented APIs, reporting, packaging and API
stability. The installed guard was rerun separately after sandbox DNS prevented
setuptools download; it passes with authorized network access. The remaining
388 cases passed in the initial selection with no skips or warnings. This is
selected boundary evidence, not a new full scientific or release qualification.

Ruff 0.16.5 lint and format, generated indexes, the 16 dependency routes and
strict Sphinx pass. Sphinx's external Python inventory required authorized
network access. The owning #113 issue records the published exact source head
and its hosted controls after publication; local editable installation is not
evidence for a new immutable public artifact. No synchronized guide was edited.
