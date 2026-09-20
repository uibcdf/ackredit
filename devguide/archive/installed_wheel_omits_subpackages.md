---
summary: A literal package list shipped only __init__ and cli, so an installed FlowCite could not be imported.
issue: uibcdf/ackredit#2
status: resolved
opened: 2026-09-20
closed: 2026-09-20
severity: critical
verification: reproduced
area: [packaging]
guard: tests/test_packaging.py
normative:
blocked_by: []
supersedes: []
---

# An installed wheel omits every subpackage

## What

`pyproject.toml` declared:

```toml
[tool.setuptools]
packages = ["flowcite"]
```

A literal list names exactly one package. `flowcite.core`, `flowcite.formats` and
`flowcite.contrib` were never included, so a built wheel contained only
`flowcite/__init__.py` and `flowcite/cli.py`. Since `flowcite/__init__.py` imports
from `.core.registry` on the first line, importing the installed distribution raised
`ModuleNotFoundError: No module named 'flowcite.core'`.

## How

```bash
python -m pip wheel --no-deps -w dist .
python -m zipfile -l dist/flowcite-*.whl      # only __init__.py and cli.py
python -m pip install --target /tmp/probe dist/flowcite-*.whl
PYTHONPATH=/tmp/probe python -c "import flowcite"
```

Reproduced before the fix and verified after it: the wheel now ships all 25 modules,
and an import from an installed prefix followed by `register_item`, `track_item` and
`report` succeeds.

## Why

The package was unusable in the only way a host library would consume it. Every
release from 0.1.0 onward carried the defect.

It stayed invisible because the test suite imports `flowcite` from the repository
root, where the source tree is already on `sys.path`. Every local gate passed while
the distribution was broken, so no existing check could have caught it.

## What was refuted

Not a metadata or entry-point problem: `flowcite.cli:main` resolved correctly, and
the failure was purely the absence of the subpackage directories from the archive.

## Scope and exclusions

Covers package discovery for the distribution. Excludes the conda recipes and the
release workflow, which FlowCite does not yet have.

## Acceptance criteria

Met by commit `8e36ce7`, with the guard added when this record was filed:

- `[tool.setuptools.packages.find]` with `include = ["flowcite*"]` replaces the
  literal list;
- a built wheel contains `flowcite`, `flowcite.core`, `flowcite.formats` and
  `flowcite.contrib`;
- importing and using the installed distribution outside the source tree works;
- `tests/test_packaging.py` fails if the literal list returns, checking the declared
  discovery patterns against the packages present on disk rather than building a
  wheel, so the guard stays fast and needs no build backend.

## Correction (2026-09-20)

The repository was renamed from `flowcite` to `ackredit` after this record was
archived. The owning issue keeps its number and is now `uibcdf/ackredit#2`; the
front matter was updated to follow that identity. The analysis above is left as
written, because the defect it describes occurred under the former name and
rewriting it would misstate the history.
