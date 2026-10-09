"""Guard actual benchmark tracing custody with inert callbacks (#131)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROBE = r"""
import json, runpy, sys, tracemalloc
from types import ModuleType
from pathlib import Path
root = Path(sys.argv[1])
case = json.loads(sys.argv[2])
sys.path.insert(0, str(root / 'devtools'))
import benchmark_lifecycle as lifecycle
lifecycle.identities = lambda: {}
fake = ModuleType('ackredit')
class Observer:
    def __enter__(self):
        if case.get('fail'): raise RuntimeError('controlled callback failure')
    def __exit__(self, *args): pass
fake.observe_calls = lambda module: Observer()
fake.register_item = lambda **kwargs: None
fake.get_used_items = lambda: {}
def load(): raise RuntimeError('controlled callback failure')
fake.load_plugins = load
sys.modules['ackredit'] = fake
core = ModuleType('ackredit.core')
registry = ModuleType('ackredit.core.registry')
registry.Registry = object
sys.modules['ackredit.core'] = core
sys.modules['ackredit.core.registry'] = registry
if case['caller']: tracemalloc.start()
error = None
result = None
try:
    try:
        if case['operation'] == 'worker':
            result = lifecycle.worker({'kind': 'activation', 'size': 1}, case['memory'])
        elif case['operation'] == 'plugin':
            tools = runpy.run_path(str(root / 'devtools/benchmark_plugins.py'))
            tools['operations']({'packs': {}}, memory=True)
        else:
            stages = lifecycle.Stages(True)
            assert stages.call('sample', lambda: 'unchanged') == 'unchanged'
            values = stages.finish()
            assert set(values['sample']) == {'retained_delta_bytes', 'peak_extra_bytes'}
            assert not tracemalloc.is_tracing()
            tracemalloc.start()  # New caller session after the owned one closed.
            assert stages.finish() is values
    except RuntimeError as exc:
        error = str(exc)
    observed = tracemalloc.is_tracing()
    if result is not None:
        expected = {'retained_delta_bytes', 'peak_extra_bytes'} if case['memory'] else {'elapsed_us'}
        assert all(set(v) == expected for v in result['measurements'].values())
    assert not any(name in sys.modules for name in ('numpy', 'pyunitwizard', 'pint', 'unyt', 'molsysmt'))
    print(json.dumps({'tracing_after': observed, 'error': error}))
finally:
    tracemalloc.stop()
"""


def probe(case):
    result = subprocess.run(
        [sys.executable, "-S", "-c", PROBE, str(ROOT), json.dumps(case)],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    return json.loads(result.stdout)


@pytest.mark.parametrize(
    ("caller", "fail", "memory"),
    [
        (False, False, True),
        (True, False, True),
        (False, True, True),
        (True, True, True),
        (True, False, False),
        (True, True, False),
    ],
)
def test_worker_preserves_caller_and_releases_owned_tracing(caller, fail, memory):
    result = probe(dict(operation="worker", caller=caller, fail=fail, memory=memory))
    assert result["tracing_after"] is caller
    assert result["error"] == ("controlled callback failure" if fail else None)


@pytest.mark.parametrize("caller", [False, True])
def test_plugin_callback_failure_releases_only_owned_tracing(caller):
    result = probe(dict(operation="plugin", caller=caller, fail=True, memory=True))
    assert result["tracing_after"] is caller
    assert result["error"] == "controlled callback failure"


def test_repeated_finish_preserves_a_new_caller_session():
    result = probe(dict(operation="finish", caller=False, memory=True))
    assert result["tracing_after"] is True
    assert result["error"] is None
