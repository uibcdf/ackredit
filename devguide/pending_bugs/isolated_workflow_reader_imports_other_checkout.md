---
summary: Workflow output guards can import an editable provider from another checkout.
issue: uibcdf/ackredit#77
status: partial
opened: 2026-10-02
closed:
severity: low
verification: reproduced
area: [tests, examples]
guard: tests/test_example_workflow.py::test_the_workflow_reader_prefers_its_checkout_over_another_editable_import
normative:
blocked_by: []
supersedes: []
---

# Isolated workflow readers must use their owning checkout

## What

The workflow-output guard launches a child interpreter from `examples/`.
In an isolated worktree, its editable Ackredit installation may resolve to a
separate checkout, so the guard compares one checkout's stored notebook with
another checkout's renderer. This was exposed while qualifying portable
attribution under uibcdf/ackredit#75 before guide delivery in
uibcdf/molsyssuite#71.

## How

A normal full run in the shared working tree passed 1,519 tests. An isolated
source run at `4228444` reported 1,439 passed and one workflow-output failure;
baseline `2e9f509` showed the same failure. The child was resolving the editable
installation in the original working tree, which contains separate uncommitted
cite-key changes. The outputs belong to different providers.

Setting the isolated checkout first on `PYTHONPATH` makes all eight original
workflow tests pass with the unchanged committed notebook. The initial diagnosis
of stale committed outputs was therefore refuted; no notebook correction is
needed. A regression supplies a competing provider that fails on import and
checks that the workflow reader still resolves the owning checkout.

The fix supplies an explicit source environment for the script and notebook
child interpreters, prepending their owning ROOT while preserving the existing
Python path. It changes test qualification, not product behavior. Keep kernel
and subprocess imports bounded to the source being qualified.

## Why

A dirty-tree success must not qualify a clean source through hidden imports from
another checkout; a correct committed example must not fail for the same reason.

## What was refuted

The notebook's committed outputs are correct. Portable capture did not alter
those outputs, and the maintainer's renderer/notebook work is not part of this
fix. The temporary refresh changed only execution timestamps and was restored
to the original committed artifact. Earlier stale-output claims in the initial
issue body were corrected before source publication.

## Scope and exclusions

Workflow test child-import isolation and a regression only. No BibTeX/LaTeX
implementation changes, notebook modifications or inclusion of the maintainer's
uncommitted content.

## Acceptance criteria

- The workflow reader chooses its own checkout over a competing Python path.
- The stored-output guard and isolated-source full suite pass.
- The maintainer's nine original files remain byte-identical to their backup.
- The source qualification fix is separately committed and its issue/report
  lifecycle is synchronized after publication.

## Validated local fix

The nine workflow tests pass, including the competing-provider regression.
The isolated full source suite passes 1,505 tests with the original committed
notebook. Ruff and devguide gates pass, and SHA-256 checks confirm that all nine
original maintainer files retain their original bytes. Publication and the
corresponding issue/archive transition remain pending.
