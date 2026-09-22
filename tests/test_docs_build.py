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

ROOT = Path(__file__).resolve().parents[1]
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


def test_the_performance_page_points_at_something_runnable():
    """The numbers on that page are only as good as the ability to redo them,
    so the script it names has to exist and to compile."""
    import py_compile
    import tempfile

    page = (ROOT / "docs/content/about/performance.md").read_text(encoding="utf-8")
    script = ROOT / "devtools/benchmark.py"

    assert "devtools/benchmark.py" in page
    assert script.exists()
    with tempfile.NamedTemporaryFile(suffix=".pyc") as out:
        py_compile.compile(str(script), cfile=out.name, doraise=True)


def test_the_performance_page_gives_numbers_not_adjectives():
    """Roadmap theme D asks for the overhead 'as a number, not an adjective'."""
    import re

    page = (ROOT / "docs/content/about/performance.md").read_text(encoding="utf-8")
    assert re.search(r"\d+\.\d+ µs", page), "no per-call number"
    assert "under the noise" in page, "the workflow result is stated as what it is"
