from flowcite.core.collector import Collector, track_item, track_target


def test_tracking():
    track_target("pkg.func")
    track_item("paper:1", used_by="pkg.func")
    assert "pkg.func" in Collector.used_targets
    assert "paper:1" in Collector.used_items
