"""Concurrent workflows must not cross-attribute credit or corrupt their session.

Attribution is the whole product. A tracker that credits the wrong caller under
threads is worse than one that credits nothing, because the report looks complete.
"""

import json
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

import ackredit
from ackredit.core import session
from ackredit.core.collector import Collector
from ackredit.core.context import get_current_scope

# Every rendezvous is bounded. A concurrency test that deadlocks on failure hides
# the failure instead of reporting it, so barriers time out and raise BrokenBarrierError.
TIMEOUT = 10.0


def _isolated():
    """Clear the process-wide collector so a test sees only its own tracking."""
    Collector.used_items.clear()
    Collector.used_targets.clear()
    Collector.usage_tree.clear()
    Collector.close_persistence()


def test_scopes_are_isolated_between_threads():
    _isolated()
    started = threading.Barrier(8, timeout=TIMEOUT)

    def worker(index: int):
        with ackredit.scope(f"thread_{index}"):
            # Make every thread sit inside its scope at the same time, which is
            # what a shared class attribute could not survive.
            started.wait()
            ackredit.track_item(f"item_{index}")

    try:
        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(worker, range(8)))
    except threading.BrokenBarrierError:  # pragma: no cover - only on regression
        pytest.fail("threads could not rendezvous inside their scopes")

    used = ackredit.get_used_items()
    for index in range(8):
        assert used[f"item_{index}"] == [f"thread_{index}"]


def test_a_thread_does_not_leak_its_scope():
    _isolated()

    def worker():
        with ackredit.scope("worker_scope"):
            pass

    assert get_current_scope() is None
    thread = threading.Thread(target=worker)
    thread.start()
    thread.join()

    assert get_current_scope() is None


def test_the_main_scope_survives_a_concurrent_worker():
    _isolated()
    running = threading.Barrier(2, timeout=TIMEOUT)

    release = threading.Event()

    def worker():
        with ackredit.scope("other_thread"):
            running.wait()
            release.wait(TIMEOUT)

    thread = threading.Thread(target=worker)
    observed = None
    with ackredit.scope("main_scope"):
        thread.start()
        try:
            running.wait()
            # The worker is inside its own scope right now.
            observed = get_current_scope()
            ackredit.track_item("main_item")
        finally:
            # Release the worker whatever happened, so a failure reports itself
            # instead of hanging on join().
            release.set()
    thread.join(TIMEOUT)

    assert not thread.is_alive()
    assert observed == "main_scope"
    assert ackredit.get_used_items()["main_item"] == ["main_scope"]


def test_decorated_functions_are_isolated_too():
    _isolated()
    started = threading.Barrier(6, timeout=TIMEOUT)

    def make(index: int):
        @ackredit.scoped_usage(f"target_{index}")
        def run():
            started.wait()
            ackredit.track_item(f"decorated_{index}")

        return run

    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(lambda index: make(index)(), range(6)))

    used = ackredit.get_used_items()
    for index in range(6):
        assert used[f"decorated_{index}"] == [f"target_{index}"]


def test_nested_scopes_still_restore_within_one_thread():
    _isolated()

    with ackredit.scope("outer"):
        with ackredit.scope("inner"):
            assert get_current_scope() == "inner"
        assert get_current_scope() == "outer"
        ackredit.track_item("after_inner")
    assert get_current_scope() is None

    assert ackredit.get_used_items()["after_inner"] == ["outer"]


def test_a_raising_body_restores_the_previous_scope():
    _isolated()

    with ackredit.scope("outer"):
        try:
            with ackredit.scope("inner"):
                raise ValueError("boom")
        except ValueError:
            pass
        assert get_current_scope() == "outer"
    assert get_current_scope() is None


def test_no_tracked_item_is_lost_under_contention():
    _isolated()
    threads, per_thread = 12, 200

    def worker(index: int):
        for step in range(per_thread):
            ackredit.track_item("shared:item", used_by=f"caller_{index}_{step}")

    with ThreadPoolExecutor(max_workers=threads) as pool:
        list(pool.map(worker, range(threads)))

    assert len(ackredit.get_used_items()["shared:item"]) == threads * per_thread


def test_no_journal_line_is_ever_torn(tmp_path):
    """Threads append to one journal. A reader must find whole lines, always.

    The session used to be a document rewritten in full, and a concurrent
    reader saw a truncated one in 316 of 480 attempts. An appended line either
    is there or is not.
    """
    _isolated()
    journal = tmp_path / "session.jsonl"
    Collector.enable_persistence(journal)
    try:
        torn = []

        def worker(index: int):
            for step in range(40):
                ackredit.track_item(f"it_{index}_{step}", used_by=f"c{index}")
                for line in journal.read_text().splitlines():
                    if not line.strip():
                        continue
                    try:
                        json.loads(line)
                    except Exception as error:  # noqa: BLE001 - recorded, not swallowed
                        torn.append(f"{index}/{step}: {error}")

        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(worker, range(8)))

        assert not torn, f"{len(torn)} reads saw a torn line"
        assert len(session.read(journal)["used_items"]) == 8 * 40
    finally:
        Collector.close_persistence()


def test_no_temporary_files_are_left_behind(tmp_path):
    _isolated()
    journal = tmp_path / "session.jsonl"
    Collector.enable_persistence(journal)
    try:
        for index in range(20):
            ackredit.track_item(f"leftover_probe_{index}")
        assert [p.name for p in tmp_path.iterdir()] == ["session.jsonl"]
    finally:
        Collector.close_persistence()
