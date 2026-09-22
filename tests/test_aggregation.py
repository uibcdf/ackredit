"""Merging saved sessions must reach the file, not only memory.

`aggregate` is the multi-run story: N jobs each write a journal, a final step
merges them and reports. That merge went through `Session.record_item` and
`record_target` directly, while a tracked event goes through the same methods
*and* appends to the journal. So `report()` showed everything and the file held
only what the process had tracked itself — silently, and the file is what
outlives the process.

Two ways that lost work. The aggregating process, which is the natural place to
enable persistence, crashes and everything merged is gone although the guide
promises otherwise. Or a later run aggregates *that* journal and receives only
part of it, one level down, with nothing to show.
"""

import pytest

import ackredit
from ackredit.core import session
from ackredit.core.collector import Collector
from ackredit.core.session import current_session


@pytest.fixture
def saved(tmp_path):
    """A journal from an earlier run, with an item, a caller and a parent."""
    path = tmp_path / "earlier.json"
    ackredit.register_item(id="a:1", title="From the earlier run")
    ackredit.enable_persistence(path)
    ackredit.track_item("a:1", used_by="inner")
    ackredit.track_target("inner", parent="outer")
    ackredit.close_persistence()
    current_session().clear()
    return path


def tree() -> dict:
    return {
        name: {key: sorted(value) for key, value in node.items()}
        for name, node in Collector.usage_tree.items()
    }


def tree_of(state: dict) -> dict:
    return {
        name: {key: sorted(value) for key, value in node.items()}
        for name, node in state["usage_tree"].items()
    }


def test_the_file_holds_what_the_report_holds(saved, tmp_path):
    """The defect: in memory a:1 and b:1, on disk only b:1."""
    later = tmp_path / "later.json"
    ackredit.register_item(id="b:1", title="From this run")
    ackredit.enable_persistence(later)
    ackredit.track_item("b:1", used_by="thisRun")
    ackredit.aggregate([saved])

    in_memory = dict(ackredit.get_used_items())
    ackredit.close_persistence()

    assert sorted(in_memory) == ["a:1", "b:1"]
    assert session.read(later)["used_items"] == in_memory


def test_the_provenance_survives_the_round_trip(saved, tmp_path):
    """The parent-to-child link lives only in the tree, so it is the part a
    `used_targets` entry cannot carry and the easiest to lose."""
    later = tmp_path / "later.json"
    ackredit.enable_persistence(later)
    ackredit.aggregate([saved])
    expected = tree()
    ackredit.close_persistence()

    assert tree_of(session.read(later)) == expected
    assert "inner" in expected["outer"]["children"]


def test_a_later_run_aggregating_that_journal_gets_everything(saved, tmp_path):
    """The loss compounded: merged citations disappeared one level down."""
    middle = tmp_path / "middle.json"
    ackredit.register_item(id="b:1", title="From the middle run")
    ackredit.enable_persistence(middle)
    ackredit.track_item("b:1", used_by="middleRun")
    ackredit.aggregate([saved])
    ackredit.close_persistence()
    current_session().clear()

    ackredit.aggregate([middle])
    assert sorted(ackredit.get_used_items()) == ["a:1", "b:1"]


def test_merging_the_same_file_twice_appends_nothing(saved, tmp_path):
    """`record_item` and `record_target` report whether they changed anything,
    so the journal records state changes rather than calls."""
    later = tmp_path / "later.json"
    ackredit.enable_persistence(later)

    ackredit.aggregate([saved])
    once = later.read_text()
    ackredit.aggregate([saved])
    twice = later.read_text()
    ackredit.close_persistence()

    assert once == twice


def test_merging_without_persistence_still_works(saved):
    """Nothing to journal, and nothing may break for the absence of it."""
    ackredit.aggregate([saved])
    assert "a:1" in ackredit.get_used_items()


def test_adopting_a_file_on_open_does_not_duplicate_it(saved):
    """`enable_persistence` merges what the file holds into the session, and
    must not append it back to the file it just read."""
    before = saved.read_text()
    ackredit.enable_persistence(saved)
    ackredit.close_persistence()

    assert saved.read_text() == before


def test_reopening_and_tracking_appends_only_the_new(saved):
    ackredit.register_item(id="c:1", title="New")
    ackredit.enable_persistence(saved)
    ackredit.track_item("c:1", used_by="later")
    ackredit.close_persistence()

    state = session.read(saved)
    assert sorted(state["used_items"]) == ["a:1", "c:1"]
    assert state["used_items"]["a:1"] == ["inner"], "the earlier caller is intact"
