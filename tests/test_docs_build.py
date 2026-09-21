"""The documentation build must be repeatable.

`exclude_patterns` was empty, so Sphinx scanned its own output directory. The
first build passed because `_build/jupyter_execute/` did not exist yet when
sources were collected; the second read the first one's notebooks as documents
and failed on duplicate labels, and `-W` made that a failure.

The failure named the contributor's notebooks and their labels, so it read as
something they had broken. What that costs is the time spent looking for a
defect that is not there.

Building twice is the honest test and costs more than the whole suite, so this
holds the configuration to the line that caused it instead.
"""

import re
from pathlib import Path

CONF = (Path(__file__).resolve().parents[1] / "docs/conf.py").read_text(
    encoding="utf-8"
)


def _excluded() -> list[str]:
    match = re.search(
        r"^exclude_patterns\s*=\s*\[(.*?)\]", CONF, re.MULTILINE | re.DOTALL
    )
    assert match, "docs/conf.py no longer sets exclude_patterns"
    return re.findall(r"""["']([^"']+)["']""", match.group(1))


def test_sphinx_does_not_scan_its_own_output():
    assert "_build" in _excluded(), (
        "docs/conf.py must exclude _build, or the second consecutive build "
        "reads the first one's executed notebooks as source and fails"
    )


def test_notebook_checkpoints_are_not_documents():
    assert any("ipynb_checkpoints" in pattern for pattern in _excluded())
