(About_RelationToDueCredit)=
# Relation to DueCredit

Ackredit is conceptually related to the DueCredit project: both aim to collect and report citations
based on actual usage of scientific software. Ackredit extends the idea with:

- explicit separation of **static registration** and **dynamic tracking per code path**;
- first-class support for non-publication items (repos, websites, datasets);
- optional dependency pattern for embedding in other libraries;
- implemented export of collected references through `export_to_duecredit`,
  using DueCredit as an optional dependency.

The bridge forwards current-session references as DOI or BibTeX entries. It does
not import a DueCredit run into Ackredit or reconstruct detached result provenance.
See [interoperability](../developer_guide/interoperability.md) for its scope.
