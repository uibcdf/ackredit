import time

import ackredit

# 1. Enable persistence, so nothing is lost if the script fails
ackredit.enable_persistence("session_cache.json")

# 2. Register an item with a DOI only, carrying no metadata
print("Registry: Registering item with DOI...")
ackredit.register_item(id="matplotlib:paper", doi="10.1038/nmeth.1618")

# 3. Enrich the metadata from Crossref
print("Enrichment: Fetching metadata from Crossref...")
ackredit.enrich_all()


# 4. Simulate a hierarchical workflow
@ackredit.scoped_usage("plotting_workflow")
def run_analysis():
    with ackredit.scope("initialization"):
        ackredit.track_item("matplotlib:paper")
        time.sleep(0.1)

    with ackredit.scope("heavy_computation"):
        # Simulate an injection for an external library
        ackredit.add_injection("numpy", ["paper:numpy"])
        ackredit.enable_import_hooks()
        import numpy  # noqa: F401  # the import itself triggers the citation

        time.sleep(0.1)


print("Workflow: Running scientific analysis...")
run_analysis()

# 5. Generate the citation package
print("Reporting: Dumping all formats to './citation_package/'...")
ackredit.dump(
    "citation_package", formats=["markdown", "bibtex", "provenance", "csl-json"]
)

# 6. Show the summary: plain text in a script, HTML in a notebook
print("\n--- QUICK SUMMARY ---")
print(ackredit.report(format="text"))

print("\nDone! Check the 'citation_package' directory for all files.")
