"""The command Ackredit ships, run the way a user runs it.

`ackredit` is a console script in the package's `entry_points` and the conda
recipe tests it — with `ackredit --help`, the only check that existed anywhere.
It passed while `ackredit aggregate` raised `AttributeError`, because it called
`Collector._save_state()`, removed by the persistence rewrite in #17. The
subcommand had been dead since then and nothing ran it.

`report` opened its input with `enable_persistence`, which exists to append and
therefore creates, so a mistyped name produced an empty journal, a report saying
the session held nothing, and a success exit code.

These run the real program in a real process, because every one of those
defects survived being read.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest


def run(*arguments, cwd) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "ackredit.cli", *arguments],
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def write_session(directory: Path, name: str, item: str, caller: str) -> Path:
    """A session file, written by a process that is not this one."""
    script = f"""
import ackredit
ackredit.register_item(id={item!r}, title="A Work")
ackredit.enable_persistence({name!r})
ackredit.track_item({item!r}, used_by={caller!r})
ackredit.close_persistence()
"""
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, cwd=directory
    )
    assert result.returncode == 0, result.stderr
    return directory / name


@pytest.fixture
def one(tmp_path):
    return write_session(tmp_path, "one.json", "a:1", "run")


@pytest.fixture
def two(tmp_path):
    return write_session(tmp_path, "two.json", "b:1", "other")


# --- reading must not write ----------------------------------------------


def test_a_missing_session_file_is_an_error(tmp_path):
    """It used to create the file, report emptiness and exit 0."""
    result = run("report", "nope.json", cwd=tmp_path)

    assert result.returncode == 1
    assert "no session file" in result.stderr
    assert not (tmp_path / "nope.json").exists(), "reading created the file"


def test_an_unreadable_session_file_is_an_error(tmp_path):
    (tmp_path / "bad.json").write_text("{not json at all")
    result = run("report", "bad.json", cwd=tmp_path)

    assert result.returncode == 1
    assert "could not be read" in result.stderr


def test_reporting_does_not_touch_the_file(one, tmp_path):
    before = one.read_bytes()
    assert run("report", "one.json", cwd=tmp_path).returncode == 0
    assert one.read_bytes() == before


# --- report ---------------------------------------------------------------


def test_the_report_names_what_the_session_credited(one, tmp_path):
    result = run("report", "one.json", cwd=tmp_path)
    assert result.returncode == 0
    assert "a:1" in result.stdout


def test_a_format_the_hardcoded_list_used_to_omit(one, tmp_path):
    """`json` was refused although available_formats() returns it."""
    result = run("report", "one.json", "--format", "json", cwd=tmp_path)

    assert result.returncode == 0
    (record,) = json.loads(result.stdout)
    assert record["id"] == "a:1"


def test_the_csl_alias_reaches_its_format(one, tmp_path):
    """`choices` would have refused the alias, so it is not used."""
    result = run("report", "one.json", "--format", "csl", cwd=tmp_path)
    assert result.returncode == 0
    assert json.loads(result.stdout)


def test_an_unknown_format_fails_and_says_what_exists(one, tmp_path):
    result = run("report", "one.json", "--format", "bibtext", cwd=tmp_path)

    assert result.returncode == 1
    assert "bibtex" in result.stderr, "the catalog names what to use instead"
    assert result.stderr.count("bibtext") == 1, "reported once, by the catalog"


def test_the_help_lists_every_format(one, tmp_path):
    import ackredit

    # argparse wraps to the terminal width, so `csl-json` can arrive split
    # across two lines. Undo the wrapping before looking for the names.
    help_text = re.sub(r"\n\s+", "", run("report", "--help", cwd=tmp_path).stdout)
    for name in ackredit.available_formats():
        assert name in help_text


# --- aggregate ------------------------------------------------------------


def test_aggregate_writes_a_session_holding_both(one, two, tmp_path):
    """The subcommand that raised AttributeError for every run since #17."""
    result = run("aggregate", "one.json", "two.json", "-o", "m.json", cwd=tmp_path)
    assert result.returncode == 0, result.stderr

    from ackredit.core import session

    merged = session.read(tmp_path / "m.json")
    assert sorted(merged["used_items"]) == ["a:1", "b:1"]


def test_aggregate_counts_what_it_merged_not_what_it_was_given(one, tmp_path):
    """ "Successfully merged N sessions" counted the arguments."""
    result = run("aggregate", "one.json", "gone.json", "-o", "m.json", cwd=tmp_path)

    assert "Merged 1 of 2" in result.stdout
    assert "gone.json" in result.stderr
    assert result.returncode == 1, "something the user asked for did not happen"


def test_aggregate_writes_nothing_when_it_can_read_nothing(tmp_path):
    result = run("aggregate", "gone.json", "-o", "m.json", cwd=tmp_path)

    assert result.returncode == 1
    assert not (tmp_path / "m.json").exists()


def test_aggregate_says_it_in_the_singular_for_one(one, tmp_path):
    result = run("aggregate", "one.json", "-o", "m.json", cwd=tmp_path)
    assert "1 of 1 session file into" in result.stdout
    assert "(1 citation)" in result.stdout


# --- dump -----------------------------------------------------------------


def test_dump_writes_the_reports(one, tmp_path):
    result = run("dump", "one.json", "out", cwd=tmp_path)

    assert result.returncode == 0
    written = sorted(path.name for path in (tmp_path / "out").iterdir())
    assert "ackredit_report.bib" in written
    assert "ackredit_report.md" in written


def test_dump_refuses_a_missing_session(tmp_path):
    assert run("dump", "gone.json", "out", cwd=tmp_path).returncode == 1
    assert not (tmp_path / "out").exists()


# --- the program itself ---------------------------------------------------


def test_running_it_with_no_command_shows_the_help(tmp_path):
    result = run(cwd=tmp_path)
    assert result.returncode == 0
    assert "aggregate" in result.stdout


def test_the_entry_point_in_pyproject_resolves(tmp_path):
    """The console script is what a user installs, not `python -m`."""
    import tomllib

    root = Path(__file__).resolve().parents[1]
    scripts = tomllib.loads((root / "pyproject.toml").read_text())["project"]["scripts"]
    module, _, function = scripts["ackredit"].partition(":")

    import importlib

    assert callable(getattr(importlib.import_module(module), function))
