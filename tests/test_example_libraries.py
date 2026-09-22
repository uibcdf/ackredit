"""Two host libraries, integrated the way a real one would be.

`tests/test_integration_guide.py` executes the guide's template and compares
every fallback signature against the real one. That checks shapes. These check
integration: registering while a host is imported, citations nesting across two
libraries, a branch that is not taken not being cited, and both hosts working
when Ackredit is absent.

The libraries live in `examples/`, outside the packaged distribution, so the
documentation can show them working rather than describing them.
"""

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

import ackredit
from ackredit.core.registry import Registry
from ackredit.core.session import current_session

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
GUIDE = ROOT / "standards" / "ACKREDIT_GUIDE.md"

sys.path.insert(0, str(EXAMPLES))


@pytest.fixture(autouse=True)
def _fresh():
    current_session().clear()
    yield
    current_session().clear()


def _guide_template() -> str:
    text = GUIDE.read_text(encoding="utf-8")
    marker = "### Template for `_ackredit.py`:"
    return (
        text.split(marker, 1)[1].split("```python", 1)[1].split("```", 1)[0].strip("\n")
    )


@pytest.mark.parametrize("package", ["dummy_solver", "dummy_pipeline"])
def test_the_integration_file_is_the_guide_verbatim(package):
    """The guide is not a snippet checked in isolation; it is this file.

    If they are allowed to differ, the guide becomes documentation of something
    nobody runs, which is how its four previous defects survived.
    """
    shipped = (EXAMPLES / package / "_ackredit.py").read_text(encoding="utf-8")
    body = shipped.split('"""Ackredit integration', 1)[1]

    assert '"""Ackredit integration' + body.rstrip("\n") == _guide_template(), (
        f"{package}/_ackredit.py has drifted from the template in "
        f"{GUIDE.name}. The guide is the authority; copy it over."
    )


def test_a_host_declares_what_it_can_cite_while_being_imported():
    """The moment a host has. The registry is shared and outlives a session."""
    import dummy_solver  # noqa: F401

    assert "dummysolver:2026:method" in Registry.items
    assert ackredit.bound_items("dummy_solver.solve") == ["dummysolver:2026:method"]


def test_a_run_credits_only_the_path_it_took():
    """The claim the product is built on, across two libraries."""
    import dummy_pipeline

    dummy_pipeline.analyse("system A")

    assert sorted(ackredit.get_used_items()) == [
        "dummypipeline:2026:workflow",
        "dummysolver:2026:method",
    ]


def test_another_path_credits_more():
    import dummy_pipeline

    dummy_pipeline.analyse("system A", method="iterative", use_reference=True)

    assert sorted(ackredit.get_used_items()) == [
        "dummypipeline:2026:workflow",
        "dummypipeline:dataset",
        "dummysolver:2026:iterative",
        "dummysolver:2026:method",
    ]


def test_citations_nest_across_libraries():
    """Neither host knows what the other cites, and the tree says which call
    led to which citation."""
    import dummy_pipeline

    dummy_pipeline.analyse("system A")
    tree = current_session().usage_tree

    assert tree["dummy_pipeline.analyse"]["items"] == {"dummypipeline:2026:workflow"}
    assert "dummy_solver.solve" in tree["dummy_pipeline.analyse"]["children"]
    assert tree["dummy_solver.solve"]["items"] == {"dummysolver:2026:method"}


def test_the_bound_item_is_credited_without_being_named_in_the_body():
    """`credit_bound=True` is what keeps the coarse case out of the code."""
    import dummy_solver

    solver_source = (EXAMPLES / "dummy_solver" / "core.py").read_text(encoding="utf-8")
    assert "dummysolver:2026:method" not in solver_source

    dummy_solver.solve("system")

    assert "dummysolver:2026:method" in ackredit.get_used_items()


def test_a_report_of_a_run_names_both_libraries():
    import dummy_pipeline

    dummy_pipeline.analyse("system A", use_reference=True)
    rendered = ackredit.report(format="markdown")

    assert "A workflow for dummy analyses" in rendered
    assert "A direct method for dummy systems" in rendered


@pytest.mark.parametrize("package", ["dummy_solver", "dummy_pipeline"])
def test_a_host_works_with_ackredit_genuinely_absent(package):
    """Not a stubbed import: a subprocess where importing ackredit raises, which
    is the state a user without it is in."""
    script = textwrap.dedent(f"""
        import sys

        class Absent:
            def find_module(self, name, path=None):
                if name == "ackredit" or name.startswith("ackredit."):
                    raise ImportError("ackredit is not installed")
                return None

            def find_spec(self, name, path=None, target=None):
                return self.find_module(name, path)

        sys.meta_path.insert(0, Absent())
        sys.path.insert(0, {str(EXAMPLES)!r})

        import dummy_pipeline
        import dummy_solver

        assert dummy_solver.ACKREDIT_INSTALLED is False
        assert dummy_pipeline.ACKREDIT_INSTALLED is False
        assert dummy_solver.solve("s") == "s solved directly"
        assert dummy_pipeline.analyse("s", method="iterative") == "s solved iteratively"
        print("host works without ackredit")
    """)

    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, cwd=str(ROOT)
    )

    assert result.returncode == 0, result.stderr[-1500:]
    assert "host works without ackredit" in result.stdout


def test_the_examples_are_not_shipped_in_the_distribution():
    """They are documentation and fixtures, not part of the library."""
    import tomllib

    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    include = config["tool"]["setuptools"]["packages"]["find"]["include"]

    assert include == ["ackredit*"], include


def test_the_documentation_shows_the_output_the_code_produces():
    """The provenance block on the example page was written from memory once and
    was wrong. Documentation that quotes output should be held to it."""
    import dummy_pipeline

    dummy_pipeline.analyse("system A")
    rendered = ackredit.report(format="provenance")

    page = (
        ROOT / "docs" / "content" / "user_guide" / "example_libraries.md"
    ).read_text(encoding="utf-8")

    for line in rendered.splitlines():
        if line.strip():
            assert line in page, (
                f"the page does not show this line of real output: {line!r}"
            )
