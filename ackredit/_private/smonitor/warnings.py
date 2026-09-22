"""Catalog-backed warning categories, one per diagnostic code.

Each class only names its catalog key and binds the catalog and metadata, so the
wording stays in `catalog.py` and the call site passes typed facts:

    warn(SessionLoadWarning(extra={"path": ..., "error": ...}))

`CatalogWarning` owns `code`, `message`, `raw_message`, `extra` and `hint`, and
assigns them last. A subclass must not set any of them before calling
`super().__init__()`; the value would simply be discarded.

Users filter these with the standard `warnings` module. Every class descends from
`AckreditWarning`, so one filter silences the library and a specific class
silences one diagnostic.
"""

from smonitor.integrations import CatalogWarning

from . import CATALOG, META


class AckreditWarning(CatalogWarning):
    """Base for every Ackredit warning."""

    def __init__(self, message=None, **kwargs):
        # Only bind the catalog when there are structured inputs to resolve.
        # `warnings.warn(text, category)` and pytest-xdist rebuild from `args`
        # alone; the base treats that text as authoritative, but only when it
        # receives no catalog. Injecting one unconditionally makes the rendered
        # message resolve a second time and appends the hint twice.
        if message is None or kwargs:
            kwargs.setdefault("catalog", CATALOG)
            kwargs.setdefault("meta", META)
        super().__init__(message, **kwargs)


class SessionLoadWarning(AckreditWarning):
    catalog_key = "SessionLoadWarning"


class SessionSaveWarning(AckreditWarning):
    catalog_key = "SessionSaveWarning"


class SessionMergeWarning(AckreditWarning):
    catalog_key = "SessionMergeWarning"


class CitationFileWarning(AckreditWarning):
    catalog_key = "CitationFileWarning"


class PackageMetadataWarning(AckreditWarning):
    catalog_key = "PackageMetadataWarning"


class MetadataFetchWarning(AckreditWarning):
    catalog_key = "MetadataFetchWarning"


class MetadataCacheWarning(AckreditWarning):
    catalog_key = "MetadataCacheWarning"


class FormatPluginWarning(AckreditWarning):
    catalog_key = "FormatPluginWarning"


class MetadataRecordWarning(AckreditWarning):
    catalog_key = "MetadataRecordWarning"


class PluginLoadWarning(AckreditWarning):
    catalog_key = "PluginLoadWarning"


class BibtexEntryWarning(AckreditWarning):
    catalog_key = "BibtexEntryWarning"


class BibtexFieldWarning(AckreditWarning):
    catalog_key = "BibtexFieldWarning"


class SourceInspectionWarning(AckreditWarning):
    catalog_key = "SourceInspectionWarning"


class PdfToolWarning(AckreditWarning):
    catalog_key = "PdfToolWarning"


class PdfCompilationWarning(AckreditWarning):
    catalog_key = "PdfCompilationWarning"


class DependencySchemaWarning(AckreditWarning):
    catalog_key = "DependencySchemaWarning"


class FormatExtensionWarning(AckreditWarning):
    catalog_key = "FormatExtensionWarning"


class DueCreditExportWarning(AckreditWarning):
    catalog_key = "DueCreditExportWarning"


__all__ = [
    "AckreditWarning",
    "BibtexEntryWarning",
    "BibtexFieldWarning",
    "CitationFileWarning",
    "DependencySchemaWarning",
    "DueCreditExportWarning",
    "FormatPluginWarning",
    "MetadataCacheWarning",
    "MetadataFetchWarning",
    "MetadataRecordWarning",
    "PackageMetadataWarning",
    "PdfCompilationWarning",
    "PdfToolWarning",
    "PluginLoadWarning",
    "SessionLoadWarning",
    "SessionMergeWarning",
    "SessionSaveWarning",
    "SourceInspectionWarning",
]
