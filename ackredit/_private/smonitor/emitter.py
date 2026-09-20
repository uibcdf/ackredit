"""The one place diagnostics are emitted from."""

from smonitor.integrations import DiagnosticBundle

from . import CATALOG, META, PACKAGE_ROOT

bundle = DiagnosticBundle(CATALOG, META, PACKAGE_ROOT)

warn = bundle.warn
warn_once = bundle.warn_once
resolve = bundle.resolve

__all__ = ["bundle", "resolve", "warn", "warn_once"]
