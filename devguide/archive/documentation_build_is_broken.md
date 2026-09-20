---
summary: The Sphinx build aborted on a missing linkify dependency, and four further defects hid behind it.
issue: uibcdf/ackredit#4
status: resolved
opened: 2026-09-20
closed: 2026-09-20
severity: medium
verification: reproduced
area: [documentation, tooling]
guard: .github/workflows/ci.yml
normative:
blocked_by: []
supersedes: []
---

# The documentation build aborts and cannot produce a site

## What

`docs/conf.py` enabled MyST's `linkify` extension without `linkify-it-py` installed, so
`sphinx-build` aborted before producing any output.

Four defects were hidden behind that failure:

- no extension handled `.ipynb`, so the Showcase toctree glob matched nothing and both
  showcase notebooks were written but never published;
- three docstrings (`scope`, `summary`) used a bare `Usage:` followed by an indented
  block, which docutils rejects;
- `html_static_path` pointed at a `_static` directory that did not exist;
- `devguide/status.md`, `roadmap.md` and `decisions.md` were duplicated under `docs/`,
  and `decisions.md` had already drifted from its source.

## How

```bash
python -m sphinx -b html docs /tmp/out
# ModuleNotFoundError: Linkify enabled but not installed.
```

Removing `linkify` revealed the rest: three docutils errors and one toctree warning.

## Why

Documentation that cannot be built is documentation nobody checks, which is how the rot
accumulated. No gate ever ran the build.

## What was refuted

`nbsphinx` was considered for the notebooks and rejected: it requires pandoc as a system
dependency, which is not present, so it would have traded one broken build for another.
`myst_nb` renders notebooks natively, needs no pandoc, and is what every other
MolSysSuite component already uses.

Declaring `linkify-it-py` rather than dropping the extension was also rejected: it only
auto-links bare URLs, which does not justify a dependency.

## Scope and exclusions

Covers the build, its configuration and the cross-reference conventions. Excludes the
conda packaging of the documentation environment: the suite pattern is
`devtools/conda-envs/docs_env.yaml` with a gh-pages workflow, which belongs with the
conda infrastructure Ackredit does not yet have.

## Acceptance criteria

Met by commit `11ce90e`:

- `python -m sphinx -b html -W docs <out>` succeeds with no warnings;
- `conf.py` matches the shared MolSysSuite setup: `myst_nb` with `nb_execution_mode`
  off, `myst_heading_anchors`, the same MyST extensions, `sphinx_copybutton`,
  `sphinx_design` and `autodoc_typehints` in descriptions;
- both showcase notebooks render;
- every page carries a label, internal links use `{ref}`, and API objects use `{func}`
  and `{class}`, verified to resolve to real anchors in the generated HTML;
- the duplicated devguide pages under `docs/` are `{include}` directives and cannot
  diverge again;
- a `docs` extra is declared and a CI job builds with `-W`, so a broken cross-reference
  or an unrenderable docstring fails the build.
