"""A session is what one run tracked. There can be more than one.

Tracking state used to be class attributes, one set per interpreter, so a
notebook could not start a fresh count between cells, a host library could not
keep its tracking apart from its user's, and nothing could produce two reports
in one process. The only available workaround was reaching into internals:

    Collector.used_items.clear()

Declarations and observations are scoped differently on purpose. `Registry`
holds what *could* be cited and stays shared, because a host library registers
it once at import. A session holds what *was* used.
"""

import time
from concurrent.futures import ThreadPoolExecutor

import pytest

import ackredit
from ackredit.core.session import current_session


@pytest.fixture(autouse=True)
def _clean():
    current_session().clear()
    ackredit.register_item(id="p:1", title="One")
    ackredit.register_item(id="p:2", title="Two")
    yield
    current_session().clear()


def test_a_session_does_not_leak_into_the_one_around_it():
    ackredit.track_item("p:1", used_by="outer")

    with ackredit.session("inner"):
        ackredit.track_item("p:2", used_by="inner")
        assert list(ackredit.get_used_items()) == ["p:2"]

    assert list(ackredit.get_used_items()) == ["p:1"]


def test_the_enclosing_session_is_restored_after_an_exception():
    with pytest.raises(ValueError):
        with ackredit.session("failing"):
            ackredit.track_item("p:2", used_by="inner")
            raise ValueError("boom")

    assert current_session().name == "default"
    assert list(ackredit.get_used_items()) == []


def test_declarations_stay_shared():
    """A host library registers what it can cite once, at import."""
    with ackredit.session():
        ackredit.register_item(id="p:3", title="Registered inside")

    assert "p:3" in ackredit.Registry.items


def test_inherit_starts_from_what_is_already_tracked():
    ackredit.track_item("p:1", used_by="before")

    with ackredit.session(inherit=True):
        assert list(ackredit.get_used_items()) == ["p:1"]
        ackredit.track_item("p:2", used_by="inside")
        assert sorted(ackredit.get_used_items()) == ["p:1", "p:2"]

    # Inheriting copies; it does not alias.
    assert list(ackredit.get_used_items()) == ["p:1"]


def test_sessions_are_isolated_between_threads():
    """Entering a session is context-local, so a thread that does not enter one
    keeps recording where it was."""
    seen = {}

    def worker(index: int):
        with ackredit.session(f"t{index}"):
            ackredit.track_item("p:1", used_by=f"w{index}")
            time.sleep(0.01)
            seen[index] = ackredit.get_used_items()["p:1"]

    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(worker, range(6)))

    for index in range(6):
        assert seen[index] == [f"w{index}"]
    assert ackredit.get_used_items() == {}


def test_a_report_describes_only_its_own_session():
    ackredit.track_item("p:1", used_by="outer")

    with ackredit.session():
        ackredit.track_item("p:2", used_by="inner")
        inside = ackredit.report(format="markdown")

    assert "Two" in inside
    assert "One" not in inside


def test_the_journal_of_a_session_closes_with_it(tmp_path):
    journal = tmp_path / "run.jsonl"

    with ackredit.session("recorded"):
        ackredit.enable_persistence(journal)
        ackredit.track_item("p:1", used_by="inside")

    # Leaving the block closed it; the default session has no journal.
    assert current_session().journal_path is None
    assert journal.exists()


def test_the_default_session_still_needs_no_ceremony():
    """The ergonomics the global was there for must survive."""
    ackredit.track_item("p:1", used_by="plain")

    assert ackredit.get_used_items() == {"p:1": ["plain"]}
    assert "One" in ackredit.report()


def test_collector_reads_whichever_session_is_current():
    """`Collector.used_items` is a published name; what changes is which
    session answers it."""
    from ackredit.core.collector import Collector

    ackredit.track_item("p:1", used_by="outer")
    assert list(Collector.used_items) == ["p:1"]

    with ackredit.session():
        assert list(Collector.used_items) == []
