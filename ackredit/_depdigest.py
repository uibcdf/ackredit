"""DepDigest configuration for Ackredit.

Declares the optional Python packages Ackredit can use, so that a missing one
produces an actionable message instead of a bare ImportError or a print to
stdout, and so that a user can ask what their environment supports.

`pdflatex` and `bibtex` are deliberately absent: they are system binaries, not
Python distributions, and are probed with `shutil.which` in
`ackredit.core.report`.
"""

from ._private.smonitor.exceptions import MissingDependencyError

# Every entry is soft. Ackredit's core reporting works with none of them
# installed; each unlocks one optional feature.
LIBRARIES = {
    "flask": {"type": "soft", "pypi": "flask", "conda": "flask"},
    "duecredit": {"type": "soft", "pypi": "duecredit", "conda": "duecredit"},
}

# Ackredit has no lazily discovered plugin directories of its own: external
# citation packs arrive through the `ackredit.citations` entry-point group,
# which importlib.metadata resolves directly.
MAPPING: dict[str, str] = {}

SHOW_ALL_CAPABILITIES = True

EXCEPTION_CLASS = MissingDependencyError
