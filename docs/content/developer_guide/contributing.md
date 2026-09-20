(Dev_Contributing)=
# Workflow and Standards

## System Requirements & Dependencies

Ackredit aims to be zero-dependency for its core features. However, some advanced features require additional software:

1.  **PDF Compilation:** Requires `pdflatex` and `bibtex` to be installed on the system (e.g., via TeX Live or MiKTeX).
2.  **Web UI:** Requires the `flask` Python package (install via `pip install ackredit[web]`).

## Golden Rules
1.  **Do not break optionality:** Any change must ensure that `ackredit` can be used optionally by another library.
2.  **Mandatory Tests:** Every new feature or bug fix must include a test in `/tests`.
3.  **Strict Typing:** All new code must use type hints.
4.  **Zero-Dependency Core:** Keep `[project.dependencies]` empty. Use `optional-dependencies` for extra features.

## How to Contribute
1.  Check `status.md` to see which tasks are pending.
2.  Create a branch for the specific task.
3.  Validate with `pytest`.
