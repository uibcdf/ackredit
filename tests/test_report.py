from flowcite.core.collector import track_item
from flowcite.core.registry import register_item
from flowcite.core.report import report


def test_markdown_report():
    register_item(id="paper:1", type="article", title="Paper 1", year=2024)
    track_item("paper:1", used_by="pkg.func")
    md = report(format="markdown")
    assert "Paper 1" in md
