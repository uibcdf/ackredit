# Workflow and Standards

Ackredit follows the MolSysSuite common baseline. The suite owns the shared rules; see
[`../MOLSYSSUITE_GUIDE.md`](../MOLSYSSUITE_GUIDE.md). Local rules may be stricter, but they
must not silently contradict a common policy.

## System Requirements & Dependencies

Routine development uses Python 3.14; the required source contract is Python
3.11–3.14 (`requires-python = ">=3.11,<3.15"`). Metadata, maintained environments,
recipe and full installed/source matrices follow that range. Use the maintained
Conda development environment and install Ackredit with `pip install --no-deps
--editable .`; SMonitor and DepDigest are distributed through the public `uibcdf`
channel, so a pip-only environment cannot resolve the core dependencies.

Some advanced features require additional software:

1.  **PDF Compilation:** Requires `pdflatex` and `bibtex` to be installed on the system (e.g., via TeX Live or MiKTeX).

## Golden Rules
1.  **Do not break optionality:** Any change must ensure that `ackredit` can be used optionally by another library.
2.  **Meaningful regression checks:** Executable features and fixes need relevant
    user-visible contract tests in `tests/` or `devtools/tests/`. Documentation
    and evidence use the applicable checks below; do not add tests that merely
    repeat prose or broaden to science without an affected boundary.
3.  **Strict Typing:** All new code must use type hints.
4.  **Lean core:** Keep the runtime footprint small and put extra features behind
    `optional-dependencies`. The four runtime dependencies are `smonitor`,
    `depdigest`, `argdigest` and `pyyaml`. Additional runtime dependencies need
    an owned decision; shared infrastructure remains provider-owned.
5.  **English only:** Code, documentation, issues and commits are written in English.

## Local gates

Select gates by the changed code, inputs and scope, following
[root instructions](../AGENTS.md#local-gates). Documentation and evidence require
applicable reporting/index, link and synchronized-guide checks; prose alone does
not require the scientific suite. Executable/dependency/packaging changes require
relevant contract tests plus applicable lint, format and type checks. Scientific
claims require informative cases and explicit limits. Available commands are:

```bash
ruff check .
ruff format --check .
pytest --receptor=llm
python devtools/devguide_index.py --check
```

Ruff is the formatter, import sorter and linter, pinned to the suite policy release.
The required shared lint core is `E4`, `E7`, `E9`, `F` and `I`. Review fixes from
`ruff check --fix .` and `ruff format .`, then run the selected applicable gates.
Retain existing results only while their code, inputs, environment and scope
remain applicable. Black, isort and flake8 are not used.

Use Pytest Receptor's `llm` profile locally and `ci` in hosted workflows. Inspect
remote execution with `gh run-receptor inspect RUN_ID --repo uibcdf/ackredit
--receptor=llm`; use targeted native evidence only for facts the report omits.
The root synchronized receptor guides define their contracts.

`MOLSYSSUITE_GUIDE.md` is a synchronized, read-only copy listed in Ruff's `extend-exclude`;
never reformat or edit it here.

## How to Contribute
1.  Start with [checkpoint.md](checkpoint.md), then current status and queues.
    Respect the adoption pause; resume for concrete owning feedback, a
    demonstrated defect or an explicit maintainer request.
2.  Open the owning GitHub issue first, following
    [`reporting_protocol.md`](reporting_protocol.md).
3.  Run the applicable scoped gates before committing; archive resolved reports
    and regenerate indexes together.
4.  Follow the [accepted direct-push/checkpoint policy](../MOLSYSSUITE_GUIDE.md#direct-pushes-and-validation-checkpoints).
    Authorized internal direct pushes by `dprada`/`LMMV` retain their approved
    scope; this is not blanket authorization for other contributors or sibling
    fixes. Batch focused commits where remote visibility is unnecessary. Finish
    with an unskipped head and inspect applicable CI, or follow the explicitly
    authorized exact-head manual route. Record missing evidence, owner and
    recovery; local administrative checks do not clear scientific backlog.
    External PRs, admission and publication require all mandatory executed gates
    for their exact candidate and required installed file.
