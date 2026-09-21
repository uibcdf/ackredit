"""Several processes may write one session, because a journal is appended to.

This file used to assert a warning. The session was a document rewritten in
full, so two processes sharing a path meant the last writer won and the other's
citations vanished — four processes kept 106 of 240 items. A journal cannot
lose them: POSIX makes an O_APPEND write below PIPE_BUF atomic, and an event
line is far below it.

That guarantee is a local-filesystem one. NFS does not provide it, so a network
filesystem still wants one journal per process, which `aggregate` merges.
"""

import json
import subprocess
import sys
import textwrap

import pytest

import ackredit
from ackredit.core import session
from ackredit.core.collector import Collector

WORKER = textwrap.dedent(
    """
    import sys
    sys.path.insert(0, {root!r})
    import ackredit
    from ackredit.core.collector import Collector

    path, tag, count = sys.argv[1], sys.argv[2], int(sys.argv[3])
    Collector.enable_persistence(path)
    for index in range(count):
        ackredit.track_item(f"{{tag}}:item{{index}}", used_by=f"worker-{{tag}}")
    Collector.close_persistence()
    """
)


@pytest.fixture(autouse=True)
def _isolated():
    Collector.close_persistence()
    Collector.used_items.clear()
    Collector.used_targets.clear()
    Collector.usage_tree.clear()
    yield
    Collector.close_persistence()


def _run_workers(tmp_path, journal, processes, per_process, tag_prefix="p"):
    script = tmp_path / "worker.py"
    script.write_text(
        WORKER.format(
            root=str(__import__("pathlib").Path(ackredit.__file__).parents[1])
        )
    )
    running = [
        subprocess.Popen(
            [
                sys.executable,
                str(script),
                str(journal),
                f"{tag_prefix}{index}",
                str(per_process),
            ]
        )
        for index in range(processes)
    ]
    for process in running:
        assert process.wait() == 0


def test_processes_sharing_one_journal_lose_nothing(tmp_path):
    """The case that used to keep 106 of 240 items."""
    journal = tmp_path / "shared.jsonl"
    _run_workers(tmp_path, journal, processes=4, per_process=60)

    state = session.read(journal)

    assert len(state["used_items"]) == 240
    assert {key.split(":")[0] for key in state["used_items"]} == {
        "p0",
        "p1",
        "p2",
        "p3",
    }


def test_no_line_is_torn_by_a_concurrent_writer(tmp_path):
    journal = tmp_path / "shared.jsonl"
    _run_workers(tmp_path, journal, processes=4, per_process=60)

    lines = [line for line in journal.read_text().splitlines() if line.strip()]
    events = []
    for line in lines:
        parsed = json.loads(line)  # raises if a write was interleaved
        if "e" in parsed:
            events.append(parsed)

    assert len(events) == 240
    # Concurrent openers may each write a schema line; the reader ignores the
    # extras, and serialising that would need a cross-process lock.
    assert json.loads(lines[0])["schema"] == session.SCHEMA


def test_one_journal_per_process_still_merges(tmp_path):
    """The pattern a network filesystem needs, and what `ackredit merge` does."""
    journals = []
    for index in range(4):
        journal = tmp_path / f"session_{index}.jsonl"
        _run_workers(
            tmp_path, journal, processes=1, per_process=15, tag_prefix=f"q{index}"
        )
        journals.append(str(journal))

    Collector.aggregate(journals)

    assert len(Collector.used_items) == 60
    assert {key.split(":")[0] for key in Collector.used_items} == {
        "q00",
        "q10",
        "q20",
        "q30",
    }


def test_reopening_a_journal_adopts_what_it_holds(tmp_path):
    journal = tmp_path / "resume.jsonl"
    Collector.enable_persistence(journal)
    ackredit.track_item("before:1", used_by="caller")
    Collector.close_persistence()

    Collector.used_items.clear()
    Collector.enable_persistence(journal)

    assert "before:1" in ackredit.get_used_items()

    ackredit.track_item("after:1", used_by="caller")
    Collector.close_persistence()

    state = session.read(journal)
    assert set(state["used_items"]) == {"before:1", "after:1"}
