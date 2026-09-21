"""
Ackredit — acknowledge what you used, credit what matters.
"""

# Everything this module imports for its own setup is bound to a private name.
# A public one would join the namespace and become something a user can depend
# on: `version` in particular sits one tab-completion from `__version__` and
# answers, plausibly and wrongly, what a citation tool's own version is.
from importlib.metadata import PackageNotFoundError as _PackageNotFoundError
from importlib.metadata import version as _distribution_version

try:
    __version__ = _distribution_version("ackredit")
except _PackageNotFoundError:
    # Running from a source tree that was never installed.
    try:
        from ._version import __version__
    except ImportError:
        __version__ = "0.0.0+unknown"

from smonitor.integrations import ensure_configured as _ensure_smonitor_configured

from ._private.smonitor import PACKAGE_ROOT as _SMONITOR_PACKAGE_ROOT

# Activate diagnostics before anything else runs, so a failure during the imports
# below is reported through the catalog rather than lost.
_ensure_smonitor_configured(_SMONITOR_PACKAGE_ROOT)

from .contrib.duecredit_compat import export_to_duecredit
from .contrib.jupyter import summary
from .contrib.web_ui import serve_ui
from .core.collector import (
    Collector,
    close_persistence,
    credit_bound,
    get_used_items,
    track_item,
    track_target,
)
from .core.context import scope
from .core.decorators import scoped_usage
from .core.hooks import enable_auto_reminder, enable_import_hooks
from .core.inspection import auto_track_calls
from .core.registry import (
    Registry,
    add_injection,
    bind,
    bound_items,
    enrich_all,
    load_bibtex,
    load_plugins,
    register_item,
)
from .core.report import (
    available_formats,
    compile_pdf,
    dependency_info,
    dump,
    report,
)
from .core.session import Session, current_session, session

enable_persistence = Collector.enable_persistence
aggregate = Collector.aggregate

# Automatically load citations from installed plugins
load_plugins()

__all__ = [
    "__version__",
    "Collector",
    "Registry",
    "Session",
    "register_item",
    "bind",
    "bound_items",
    "add_injection",
    "load_bibtex",
    "enrich_all",
    "load_plugins",
    "track_item",
    "track_target",
    "credit_bound",
    "get_used_items",
    "scoped_usage",
    "report",
    "dump",
    "available_formats",
    "close_persistence",
    "compile_pdf",
    "dependency_info",
    "auto_track_calls",
    "current_session",
    "scope",
    "session",
    "summary",
    "serve_ui",
    "enable_auto_reminder",
    "enable_import_hooks",
    "enable_persistence",
    "aggregate",
    "export_to_duecredit",
]
