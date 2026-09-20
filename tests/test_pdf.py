from ackredit import dump, register_item, track_item


def test_pdf_compilation(tmp_path):
    # Register and track
    register_item(id="paper:1", title="Test Paper", authors=["Author A"], year=2024)
    track_item("paper:1")

    # Dump with PDF build
    report_dir = tmp_path / "report"
    dump(report_dir, build_pdf=True)

    # Check if PDF exists
    pdf_file = report_dir / "ackredit_report.pdf"
    assert pdf_file.exists()
    assert pdf_file.stat().st_size > 0
