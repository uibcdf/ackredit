"""Runtime SMonitor configuration for Ackredit.

SMonitor discovers this file by walking upward from the caller's module and
executes it as a standalone module, so the import below must be absolute: a
relative import has no parent package at that point.

It must also live inside the package. Discovery finds a file at the repository
root in a development checkout, and that file is not packaged into the wheel, so
it is simply absent for everyone who installed the library. The failure is
silent: every catalog code then resolves against no template.

Templates are imported from the private catalog rather than redefined here, so
an emitted code cannot drift away from its wording.
"""

from ackredit._private.smonitor.catalog import CODES, SIGNALS

PROFILE = "user"

SMONITOR = {
    "level": "WARNING",
    "trace_depth": 3,
    "capture_warnings": True,
    "capture_logging": True,
    "theme": "plain",
}

PROFILES = {
    "user": {
        "level": "WARNING",
    },
    "dev": {
        "level": "INFO",
        "show_traceback": True,
    },
    "qa": {
        "level": "INFO",
        "show_traceback": True,
    },
    "agent": {
        "level": "WARNING",
    },
    "debug": {
        "level": "DEBUG",
        "show_traceback": True,
    },
}

__all__ = ["CODES", "PROFILE", "PROFILES", "SIGNALS", "SMONITOR"]
