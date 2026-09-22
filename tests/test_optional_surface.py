"""The public names that depend on something Ackredit does not require.

Seven names in `__all__` had no test at all: `compile_pdf`, `dependency_info`,
`enable_auto_reminder`, `enrich_all`, `export_to_duecredit` and
`load_plugins`. They are the part of the surface that reaches outside — a system
binary, a network, a third party's API, another package's entry points — which
is why they were skipped, and why it matters that they work.

Ackredit's core promise is that none of this is required: a missing optional
dependency produces a catalog diagnostic naming what to install, never a bare
ImportError and never a silent no-op. That is what these check.

They also make the stability classification in `docs/content/about/stability.md`
mean something. A name called provisional because nobody looked at it says
nothing; one called provisional with its behaviour written down is a decision.
"""

import importlib.util

import pytest

import ackredit
from ackredit._depdigest import LIBRARIES
from ackredit._private.smonitor.exceptions import MissingDependencyError
from ackredit._private.smonitor.warnings import PdfCompilationWarning, PdfToolWarning
from ackredit.core.registry import Registry


def absent(library: str) -> bool:
    return importlib.util.find_spec(library) is None


# --- what the environment supports ---------------------------------------


def test_dependency_info_names_every_optional_library():
    reported = {entry["Library"] for entry in ackredit.dependency_info()}
    assert reported == set(LIBRARIES), (
        "dependency_info() and _depdigest.py disagree about what is optional"
    )


def test_dependency_info_says_how_to_install_each_one():
    for entry in ackredit.dependency_info():
        assert entry["Status"], f"{entry['Library']} is reported with no status"
        assert entry["Install (Conda)"], f"{entry['Library']} gives no conda command"


# --- a missing optional dependency is a diagnostic, not a traceback -------


@pytest.mark.skipif(
    not absent("duecredit"), reason="checks the path where duecredit is absent"
)
def test_export_to_duecredit_names_duecredit():
    with pytest.raises(MissingDependencyError) as raised:
        ackredit.export_to_duecredit()
    assert "duecredit" in str(raised.value)


# --- the ones that reach outside and must not be loud about it ------------


def test_load_plugins_does_nothing_when_nothing_provides_a_pack():
    """Nothing in this environment declares an `ackredit.citations` entry point."""
    before = dict(Registry.items)
    assert ackredit.load_plugins() is None
    assert dict(Registry.items) == before


def test_enable_auto_reminder_is_quiet_and_repeatable():
    assert ackredit.enable_auto_reminder() is None
    assert ackredit.enable_auto_reminder() is None


def test_enrich_all_touches_no_network_without_a_doi(clean_registry):
    """Enrichment is keyed on the DOI. With none registered there is nothing to
    look up, and the call must not reach out to discover that.

    `clean_registry` is not decoration: without it the registry still holds
    whatever other files registered, DOIs included, and this test reached
    Crossref for them while asserting that it did not."""
    ackredit.register_item(id="local:1", title="No DOI here", authors=["Ruiz, Ana"])
    ackredit.track_item("local:1")

    assert ackredit.enrich_all() is None
    assert Registry.items["local:1"]["title"] == "No DOI here"


# --- the system binary ----------------------------------------------------


def test_compile_pdf_reports_a_failure_rather_than_raising(tmp_path):
    """There is no .tex to compile, so the tool fails and says so."""
    with pytest.warns(PdfCompilationWarning):
        assert ackredit.compile_pdf(tmp_path) is None


def test_compile_pdf_reports_a_missing_tool_rather_than_raising(tmp_path, monkeypatch):
    """The reason Ackredit does not require a LaTeX distribution."""
    # The source has to exist, or the missing-source path answers first.
    (tmp_path / "ackredit_report.tex").write_text("\\documentclass{article}")
    monkeypatch.setattr("shutil.which", lambda tool: None)
    with pytest.warns(PdfToolWarning):
        assert ackredit.compile_pdf(tmp_path) is None
