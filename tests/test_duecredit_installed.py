"""Optional receiving checks against DueCredit's real offline collector (#138)."""

import pytest

import ackredit


@pytest.mark.parametrize("has_doi", [False, True])
def test_real_collector_receives_observed_reference(
    clean_registry, monkeypatch, has_doi
):
    duecredit = pytest.importorskip("duecredit", reason="optional DueCredit receiving")
    from duecredit.collector import DueCreditCollector
    from duecredit.entries import BibTeX, Doi

    collector = DueCreditCollector()
    # The application explicitly selects a real collector. No import hooks,
    # atexit dumps, network enrichment or user configuration are enabled here.
    monkeypatch.setattr(duecredit, "due", collector)
    fields = {"doi": "10.0000/ackredit-offline-fixture"} if has_doi else {}
    ackredit.register_item(
        id="receiving:used", type="article", title="Observed work", **fields
    )
    ackredit.register_item(
        id="receiving:unused", type="article", title="Unreached work"
    )
    ackredit.track_item("receiving:used", used_by="receiving.workflow")
    ackredit.export_to_duecredit()
    (citation,) = collector.citations.values()
    assert citation.path == "ackredit.receiving:used"
    assert citation.description == "Observed work"
    assert isinstance(citation.entry, Doi if has_doi else BibTeX)
