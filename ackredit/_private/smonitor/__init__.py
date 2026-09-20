"""Ackredit's SMonitor integration surface.

Exports the three objects the rest of the integration needs: the catalog, the
project metadata, and the package root SMonitor uses to find `_smonitor.py`.
"""

from pathlib import Path

from .catalog import CATALOG, CODES, SIGNALS
from .meta import META

# ackredit/_private/smonitor/__init__.py -> ackredit/
# Discovery walks upward from here, so this must point at the installed package
# directory rather than the repository root: a file outside the package is found
# in a checkout and absent from the wheel, and the failure is silent.
PACKAGE_ROOT = Path(__file__).resolve().parents[1].parent

__all__ = ["CATALOG", "CODES", "META", "PACKAGE_ROOT", "SIGNALS"]
