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
*   **Lean core:** Ackredit has three runtime dependencies and no more. Two are the
    MolSysSuite infrastructure components, `smonitor` and `depdigest`; the third is
    `pyyaml`, because `CITATION.cff` is YAML and reading it with less produces confident
    wrong answers on constructs the specification documents. All three are pure Python.

    This supersedes the original "Zero Core Dependencies" pillar. Reimplementing
    diagnostics, optional-dependency handling or a YAML parser inside a library that sits
    in every host is the duplication the suite exists to prevent. Everything beyond those
    three stays in `optional-dependencies`, and adding a fourth is a decision to record,
    not a convenience.
*   **Extensible:** Anyone can add new output formats or injections for third-party
    libraries, through a public function and an entry-point group each:
    `register_format` with `ackredit.formats`, and `add_injection` with
    `ackredit.citations`. A registered name is never replaced, so an extension adds to the
    library and cannot quietly change what it already does.

