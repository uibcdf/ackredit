"""The cost of tracking one more item must not depend on how many came before.

Persistence used to rewrite the whole document on every `track_item`, so a run
was O(n squared): 1 199 µs per item at a hundred items, 2 958 at a thousand.
One thousand items took three seconds and wrote 23 MiB to produce a 48 KiB
file, in the mode advertised for HPC clusters.

A ratio is asserted rather than an absolute time, so the test says the same
thing on a fast machine and a loaded CI runner.

Two rules make that ratio mean something on a machine we do not own. Both sides
measure **the same number of operations**, so their noise is comparable — the
first version compared 200 items against 2 000, and the smaller, noisier sample
set the threshold the larger one had to meet. And each side is the **minimum of
several repetitions**, because interference only ever adds time: the minimum is
the closest estimate of the real cost available here.
"""

import json
import time

import pytest

import ackredit
from ackredit.core import session
from ackredit.core.collector import Collector
from ackredit.core.session import current_session


@pytest.fixture(autouse=True)
def _isolated():
    Collector.close_persistence()
    current_session().clear()
    yield
    Collector.close_persistence()


# The same count on both sides, and enough repetitions for the minimum to mean
# something without the suite noticing the time.
MEASURED = 400
REPEATS = 3


def _cost_per_item(journal, existing: int) -> float:
    """Seconds per tracked item, in a session that already holds *existing*."""
    current_session().clear()
    Collector.enable_persistence(journal)
    for index in range(existing):
        ackredit.track_item(f"old:{index}", used_by="caller")

    start = time.perf_counter()
    for index in range(MEASURED):
        ackredit.track_item(f"new:{index}", used_by="caller")
    elapsed = time.perf_counter() - start

    Collector.close_persistence()
    return elapsed / MEASURED


def _best_cost_per_item(tmp_path, label: str, existing: int) -> float:
    return min(
        _cost_per_item(tmp_path / f"{label}{run}.jsonl", existing)
        for run in range(REPEATS)
    )


def test_the_cost_per_item_does_not_grow_with_the_session(tmp_path):
    empty = _best_cost_per_item(tmp_path, "empty", 0)
    full = _best_cost_per_item(tmp_path, "full", 4000)

    # The same 400 items, written into an empty session and into one holding
    # 4 000. Rewriting the document made the second cost 4 000 lines more than
    # the first; an append makes them the same.
    assert full < empty * 2, (
        f"{empty * 1e6:.1f} µs/item into an empty session became "
        f"{full * 1e6:.1f} µs into one holding 4 000; "
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


def test_crediting_one_more_caller_costs_the_same_at_ten_thousand():
    """`used_by not in callers` scanned a list, so an item reached from many
    call sites got slower with every one: 4.3 µs at 500 callers, 47.4 at 8 000.

    This is the realistic shape. The items credited most often are the central
    ones — a library's own paper, a numerical method — and `used_by` is a
    qualified function name, so every call site is another entry to scan.
    """
    ackredit.register_item(id="hot:item", title="Cited from everywhere")

    def cost(existing: int) -> float:
        """Seconds per call, for an item already credited to *existing* callers."""
        current_session().clear()
        for index in range(existing):
            ackredit.track_item("hot:item", used_by=f"old{index}")

        start = time.perf_counter()
        for index in range(MEASURED):
            ackredit.track_item("hot:item", used_by=f"new{index}")
        return (time.perf_counter() - start) / MEASURED

    few = min(cost(0) for _ in range(REPEATS))
    many = min(cost(5000) for _ in range(REPEATS))

    # The same 400 calls, against no callers and against 5 000. Scanning the
    # list meant thousands of comparisons per call in the second case, so a
    # return to it is enormous rather than marginal.
    assert many < few * 3, (
        f"{few * 1e6:.1f} µs/call against no callers became {many * 1e6:.1f} µs "
        "against 5 000; the cost is growing with the callers again"
    )


def test_the_order_callers_appeared_in_is_kept():
    """Reports show it, so the index may not replace the list."""
    current_session().clear()

    for caller in ("gamma", "alpha", "beta", "alpha"):
        ackredit.track_item("ordered:item", used_by=caller)

    assert ackredit.get_used_items()["ordered:item"] == ["gamma", "alpha", "beta"]


def test_the_journal_records_changes_not_calls(tmp_path):
    """Crediting the same pair in a loop is one fact, not five thousand."""
    current_session().clear()
    journal = tmp_path / "repeated.jsonl"
    Collector.enable_persistence(journal)
    for _ in range(5000):
        ackredit.track_item("same:item", used_by="same.caller")
    Collector.close_persistence()

    lines = [line for line in journal.read_text().splitlines() if line.strip()]

    assert len(lines) == 2  # the schema header, and one event
    assert session.read(journal)["used_items"] == {"same:item": ["same.caller"]}
