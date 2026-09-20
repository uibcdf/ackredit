# What is Ackredit?

**Ackredit** is a lightweight Python library designed to provide **runtime-aware citation and acknowledgement tracking** for scientific software and workflows.

## The Challenge
Scientific research increasingly relies on a complex stack of libraries, algorithms, and datasets. Typical citation practices are often imprecise:
*   Users cite a large library (like SciPy) but not the specific algorithm used.
*   Datasets or sub-modules go uncredited because they are buried deep in the execution path.
*   Citation lists in READMEs are static and often overwhelming.

## The Ackredit Approach
Ackredit solves this by tracking what is **actually executed** at runtime. It allows developers to:
1.  **Register items** (papers, repositories, datasets) with their metadata (DOIs, authors, etc.).
2.  **Bind items** to specific functions, methods, or code blocks.
3.  **Track dynamically** only those items that were triggered during a session.

## Key Features
*   **Hierarchical Provenance:** See exactly *why* a citation was triggered (which function called which).
*   **Auto-Discovery:** Automatically detect citations from `CITATION.cff` files or package metadata.
*   **Rich Formats:** Generate reports in BibTeX, CSL-JSON (for Zotero/Mendeley), Markdown, and compilable LaTeX/PDF.
*   **Ecosytem Ready:** Designed as an optional dependency that stays invisible if not installed.
*   **Automated Enrichment:** Fetch metadata automatically from DOIs via Crossref and DataCite.
