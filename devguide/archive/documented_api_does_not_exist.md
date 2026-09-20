---
summary: Documentation taught imports that raise ImportError, and the integration guide's except clause hid it.
issue: uibcdf/ackredit#3
status: resolved
opened: 2026-09-20
closed: 2026-09-20
severity: high
verification: reproduced
area: [documentation, integration]
guard: tests/test_documented_api.py
normative:
blocked_by: []
supersedes: []
---

# Documented API does not exist, and the integration guide hides it

## What

`standards/ACKREDIT_GUIDE.md` is the file host libraries copy into `_ackredit.py`. Its
template imported `registry` from `ackredit`, which is not exported. The template's own
`try`/`except ImportError` caught the failure, so a host with Ackredit installed and
importable would have run in no-op mode and recorded nothing, with no diagnostic.

The same broken import appeared in `DEVELOPER_GUIDE.md` and `ROADMAP.md`, together with
`from ackredit import injections`. `notes_dev.md` named `export_duecredit_json` and
`inject_into_duecredit`, which have never existed; the real function is
`export_to_duecredit`.

Three further defects in the template:

- the `scoped_usage` fallback took only `target`. The bind work in `uibcdf/ackredit#1`
  added `credit_bound`, so a host using it would raise `TypeError` exactly when Ackredit
  is absent, which is the case the optional-dependency pattern exists to protect;
- the advanced-features sections called `ackredit.enable_import_hooks()` and
  `ackredit.enable_persistence(...)` although the template never imported the module,
  raising `NameError`;
- `scope`, `bound_items`, `credit_bound` and `add_injection` had no fallbacks.

## How

```python
from ackredit import registry
# ImportError: cannot import name 'registry' from 'ackredit'
```

Reproduced directly, and then reproduced through the template: executing the documented
block leaves `ACKREDIT_INSTALLED` false in an environment where `import ackredit`
succeeds.

## Why

Silent no-op is the worst failure mode for a citation tracker. The workflow completes,
the report is empty, and nothing indicates that credit was lost. This was the file
`molsysmt` and `topomt` were about to copy.

## What was refuted

Exporting `registry` and `injections` as module aliases would have made every broken
snippet correct in two lines. It was rejected: it would expand the public surface only to
vindicate documentation that was never true, and leave two ways to do the same thing. The
flat API is what `__all__` exports and what the user guide already taught.

## Scope and exclusions

Covers documented names that do not resolve, and the integration template. Excludes the
prose and structure of the documentation site, tracked in `uibcdf/ackredit#4`.

## Acceptance criteria

Met by commits `dddea80` and `11ce90e`:

- the template imports the module and the flat names, and every exported name has a
  fallback whose signature matches the real one;
- fallbacks return `[]` rather than `None` where the real API returns a list, and `scope`
  is a context manager class;
- a new guide section tells integrators to assert `ACKREDIT_INSTALLED`, since silent
  fallback is the failure mode here;
- `tests/test_integration_guide.py` executes the template from the Markdown in both
  modes and compares every fallback signature against the real one. Verified to fail when
  either the original import or the old `scoped_usage` shim is reintroduced;
- `tests/test_documented_api.py` resolves every name every documented snippet imports
  from or reads off `ackredit`, across all Markdown and both notebooks. It found the
  `notes_dev.md` defect on its first run.
