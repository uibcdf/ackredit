"""The cost of tracking one more item must not depend on how many came before.

Persistence used to rewrite the whole document on every `track_item`, so a run
was O(n squared): 1 199 µs per item at a hundred items, 2 958 at a thousand.
One thousand items took three seconds and wrote 23 MiB to produce a 48 KiB
file, in the mode advertised for HPC clusters.

A ratio is asserted rather than an absolute time, so the test says the same
thing on a fast machine and a loaded CI runner.
"""

import json
import time

import pytest

import ackredit
from ackredit.core import session
from ackredit.core.collector import Collector


@pytest.fixture(autouse=True)
def _isolated():
    Collector.close_persistence()
    Collector.used_items.clear()
    Collector.used_targets.clear()
    Collector.usage_tree.clear()
    yield
    Collector.close_persistence()


def _cost_per_item(journal, count):
    Collector.enable_persistence(journal)
    start = time.perf_counter()
    for index in range(count):
        ackredit.track_item(f"item:{index}", used_by="caller")
    elapsed = time.perf_counter() - start
    Collector.close_persistence()
    return elapsed / count


def test_the_cost_per_item_does_not_grow_with_the_session(tmp_path):
    small = _cost_per_item(tmp_path / "small.jsonl", 200)

    Collector.used_items.clear()
    Collector.usage_tree.clear()
    large = _cost_per_item(tmp_path / "large.jsonl", 2000)

    # Ten times the items. Under the old design this ratio was about 2.5; a
    # constant-cost append keeps it near 1, and the bound is loose enough to
    # survive a noisy runner while still failing on a return to O(n).
    assert large < small * 2, (
        f"{small * 1e6:.1f} µs/item at 200 became {large * 1e6:.1f} µs at 2000; "
        "the per-item cost is growing with the session again"
    )


def test_the_journal_grows_by_one_line_per_event(tmp_path):
    """Bytes written stay proportional to events, not to events squared."""
    journal = tmp_path / "session.jsonl"
    Collector.enable_persistence(journal)
    for index in range(500):
        ackredit.track_item(f"item:{index}", used_by="caller")
    Collector.close_persistence()

    lines = [line for line in journal.read_text().splitlines() if line.strip()]

    assert len(lines) == 500 + 1  # the events, plus the schema header
    assert json.loads(lines[0])["schema"] == session.SCHEMA


def test_what_was_tracked_survives_the_round_trip(tmp_path):
    journal = tmp_path / "session.jsonl"
    Collector.enable_persistence(journal)
    for index in range(300):
        ackredit.track_item(f"item:{index}", used_by="caller")
    ackredit.track_target("some.target", parent=None)
    Collector.close_persistence()

    state = session.read(journal)

    assert len(state["used_items"]) == 300
    assert "some.target" in state["used_targets"]
    assert state["usage_tree"]["caller"]["items"] == {f"item:{i}" for i in range(300)}


def test_an_interrupted_run_keeps_every_complete_event(tmp_path):
    """A torn last line is what a killed process leaves. Everything before it
    is still good, so the journal is read up to the damage."""
    journal = tmp_path / "session.jsonl"
    Collector.enable_persistence(journal)
    for index in range(50):
        ackredit.track_item(f"item:{index}", used_by="caller")
    Collector.close_persistence()

    with journal.open("a") as handle:
        handle.write('{"e":"i","i":"truncated:')  # no newline, no closing brace

    state = session.read(journal)

    assert len(state["used_items"]) == 50


def test_a_session_written_before_journals_still_loads(tmp_path):
    """The format Ackredit wrote until this change."""
    legacy = tmp_path / "legacy.json"
    legacy.write_text(
        json.dumps(
            {
                "used_targets": ["old.target"],
                "used_items": {"old:1": ["old.target"]},
                "usage_tree": {"old.target": {"items": ["old:1"], "children": []}},
            }
        )
    )

    state = session.read(legacy)

    assert state["used_items"] == {"old:1": ["old.target"]}
    assert state["used_targets"] == {"old.target"}
