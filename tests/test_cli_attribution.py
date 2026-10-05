"""Saved scientific attribution, consumed by the actual CLI in fresh processes."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

import ackredit

FIXTURE = Path(__file__).parent / "data" / "attribution_v1_pyunitwizard.json"


def run(path, *arguments, cwd):
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "ackredit.cli",
            "report",
            str(path),
            "--input-format",
            "attribution",
            *arguments,
        ],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )


@pytest.fixture
def saved(tmp_path):
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    payload["items"][0]["title"] = "unyt — original software"
    path = tmp_path / "result.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


@pytest.mark.parametrize("format", [*ackredit.available_formats(), "csl"])
def test_fresh_cli_uses_original_bibliography_and_every_format(saved, format, tmp_path):
    original = saved.read_bytes()
    expected = ackredit.Attribution.from_json(original.decode()).report(format=format)
    result = run(saved, "--format", format, cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout == expected + "\n"
    assert saved.read_bytes() == original
    assert ackredit.get_used_items() == {}


@pytest.mark.parametrize("format", ["bibtex", "csl-json", "workflow", "json"])
def test_export_retains_selected_format_and_original_input(saved, format, tmp_path):
    original = saved.read_bytes()
    output = tmp_path / "export.txt"
    output.write_text("previous report", encoding="utf-8")
    expected = ackredit.Attribution.from_json(original.decode()).report(format=format)
    result = run(saved, "-f", format, "-o", str(output), cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    assert output.read_text(encoding="utf-8") == expected
    assert saved.read_bytes() == original
    if format == "json":
        assert isinstance(json.loads(expected), list), "JSON remains bibliography"


def test_portable_cli_without_producer_network_or_live_recording(saved, tmp_path):
    script = """
import importlib.abc, json, pathlib, socket, sys
class NoProducer(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'pyunitwizard', 'pint', 'unyt'}:
            raise AssertionError('original producer imported: ' + fullname)
sys.meta_path.insert(0, NoProducer())
def forbidden(*args, **kwargs):
    raise AssertionError('reader performed network or live recording')
socket.create_connection = forbidden
socket.socket.connect = forbidden
import ackredit
from ackredit.core import collector, registry, session
original = ackredit.get_attribution().to_dict()
records = dict(registry.Registry.items)
collector.aggregate = collector.track_item = collector.track_target = forbidden
registry.register_item = session.read = forbidden
from ackredit.cli import main
sys.argv = ['ackredit', 'report', sys.argv[1], '--input-format', 'attribution',
            '--format', 'workflow']
