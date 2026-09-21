"""A session file that two processes replace must not lose citations in silence.

Each save replaces the whole document, so two writers do not merge: the last one
wins and the other's items disappear, leaving a file that is valid JSON and
quietly incomplete. Four processes sharing one path lost 55% of what they
tracked, and two of them vanished entirely.

The fix is not locking. One file per process and `aggregate` already produces the
correct result; what was missing is noticing the mistake.
"""

import json
import warnings

import pytest

import ackredit
from ackredit._private.smonitor.warnings import SessionSharedWarning
from ackredit.core.collector import Collector


@pytest.fixture
def session(tmp_path):
    Collector.used_items.clear()
    Collector.used_targets.clear()
    Collector.usage_tree.clear()
    path = tmp_path / "session.json"
    Collector.enable_persistence(path)
    yield path
    Collector._persistence_path = None
    Collector._persistence_stamp = None


def _codes(caught):
    return [
        w.message.code for w in caught if isinstance(w.message, SessionSharedWarning)
    ]


def test_a_foreign_writer_is_reported(session):
    ackredit.track_item("first:item")

    # Stand in for another process replacing the file between our writes.
    session.write_text(
        json.dumps({"used_targets": [], "used_items": {}, "usage_tree": {}})
    )

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        ackredit.track_item("second:item")

    assert _codes(caught) == ["ACKREDIT-W014"]


def test_the_warning_names_the_path_and_the_way_out(session):
    ackredit.track_item("first:item")
    session.write_text("{}")

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        ackredit.track_item("second:item")

    message = str(caught[0].message)
    assert str(session) in message
    assert "aggregate" in message


def test_ordinary_tracking_reports_nothing(session):
    """The detection must not fire on a file only this process writes."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        for index in range(25):
            ackredit.track_item(f"mine:item{index}")

    assert _codes(caught) == []


def test_it_is_reported_once_rather_than_on_every_write(session):
    ackredit.track_item("first:item")

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        for index in range(5):
            session.write_text("{}")
            ackredit.track_item(f"later:item{index}")

    assert len(_codes(caught)) <= 1


def test_tracking_continues_after_the_warning(session):
    """The diagnostic must not cost the caller their own data."""
    ackredit.track_item("first:item")
    session.write_text("{}")
    with warnings.catch_warnings(record=True):
        # The diagnostic is asserted elsewhere; captured here so the suite itself
        # stays free of emitted warnings.
        warnings.simplefilter("always")
        ackredit.track_item("second:item")

    assert "second:item" in ackredit.get_used_items()
    assert json.loads(session.read_text())["used_items"]


def test_the_documented_pattern_merges_every_file(tmp_path):
    """One file per worker, then aggregate: the path that is supposed to work."""
    Collector.used_items.clear()
    Collector.used_targets.clear()
    Collector.usage_tree.clear()
    Collector._persistence_path = None

    files = []
    for worker in range(4):
        path = tmp_path / f"session_{worker}.json"
        Collector.enable_persistence(path)
        for index in range(15):
            ackredit.track_item(f"w{worker}:item{index}")
        Collector.used_items.clear()
        Collector.used_targets.clear()
        Collector.usage_tree.clear()
        files.append(str(path))
    Collector._persistence_path = None
    Collector._persistence_stamp = None

    Collector.aggregate(files)

    assert len(Collector.used_items) == 60
    assert {key.split(":")[0] for key in Collector.used_items} == {
        "w0",
        "w1",
        "w2",
        "w3",
    }
