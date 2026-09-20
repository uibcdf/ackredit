"""
FlowCite — trace what you used, cite what matters.
"""

from .contrib.duecredit_compat import export_to_duecredit
from .contrib.jupyter import summary
from .contrib.web_ui import serve_ui
from .core.collector import Collector, get_used_items, track_item, track_target
from .core.context import scope
from .core.decorators import scoped_usage
from .core.hooks import enable_auto_reminder, enable_import_hooks
from .core.inspection import auto_track_calls
from .core.registry import (
    Registry,
    add_injection,
    bind,
    enrich_all,
    load_bibtex,
    load_plugins,
    register_item,
)
from .core.report import compile_pdf, dump, report

enable_persistence = Collector.enable_persistence
aggregate = Collector.aggregate

# Automatically load citations from installed plugins
load_plugins()

__all__ = [
    "Registry",
    "register_item",
    "bind",
    "add_injection",
    "load_bibtex",
    "enrich_all",
    "load_plugins",
    "track_item",
    "track_target",
    "get_used_items",
    "scoped_usage",
    "report",
    "dump",
    "compile_pdf",
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