assert main() == 0
assert ackredit.get_attribution().to_dict() == original
assert registry.Registry.items == records
"""
    result = subprocess.run(
        [sys.executable, "-c", script, str(saved)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    for original in (
        "3.1.0",
        "0.27.0",
        "executed_software",
        "software_description",
        "pyunitwizard.forms.unyt.convert",
        "10.21105/joss.00809",
    ):
        assert original in result.stdout.replace("\\_", "_")


@pytest.mark.parametrize(
    "content",
    [
        "{broken",
        "[]",
        '{"schema": "ackredit.attribution@2"}',
        '{"schema": "ackredit.session@1"}\n{"e":"i","i":"x"}',
        '{"used_items": {"x": []}, "usage_tree": {}}',
        json.dumps({**json.loads(FIXTURE.read_text()), "future_field": []}),
        json.dumps({**json.loads(FIXTURE.read_text()), "items": []}),
    ],
)
@pytest.mark.parametrize("existing_output", [False, True])
def test_invalid_portable_input_never_creates_or_replaces_output(
    content, existing_output, tmp_path
):
    path = tmp_path / "invalid.json"
    path.write_text(content, encoding="utf-8")
    output = tmp_path / "report.bib"
    if existing_output:
        output.write_bytes(b"previous report")
    result = run(path, "-f", "bibtex", "-o", str(output), cwd=tmp_path)
    assert result.returncode == 1
    assert "Cannot read attribution" in result.stderr
    assert "ackredit.attribution@1" in result.stderr
    assert result.stdout == ""
    assert (
        output.read_bytes() == b"previous report"
        if existing_output
        else not output.exists()
    )
    assert path.read_text(encoding="utf-8") == content


def test_unknown_format_preserves_output_and_is_diagnosed_once(saved, tmp_path):
    output = tmp_path / "report.bib"
    output.write_bytes(b"previous report")
    result = run(saved, "-f", "bibtext", "-o", str(output), cwd=tmp_path)
    assert result.returncode == 1
    assert "not a report format" in result.stderr
    assert result.stderr.count("bibtext") == 1
    assert output.read_bytes() == b"previous report"


@pytest.mark.parametrize("failure", ["missing", "directory", "encoding"])
def test_unreadable_inputs_have_catalog_diagnostics_and_create_nothing(
    failure, tmp_path
):
    path = tmp_path / "input"
    if failure == "directory":
        path.mkdir()
    elif failure == "encoding":
        path.write_bytes(b"\xff\xfe")
    output = tmp_path / "report"
    result = run(path, "-o", str(output), cwd=tmp_path)
    assert result.returncode == 1
    assert "Cannot read attribution at" in result.stderr
    assert result.stdout == ""
    assert not output.exists()


@pytest.mark.parametrize("failure", ["directory", "missing_parent"])
def test_export_io_failure_returns_nonzero(saved, failure, tmp_path):
    output = tmp_path if failure == "directory" else tmp_path / "absent" / "report"
    before = saved.read_bytes()
    result = run(saved, "-o", str(output), cwd=tmp_path)
    assert result.returncode == 1
    assert "Cannot export report at" in result.stderr
    assert result.stdout == ""
    assert saved.read_bytes() == before


@pytest.mark.parametrize("alias", ["same", "symlink", "hardlink"])
def test_export_refuses_input_aliases(saved, alias, tmp_path):
    original = saved.read_bytes()
    output = saved if alias == "same" else tmp_path / "alias.json"
    if alias == "symlink":
        output.symlink_to(saved)
    elif alias == "hardlink":
        output.hardlink_to(saved)
    result = run(saved, "-f", "bibtex", "-o", str(output), cwd=tmp_path)
    assert result.returncode == 1
    assert "refers to the input" in result.stderr
    assert saved.read_bytes() == output.read_bytes() == original


def test_empty_portable_record_is_a_valid_export(tmp_path):
    path = tmp_path / "empty.json"
    path.write_text(
        json.dumps(
            {
                "schema": "ackredit.attribution@1",
                "name": "empty result",
                "context": {},
                "items": [],
                "uses": [],
                "usage_tree": {},
            }
        ),
        encoding="utf-8",
    )
    result = run(path, "-f", "csl", cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == []


def test_session_mode_still_exports_its_identifier_report(tmp_path):
    path = tmp_path / "session.json"
    path.write_text(
        '{"schema":"ackredit.session@1"}\n{"e":"i","i":"original:id"}\n',
        encoding="utf-8",
    )
    output = tmp_path / "journal-report.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ackredit.cli",
            "report",
            str(path),
            "-f",
            "json",
            "-o",
            str(output),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(output.read_text())[0]["id"] == "original:id"


def test_file_failures_retain_structured_catalog_codes_and_facts(saved, tmp_path):
    from ackredit._private.smonitor.exceptions import (
        CliFileError,
        ReportInputOverwriteError,
    )
    from ackredit.cli import _attribution_report, _export_report

    missing = str(tmp_path / "missing")
    with pytest.raises(CliFileError) as caught:
        _attribution_report(missing, "bibtex")
    assert caught.value.code == "ACKREDIT-E013"
    assert caught.value.extra["path"] == missing
    assert caught.value.extra["error_type"] == "FileNotFoundError"
    with pytest.raises(ReportInputOverwriteError) as caught:
        _export_report("new report", str(saved), str(saved))
    assert caught.value.code == "ACKREDIT-E014"
    assert caught.value.extra["input"] == str(saved)
