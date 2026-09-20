# Roadmap

## Phase 1: Core Consolidation (0.1.0) - [DONE]
*   [x] Refactor the BibTeX generator to be robust.
*   [x] Implement the documented and tested 'Optional Dependency' pattern.
*   [x] Add the Context Manager for granular tracking.

## Phase 2: Automation & Metadata (0.2.0) - [DONE]
*   [x] Launch `ackredit.contrib.jupyter` for rich visualization.
*   [x] Auto-discovery of `CITATION.cff` and package metadata.
*   [x] DOI Enrichment (Crossref).
*   [x] Session Persistence and Auto-reminders.

## Phase 3: Ecosystem & Connectivity (0.3.0) - [DONE]
*   [x] **Plugin System (Entry Points):** Allow external libraries to ship citation packs.
*   [x] **Metadata Cache:** Persistent storage for fetched DOI metadata.
*   [x] **DueCredit Bridge:** Interoperability with DueCredit.
*   [x] **CLI Tool:** Command-line reporter for stored sessions.

## Phase 4: Full Feature Set (0.5.0) - [DONE]
*   [x] **LaTeX/PDF Suite:** Compilable bibliographies and automatic PDF build.
*   [x] **Multi-session Aggregator:** Merge JSON sessions from HPC/parallel runs.
*   [x] **DataCite Support:** Track datasets and Zenodo software via DOI enrichment.
*   [x] **Custom Styles:** Support for different bibliography styles in LaTeX.
*   [x] **Deep API Inspection:** Detect algorithm usage via AST analysis (hybrid).

## Towards Stable Release (1.0.0)
1.  **API Hardening:** Finalize signatures and ensure backward compatibility.
2.  **Exhaustive Testing:** Integration tests with all MolSysSuite tools.
3.  **Comprehensive Docs:** Tutorials, use cases, and full API documentation.
