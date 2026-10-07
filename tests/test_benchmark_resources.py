"""Exercise the historical harness lifecycle without MolSysMT (#130)."""

from __future__ import annotations

import json
import os
import runpy
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

import pytest

from ackredit.core import session

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = runpy.run_path(str(ROOT / "devtools/benchmark.py"))
STABILITY = runpy.run_path(str(ROOT / "tests/test_api_stability.py"))

STUBS = textwrap.dedent(
    """
    import contextlib, json, os, pathlib, sys, tempfile, time, types
    settings = json.loads(os.environ['BENCHMARK_PROBE_SETTINGS'])
    events = []
    state = {'writer_closed': False, 'session_path': None}

    def noop(*args, **kwargs): return object()

    def enable(path):
        events.append('enable')
        state['session_path'] = str(path)
        path.write_text('synthetic session')
        if settings['failure'] == 'enable':
            raise RuntimeError('controlled enable failure')

    def close():
        events.append('close')
        assert pathlib.Path(state['session_path']).exists(), 'removed before close'
        state['writer_closed'] = True
        if settings['failure'] == 'close':
            raise RuntimeError('controlled close failure')

    def info(*args, **kwargs):
        if settings['failure'] == 'info':
            raise RuntimeError('controlled info failure')

    def clock():
        events.append('clock')
        return next(ticks)

    ticks = iter((10.0, 10.25))
    time.perf_counter = clock
    ack = types.ModuleType('ackredit')
    for name in ('register_item', 'bind', 'track_item'):
        setattr(ack, name, noop)
    ack.scope = lambda *args, **kwargs: contextlib.nullcontext()
    ack.enable_persistence, ack.close_persistence = enable, close
    msm = types.ModuleType('molsysmt')
    msm.systems = {'T4 lysozyme L99A': {'181l.pdb': 'synthetic input'}}
    for name in ('convert', 'get', 'select'):
        setattr(msm, name, noop)
    msm.info = info
    sys.modules.update(ackredit=ack, molsysmt=msm)

    if settings['cleanup_failure']:
        def remove(cls, name, **kwargs):
            events.append('cleanup')
            raise PermissionError('controlled cleanup failure')
        tempfile.TemporaryDirectory._rmtree = classmethod(remove)
    """
)


def probe(tmp_path, *, mode="persist", failure=None, cleanup_failure=False):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    output = tmp_path / "observations.json"
    source = textwrap.dedent(BENCHMARK["WORKFLOW"]).format(mode=mode)
    runner = STUBS + (
        f"\ntry:\n    exec({source!r})\n"
        "finally:\n"
        "    state['events'] = events\n"
        "    pathlib.Path(os.environ['BENCHMARK_PROBE_OUTPUT']).write_text(json.dumps(state))\n"
    )
    environment = dict(
        os.environ,
        TMPDIR=str(workspace),
        TEMP=str(workspace),
        TMP=str(workspace),
        BENCHMARK_PROBE_OUTPUT=str(output),
        BENCHMARK_PROBE_SETTINGS=json.dumps(
            {"failure": failure, "cleanup_failure": cleanup_failure}
        ),
    )
    result = subprocess.run(
        [sys.executable, "-c", runner],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=20,
    )
    assert output.exists(), result.stderr
    return result, json.loads(output.read_text()), workspace


@pytest.mark.parametrize("failure", [None, "enable", "info", "close"])
def test_persistence_fixture_closes_writer_and_cleans_on_both_outcomes(
    tmp_path, failure
):
    caller = tmp_path / "caller-session.json"
    caller.write_text("caller-owned evidence")
    result, observed, workspace = probe(tmp_path, failure=failure)
    if failure:
        assert result.returncode != 0
        assert f"controlled {failure} failure" in result.stderr
    else:
        assert result.returncode == 0, result.stderr
        assert float(result.stdout.strip()) == 0.25
    assert observed["writer_closed"]
    assert not Path(observed["session_path"]).exists()
    assert workspace.exists() and not list(workspace.iterdir())
    assert caller.read_text() == "caller-owned evidence"
    if failure != "enable":
        events = observed["events"]
        assert events.index("enable") < events.index("clock") < events.index("close")
        if failure is None or failure == "close":
            assert events.count("clock") == 2
            assert events[-1] == "close"


@pytest.mark.parametrize("mode", ["bare", "tracked"])
def test_other_modes_do_not_create_or_close_persistence(tmp_path, mode):
    result, observed, workspace = probe(tmp_path, mode=mode)
    assert result.returncode == 0, result.stderr
    assert float(result.stdout.strip()) == 0.25
    assert observed == {
        "writer_closed": False,
        "session_path": None,
        "events": ["clock", "clock"],
    }
    assert not list(workspace.iterdir())


@pytest.mark.parametrize("failure", [None, "info"])
def test_cleanup_failure_is_visible_after_writer_close(tmp_path, failure):
    result, observed, workspace = probe(tmp_path, failure=failure, cleanup_failure=True)
    assert result.returncode != 0
    assert "controlled cleanup failure" in result.stderr
    if failure:
        assert "controlled info failure" in result.stderr
    assert observed["writer_closed"]
    assert observed["events"][-2:] == ["close", "cleanup"]
    assert list(workspace.iterdir()), "probe must retain the failed removal"


@pytest.mark.parametrize("failure", ["read", "assertion"])
def test_session_contract_fixture_cleans_after_failure(tmp_path, monkeypatch, failure):
    seen = []

    def read(path):
        seen.append(Path(path))
        assert json.loads(Path(path).read_text())["used_items"] == {"a:1": ["run"]}
        if failure == "read":
            raise OSError("controlled session read failure")
        return {"used_items": {}}

    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    monkeypatch.setattr(session, "read", read)
    error = OSError if failure == "read" else AssertionError
    with pytest.raises(error):
        STABILITY["test_the_session_file_contract_is_stated_and_true"]()
    assert seen and not seen[0].exists()
    assert not list(tmp_path.iterdir())
