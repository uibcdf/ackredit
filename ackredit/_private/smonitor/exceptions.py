"""Catalog-backed exceptions.

Each subclass only names its catalog key. `CatalogException` owns `code`,
`message`, `raw_message`, `extra` and `hint`, and assigns them last, so a
subclass must not set them before calling `super().__init__()`.
"""

from smonitor.integrations import CatalogException

from . import CATALOG, META


class AckreditError(CatalogException):
    """Base for every Ackredit exception, so hosts can catch one type."""

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


class ItemIdMissingError(AckreditError):
    catalog_key = "ItemIdMissingError"


class BibtexFileNotFoundError(AckreditError, FileNotFoundError):
    """Also a FileNotFoundError, so existing callers keep working."""

    catalog_key = "BibtexFileNotFoundError"


class UnknownFormatError(AckreditError, ValueError):
    """Also a ValueError, which is what a bad argument value normally raises."""

    catalog_key = "UnknownFormatError"


class ArgumentError(AckreditError, ValueError):
    """An argument a digester refused. Also a ValueError, which is what a bad
    argument value normally raises."""

    catalog_key = "ArgumentError"


class FormatNameTakenError(AckreditError, ValueError):
    """Registering a format over one that exists. Also a ValueError."""

    catalog_key = "FormatNameTakenError"


class InvalidFormatError(AckreditError, ValueError):
    """A format whose name, renderer or extension cannot be used."""

    catalog_key = "InvalidFormatError"


class MissingDependencyError(AckreditError, ImportError):
    """Also an ImportError, which is what the optional-dependency pattern expects."""

    catalog_key = "MissingDependencyError"


__all__ = [
    "AckreditError",
    "ArgumentError",
    "BibtexFileNotFoundError",
    "FormatNameTakenError",
    "InvalidFormatError",
    "ItemIdMissingError",
    "MissingDependencyError",
    "UnknownFormatError",
]
