"""
Ackredit — acknowledge what you used, credit what matters.
"""

from smonitor.integrations import ensure_configured

from ._private.smonitor import PACKAGE_ROOT

# Activate diagnostics before anything else runs, so a failure during the imports
# below is reported through the catalog rather than lost.
ensure_configured(PACKAGE_ROOT)

from .contrib.duecredit_compat import export_to_duecredit
from .contrib.jupyter import summary
from .contrib.web_ui import serve_ui
from .core.collector import (
    Collector,
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
from .core.report import compile_pdf, dependency_info, dump, report

enable_persistence = Collector.enable_persistence
aggregate = Collector.aggregate

# Automatically load citations from installed plugins
load_plugins()

__all__ = [
    "Registry",
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
    "compile_pdf",
    "dependency_info",
    "auto_track_calls",
    "scope",
    "summary",
    "serve_ui",
    "enable_auto_reminder",
    "enable_import_hooks",
    "enable_persistence",
    "aggregate",
    "export_to_duecredit",
]
