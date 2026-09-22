"""The single authoritative source of Ackredit's diagnostic codes and wording.

`_smonitor.py` imports `CODES` and `SIGNALS` from here rather than redefining
them, so an emitted code cannot drift away from its template.

Every entry writes `user_*` and `dev_*` fields. Per-profile fallback only arrived
in SMonitor 0.14, and Ackredit supports 0.13, where an entry defining one field
renders empty in the other profiles.

Prose belongs here. The typed facts of an occurrence belong to the call site, in
`extra`.
"""

CODES = {
    # --- Session persistence -------------------------------------------------
    "ACKREDIT-W001": {
        "title": "Saved session could not be read",
        "user_message": "The citation session at '{path}' could not be read, so this run starts empty.",
        "user_hint": "Previously collected citations in that file are not lost; check whether it is valid JSON.",
        "dev_message": "enable_persistence failed to load '{path}': {error_type}: {error}.",
        "dev_hint": "The file is written atomically, so a truncated document points at an external writer.",
    },
    "ACKREDIT-W002": {
        "title": "Session could not be saved",
        "user_message": "Citations collected so far could not be written to '{path}'.",
        "user_hint": "Check that the directory exists and is writable; tracking continues in memory.",
        "dev_message": "_save_state failed for '{path}': {error_type}: {error}.",
        "dev_hint": "The temporary file is removed on failure; no partial document is left behind.",
    },
    "ACKREDIT-W003": {
        "title": "Session file skipped while merging",
        "user_message": "The session file '{path}' was skipped while merging; its citations are not in this report.",
        "user_hint": "Aggregation continues with the remaining files. Re-run the job that produced it if the citations matter.",
        "dev_message": "aggregate skipped '{path}': {reason}.",
        "dev_hint": "A missing file is skipped silently by design; this code covers unreadable ones.",
    },
    # --- Discovery -----------------------------------------------------------
    "ACKREDIT-W004": {
        "title": "CITATION.cff could not be parsed",
        "user_message": "'{package}' ships a CITATION.cff that could not be read, so it is credited from package metadata instead.",
        "user_hint": "The citation may be less complete than the file intended.",
        "dev_message": "find_and_parse_cff failed for '{path}': {error_type}: {error}.",
        "dev_hint": "The CFF parser is a zero-dependency subset; unusual YAML is expected to fail here.",
    },
    "ACKREDIT-W005": {
        "title": "Package metadata unavailable",
        "user_message": "No citation information could be discovered for '{package}'.",
        "user_hint": "Register it explicitly with register_item() if it should be credited.",
        "dev_message": "importlib.metadata found no distribution for import name '{package}'.",
        "dev_hint": "Import name and distribution name differ for some packages, for example sklearn and scikit-learn.",
    },
    # --- Metadata enrichment -------------------------------------------------
    "ACKREDIT-W006": {
        "title": "DOI metadata could not be fetched",
        "user_message": "Metadata for DOI '{doi}' could not be retrieved, so '{item_id}' is reported with what is already known.",
        "user_hint": "Check network access, or fill the title and authors in register_item().",
        "dev_message": "Enrichment of '{item_id}' failed against {source}: {error_type}: {error}.",
        "dev_hint": "Crossref is tried first, then DataCite; this reports the last failure.",
    },
    "ACKREDIT-W007": {
        "title": "Metadata cache unavailable",
        "user_message": "The local metadata cache could not be used; DOI lookups will not be reused between runs.",
        "user_hint": "Check permissions on '{path}'.",
        "dev_message": "Cache {operation} failed for '{path}': {error_type}: {error}.",
        "dev_hint": "Enrichment continues over the network; only the cache is affected.",
    },
    # --- Registry ------------------------------------------------------------
    "ACKREDIT-W008": {
        "title": "Citation plugin failed to load",
        "user_message": "The citation pack provided by '{plugin}' could not be loaded, so its items are unavailable.",
        "user_hint": "Report this to the package that provides the plugin.",
        "dev_message": "Entry point '{plugin}' in group 'ackredit.citations' raised {error_type}: {error}.",
        "dev_hint": "Plugin failures never propagate, so a broken third-party pack cannot take the host down.",
    },
    "ACKREDIT-W009": {
        "title": "BibTeX field kept as text",
        "user_message": "The year of BibTeX entry '{item_id}' is not a number and was kept as written.",
        "user_hint": "Formats expecting a numeric year may render it unchanged.",
        "dev_message": "Could not coerce year '{value}' of '{item_id}' to int.",
        "dev_hint": "Biblatex date ranges and 'in press' reach this path legitimately.",
    },
    "ACKREDIT-W010": {
        "title": "Source could not be inspected",
        "user_message": "Automatic detection could not read the source of '{function}', so no citations were inferred from it.",
        "user_hint": "Track the items explicitly with track_item() if they are needed.",
        "dev_message": "inspect_function failed for '{function}': {error_type}: {error}.",
        "dev_hint": "Functions defined in a REPL or a C extension have no retrievable source.",
    },
    # --- Reporting -----------------------------------------------------------
    "ACKREDIT-W011": {
        "title": "PDF tooling not found",
        "user_message": "No PDF was produced because '{tool}' is not installed.",
        "user_hint": "Install a LaTeX distribution, or use the .tex and .bib files that were written.",
        "dev_message": "shutil.which('{tool}') returned nothing; PDF compilation skipped.",
        "dev_hint": "The LaTeX and BibTeX outputs are complete regardless.",
    },
    "ACKREDIT-W012": {
        "title": "PDF compilation failed",
        "user_message": "The citation report could not be compiled into a PDF.",
        "user_hint": "The .tex and .bib files in '{directory}' are complete and can be compiled by hand.",
        "dev_message": "{tool} exited with status {status} in '{directory}'.",
        "dev_hint": "Entry types such as @software are unknown to some .bst styles and abort bibtex.",
    },
    "ACKREDIT-W013": {
        "title": "Citation could not be exported to DueCredit",
        "user_message": "'{item_id}' could not be handed over to DueCredit and is missing from its summary.",
        "user_hint": "It is still present in Ackredit's own report.",
        "dev_message": "due.cite failed for '{item_id}': {error_type}: {error}.",
        "dev_hint": "Export continues with the remaining items.",
    },
    "ACKREDIT-W014": {
        "title": "Report format plugin failed to load",
        "user_message": "The report format provided by '{plugin}' could not be loaded, so it is unavailable.",
        "user_hint": "Report this to the package that provides the plugin; the built-in formats are unaffected.",
        "dev_message": "Entry point '{plugin}' in group 'ackredit.formats' raised {error_type}: {error}.",
        "dev_hint": "A name already taken raises ACKREDIT-E005 and arrives here; plugin failures never propagate.",
    },
    "ACKREDIT-W015": {
        "title": "Metadata record could not be read",
        "user_message": "The metadata retrieved for DOI '{doi}' could not be read, so '{item_id}' keeps what was already known.",
        "user_hint": "Fill the title and authors in register_item() if they matter.",
        "dev_message": "Applying the record for '{item_id}' failed: {error_type}: {error}.",
        "dev_hint": "A malformed record is data, not a defect here; enrichment must never cost a caller their run.",
    },
    "ACKREDIT-W016": {
        "title": "Incomplete BibTeX entry",
        "user_message": "An entry in '{path}' is not closed, so it was skipped and its citation is missing.",
        "user_hint": "The '{entry_type}' entry beginning at character {offset} is never closed; check whether the file is complete.",
        "dev_message": "load_bibtex found an unterminated '{entry_type}' entry in '{path}' at offset {offset}.",
        "dev_hint": "A truncated download or a hand-edited file reaches this; the entries before it are still loaded.",
    },
    "ACKREDIT-W017": {
        "title": "Dependency report schema changed",
        "user_message": "The optional-dependency report arrived as '{found}' where Ackredit promises '{promised}', so its fields may differ from what is documented.",
        "user_hint": "The payload states its own schema; read it from the 'schema' key before relying on a field.",
        "dev_message": "get_info returned schema version {found}; ackredit.dependency_info documents {promised}.",
        "dev_hint": "Ackredit relays DepDigest's machine shape rather than defining one, so a version change there is a change to this function's contract and is never handed over silently.",
    },
    # --- Errors --------------------------------------------------------------
    "ACKREDIT-E001": {
        "title": "Citation item has no id",
        "user_message": "A citation item was registered without an 'id'.",
        "user_hint": "Every item needs a stable id, for example 'mylib:2026:paper'; it is what track_item() refers to.",
        "dev_message": "register_item called with keys {keys} and no 'id'.",
        "dev_hint": "The id is the registry key; there is no meaningful default.",
    },
    "ACKREDIT-E002": {
        "title": "BibTeX file not found",
        "user_message": "The BibTeX file '{path}' does not exist.",
        "user_hint": "Check the path passed to load_bibtex().",
        "dev_message": "load_bibtex could not stat '{path}'.",
        "dev_hint": "Relative paths resolve against the current working directory.",
    },
    "ACKREDIT-E004": {
        "title": "Unknown report format",
        "user_message": "'{format}' is not a report format Ackredit knows.",
        "user_hint": "Use one of: {available}, or ask ackredit.available_formats().",
        "dev_message": "No renderer registered for '{format}'.",
        "dev_hint": "An unknown name used to fall through to plain text, so a typo produced a report that was not the one requested.",
    },
    "ACKREDIT-E005": {
        "title": "Report format name already taken",
        "user_message": "'{format}' is already a report format and cannot be replaced.",
        "user_hint": "Choose a name nobody has taken; ackredit.available_formats() lists them.",
        "dev_message": "register_format refused '{format}': the name is already registered.",
        "dev_hint": "Replacing a format would let a request succeed and return a report that is not the one asked for, which is the defect closed in ACKREDIT-E004.",
    },
    "ACKREDIT-E006": {
        "title": "Report format cannot be registered",
        "user_message": "A report format could not be registered: {reason}.",
        "user_hint": "A format needs a lower-case name, a callable that renders it, and a file extension.",
        "dev_message": "register_format rejected name={format!r}: {reason}.",
        "dev_hint": "Names are matched exactly, so one style is enforced at registration rather than guessed at lookup.",
    },
    "ACKREDIT-E007": {
        "title": "Report format does not take that option",
        "user_message": "The '{format}' report does not take {option}.",
        "user_hint": "It accepts: {accepted}.",
        "dev_message": "Binding {option} to the '{format}' renderer failed: {reason}.",
        "dev_hint": "Options used to reach only the latex renderer and be dropped for every other format, so a request succeeded and returned a report that was not the one asked for.",
    },
    # DepDigest raises this one and renders its own prose, because it knows the
    # install channels. The template must not invent fields DepDigest does not
    # pass: '{pypi}' would reach the user literally.
    "ACKREDIT-E003": {
        "title": "Missing dependency",
        "user_message": "{message}",
        "user_hint": "Ackredit's core reporting works without it; only this feature needs it.",
        "dev_message": "{message}",
        "dev_hint": "Declared in ackredit/_depdigest.py; every optional dependency is soft.",
    },
}

