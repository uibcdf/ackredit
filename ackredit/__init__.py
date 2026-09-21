"""
Ackredit — acknowledge what you used, credit what matters.
"""

# The build writes `_version.py`, so an installed distribution reports the same
# string either way — but reading it costs nothing, while `importlib.metadata`
# pulls in `email.message`, `zipfile` and `inspect`. Measured here: 55 to 65 ms
# of a 118 ms import, about half. Ackredit is an optional dependency living
# inside host libraries, so every host would pay that before doing any work.
#
# Everything imported for this module's own setup is bound to a private name. A
# public one becomes something a user can depend on, and `version` in particular
# sits one tab-completion from `__version__` while answering, plausibly and
# wrongly, what a citation tool's own version is.
try:
    from ._version import __version__
except ImportError:  # pragma: no cover - a source tree with no build
    try:
        from importlib.metadata import version as _distribution_version

        __version__ = _distribution_version("ackredit")
    except Exception:
        # Nothing here may keep the package from importing.
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
    aggregate,
    close_persistence,
    credit_bound,
    enable_persistence,
    get_used_items,
    track_item,
    track_target,
)
from .core.context import scope
from .core.decorators import scoped_usage
from .core.hooks import (
    disable_auto_reminder,
    disable_import_hooks,
    enable_auto_reminder,
    enable_import_hooks,
)
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
    register_format,
    report,
)
from .core.session import Session, current_session, session

# Automatically load citations from installed plugins
load_plugins()

__all__ = [
    "__version__",
    "Collector",
    "Registry",
    "Session",
    "register_format",
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
    "disable_auto_reminder",
    "disable_import_hooks",
    "enable_auto_reminder",
    "enable_import_hooks",
    "enable_persistence",
    "aggregate",
    "export_to_duecredit",
]
