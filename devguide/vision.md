# Vision and Concept: The Ackredit Bible

## What is Ackredit?
Ackredit is a runtime citation and acknowledgement tracking engine for scientific workflows in Python.

Unlike static citation lists (which tell you what to cite just by installing a library), Ackredit is **context-aware**: it only asks you to cite what you actually used during the execution of your code.

## Why does it exist? (The Value)
1.  **Fairness in Attribution:** It allows giving credit to specific algorithms, datasets, or sub-modules that would otherwise be hidden under the general name of a large library.
2.  **Noise Reduction:** Users only receive a list of what is relevant to their current analysis.
3.  **Automation:** Generates reports ready for publications (BibTeX) or notebooks (Markdown) without manual effort.
4.  **Workflow Integration:** Designed to integrate seamlessly into a researcher's daily life, aiming for compatibility with modern reference managers (like Zotero via CSL-JSON) and providing absolute transparency on *why* something is cited.

## Ecosystem: MolSysSuite
Ackredit is a core support library within the **MolSysSuite** ecosystem. It sits hierarchically alongside other specialized support tools:
*   `argdigest` (Argument validation)
*   `depdigest` (Dependency management)
*   `smonitor` (Session monitoring)
*   `pyunitwizard` (Unit conversion)

All these libraries, including Ackredit, share a common purpose: providing robust infrastructure for scientific host libraries like `molsysmt`.

### Integration Pattern
Following the suite's standard, host libraries should centralize Ackredit usage through a `_ackredit.py` file. This ensures:
1.  **Optionality:** The host library functions even without Ackredit.
2.  **Centralization:** All citation registration and tracking logic are easy to find and maintain.
3.  **Consistency:** Users across the ecosystem find familiar patterns in every library.

## Design Pillars
*   **Invisible and Optional:** If Ackredit is not installed, the host library must continue to function without changes.
*   **Lean core:** Ackredit has four runtime dependencies and no more. Three are the
    MolSysSuite infrastructure components — `smonitor` for diagnostics, `depdigest` for
    optional dependencies and `argdigest` for arguments; the fourth is `pyyaml`, because
    `CITATION.cff` is YAML and reading it with less produces confident wrong answers on
    constructs the specification documents. All four are pure Python.

    This supersedes the original "Zero Core Dependencies" pillar. Reimplementing
    diagnostics, optional-dependency handling, argument auditing or a YAML parser inside a
    library that sits in every host is the duplication the suite exists to prevent.
    Everything beyond those four stays in `optional-dependencies`, and adding a fifth is a
    decision to record, not a convenience.

    ArgDigest arrived last and on evidence, in `uibcdf/ackredit#62`: six public functions
    accepted arguments that could not be right, and `bind("t", "paper:2024")` bound eight
    citations, one per character. It is used where it fits — declaration and reporting —
    and not on the tracking path, which runs once per credited citation and where the
    decorator costs 11.71 µs against 1.02.
*   **Extensible:** Anyone can add new output formats or injections for third-party
    libraries, through a public function and an entry-point group each:
    `register_format` with `ackredit.formats`, and `add_injection` with
    `ackredit.citations`. A registered name is never replaced, so an extension adds to the
    library and cannot quietly change what it already does.