# Catalog entries carry the identity of each incident; CODES carries its wording.
# Every key here must exist in CODES, and vice versa: a code in one and not the
# other emits an event with an empty message and nothing complains.
_WARNINGS = {
    "SessionLoadWarning": "ACKREDIT-W001",
    "SessionSaveWarning": "ACKREDIT-W002",
    "SessionMergeWarning": "ACKREDIT-W003",
    "CitationFileWarning": "ACKREDIT-W004",
    "PackageMetadataWarning": "ACKREDIT-W005",
    "MetadataFetchWarning": "ACKREDIT-W006",
    "MetadataCacheWarning": "ACKREDIT-W007",
    "PluginLoadWarning": "ACKREDIT-W008",
    "BibtexFieldWarning": "ACKREDIT-W009",
    "BibtexEntryWarning": "ACKREDIT-W016",
    "SourceInspectionWarning": "ACKREDIT-W010",
    "PdfToolWarning": "ACKREDIT-W011",
    "PdfCompilationWarning": "ACKREDIT-W012",
    "DueCreditExportWarning": "ACKREDIT-W013",
    "FormatPluginWarning": "ACKREDIT-W014",
    "MetadataRecordWarning": "ACKREDIT-W015",
    "DependencySchemaWarning": "ACKREDIT-W017",
}

_ERRORS = {
    "ItemIdMissingError": "ACKREDIT-E001",
    "BibtexFileNotFoundError": "ACKREDIT-E002",
    "MissingDependencyError": "ACKREDIT-E003",
    "UnknownFormatError": "ACKREDIT-E004",
    "FormatNameTakenError": "ACKREDIT-E005",
    "InvalidFormatError": "ACKREDIT-E006",
    "UnknownFormatOptionError": "ACKREDIT-E007",
}

CATALOG = {
    "warnings": {
        name: {
            "code": code,
            "source": "ackredit",
            "category": "citation",
            "level": "WARNING",
        }
        for name, code in _WARNINGS.items()
    },
    # SMonitor resolves exception entries from the "exceptions" group.
    "exceptions": {
        name: {
            "code": code,
            "source": "ackredit",
            "category": "citation",
            "level": "ERROR",
        }
        for name, code in _ERRORS.items()
    },
    "codes": CODES,
}

# Structured fields a signal must carry, checked in the dev and qa profiles.
SIGNALS = {
    "ackredit.report": {"extra_required": ["format"]},
    "ackredit.dump": {"extra_required": ["path"]},
}
