"""Keep the first reviewed portable contract readable without its producer."""

import inspect
import json
import subprocess
import sys
from pathlib import Path

import ackredit

FIXTURE = Path(__file__).parent / "data" / "attribution_v1_pyunitwizard.json"


def test_reviewed_public_call_shapes():
    assert not inspect.signature(ackredit.get_attribution).parameters
    for name in ("Attribution", "capture", "get_attribution"):
        assert name in ackredit.__all__
    capture = inspect.signature(ackredit.capture).parameters
    assert capture["name"].default == "capture"
    assert capture["context"].kind is inspect.Parameter.KEYWORD_ONLY
    tracking = inspect.signature(ackredit.track_item).parameters
    assert tracking["roles"].kind is inspect.Parameter.KEYWORD_ONLY
    assert tracking["context"].kind is inspect.Parameter.KEYWORD_ONLY


def test_v1_consumer_fixture_retains_original_records_and_detached_ownership():
    saved = json.loads(FIXTURE.read_text())
    restored = ackredit.Attribution.from_dict(saved)
    assert restored.to_dict() == saved
    assert ackredit.Attribution.from_json(restored.to_json()).to_dict() == saved
    copied = restored.to_dict()
    copied["items"].clear()
    saved["context"].clear()
    assert len(restored.to_dict()["items"]) == 2
    assert restored.to_dict()["context"]["version"] == "0.27.0"
    assert "10.21105/joss.00809" in restored.report(format="bibtex")
    assert ackredit.get_used_items() == {}


def test_v1_fresh_reader_needs_neither_original_engines_nor_network(tmp_path):
    script = """
import importlib.abc, json, pathlib, socket, sys
class NoOriginalEngine(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'pint', 'unyt', 'pyunitwizard'}:
            raise AssertionError('reader imported an original engine: ' + fullname)
sys.meta_path.insert(0, NoOriginalEngine())
def no_network(*args, **kwargs):
    raise AssertionError('reader attempted network access')
socket.create_connection = no_network
import ackredit
original = json.loads(pathlib.Path(sys.argv[1]).read_text())
saved = ackredit.Attribution.from_dict(original)
assert saved.to_dict() == original
assert saved.to_dict()['items'][0]['version'] == '3.1.0'
assert saved.to_dict()['uses'][1]['context']['version'] == '3.1.0'
assert '10.21105/joss.00809' in saved.report(format='bibtex')
assert ackredit.get_attribution().to_dict()['items'] == []
"""
    completed = subprocess.run(
        [sys.executable, "-c", script, str(FIXTURE)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
