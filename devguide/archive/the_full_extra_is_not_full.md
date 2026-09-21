---
summary: duecredit was declared as an optional feature with no extra installing it, so `full` was not full.
issue: uibcdf/ackredit#32
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: low
verification: measured
area: [packaging]
guard: tests/test_packaging.py
normative:
blocked_by: []
supersedes: []
---

# The full extra is not full

## What

`ackredit/_depdigest.py` declares `flask` and `duecredit` as optional libraries, and
`ackredit.dependency_info()` reports both as features the environment may support.
`pyproject.toml` declared `web = ["flask"]` and `full = ["flask"]`.

So `duecredit` had no extra at all. `pip install ackredit[full]` left
`export_to_duecredit()` raising `ACKREDIT-E003` — the diagnostic for a missing dependency —
for a user who had asked for everything.

## How

One extra per optional feature, and `full` as their union.

## Why

`dependency_info()` exists to tell a user what their environment supports. Naming a feature
there while offering no way to install it turns an informative report into a dead end.

## What was refuted

- **Letting `full` be the only extra that carries `duecredit`.** The first version of the
  guard accepted that, because a library reachable through `full` is reachable. It
  contradicted the rule written beside it in `pyproject.toml`, and a guard that does not
  check what the comment claims is how the two drift apart. `full` is excluded from that
  test now, so each feature must be installable without dragging in the others.

## Scope and exclusions

Covers the optional Python distributions. `pdflatex` and `bibtex` are system binaries,
deliberately outside DepDigest and probed with `shutil.which`.

## Acceptance criteria

- every library declared to DepDigest has an extra of its own — met;
- `full` contains all of them — met;
- both computed from `pyproject.toml` and `_depdigest.py` rather than written twice.
