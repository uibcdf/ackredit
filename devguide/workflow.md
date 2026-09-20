# Workflow and Standards

FlowCite follows the MolSysSuite common baseline. The suite owns the shared rules; see
[`../MOLSYSSUITE_GUIDE.md`](../MOLSYSSUITE_GUIDE.md). Local rules may be stricter, but they
must not silently contradict a common policy.

## System Requirements & Dependencies

Routine development uses Python 3.13; the supported user range is Python 3.11 to 3.13
(`requires-python = ">=3.11,<3.14"`), as required by the suite Python policy.

Some advanced features require additional software:

1.  **PDF Compilation:** Requires `pdflatex` and `bibtex` to be installed on the system (e.g., via TeX Live or MiKTeX).
2.  **Web UI:** Requires the `flask` Python package (install via `pip install flowcite[web]`).

## Golden Rules
1.  **Do not break optionality:** Any change must ensure that `flowcite` can be used optionally by another library.
2.  **Mandatory Tests:** Every new feature or bug fix must include a test in `/tests`.
3.  **Strict Typing:** All new code must use type hints.
4.  **Lean core:** Keep the runtime footprint small and put extra features behind
    `optional-dependencies`. The core was historically dependency-free; adopting the suite
    infrastructure components is tracked separately and any remaining deviation from the
    common baseline needs a documented exception with a reason and expiration condition.
5.  **English only:** Code, documentation, issues and commits are written in English.

## Local gates

```bash
ruff check .
ruff format --check .
pytest
python devtools/devguide_index.py --check
```

Ruff is the formatter, import sorter and linter, pinned to the suite policy release. The
required shared lint core is `E4`, `E7`, `E9`, `F` and `I`. The local cleanup sequence is
`ruff check --fix .` then `ruff format .`, review, and the complete test suite. Black,
isort and flake8 are not used.

`MOLSYSSUITE_GUIDE.md` is a synchronized, read-only copy listed in Ruff's `extend-exclude`;
never reformat or edit it here.

## How to Contribute
1.  Check `status.md` to see which tasks are pending, and the queues in
    `pending_bugs/` and `pending_proposals/` for tracked work.
2.  Open the owning GitHub issue first, following
    [`reporting_protocol.md`](reporting_protocol.md).
3.  Create a branch for the specific task.
4.  Validate with the four local gates above before committing.
