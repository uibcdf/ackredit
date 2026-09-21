"""PDF compilation, and what happens when the tooling for it is absent.

`pdflatex` and `bibtex` are system binaries, not Python distributions, so they
cannot be declared as dependencies. The documented contract is that Ackredit
still writes the LaTeX and BibTeX sources and reports that the PDF step was
skipped.
"""

import importlib
import shutil
import warnings

import pytest

from ackredit import dump, register_item, track_item
from ackredit._private.smonitor.warnings import PdfToolWarning

# Resolved explicitly: ackredit.core re-exports a function named `report`,
# which shadows the submodule of the same name.
report_module = importlib.import_module("ackredit.core.report")

needs_latex = pytest.mark.skipif(
    shutil.which("pdflatex") is None,
    reason="pdflatex is an optional system binary and is not installed here",
)


@needs_latex
def test_pdf_compilation(tmp_path):
    register_item(id="paper:1", title="Test Paper", authors=["Author A"], year=2024)
    track_item("paper:1")

    report_dir = tmp_path / "report"
    dump(report_dir, build_pdf=True)

    pdf_file = report_dir / "ackredit_report.pdf"
    assert pdf_file.exists()
    assert pdf_file.stat().st_size > 0


@needs_latex
def test_compilation_emits_no_diagnostic_when_it_succeeds(tmp_path):
    """The whole of #7 was a compilation that warned while the suite stayed green."""
    register_item(id="paper:clean", title="Clean Run", authors=["Author A"], year=2024)
    track_item("paper:clean")

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        dump(tmp_path / "report", build_pdf=True)

    reported = [w for w in caught if isinstance(w.message, PdfToolWarning)]
    assert not reported, [str(w.message) for w in reported]


def test_sources_are_written_and_reported_when_latex_is_missing(tmp_path, monkeypatch):
    """Simulated rather than skipped, so the degradation path is covered on a
    developer machine that has LaTeX as well as on a runner that does not."""
    monkeypatch.setattr(report_module.shutil, "which", lambda name: None)

    register_item(id="paper:2", title="No LaTeX Here", authors=["Author B"], year=2024)
    track_item("paper:2")

    report_dir = tmp_path / "report"
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        dump(report_dir, build_pdf=True)

    # The sources are complete, so the user can compile them by hand.
    assert (report_dir / "ackredit_report.tex").read_text().strip()
    assert (report_dir / "ackredit_report.bib").read_text().strip()
    assert not (report_dir / "ackredit_report.pdf").exists()

    # And the reason is reported rather than swallowed.
    reported = [w for w in caught if isinstance(w.message, PdfToolWarning)]
    assert reported, "a missing pdflatex must be reported, not silently skipped"
    assert reported[0].message.code == "ACKREDIT-W011"
