(Dev_WhatIsAckredit)=
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
*   **Zero Core Dependencies:** The Ackredit core must be pure Python to facilitate its inclusion in any environment.
*   **Extensible:** Anyone can add new output formats or injections for third-party libraries.

